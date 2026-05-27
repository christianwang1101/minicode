<template>
  <div class="layout" :class="{ 'is-resizing': !!resizing }">
    <!-- Topbar -->
    <div class="topbar">
      <div class="logo">MINICODE V1.12.5</div>
    </div>

    <!-- 主内容区 -->
    <div class="main">
      <!-- Sidebar -->
      <div
        class="sidebar"
        :class="{ 'is-collapsed': isSidebarCollapsed }"
        :style="{ width: isSidebarCollapsed ? COLLAPSED_WIDTH + 'px' : sidebarWidth + 'px' }"
      >
        <Sidebar v-show="!isSidebarCollapsed" />
        <!-- 左侧折叠按钮 -->
        <button class="toggle-btn left" @click="toggleSidebar">
          {{ isSidebarCollapsed ? '▶' : '◀' }}
        </button>
      </div>

      <!-- 左侧 resizer -->
      <div v-if="!isSidebarCollapsed" class="resizer" @mousedown="startLeftResize"></div>

      <!-- Editor -->
      <div class="editor" :style="{ width: editorWidth + 'px' }">
        <Editor />
      </div>

      <!-- Chat 固定宽度 360px -->
      <div class="chat-wrapper">
        <div class="chat" :style="{ width: CHAT_WIDTH + 'px' }">
          <Chat />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Editor from './components/Editor.vue'
import Chat from './components/Chat.vue'

// 基础配置
const MIN_SIDEBAR = 180
const MIN_EDITOR = 200
const COLLAPSED_WIDTH = 60
const CHAT_WIDTH = 360 // 固定宽度

// 状态
const sidebarWidth = ref(Number(localStorage.getItem('sidebarWidth')) || 260)
const editorWidth = ref(0)
const isSidebarCollapsed = ref(false)
const resizing = ref(null)

// 保存 Sidebar 宽度
watch(sidebarWidth, () => {
  localStorage.setItem('sidebarWidth', sidebarWidth.value)
})

// 左侧折叠/展开
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  updateEditorWidth()
}

// 计算 Editor 宽度
function updateEditorWidth() {
  const activeSidebarWidth = isSidebarCollapsed.value ? COLLAPSED_WIDTH : sidebarWidth.value
  editorWidth.value = Math.max(
    MIN_EDITOR,
    window.innerWidth - activeSidebarWidth - CHAT_WIDTH - 6 // 6px 左 resizer
  )
}

// 拖拽逻辑（只针对左侧 Sidebar）
function onMouseMove(e) {
  if (!resizing.value) return
  const maxAllowed = window.innerWidth - CHAT_WIDTH - MIN_EDITOR
  sidebarWidth.value = Math.max(MIN_SIDEBAR, Math.min(maxAllowed, e.clientX))
  updateEditorWidth()
}

function startLeftResize() {
  resizing.value = 'left'
  document.body.classList.add('is-resizing')
  initListeners()
}

function stopResize() {
  resizing.value = null
  document.body.classList.remove('is-resizing')
  document.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', stopResize)
}

function initListeners() {
  document.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', stopResize)
}

// 窗口大小变化时同步 Editor
onMounted(() => {
  updateEditorWidth()
  window.addEventListener('resize', updateEditorWidth)
})
onUnmounted(() => {
  stopResize()
  window.removeEventListener('resize', updateEditorWidth)
})
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #0f1117;
}

.topbar {
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f1117;
  border-bottom: 1px solid #21262d;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #58a6ff;
  user-select: none;
}

.main {
  display: flex;
  flex: 1;
  min-height: 0;
}

.sidebar {
  position: relative;
  flex-shrink: 0;
  overflow: hidden;
  transition: width 0.2s;
}

.editor {
  background: #1a1c24;
  min-width: 200px;
  position: relative;
}

.chat-wrapper {
  position: relative;
  flex-shrink: 0;
  display: flex;
  align-items: stretch;
}

.chat {
  flex-shrink: 0;
  position: relative;
  background: #151822;
  transition: width 0.2s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 左侧 resizer */
.resizer {
  width: 3px;
  cursor: col-resize;
  background: transparent;
  position: relative;
}
.resizer::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(255,255,255,0.08);
  transform: translateX(-50%);
}
.resizer:hover {
  background: rgba(88,166,255,0.2);
}

/* 拖拽中蓝色高亮 */
body.is-resizing .resizer {
  background: rgba(88,166,255,0.4);
}

/* 按钮样式 */
.toggle-btn {
  position: absolute;
  bottom: 10px;
  z-index: 20;
  background: #21262d;
  border: 1px solid #30363d;
  color: white;
  cursor: pointer;
  padding: 1px 2px;
  border-radius: 3px;
  font-size: 10px;
}
.toggle-btn.left { right: 10px; }
</style>