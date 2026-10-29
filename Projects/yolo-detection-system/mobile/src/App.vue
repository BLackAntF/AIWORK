<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 通过组合式 API 注册应用生命周期，登录守卫才会真正执行
onLaunch(async () => {
	const token = uni.getStorageSync('token')
	if (!token) {
		uni.reLaunch({ url: '/pages/login/index' })
		return
	}

	try {
		await userStore.fetchUserInfo()
	} catch (e) {
		uni.removeStorageSync('token')
		uni.reLaunch({ url: '/pages/login/index' })
	}
})

onShow(() => {
	console.log('App Show')
})

onHide(() => {
	console.log('App Hide')
})
</script>

<style lang="scss">
@use './styles/tokens.scss';

page {
	background-color: var(--bg-2);
	font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
	font-size: 28rpx;
	color: var(--text-1);
}

button {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0;
	margin: 0;
	line-height: normal;
}

button::after {
	border: none;
}
</style>
