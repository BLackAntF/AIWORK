<template>
	<image class="app-icon" :src="src" :style="iconStyle" mode="aspectFit" />
</template>

<script setup>
import { computed } from 'vue'
import { iconSrc } from '@/utils/icons'

const props = defineProps({
	name: { type: String, required: true },
	size: { type: [Number, String], default: 32 },
	color: { type: String, default: '#6C757D' }
})

const src = computed(() => iconSrc(props.name, props.color))

const iconStyle = computed(() => {
	const side = typeof props.size === 'number' ? `${props.size}rpx` : props.size
	return { width: side, height: side }
})
</script>

<style lang="scss" scoped>
.app-icon {
	display: block;
	flex-shrink: 0;
}
</style>