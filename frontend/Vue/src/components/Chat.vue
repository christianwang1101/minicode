<template>
  <div class="chat-panel">
    <div class="messages" ref="messagesContainer">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="message"
        :class="m.role"
        :style="m.role === 'user' ? { '--msg-border': uiState.mode === 'plan' ? '#a371f7' : '#58a6ff' } : {}"
      >
        <div v-if="m.role !== 'user'" class="role-label">ASSISTANT：</div>

        <div class="content-bubble" :class="m.role === 'user' ? 'user-bubble' : ''">
          <div v-if="m.text" class="text" v-html="mdToHtml(m.text)"></div>

          <div v-if="m.thinking" class="thinking">
            🧠 {{ m.thinking }}
          </div>

          <div v-if="m.tools && m.tools.length" class="tools">
            <div
              v-for="(t, j) in m.tools"
              :key="j"
              class="tool"
              :class="t.type"
            >
              <div v-if="t.type === 'call'" class="tool-call">
                ▶ {{ t.name }}({{ JSON.stringify(t.args) }})
              </div>
              <div v-else class="tool-result"><pre class="tool-pre">{{ t.content }}</pre></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <InputBox @send="handleSend" />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { streamChat } from '../api/chat'
import InputBox from './InputBox.vue'
import { uiState } from '../stores/uiState'
import { uiActions } from '../stores/uiActions'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  html: true,
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre><code class="hljs language-${lang}">${hljs.highlight(code, { language: lang }).value}</code></pre>`
      } catch (_) {}
    }
    try {
      return `<pre><code class="hljs">${hljs.highlightAuto(code).value}</code></pre>`
    } catch (_) {}
    return ''
  }
})

function mdToHtml(text) {
  if (!text) return ''
  try {
    if (text.includes('&amp;') || text.includes('&lt;')) {
      console.log('mdToHtml INPUT has entities:', JSON.stringify(text.slice(0, 200)))
    }
    const html = md.render(text)
    if (html.includes('&amp;') || html.includes('&lt;')) {
      console.log('mdToHtml OUTPUT has entities:', JSON.stringify(html.slice(0, 200)))
    }
    return html
  } catch (e) {
    console.error('mdToHtml error:', e)
    return text
  }
}

const messages = ref([])
const messagesContainer = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
    setupCopyButtons()
  })
}

function setupCopyButtons() {
  document.querySelectorAll('.text pre').forEach(pre => {
    if (pre.querySelector('.copy-btn')) return
    pre.style.position = 'relative'
    const btn = document.createElement('button')
    btn.className = 'copy-btn'
    btn.textContent = '📋'
    Object.assign(btn.style, {
      position: 'absolute',
      top: '4px',
      right: '4px',
      background: '#1a1d2e',
      border: '1px solid #30363d',
      borderRadius: '4px',
      color: '#8b949e',
      cursor: 'pointer',
      fontSize: '12px',
      padding: '2px 6px',
      lineHeight: '1.4',
      opacity: '0.6',
      zIndex: '1'
    })
    btn.addEventListener('mouseenter', () => { btn.style.opacity = '1' })
    btn.addEventListener('mouseleave', () => { btn.style.opacity = '0.6' })
    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code')
      if (!code) return
      try {
        await navigator.clipboard.writeText(code.textContent || '')
        btn.textContent = '✓'
        setTimeout(() => { btn.textContent = '📋' }, 2000)
      } catch {
        btn.textContent = '✗'
        setTimeout(() => { btn.textContent = '📋' }, 2000)
      }
    })
    pre.appendChild(btn)
  })
}

function handleSend(text) {
  messages.value.push({
    role: 'user',
    text: text,
    thinking: '',
    tools: []
  })
  scrollToBottom()

  const assistantMsg = {
    role: 'assistant',
    text: '',
    thinking: '',
    tools: []
  }
  messages.value.push(assistantMsg)

  const assistantIndex = messages.value.length - 1
  scrollToBottom()

  streamChat(text, uiState.mode, (event) => {
    handleEvent(event, assistantIndex)
    scrollToBottom()
  })
}

function handleEvent(e, assistantIndex) {
  const msg = messages.value[assistantIndex]
  if (!msg) return

  switch (e.type) {
    case 'token':
      msg.text += e.content
      if (e.content.includes('&') || e.content.includes('<')) {
        console.log('TOKEN with entities:', JSON.stringify(e.content.slice(0, 100)))
      }
      break

    case 'thinking':
      msg.thinking = e.content
      break

    case 'tool_call':
      msg.tools.push({
        type: 'call',
        name: e.name,
        args: e.args
      })
      break

    case 'tool_result':
      msg.tools.push({
        type: 'result',
        name: e.name,
        content: e.content
      })

      if (e.name === 'patch_file') {
        uiActions.setDiff({
          old: uiState.previousCode,
          new: e.content
        })
      }
      break

    case 'plan_step':
      msg.tools.push({
        type: 'call',
        name: e.tool,
        args: e.args
      })
      msg.tools.push({
        type: 'result',
        name: e.tool,
        content: typeof e.result === 'string' ? e.result : JSON.stringify(e.result)
      })
      break

    case 'plan':
      msg.tools.push({
        type: 'result',
        name: 'Plan',
        content: JSON.stringify(e.content, null, 2)
      })
      break

    case 'error':
      msg.tools.push({
        type: 'result',
        name: 'Error',
        content: typeof e.content === 'string' ? e.content : JSON.stringify(e.content)
      })
      break
  }
}
</script>

<style scoped>
.chat-panel {
  width: 360px;
  background: #151822;
  border-left: none;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  min-height: 0;
  max-height: 100%;
}

.messages::-webkit-scrollbar {
  width: 8px;
}
.messages::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}
.messages::-webkit-scrollbar-track {
  background: transparent;
}

.message {
  margin-bottom: 16px;
}

.message.user {
  text-align: right;
}

.content-bubble {
  display: inline-block;
  text-align: left;
  max-width: 95%;
}

.content-bubble.user-bubble {
  border: 1px solid var(--msg-border);
  border-radius: 6px;
  background: #0f1117;
  padding: 8px 10px;
}

.role-label {
  font-size: 11px;
  color: #8b949e;
  margin-bottom: 4px;
}

.message.user .role-label {
  color: #58a6ff;
}

.message.assistant .role-label {
  color: #22c55e;
}

.text {
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

.text :deep(*) {
  max-width: 100%;
}

.thinking {
  font-size: 11px;
  color: #8b949e;
  margin-top: 6px;
  font-style: italic;
  background: #0a0a0f;
  border-radius: 4px;
  padding: 6px 8px;
}

.tools {
  margin-top: 8px;
  background: #0a0a0f;
  border-radius: 4px;
  padding: 6px 8px;
}

.tool {
  font-size: 11px;
  margin-top: 4px;
}

.tool-call {
  color: #60a5fa;
}

.text :deep(h1),
.text :deep(h2),
.text :deep(h3),
.text :deep(h4) {
  margin: 10px 0 6px;
  color: #e6edf3;
}
.text :deep(h1) { font-size: 16px; }
.text :deep(h2) { font-size: 15px; }
.text :deep(h3) { font-size: 14px; }
.text :deep(p) { margin: 4px 0; }
.text :deep(ul),
.text :deep(ol) { padding-left: 20px; margin: 4px 0; }
.text :deep(li) { margin: 2px 0; }
.text :deep(code) {
  background: #1a1d2e;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  color: #f97583;
}
.text :deep(pre) {
  background: #0d1117;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
  line-height: 1.45;
  position: relative;
}

:global(.copy-btn) {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #1a1d2e;
  border: 1px solid #30363d;
  border-radius: 4px;
  color: #8b949e;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 6px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.15s;
  z-index: 1;
}

:global(.copy-btn:hover) {
  background: #30363d;
  color: #e6edf3;
}
.text :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
  font-size: 12px;
}
.text :deep(.hljs) { color: #c9d1d9; }
.text :deep(.hljs-keyword) { color: #ff7b72; }
.text :deep(.hljs-number) { color: #79c0ff; }
.text :deep(.hljs-built_in) { color: #ffa657; }
.text :deep(.hljs-string) { color: #a5d6ff; }
.text :deep(.hljs-comment) { color: #8b949e; font-style: italic; }
.text :deep(.hljs-function) { color: #d2a8ff; }
.text :deep(.hljs-title) { color: #d2a8ff; }
.text :deep(.hljs-params) { color: #c9d1d9; }
.text :deep(.hljs-attr) { color: #79c0ff; }
.text :deep(.hljs-attribute) { color: #79c0ff; }
.text :deep(strong) { font-weight: 600; }
.text :deep(a) { color: #58a6ff; }
.text :deep(blockquote) {
  border-left: 3px solid #30363d;
  padding-left: 10px;
  color: #8b949e;
  margin: 6px 0;
}
.text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 6px 0;
  font-size: 12px;
}
.text :deep(th),
.text :deep(td) {
  border: 1px solid #30363d;
  padding: 4px 8px;
  text-align: left;
}
.text :deep(th) { background: #161b22; }

.tool-result :deep(p) { margin: 2px 0; }
.tool-result :deep(table) { width: 100%; border-collapse: collapse; }
.tool-result :deep(ul),
.tool-result :deep(ol) { padding-left: 18px; margin: 2px 0; }
.tool-result :deep(code) {
  background: #1a1d2e;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 11px;
  color: #f97583;
}
.tool-result :deep(pre) {
  background: #0d1117;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 4px 0;
}
.tool-result :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}
.tool-pre {
  margin: 0;
  font-size: 11px;
  line-height: 1.5;
  white-space: pre;
  word-break: keep-all;
  overflow-x: auto;
  color: #34d399;
  background: none;
  border: none;
  padding: 0;
}
.tool-result :deep(strong) { font-weight: 600; }
.tool-result :deep(a) { color: #58a6ff; }
.tool-result :deep(blockquote) {
  border-left: 2px solid #30363d;
  padding-left: 8px;
  color: #8b949e;
  margin: 4px 0;
}
.tool-result :deep(.hljs) { color: #c9d1d9; }
.tool-result :deep(.hljs-keyword) { color: #ff7b72; }
.tool-result :deep(.hljs-number) { color: #79c0ff; }
.tool-result :deep(.hljs-built_in) { color: #ffa657; }
.tool-result :deep(.hljs-string) { color: #a5d6ff; }
.tool-result :deep(.hljs-comment) { color: #8b949e; font-style: italic; }
.tool-result :deep(.hljs-function) { color: #d2a8ff; }
.tool-result :deep(.hljs-title) { color: #d2a8ff; }

.tool-result {
  color: #34d399;
  background: #0f1117;
  padding: 8px 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  word-break: break-word;
  line-height: 1.5;
}
</style>
