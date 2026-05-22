<script>
	export default {
		onLaunch: function() {
			console.log('智慧烹饪系统启动')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/* 全局样式 */
	page {
		background-color: #0f0f23;
		color: #ffffff;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}
	
	/* 滚动条样式 */
	::-webkit-scrollbar {
		width: 4rpx;
	}
	
	::-webkit-scrollbar-thumb {
		background: #2a2a4a;
		border-radius: 4rpx;
	}
	
	/* 通用按钮样式 */
	.btn-primary {
		background: linear-gradient(135deg, #e94560, #c23152);
		color: #fff;
		border: none;
		border-radius: 24rpx;
		padding: 20rpx 40rpx;
		font-size: 28rpx;
		font-weight: 600;
		box-shadow: 0 8rpx 24rpx rgba(233, 69, 96, 0.3);
	}
	
	.btn-primary:active {
		transform: scale(0.96);
		opacity: 0.9;
	}
	
	/* 卡片样式 */
	.card {
		background: #1a1a2e;
		border-radius: 24rpx;
		padding: 32rpx;
		margin: 16rpx 24rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.3);
	}
	
	/* 状态指示灯 */
	.status-dot {
		width: 16rpx;
		height: 16rpx;
		border-radius: 50%;
		display: inline-block;
	}
	
	.status-dot.online {
		background: #2ecc71;
		box-shadow: 0 0 12rpx rgba(46, 204, 113, 0.6);
	}
	
	.status-dot.offline {
		background: #666;
	}
	
	.status-dot.error {
		background: #e74c3c;
		box-shadow: 0 0 12rpx rgba(231, 76, 60, 0.6);
	}
</style>
