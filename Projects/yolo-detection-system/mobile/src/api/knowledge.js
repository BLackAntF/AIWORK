/**
 * 知识库与 AI 问答接口
 */
import { request, BASE_URL, buildHeader } from './request'

/** AI 问答（支持图片上下文） */
export function askQuestion(data) {
  return request({ url: '/knowledge/ask', method: 'POST', data })
}

/**
 * SSE 流式问答
 * @param {Object} data - 与 askQuestion 相同的入参，内部自动附加 stream: true
 * @param {Function} onDelta - 收到增量文本回调 (text) => void
 * @returns {Promise<Object>} 解析后端 done 事件 payload（answer/sources/session_id 等）
 *   若未收到任何 delta 或平台不支持流式，reject Error('NO_DELTA')，调用方回退非流式
 */
export function askQuestionStream(data, onDelta) {
  const url = BASE_URL + '/knowledge/ask'
  const payload = { ...data, stream: true }
  const header = buildHeader({ Accept: 'text/event-stream' })

  // #ifdef H5
  return streamFetch(url, payload, header, onDelta)
  // #endif

  // #ifdef MP-WEIXIN
  return streamChunked(url, payload, header, onDelta)
  // #endif

  // #ifndef H5
  // #ifndef MP-WEIXIN
  return Promise.reject(new Error('NO_DELTA'))
  // #endif
  // #endif
}

/**
 * H5：fetch + ReadableStream 解析 SSE
 */
function streamFetch(url, payload, header, onDelta) {
  return new Promise((resolve, reject) => {
    const doneRef = { payload: null, error: '' }
    const dispatch = makeDispatcher(onDelta, doneRef)
    let receivedDelta = false
    let buffer = ''

    fetch(url, {
      method: 'POST',
      headers: header,
      body: JSON.stringify(payload)
    })
      .then((response) => {
        if (!response.ok || !response.body) {
          throw new Error('网络错误 ' + response.status)
        }
        const reader = response.body.getReader()
        const decoder = new TextDecoder('utf-8')

        function pump() {
          reader.read().then(({ done, value }) => {
            if (done) {
              dispatch(parseEvent(buffer))
              buffer = ''
              settleStream(receivedDelta, doneRef, resolve, reject)
              return
            }
            buffer += decoder.decode(value, { stream: true })
            const events = extractEvents(buffer)
            buffer = events.rest
            for (const evt of events.list) {
              if (evt.type === 'delta') receivedDelta = true
              dispatch(evt)
            }
            pump()
          }).catch((err) => {
            settleStream(receivedDelta, doneRef, resolve, reject, err)
          })
        }

        pump()
      })
      .catch((err) => {
        reject(err)
      })
  })
}

/**
 * 微信小程序：uni.request enableChunked + onChunkReceived 解析 SSE
 * 自定义增量 UTF-8 解码，避免多字节字符被 chunk 截断
 */
function streamChunked(url, payload, header, onDelta) {
  return new Promise((resolve, reject) => {
    const doneRef = { payload: null, error: '' }
    const dispatch = makeDispatcher(onDelta, doneRef)
    let receivedDelta = false
    let buffer = ''
    let pendingBytes = []

    function appendChunk(bytes, flush = false) {
      pendingBytes = pendingBytes.concat(Array.from(new Uint8Array(bytes)))
      const text = utf8Decode(pendingBytes, flush)
      pendingBytes = text.rest
      buffer += text.str
      const events = extractEvents(buffer)
      buffer = events.rest
      for (const evt of events.list) {
        if (evt.type === 'delta') receivedDelta = true
        dispatch(evt)
      }
    }

    const task = uni.request({
      url,
      method: 'POST',
      data: payload,
      header,
      enableChunked: true,
      responseType: 'arraybuffer',
      success: (res) => {
        if (res.statusCode < 200 || res.statusCode >= 300) {
          if (!receivedDelta) reject(new Error('网络错误 ' + res.statusCode))
          else resolve(doneRef.payload || {})
          return
        }
        if (res.data && res.data.byteLength > 0) {
          appendChunk(res.data, true)
        }
        dispatch(parseEvent(buffer))
        buffer = ''
        settleStream(receivedDelta, doneRef, resolve, reject)
      },
      fail: (err) => {
        if (!receivedDelta) reject(new Error('NO_DELTA'))
        else resolve(doneRef.payload || {})
      }
    })

    if (task && task.onChunkReceived) {
      task.onChunkReceived((res) => {
        if (res && res.data) appendChunk(res.data)
      })
    }
  })
}

/**
 * 流式收尾：无 delta 时回退非流式；流式 error 事件优先报错
 */
function settleStream(receivedDelta, doneRef, resolve, reject, err) {
  if (doneRef.error) {
    reject(new Error(doneRef.error))
  } else if (err) {
    if (!receivedDelta) reject(err)
    else resolve(doneRef.payload || {})
  } else if (!receivedDelta) {
    reject(new Error('NO_DELTA'))
  } else {
    resolve(doneRef.payload || {})
  }
}

/** 构造事件分发器（每次请求独立闭包，避免跨请求串数据） */
function makeDispatcher(onDelta, doneRef) {
  return function dispatch(evt) {
    if (!evt) return
    if (evt.type === 'delta') {
      onDelta(evt.text || '')
    } else if (evt.type === 'done') {
      doneRef.payload = evt
    } else if (evt.type === 'error') {
      doneRef.error = evt.message || '回答生成失败'
    }
  }
}

/** 增量 UTF-8 解码：str + 未解码完的字节数组 */
function utf8Decode(bytesArr, flush) {
  const view = new Uint8Array(bytesArr)
  let text = ''
  let consumed = view.length
  for (let i = 0; i < view.length; i++) {
    const b = view[i]
    let seqLen = 0
    if (b < 0x80) seqLen = 1
    else if ((b & 0xE0) === 0xC0) seqLen = 2
    else if ((b & 0xF0) === 0xE0) seqLen = 3
    else if ((b & 0xF8) === 0xF0) seqLen = 4
    else seqLen = 1

    if (i + seqLen > view.length) {
      consumed = i
      break
    }
    let codePoint = 0
    if (seqLen === 1) {
      codePoint = b
    } else {
      codePoint = b & (0xFF >> (seqLen + 1))
      for (let j = 1; j < seqLen; j++) {
        codePoint = (codePoint << 6) | (view[i + j] & 0x3F)
      }
    }
    text += String.fromCodePoint(codePoint)
    i += seqLen - 1
  }
  if (flush && consumed < view.length) {
    consumed = view.length
  }
  return { str: text, rest: Array.from(view.slice(consumed)) }
}

/** 按 \n\n 切分 SSE 事件，返回事件列表与剩余 buffer */
function extractEvents(buffer) {
  const list = []
  const parts = buffer.split('\n\n')
  const rest = parts.pop() || ''
  for (const part of parts) {
    const evt = parseEvent(part)
    if (evt) list.push(evt)
  }
  return { list, rest }
}

/** 解析单个 SSE 事件块：取 data: 前缀的 JSON */
function parseEvent(block) {
  const lines = block.split('\n')
  let data = ''
  for (const line of lines) {
    if (line.startsWith('data:')) {
      data += line.slice(5).trim()
    }
  }
  if (!data) return null
  try {
    return JSON.parse(data)
  } catch (e) {
    return null
  }
}

/** 获取会话列表 */
export function getSessionList() {
  return request({ url: '/knowledge/sessions' })
}

/** 获取会话聊天历史 */
export function getChatHistory(sessionId, params = {}) {
  return request({ url: '/knowledge/history', data: { session_id: sessionId, ...params } })
}

/** 删除会话 */
export function deleteSession(sessionId) {
  return request({ url: `/knowledge/session/${sessionId}`, method: 'DELETE' })
}

/** 获取知识库列表 */
export function getKnowledgeList(params) {
  return request({ url: '/knowledge/list', data: params })
}

/** 获取知识详情 */
export function getKnowledgeDetail(id) {
  return request({ url: `/knowledge/${id}` })
}

/** 获取相关知识 */
export function getRelatedKnowledge(id, params) {
  return request({ url: `/knowledge/${id}/related`, data: params })
}

/** 获取分类列表 */
export function getCategories() {
  return request({ url: '/knowledge/category-list' })
}

/** 获取病害档案列表 */
export function getDiseaseProfileList(params) {
  return request({ url: '/disease-profiles', data: params })
}

/** 按病害类别 ID 获取档案详情 */
export function getDiseaseProfile(classId) {
  return request({ url: `/disease-profiles/${classId}` })
}
