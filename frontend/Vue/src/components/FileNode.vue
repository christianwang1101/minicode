<template>
  <li :class="['file-node', { folder: props.node.isFolder, active: isActive }]">
    <div
      class="node-label"
      @dblclick="toggleFolder"
      @click="openFile"
    >
      <span v-if="props.node.isFolder">
        {{ props.node.expanded ? '📂' : '📁' }}
      </span>
      <span v-else>📄</span>
      <span class="node-text">{{ props.node.name }}</span>
    </div>

    <ul v-show="props.node.isFolder && props.node.expanded" class="child-nodes">
      <FileNode 
        v-for="child in props.node.children" 
        :key="child.path" 
        :node="child" 
      />
    </ul>
  </li>
</template>

<script setup>
import { computed } from 'vue'
import { uiState } from '../stores/uiState'
import { uiActions } from '../stores/uiActions'
import FileNode from './FileNode.vue'

const props = defineProps({
  node: Object
})

const isActive = computed(() => uiState.currentFile === props.node.path)

function openFile(e) {
  e.stopPropagation()
  if (!props.node.isFolder && props.node.file) {
    props.node.file.text().then(content => {
      uiActions.setCurrentFile(props.node.path, content)
    })
  }
}

function toggleFolder(e) {
  e.stopPropagation()
  if (props.node.isFolder) {
    props.node.expanded = !props.node.expanded
  }
}
</script>

<style scoped>
.file-node {
  font-size: 13px;
  list-style: none;
  cursor: pointer;
}

.node-label {
  padding: 2px 6px;
  user-select: none;
}

.file-node.active > .node-label .node-text {
  display: inline-block;
  padding: 2px 4px;
  background-color: #ffffff;
  color: #222222;
  border-radius: 2px;
}

.child-nodes {
  margin-left: 16px;
  overflow-y: visible;
  overflow-x: hidden;
}
</style>
