<template>
	<view class="empty-state">
		<view class="empty-icon-wrap">
			<AppIcon class="empty-icon" :name="name" :size="84" :color="iconColor" />
		</view>
		<text class="empty-title">{{ title }}</text>
		<text class="empty-desc">{{ desc }}</text>
		<slot></slot>
	</view>
</template>

<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
	name: { type: String, default: 'inbox' },
	iconColor: { type: String, default: '#C3C9C3' },
	title: { type: String, default: '暂无数据' },
	desc: { type: String, default: '' }
})
</script>

<style lang="scss" scoped>
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 72rpx 40rpx;
}

.empty-icon-wrap {
	width: 132rpx;
	height: 132rpx;
	border-radius: 44rpx;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 28rpx;
	box-shadow: var(--shadow-sm);
}

.empty-title {
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-2);
	margin-bottom: 12rpx;
}

.empty-desc {
	font-size: 25rpx;
	line-height: 1.6;
	color: var(--text-3);
	text-align: center;
}
</style>