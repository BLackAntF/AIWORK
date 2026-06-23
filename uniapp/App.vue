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
	/* 全局样式 - 首页主题 */
	page {
		background-color: #f5f6fa;
		color: #1a1a2e;
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
</style>


