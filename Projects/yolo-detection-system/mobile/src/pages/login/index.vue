<template>
	<view class="login-page" :style="{ paddingTop: statusBarHeight + 'px' }">
		<!-- 顶部品牌区 -->
		<view class="brand-section">
			<view class="logo-wrap">
				<view class="logo-icon">
					<AppIcon class="logo-leaf" name="leaf" :size="72" color="#FFFFFF" />
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
					<AppIcon class="input-icon" name="user" :size="32" color="#C3C9C3" />
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
					<AppIcon class="input-icon" name="lock" :size="32" color="#C3C9C3" />
					<input
						v-model="form.password"
						:type="showPassword ? 'text' : 'password'"
						placeholder="请输入密码"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'password'"
						@blur="focusedField = ''"
					/>
					<view class="pwd-toggle" @click="showPassword = !showPassword">
						<AppIcon :name="showPassword ? 'eye-off' : 'eye'" :size="32" color="#C3C9C3" />
					</view>
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
import AppIcon from '@/components/AppIcon.vue'

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
	background: linear-gradient(180deg, var(--forest) 0%, var(--forest-2) 38%, var(--bg-2) 38%, var(--bg-2) 100%);
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

.brand-section::after {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 100%;
	background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1rpx, transparent 1rpx);
	background-size: 24rpx 24rpx;
	pointer-events: none;
}

.logo-wrap {
	margin-bottom: 32rpx;
}

.logo-icon {
	width: 140rpx;
	height: 140rpx;
	border-radius: 36rpx;
	background: rgba(200, 68, 47, 0.9);
	backdrop-filter: blur(20rpx);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.18);
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
	background: var(--bg-1);
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
	color: var(--text-1);
	margin-bottom: 12rpx;
}

.form-desc {
	font-size: 28rpx;
	color: var(--text-3);
}

/* 输入框 */
.input-group {
	margin-bottom: 48rpx;
}

.input-wrap {
	display: flex;
	align-items: center;
	background: var(--bg-2);
	border-radius: 24rpx;
	padding: 0 28rpx;
	margin-bottom: 28rpx;
	height: 96rpx;
	border: 2rpx solid transparent;
	transition: all 0.3s ease;
}

.input-wrap.focused {
	border-color: var(--brand);
	background: var(--bg-1);
	box-shadow: 0 0 0 6rpx rgba(200, 68, 47, 0.08);
}

.input-icon {
	font-size: 36rpx;
	margin-right: 20rpx;
}

.input {
	flex: 1;
	font-size: 30rpx;
	color: var(--text-1);
	height: 96rpx;
}

.placeholder {
	color: var(--text-disabled);
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
	background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
	color: #fff;
	font-size: 34rpx;
	font-weight: 600;
	letter-spacing: 8rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: none;
	box-shadow: 0 8rpx 24rpx rgba(200, 68, 47, 0.3);
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
	color: var(--text-3);
}

.register-link {
	color: var(--brand);
	font-weight: 600;
	margin-left: 8rpx;
}
</style>