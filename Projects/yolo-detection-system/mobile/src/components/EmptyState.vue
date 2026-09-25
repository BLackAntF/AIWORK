<template>
	<view class="empty-state">
		<AppIcon class="empty-icon" :name="name" :size="96" :color="iconColor" />
		<text class="empty-title">{{ title }}</text>
		<text class="empty-desc">{{ desc }}</text>
		<slot></slot>
	</view>
</template>

<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
	name: { type: String, default: 'inbox' },
	iconColor: { type: String, default: '#ADB5BD' },
	title: { type: String, default: '暂无数据' },
	desc: { type: String, default: '' }
})
</script>

<style lang="scss" scoped>
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 80rpx 40rpx;
}

.empty-icon {
	margin-bottom: 24rpx;
	opacity: 0.8;
}

.empty-title {
	font-size: 32rpx;
	font-weight: 600;
	color: var(--text-2);
	margin-bottom: 12rpx;
}

.empty-desc {
	font-size: 26rpx;
	color: var(--text-3);
}
</style>