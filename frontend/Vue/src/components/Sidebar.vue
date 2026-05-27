<template>
  <div class="sidebar">
    <div v-if="!treeData.length" class="empty-state">
      <label class="empty-clickable">
        <input type="file" webkitdirectory @change="onSelectRoot" />
        <span class="empty-icon">📝</span>
        <span class="empty-text">Select a folder...</span>
      </label>
    </div>

    <ul v-else class="file-tree">
      <FileNode
        v-for="node in treeData"
        :key="node.path"
        :node="node"
      />
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileNode from './FileNode.vue'

const treeData = ref([])

function onSelectRoot(event) {
  const fileList = Array.from(event.target.files)
  if (!fileList.length) return

  const rootNodes = []

  fileList.forEach(file => {
    const parts = file.webkitRelativePath.split('/')
    let currentLevel = rootNodes
    let pathAcc = ''

    parts.forEach((part, idx) => {
      pathAcc = pathAcc ? pathAcc + '/' + part : part
      let existing = currentLevel.find(n => n.name === part)
      if (!existing) {
        existing = {
          name: part,
          path: pathAcc,
          file: idx === parts.length - 1 ? file : null,
          isFolder: idx !== parts.length - 1,
          children: [],
          expanded: idx === 0,
          hidden: part.startsWith('__') || part.startsWith('venv')
        }
        currentLevel.push(existing)
      }
      currentLevel = existing.children
    })
  })

  treeData.value = rootNodes
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-width: 200px;
  max-width: 400px;
  overflow-x: auto;
  overflow-y: auto;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #484f58;
  user-select: none;
}

.empty-clickable {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.empty-clickable input[type="file"] {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.empty-icon {
  font-size: 24px;
}

.empty-text {
  font-size: 14px;
}

.file-tree {
  flex: 1;
  margin: 0;
  padding: 0;
  list-style: none;
  padding-top: 4px;
  white-space: nowrap;
}
</style>