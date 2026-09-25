<template>
	<view class="confidence-tag" :class="level">
		<text class="tag-icon">{{ icon }}</text>
		<text class="tag-text">{{ label }}</text>
	</view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	level: { type: String, default: 'low', validator: (v) => ['high', 'medium', 'low'].includes(v) }
})

const icon = computed(() => {
	const map = { high: '✅', medium: '⚠️', low: 'ℹ️' }
	return map[props.level]
})

const label = computed(() => {
	const map = { high: '高可信', medium: '中可信', low: '仅供参考' }
	return map[props.level]
})
</script>

<style lang="scss" scoped>
.confidence-tag {
	display: inline-flex;
	align-items: center;
	gap: 6rpx;
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
	font-size: 24rpx;
	font-weight: 500;
}

.confidence-tag.high {
	background: rgba(224, 122, 95, 0.15);
	color: #E07A5F;
}

.confidence-tag.medium {
	background: rgba(255, 152, 0, 0.15);
	color: #FF9800;
}

.confidence-tag.low {
	background: rgba(158, 158, 158, 0.15);
	color: #9E9E9E;
}

.tag-icon {
	font-size: 22rpx;
}

.tag-text {
	font-size: 24rpx;
}
</style>
