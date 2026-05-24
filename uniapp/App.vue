<script>
	export default {
		onLaunch: function() {
			console.log('蓝牙设备控制启动')
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
	/* 全局样式 - 蓝白主题 */
	page {
		background-color: #f0f6ff;
		color: #2c3e50;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}
	
	/* 滚动条样式 */
	::-webkit-scrollbar {
		width: 4rpx;
	}
	
	::-webkit-scrollbar-thumb {
		background: #c8d6e5;
		border-radius: 4rpx;
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
		background: #b0bec5;
	}
	
	.status-dot.error {
		background: #e74c3c;
		box-shadow: 0 0 12rpx rgba(231, 76, 60, 0.6);
	}
</style>


