<template>
  <div class="input-box" :style="{ '--border-color': uiState.mode === 'plan' ? '#a371f7' : '#58a6ff' }">
    <!-- 外层容器保持圆角，内层textarea滚动 -->
    <div class="textarea-wrapper">
      <textarea
        ref="textarea"
        v-model="text"
        @input="autoResize"
        @keydown.enter.exact.prevent="send"
        @keydown.enter.shift.exact="newline"
        @keydown.tab.prevent="uiActions.toggleMode"
        :placeholder="placeholder"
        rows="1"
      />
    </div>
    <div class="input-hint">
      <span class="mode-hint" :class="uiState.mode">
        {{ uiState.mode.toUpperCase() }} MODE
      </span>
      <span class="tab-hint">Press Tab to Switch Mode</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { uiState } from '../stores/uiState'
import { uiActions } from '../stores/uiActions'

const emit = defineEmits(['send'])
const text = ref('')
const textarea = ref(null)

const placeholder = computed(() => 'Type a Message...')

function send() {
  if (!text.value.trim()) return
  emit('send', text.value)
  text.value = ''
  nextTick(() => autoResize())
}

function newline(e) {
  text.value += '\n'
  nextTick(() => autoResize())
}

function autoResize() {
  const ta = textarea.value
  if (!ta) return
  ta.style.height = 'auto'
  const maxHeight = 200 // 最大高度，可调
  if (ta.scrollHeight > maxHeight) {
    ta.style.height = maxHeight + 'px'
    ta.style.overflowY = 'auto'
  } else {
    ta.style.height = ta.scrollHeight + 'px'
    ta.style.overflowY = 'hidden'
  }
}
</script>

<style scoped>
.input-box {
  padding: 12px;
  border-top: 1px solid #232634;
  background: #151822;
}

.textarea-wrapper {
  border: 1px solid var(--border-color);
  border-radius: 6px;       /* 外层圆角 */
  overflow: hidden;          /* 圆角外层隐藏滚动条 */
  background: #0f1117;
}

textarea {
  width: 100%;
  min-height: 36px;
  padding: 8px 10px;
  border: none;
  resize: none;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.5;
  outline: none;
  box-sizing: border-box;
  background: transparent;
  color: #e5e7eb;
  overflow-y: auto;
  max-height: 200px;
}

/* 滚动条美化 */
textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

.input-hint {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
}

.mode-hint {
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 3px;
}

.mode-hint.build {
  background: transparent;
  color: #3b82f6 !important;
}

.mode-hint.plan {
  background: transparent;
  color: #a855f7 !important;
}

.tab-hint {
  color: #484f58;
}
</style>