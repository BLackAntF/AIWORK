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
	high: { icon: 'check-circle', color: '#E07A5F', label: '高可信' },
	medium: { icon: 'alert', color: '#FAAD14', label: '中可信' },
	low: { icon: 'info', color: '#6C757D', label: '仅供参考' }
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
	background: rgba(224, 122, 95, 0.15);
	color: var(--brand);
}

.confidence-tag.medium {
	background: rgba(250, 173, 20, 0.15);
	color: var(--warning);
}

.confidence-tag.low {
	background: rgba(108, 117, 125, 0.12);
	color: var(--text-3);
}

.tag-text {
	font-size: 24rpx;
}
</style>
