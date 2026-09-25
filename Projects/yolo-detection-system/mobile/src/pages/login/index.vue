<template>
	<view class="login-page" :style="{ paddingTop: statusBarHeight + 'px' }">
		<!-- 顶部品牌区 -->
		<view class="brand-section">
			<view class="decoration-circle circle-1"></view>
			<view class="decoration-circle circle-2"></view>
			<view class="decoration-circle circle-3"></view>
			<view class="logo-wrap">
				<view class="logo-icon">
					<text class="logo-leaf">🍃</text>
				</view>
			</view>
			<text class="brand-title">番茄病害诊断</text>
			<text class="brand-subtitle">智能识别 · 科学防治</text>
		</view>

		<!-- 表单卡片 -->
		<view class="form-card">
			<view class="form-header">
				<text class="form-title">欢迎回来</text>
				<text class="form-desc">请登录您的账号</text>
			</view>

			<view class="input-group">
				<view class="input-wrap" :class="{ focused: focusedField === 'username' }">
					<text class="input-icon">👤</text>
					<input
						v-model="form.username"
						placeholder="请输入用户名"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'username'"
						@blur="focusedField = ''"
					/>
				</view>

				<view class="input-wrap" :class="{ focused: focusedField === 'password' }">
					<text class="input-icon">🔒</text>
					<input
						v-model="form.password"
						:type="showPassword ? 'text' : 'password'"
						placeholder="请输入密码"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'password'"
						@blur="focusedField = ''"
					/>
					<text class="pwd-toggle" @click="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁' }}</text>
				</view>
			</view>

			<button
				class="login-btn"
				:class="{ disabled: loading }"
				:loading="loading"
				@click="handleLogin"
			>
				<text v-if="!loading">登 录</text>
			</button>

			<view class="form-footer">
				<text class="footer-text">还没有账号？</text>
				<text class="register-link" @click="goRegister">立即注册</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const statusBarHeight = uni.getSystemInfoSync().statusBarHeight || 0

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const focusedField = ref('')
const showPassword = ref(false)

/** 表单校验 */
function validateForm() {
	if (!form.username.trim()) {
		uni.showToast({ title: '请输入用户名', icon: 'none' })
		return false
	}
	if (!form.password) {
		uni.showToast({ title: '请输入密码', icon: 'none' })
		return false
	}
	return true
}

/** 执行登录请求并跳转 */
async function doLogin() {
	loading.value = true
	try {
		await userStore.login({ username: form.username.trim(), password: form.password })
		uni.showToast({ title: '登录成功', icon: 'success' })
		setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 500)
	} catch (e) {
		// request.js 已处理错误提示
	} finally {
		loading.value = false
	}
}

/** 登录入口 */
function handleLogin() {
	if (loading.value) return
	if (!validateForm()) return
	doLogin()
}

/** 跳转注册页 */
function goRegister() {
	uni.navigateTo({ url: '/pages/register/index' })
}
</script>

<style lang="scss" scoped>
.login-page {
	min-height: 100vh;
	background: linear-gradient(180deg, #E07A5F 0%, #C96247 40%, #F5F5F5 40%, #F5F5F5 100%);
	display: flex;
	flex-direction: column;
}

/* 品牌区 */
.brand-section {
	position: relative;
	padding: 80rpx 0 120rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.decoration-circle {
	position: absolute;
	border-radius: 50%;
	filter: blur(40rpx);
	opacity: 0.35;
}

.circle-1 { width: 200rpx; height: 200rpx; background: #F29780; top: 40rpx; left: -40rpx; }
.circle-2 { width: 160rpx; height: 160rpx; background: #F5AB96; top: 120rpx; right: -30rpx; }
.circle-3 { width: 120rpx; height: 120rpx; background: #FF6B6B; top: 200rpx; left: 120rpx; opacity: 0.2; }

.logo-wrap {
	margin-bottom: 32rpx;
}

.logo-icon {
	width: 140rpx;
	height: 140rpx;
	border-radius: 36rpx;
	background: rgba(255, 255, 255, 0.25);
	backdrop-filter: blur(20rpx);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.logo-leaf {
	font-size: 72rpx;
}

.brand-title {
	font-size: 48rpx;
	font-weight: 700;
	color: #fff;
	letter-spacing: 4rpx;
	margin-bottom: 12rpx;
	position: relative;
	z-index: 2;
}

.brand-subtitle {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.9);
	letter-spacing: 2rpx;
	position: relative;
	z-index: 2;
}

/* 表单卡片 */
.form-card {
	flex: 1;
	background: #fff;
	border-radius: 48rpx 48rpx 0 0;
	padding: 64rpx 48rpx;
	margin-top: -60rpx;
	position: relative;
	z-index: 3;
	box-shadow: 0 -8rpx 32rpx rgba(0, 0, 0, 0.05);
}

.form-header {
	text-align: center;
	margin-bottom: 56rpx;
}

.form-title {
	display: block;
	font-size: 40rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 12rpx;
}

.form-desc {
	font-size: 28rpx;
	color: #999;
}

/* 输入框 */
.input-group {
	margin-bottom: 48rpx;
}

.input-wrap {
	display: flex;
	align-items: center;
	background: #F8F9FA;
	border-radius: 24rpx;
	padding: 0 28rpx;
	margin-bottom: 28rpx;
	height: 96rpx;
	border: 2rpx solid transparent;
	transition: all 0.3s ease;
}

.input-wrap.focused {
	border-color: #E07A5F;
	background: #fff;
	box-shadow: 0 0 0 6rpx rgba(224, 122, 95, 0.08);
}

.input-icon {
	font-size: 36rpx;
	margin-right: 20rpx;
}

.input {
	flex: 1;
	font-size: 30rpx;
	color: #333;
	height: 96rpx;
}

.placeholder {
	color: #bbb;
	font-size: 30rpx;
}

.pwd-toggle {
	font-size: 36rpx;
	padding: 0 8rpx;
}

/* 登录按钮 */
.login-btn {
	width: 100%;
	height: 96rpx;
	border-radius: 48rpx;
	background: linear-gradient(135deg, #E07A5F 0%, #C96247 100%);
	color: #fff;
	font-size: 34rpx;
	font-weight: 600;
	letter-spacing: 8rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	box-shadow: 0 8rpx 24rpx rgba(224, 122, 95, 0.3);
	transition: all 0.2s ease;
}

.login-btn.disabled {
	opacity: 0.6;
}

.login-btn::after {
	border: none;
}

/* 底部 */
.form-footer {
	text-align: center;
	margin-top: 48rpx;
	font-size: 28rpx;
}

.footer-text {
	color: #999;
}

.register-link {
	color: #E07A5F;
	font-weight: 600;
	margin-left: 8rpx;
}
</style>
