<template>
  <div class="tool-log">
    <div v-for="(t, i) in tools" :key="i">

      <div v-if="t.type === 'call'" class="tool-call">
        🔧 {{ t.name }} {{ JSON.stringify(t.args) }}
      </div>

      <div v-else class="tool-result">
        ✅ {{ t.content }}
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  tools: Array
})
</script>