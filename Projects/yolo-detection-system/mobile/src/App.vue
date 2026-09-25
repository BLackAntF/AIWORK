<script setup>
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

async function onLaunch() {
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
}

function onShow() {
	console.log('App Show')
}

function onHide() {
	console.log('App Hide')
}
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
	padding: 0;
	margin: 0;
	line-height: normal;
}

button::after {
	border: none;
}
</style>
