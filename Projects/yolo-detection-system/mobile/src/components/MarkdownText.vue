<template>
	<rich-text class="markdown-text" :nodes="html"></rich-text>
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps({
	content: { type: String, default: '' }
})

const html = computed(() => renderMarkdown(props.content))
</script>

<style lang="scss" scoped>
.markdown-text {
	display: block;
	width: 100%;
	overflow-wrap: anywhere;
}
</style>