<template>
	<view class="chat-bubble-wrap" :class="{ self: isSelf }">
		<view class="bubble" :class="{ self: isSelf }">
			<text v-if="isSelf" class="bubble-text">{{ content }}</text>
			<template v-else>
				<text class="bubble-text">{{ content }}</text>
			</template>
		</view>
		<text class="bubble-time">{{ time }}</text>
	</view>
</template>

<script setup>
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
	margin-bottom: 20rpx;
}

.chat-bubble-wrap.self {
	align-items: flex-end;
}

.bubble {
	max-width: 80%;
	padding: 20rpx 24rpx;
	border-radius: 20rpx;
	background: #fff;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.bubble.self {
	background: linear-gradient(135deg, #E07A5F 0%, #C96247 100%);
}

.bubble-text {
	font-size: 28rpx;
	line-height: 1.6;
	color: #333;
	word-break: break-all;
}

.bubble.self .bubble-text {
	color: #fff;
}

.bubble-time {
	font-size: 22rpx;
	color: #bbb;
	margin-top: 6rpx;
	padding: 0 8rpx;
}

.chat-bubble-wrap.self .bubble-time {
	text-align: right;
}
</style>
