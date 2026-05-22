<template>
  <details class="thinking">
    <summary>🧠 Thinking</summary>
    <pre>{{ text }}</pre>
  </details>
</template>

<script setup>
defineProps({
  text: String
})
</script>