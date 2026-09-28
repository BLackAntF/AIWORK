<template>
	<view class="chat-bubble-wrap" :class="{ self: isSelf }">
		<view class="bubble" :class="{ self: isSelf }">
			<text v-if="isSelf" class="bubble-text">{{ content }}</text>
			<MarkdownText v-else :content="content" />
		</view>
		<text class="bubble-time">{{ time }}</text>
	</view>
</template>

<script setup>
import MarkdownText from './MarkdownText.vue'

defineProps({
	isSelf: { type: Boolean, default: false },
	content: { type: String, required: true },
	time: { type: String, default: '' }
})
</script>

<style lang="scss" scoped>
.chat-bubble-wrap {
	display: flex;
	flex-direction: column;
	margin-bottom: 22rpx;
}

.chat-bubble-wrap.self {
	align-items: flex-end;
}

.bubble {
	max-width: 80%;
	padding: 22rpx 26rpx;
	border-radius: 22rpx 22rpx 22rpx 8rpx;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	box-shadow: var(--shadow-sm);
}

.bubble.self {
	border: none;
	border-radius: 22rpx 22rpx 8rpx 22rpx;
	background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
	box-shadow: var(--shadow-brand);
}

.bubble-text {
	font-size: 28rpx;
	line-height: 1.6;
	color: var(--text-1);
	word-break: break-all;
}

.bubble.self .bubble-text {
	color: #FFFFFF;
}

.bubble-time {
	font-size: 21rpx;
	color: var(--text-disabled);
	margin-top: 8rpx;
	padding: 0 8rpx;
}

.chat-bubble-wrap.self .bubble-time {
	text-align: right;
}
</style>
