/**
 * 轻量 Markdown 渲染器（跨端）
 * 小程序不支持 v-html，输出内联样式 HTML 给 <rich-text>:nodes 使用
 * 限制：不支持 class 选择器，一律使用 px 内联样式
 */

/** HTML 转义（防注入 + 避免与渲染产物冲突） */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/** 渲染围栏代码块 */
function renderFence(lang, code) {
  const escaped = escapeHtml(code.replace(/\n$/, ''))
  const lines = escaped
    .split('\n')
    .map((line) => line.replace(/^(\s+)/, (m) => m.replace(/ /g, '&nbsp;')))
  return (
    '<div style="background-color:#F6F3EE;padding:12px 14px;border-radius:6px;' +
    'font-family:monospace;font-size:13px;line-height:1.6;color:#5B665F;word-break:break-all;">' +
    lines.join('<br/>') +
    '</div>'
  )
}

/** 渲染行内代码 */
function renderInlineCode(code) {
  return (
    '<code style="background-color:#EFEAE2;color:#C73E2D;padding:2px 6px;' +
    'border-radius:4px;font-family:monospace;font-size:13px;">' +
    escapeHtml(code) +
    '</code>'
  )
}

/**
 * 行内语法渲染：行内代码 → 链接 → 粗体 → 删除线 → 斜体
 * 输入必须已 HTML 转义
 */
function renderInline(text) {
  const placeholders = []
  // 先保护行内代码，避免其内部的 * _ [] 被误渲染
  text = text.replace(/`([^`]+)`/g, (m, code) => {
    const idx = placeholders.length
    placeholders.push(renderInlineCode(code))
    return `\u0001INLINE_${idx}\u0001`
  })

  // 链接 [text](url)
  text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, label, url) => {
    const linkUrl = url.replace(/"/g, '&quot;')
    return `<a href="${linkUrl}" style="color:#C8442F;text-decoration:underline;">${label}</a>`
  })

  // 粗体 **text** / __text__
  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong style="font-weight:700;">$1</strong>')
  text = text.replace(/__([^_]+)__/g, '<strong style="font-weight:700;">$1</strong>')

  // 删除线 ~~text~~
  text = text.replace(/~~([^~]+)~~/g, '<del style="text-decoration:line-through;">$1</del>')

  // 斜体 *text*（避免误伤被 * 包裹的普通文本时，要求两侧不能是单词字符）
  text = text.replace(/(^|[^*\w])\*([^*\n]+)\*([^*\w]|$)/g, '$1<em style="font-style:italic;">$2</em>$3')

  // 还原行内代码
  text = text.replace(/\u0001INLINE_(\d+)\u0001/g, (m, i) => placeholders[Number(i)] || '')
  return text
}

/** 渲染表格 */
function renderTable(lines) {
  const cellStyle = 'border:1px solid #E7E2D9;padding:6px 8px;font-size:13px;line-height:1.5;'
  const headStyle = 'border:1px solid #E7E2D9;padding:6px 8px;font-size:13px;line-height:1.5;background-color:#F6F3EE;color:#202A24;font-weight:700;'

  const splitCells = (line) => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim())

  const header = splitCells(lines[0])
  const body = lines.slice(2).filter((l) => l.trim())

  let html = '<table style="width:100%;border-collapse:collapse;margin:8px 0;">'
  html += '<tr>' + header.map((c) => `<th style="${headStyle}">${renderInline(c)}</th>`).join('') + '</tr>'
  for (const line of body) {
    html += '<tr>' + splitCells(line).map((c) => `<td style="${cellStyle}">${renderInline(c)}</td>`).join('') + '</tr>'
  }
  html += '</table>'
  return html
}

/** 是否为表格分隔行（如 |---|---|） */
function isTableSeparator(line) {
  return /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(line) && line.includes('-')
}

/**
 * 渲染单个文本块（段落 / 标题 / 列表 / 引用等）
 * @param {String} block 已转义的文本块
 * @param {Function} restoreCode 还原代码占位符
 */
function renderBlock(block, restoreCode) {
  const trimmed = block.trim()
  if (!trimmed) return ''
  const lines = trimmed.split('\n')

  // 围栏代码占位符（提前抽取，原样返回）
  const codeMatch = trimmed.match(/^%%MDBLOCK_(\d+)%%$/g)
  if (codeMatch && /^%%MDBLOCK_\d+%%$/.test(trimmed)) {
    return restoreCode(trimmed)
  }

  // 标题
  const heading = lines[0].match(/^(#{1,6})\s+(.*)$/)
  if (heading && lines.length === 1) {
    const level = heading[1].length
    const sizes = { 1: 20, 2: 18, 3: 16, 4: 15, 5: 14, 6: 14 }
    return (
      `<h${level} style="font-size:${sizes[level]}px;font-weight:700;color:#202A24;` +
      `margin:10px 0 6px;line-height:1.5;">${renderInline(heading[2])}</h${level}>`
    )
  }

  // 分隔线
  if (/^\s*([-*_])\s*\1\s*\1+\s*$/.test(trimmed) && lines.length === 1) {
    return '<hr style="border:none;border-top:1px solid #E7E2D9;margin:10px 0;" />'
  }

  // 表格（标题行 + 分隔行 + 数据行）
  if (lines.length >= 2 && isTableSeparator(lines[1]) && lines[0].includes('|')) {
    return renderTable(lines)
  }

  // 引用块（连续 > 开头行）
  if (lines.every((l) => /^\s*>/.test(l))) {
    const quoteContent = lines.map((l) => renderInline(l.replace(/^\s*>\s?/, ''))).join('<br/>')
    return (
      '<blockquote style="border-left:3px solid #C8442F;background-color:#F6F3EE;' +
      `padding:8px 12px;margin:8px 0;color:#5B665F;font-size:14px;line-height:1.7;` +
      `">${quoteContent}</blockquote>`
    )
  }

  // 无序列表
  if (lines.every((l) => /^\s*[-*+]\s+/.test(l))) {
    const items = lines
      .map((l) => `<li style="margin:4px 0;line-height:1.7;">${renderInline(l.replace(/^\s*[-*+]\s+/, ''))}</li>`)
      .join('')
    return `<ul style="padding-left:18px;margin:8px 0;font-size:14px;color:#202A24;">${items}</ul>`
  }

  // 有序列表
  if (lines.every((l) => /^\s*\d+\.\s+/.test(l))) {
    const items = lines
      .map((l) => `<li style="margin:4px 0;line-height:1.7;">${renderInline(l.replace(/^\s*\d+\.\s+/, ''))}</li>`)
      .join('')
    return `<ol style="padding-left:18px;margin:8px 0;font-size:14px;color:#202A24;">${items}</ol>`
  }

  // 普通段落（段内单换行转 <br/>）
  const inline = lines.map((l) => renderInline(l.trim())).join('<br/>')
  return `<div style="margin:8px 0;font-size:14px;line-height:1.7;color:#202A24;word-break:break-all;">${inline}</div>`
}

/**
 * 将 Markdown 文本渲染为适合 <rich-text>:nodes 的 HTML 字符串
 */
export function renderMarkdown(content) {
  if (!content) return ''
  let source = String(content)

  // 1. 先抽取围栏代码块（内容保持原始形态独立渲染）
  const codeBlocks = []
  source = source.replace(/```[^\n]*\n?([\s\S]*?)```/g, (m, code) => {
    const idx = codeBlocks.length
    codeBlocks.push(renderFence('', code))
    return `\n\n%%MDBLOCK_${idx}%%\n\n`
  })

  // 2. 整体转义
  source = escapeHtml(source)

  const restoreCode = (placeholder) => {
    const m = placeholder.match(/%%MDBLOCK_(\d+)%%/)
    return m ? codeBlocks[Number(m[1])] : ''
  }

  // 3. 按空行切块渲染
  return source
    .split(/\n{2,}/)
    .map((block) => renderBlock(block, restoreCode))
    .filter(Boolean)
    .join('')
}