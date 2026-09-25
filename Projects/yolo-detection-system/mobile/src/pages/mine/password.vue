<template>
	<view class="password-page">
		<PageHeader title="修改密码" :show-back="true" />

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
import PageHeader from '@/components/PageHeader.vue'

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)

const canSubmit = computed(() => {
	return oldPassword.value.length >= 6 &&
		newPassword.value.length >= 6 &&
		newPassword.value === confirmPassword.value
})

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
	background: var(--bg-2);
}

.form-section {
	padding: 32rpx 24rpx;
}

.form-item {
	background: var(--bg-1);
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
}

.form-label {
	font-size: 26rpx;
	color: var(--text-3);
	margin-bottom: 12rpx;
	display: block;
}

.form-input {
	font-size: 30rpx;
	color: var(--text-1);
	height: 48rpx;
}

.hint-text {
	padding: 0 8rpx;
	margin-top: 16rpx;
}

.hint-text text {
	font-size: 24rpx;
	color: var(--text-disabled);
}

.submit-section {
	padding: 40rpx 24rpx;
}

.submit-btn {
	width: 100%;
	height: 96rpx;
	border-radius: 48rpx;
	background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
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