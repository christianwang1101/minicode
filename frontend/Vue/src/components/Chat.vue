<template>
  <div class="chat-panel">
    <div class="messages" ref="messagesContainer">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="message"
        :class="m.role"
      >
        <div class="role-label">{{ m.role === 'user' ? '>' : 'AI' }}</div>

        <div class="content">
          <div v-if="m.text" class="text">{{ m.text }}</div>

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
              <div v-else class="tool-result">
                ✔ {{ t.content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <InputBox @send="handleSend" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { streamChat } from '../api/chat'
import InputBox from './InputBox.vue'
import { uiState } from '../stores/uiState'
import { uiActions } from '../stores/uiActions'

const messages = ref([])
const messagesContainer = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
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
  height: 100%;
}

.mode-indicator {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.mode-indicator.build {
  background: transparent;
  color: #3b82f6 !important;
  border: 1px solid #3b82f6 !important;
}

.mode-indicator.plan {
  background: transparent;
  color: #a855f7 !important;
  border: 1px solid #a855f7 !important;
}

.messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
  padding: 12px;
  white-space: nowrap;
}

.message {
  margin-bottom: 16px;
}

.message.user {
  text-align: right;
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

.content {
  text-align: left;
}

.text {
  white-space: pre;
  font-size: 13px;
  line-height: 1.5;
}

.thinking {
  font-size: 12px;
  color: #8b949e;
  margin-top: 6px;
  font-style: italic;
}

.tools {
  margin-top: 8px;
}

.tool {
  font-size: 12px;
  margin-top: 4px;
}

.tool-call {
  color: #60a5fa;
}

.tool-result {
  color: #34d399;
  background: #0f1117;
  padding: 6px 8px;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre;
  word-break: break-all;
}
</style>
