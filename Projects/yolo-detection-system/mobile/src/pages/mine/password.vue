<template>
	<view class="password-page">
		<view class="page-header">
			<view class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</view>
			<text class="header-title">修改密码</text>
			<view class="placeholder"></view>
		</view>

		<view class="form-section">
			<view class="form-item">
				<text class="form-label">原密码</text>
				<input
					class="form-input"
					v-model="oldPassword"
					type="password"
					placeholder="请输入原密码"
				/>
			</view>
			<view class="form-item">
				<text class="form-label">新密码</text>
				<input
					class="form-input"
					v-model="newPassword"
					type="password"
					placeholder="请输入新密码（至少6位）"
				/>
			</view>
			<view class="form-item">
				<text class="form-label">确认新密码</text>
				<input
					class="form-input"
					v-model="confirmPassword"
					type="password"
					placeholder="请再次输入新密码"
				/>
			</view>

			<view class="hint-text">
				<text>密码长度至少6位，建议包含字母和数字</text>
			</view>
		</view>

		<view class="submit-section">
			<button
				class="submit-btn"
				:class="{ disabled: !canSubmit }"
				:loading="isSubmitting"
				@click="handleSubmit"
			>确认修改</button>
		</view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { changePassword } from '@/api/auth'

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)

const canSubmit = computed(() => {
	return oldPassword.value.length >= 6 &&
		newPassword.value.length >= 6 &&
		newPassword.value === confirmPassword.value
})

function goBack() {
	uni.navigateBack()
}

async function handleSubmit() {
	if (!canSubmit.value || isSubmitting.value) return

	isSubmitting.value = true
	try {
		await changePassword({ old_password: oldPassword.value, new_password: newPassword.value })
		uni.showToast({ title: '修改成功', icon: 'success' })
		setTimeout(() => {
			uni.navigateBack()
		}, 1500)
	} catch (e) {
		uni.showToast({ title: '修改失败，请检查原密码', icon: 'none' })
	} finally {
		isSubmitting.value = false
	}
}
</script>

<style lang="scss" scoped>
.password-page {
	min-height: 100vh;
	background: #F5F5F5;
}

.page-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 32rpx;
	background: #E07A5F;
}

.back-btn {
	width: 64rpx;
	height: 64rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.back-icon {
	font-size: 48rpx;
	color: #fff;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #fff;
}

.placeholder {
	width: 64rpx;
}

.form-section {
	padding: 32rpx 24rpx;
}

.form-item {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
}

.form-label {
	font-size: 26rpx;
	color: #999;
	margin-bottom: 12rpx;
	display: block;
}

.form-input {
	font-size: 30rpx;
	color: #333;
	height: 48rpx;
}

.hint-text {
	padding: 0 8rpx;
	margin-top: 16rpx;
}

.hint-text text {
	font-size: 24rpx;
	color: #bbb;
}

.submit-section {
	padding: 40rpx 24rpx;
}

.submit-btn {
	width: 100%;
	height: 96rpx;
	border-radius: 48rpx;
	background: linear-gradient(135deg, #E07A5F 0%, #C96247 100%);
	color: #fff;
	font-size: 32rpx;
	font-weight: 600;
}

.submit-btn.disabled {
	opacity: 0.5;
}

.submit-btn::after {
	border: none;
}
</style>
