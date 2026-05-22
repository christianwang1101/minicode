<template>
  <div :class="['msg', msg.role]">

    <div class="bubble">
      <div class="text">{{ msg.text }}</div>

      <Thinking v-if="msg.thinking" :text="msg.thinking" />

      <ToolLog v-if="msg.tools?.length" :tools="msg.tools" />
    </div>

  </div>
</template>

<script setup>
import Thinking from './Thinking.vue'
import ToolLog from './ToolLog.vue'

defineProps({
  msg: Object
})
</script>