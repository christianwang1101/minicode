<template>
  <div class="editor-wrapper">

    <!-- 空状态 -->
    <div v-if="!uiState.currentFile && !uiState.diff" class="empty-state">
      <div class="empty-icon">📝</div>
      <div class="empty-text">Select a file to edit</div>
    </div>

    <!-- Monaco 容器 -->
    <div
      class="editor-container"
      :class="{ active: uiState.activePanel === 'editor' }"
      :style="{ '--border-color': uiState.mode === 'plan' ? '#a371f7' : '#58a6ff' }"
      ref="container"
      v-show="ready"
    ></div>

    <!-- loading -->
    <div v-if="!ready" class="editor-loading">
      <div class="loading-spinner"></div>
      <span>Loading Monaco Editor...</span>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as monaco from 'monaco-editor'
import { uiState } from '../stores/uiState'

// ========================
// Monaco worker
// ========================
self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === 'json') return new Worker(new URL('monaco-editor/esm/vs/language/json/json.worker?worker', import.meta.url))
    if (label === 'typescript' || label === 'javascript') return new Worker(new URL('monaco-editor/esm/vs/language/typescript/ts.worker?worker', import.meta.url))
    return new Worker(new URL('monaco-editor/esm/vs/editor/editor.worker?worker', import.meta.url))
  }
}

const container = ref(null)
const ready = ref(false)
let editorInstance = null
let diffEditorInstance = null

function getLanguage(filePath) {
  if (!filePath) return 'plaintext'
  const ext = filePath.split('.').pop()?.toLowerCase()
  const map = { py:'python', js:'javascript', ts:'typescript', jsx:'javascript', tsx:'typescript', vue:'html', html:'html', css:'css', scss:'scss', less:'less', json:'json', md:'markdown', rs:'rust', go:'go', java:'java', c:'c', cpp:'cpp', h:'c', hpp:'cpp', yaml:'yaml', yml:'yaml', xml:'xml', sql:'sql', sh:'shell', bash:'shell', toml:'ini' }
  return map[ext] || 'plaintext'
}

function safeDispose(instance){ if(instance) try{ instance.dispose() }catch{} }
function disposeAll(){ safeDispose(editorInstance); safeDispose(diffEditorInstance); editorInstance=null; diffEditorInstance=null }

function createEditor(code, language){
  if(!container.value) return
  if(editorInstance && editorInstance.getModel()?.getValue()===code){ editorInstance.focus(); return }
  disposeAll()
  uiState.activePanel='editor'
  editorInstance=monaco.editor.create(container.value,{ value:code||'', language, theme:'vs-dark', automaticLayout:true, minimap:{enabled:false}, fontSize:13, scrollBeyondLastLine:false, readOnly:uiState.mode==='plan', wordWrap:'on', tabSize:2, padding:{top:10} })
  editorInstance.onDidFocusEditorWidget(()=>{ uiState.activePanel='editor' })
}

function createDiffEditor(oldCode,newCode,language){
  if(!container.value) return
  disposeAll()
  uiState.activePanel='editor'
  diffEditorInstance=monaco.editor.createDiffEditor(container.value,{ theme:'vs-dark', automaticLayout:true, readOnly:true })
  const originalModel=monaco.editor.createModel(oldCode||'',language)
  const modifiedModel=monaco.editor.createModel(newCode||'',language)
  diffEditorInstance.setModel({ original:originalModel, modified:modifiedModel })
  diffEditorInstance.getModifiedEditor().onDidFocusEditorWidget(()=>{ uiState.activePanel='editor' })
  diffEditorInstance.getOriginalEditor().onDidFocusEditorWidget(()=>{ uiState.activePanel='editor' })
}

// watch mode
watch(()=>uiState.mode, mode=>{ if(editorInstance) editorInstance.updateOptions({readOnly:mode==='plan'}) })

// watch currentFile/currentCode/diff
watch([()=>uiState.currentFile, ()=>uiState.currentCode, ()=>uiState.diff],([file, code, diff])=>{
  if(!ready.value || !container.value) return
  if(diff){ createDiffEditor(diff.old,diff.new,getLanguage(uiState.currentFile)) }
  else if(file && code){ createEditor(code,getLanguage(file)) }
},{ immediate:true })

onMounted(async ()=>{
  await nextTick()
  ready.value=true
  if(uiState.currentFile && uiState.currentCode) createEditor(uiState.currentCode,getLanguage(uiState.currentFile))
})

onUnmounted(()=>{ disposeAll() })
</script>

<style scoped>
.editor-wrapper{flex:1;height:100%;position:relative;background:#0f1117}
.editor-container{width:100%;height:100%;box-shadow:none}
.empty-state{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#484f58;pointer-events:none}
.empty-icon{font-size:48px;margin-bottom:12px}
.empty-text{font-size:14px}
.editor-loading{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0f1117;color:#8b949e;gap:12px}
.loading-spinner{width:24px;height:24px;border:2px solid #30363d;border-top-color:#58a6ff;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>