<template>
  <div class="sidebar">
    <div class="select-root">
      <label>
        Select Root Directory:
        <input type="file" webkitdirectory @change="onSelectRoot" />
      </label>
      <div v-if="uiState.rootPath">Root: {{ uiState.rootPath }}</div>
    </div>

    <ul class="file-tree">
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
import { uiState } from '../stores/uiState'
import { uiActions } from '../stores/uiActions'
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

.select-root {
  background-color: white;
  padding: 4px 6px;
  flex-shrink: 0;
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