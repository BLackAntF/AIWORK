<template>
	<view class="confidence-tag" :class="level">
		<AppIcon :name="iconName" :size="24" :color="iconColor" />
		<text class="tag-text">{{ label }}</text>
	</view>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
	level: { type: String, default: 'low', validator: (v) => ['high', 'medium', 'low'].includes(v) }
})

const LEVEL_STYLE = {
	high: { icon: 'check-circle', color: '#C8442F', label: '高可信' },
	medium: { icon: 'alert', color: '#D9A11E', label: '中可信' },
	low: { icon: 'info', color: '#8A938C', label: '仅供参考' }
}

const iconName = computed(() => LEVEL_STYLE[props.level].icon)
const iconColor = computed(() => LEVEL_STYLE[props.level].color)
const label = computed(() => LEVEL_STYLE[props.level].label)
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
	background: var(--brand-glow);
	color: var(--brand);
}

.confidence-tag.medium {
	background: rgba(217, 161, 30, 0.14);
	color: var(--warning);
}

.confidence-tag.low {
	background: rgba(138, 147, 140, 0.12);
	color: var(--text-3);
}

.tag-text {
	font-size: 24rpx;
}
</style>
