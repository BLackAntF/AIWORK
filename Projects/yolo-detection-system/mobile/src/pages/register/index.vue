<template>
	<view class="register-page">
		<!-- 顶部品牌区 -->
		<view class="brand-section">
			<view class="decoration-circle circle-1"></view>
			<view class="decoration-circle circle-2"></view>
			<text class="brand-title">创建账号</text>
			<text class="brand-desc">加入番茄病害诊断，开启智能种植之旅</text>
		</view>

		<!-- 表单卡片 -->
		<view class="form-card">
			<view class="input-group">
				<view class="input-wrap" :class="{ focused: focusedField === 'username' }">
					<text class="input-icon">👤</text>
					<input
						v-model="form.username"
						placeholder="请输入用户名（3-50字符）"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'username'"
						@blur="focusedField = ''"
					/>
				</view>

				<view class="input-wrap" :class="{ focused: focusedField === 'email' }">
					<text class="input-icon">✉</text>
					<input
						v-model="form.email"
						placeholder="请输入邮箱（选填）"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'email'"
						@blur="focusedField = ''"
					/>
				</view>

				<view class="input-wrap" :class="{ focused: focusedField === 'password' }">
					<text class="input-icon">🔒</text>
					<input
						v-model="form.password"
						:type="showPassword ? 'text' : 'password'"
						placeholder="请输入密码（6-50字符）"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'password'"
						@blur="focusedField = ''"
					/>
					<text class="pwd-toggle" @click="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁' }}</text>
				</view>

				<view class="input-wrap" :class="{ focused: focusedField === 'confirm' }">
					<text class="input-icon">🔒</text>
					<input
						v-model="form.confirmPassword"
						:type="showPassword ? 'text' : 'password'"
						placeholder="请确认密码"
						placeholder-class="placeholder"
						class="input"
						@focus="focusedField = 'confirm'"
						@blur="focusedField = ''"
					/>
				</view>
			</view>

			<button
				class="register-btn"
				:class="{ disabled: loading }"
				:loading="loading"
				@click="handleRegister"
			>
				<text v-if="!loading">注 册</text>
			</button>

			<view class="form-footer">
				<text class="footer-text">已有账号？</text>
				<text class="login-link" @click="goLogin">返回登录</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { register } from '@/api/auth'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })
const loading = ref(false)
const focusedField = ref('')
const showPassword = ref(false)

/** 表单校验 */
function validateForm() {
	const u = form.username.trim()
	if (u.length < 3 || u.length > 50) {
		uni.showToast({ title: '用户名长度应为3-50字符', icon: 'none' })
		return false
	}
	if (form.password.length < 6 || form.password.length > 50) {
		uni.showToast({ title: '密码长度应为6-50字符', icon: 'none' })
		return false
	}
	if (form.password !== form.confirmPassword) {
		uni.showToast({ title: '两次密码不一致', icon: 'none' })
		return false
	}
	return true
}

/** 执行注册并自动登录 */
async function doRegister() {
	loading.value = true
	try {
		await register({
			username: form.username.trim(),
			email: form.email.trim() || undefined,
			password: form.password
		})
		await autoLogin()
	} catch (e) {
		// request.js 已处理错误提示
	} finally {
		loading.value = false
	}
}

/** 注册成功后自动登录 */
async function autoLogin() {
	try {
		await userStore.login({ username: form.username.trim(), password: form.password })
		uni.showToast({ title: '注册成功', icon: 'success' })
		setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 500)
	} catch (e) {
		// 注册成功但登录失败，跳转登录页
		uni.navigateTo({ url: '/pages/login/index' })
	}
}

/** 注册入口 */
function handleRegister() {
	if (loading.value) return
	if (!validateForm()) return
	doRegister()
}

/** 返回登录页 */
function goLogin() {
	uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.register-page {
	min-height: 100vh;
	background: linear-gradient(180deg, #E07A5F 0%, #C96247 35%, #F5F5F5 35%, #F5F5F5 100%);
	display: flex;
	flex-direction: column;
}

/* 品牌区 */
.brand-section {
	position: relative;
	padding: 60rpx 48rpx 100rpx;
}

.decoration-circle {
	position: absolute;
	border-radius: 50%;
	filter: blur(40rpx);
	opacity: 0.35;
}

.circle-1 { width: 180rpx; height: 180rpx; background: #F29780; top: 20rpx; right: -40rpx; }
.circle-2 { width: 140rpx; height: 140rpx; background: #F5AB96; top: 80rpx; left: -30rpx; }

.brand-title {
	display: block;
	font-size: 44rpx;
	font-weight: 700;
	color: #fff;
	letter-spacing: 4rpx;
	margin-bottom: 16rpx;
	position: relative;
	z-index: 2;
}

.brand-desc {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.9);
	line-height: 1.6;
	position: relative;
	z-index: 2;
}

/* 表单卡片 */
.form-card {
	flex: 1;
	background: #fff;
	border-radius: 48rpx 48rpx 0 0;
	padding: 56rpx 48rpx;
	margin-top: -40rpx;
	position: relative;
	z-index: 3;
	box-shadow: 0 -8rpx 32rpx rgba(0, 0, 0, 0.05);
}

/* 输入框 */
.input-group {
	margin-bottom: 40rpx;
}

.input-wrap {
	display: flex;
	align-items: center;
	background: #F8F9FA;
	border-radius: 24rpx;
	padding: 0 28rpx;
	margin-bottom: 24rpx;
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

/* 注册按钮 */
.register-btn {
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
}

.register-btn.disabled {
	opacity: 0.6;
}

.register-btn::after {
	border: none;
}

/* 底部 */
.form-footer {
	text-align: center;
	margin-top: 40rpx;
	font-size: 28rpx;
}

.footer-text {
	color: #999;
}

.login-link {
	color: #E07A5F;
	font-weight: 600;
	margin-left: 8rpx;
}
</style>
