import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({
  breaks: true,
  gfm: true
})

const entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;'
}

function escapeHtml(string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return entityMap[s]
  })
}

const renderer = new marked.Renderer()

const originalLink = renderer.link.bind(renderer)
renderer.link = function (href, title, text) {
  const html = originalLink(href, title, text)
  return html.replace('<a', '<a target="_blank" rel="noopener noreferrer"')
}

const originalCode = renderer.code.bind(renderer)
renderer.code = function (code, language, isEscaped) {
  const escapedCode = escapeHtml(code)
  return `<pre><code class="language-${language}">${escapedCode}</code></pre>`
}

marked.use({ renderer })

export function renderMarkdown(content) {
  if (!content) return ''
  try {
    // marked 输出经 DOMPurify 消毒，防存储型 XSS（知识内容可由用户上传）
    return DOMPurify.sanitize(marked.parse(content))
  } catch (e) {
    return escapeHtml(content)
  }
}
