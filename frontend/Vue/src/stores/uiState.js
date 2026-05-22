import { reactive } from 'vue'

export const uiState = reactive({
  mode: 'build',          // build | plan
  activePanel: 'editor',  // editor | chat | sidebar
  currentFile: null,
  currentCode: '',
  files: [],
  diff: null,             // { old, new }
  previousCode: ''
})