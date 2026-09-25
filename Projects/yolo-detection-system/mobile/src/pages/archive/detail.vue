<template>
	<view class="archive-page">
		<LoadingOverlay :visible="loading" text="加载中..." />

		<view v-if="profile" class="content">
			<!-- 头部 -->
			<view class="header">
				<text class="disease-name">{{ profile.disease_name }}</text>
				<text class="disease-en">{{ profile.class_name }}</text>
			</view>

			<!-- 折叠面板 -->
			<view class="collapse-list">
				<view
					v-for="(item, idx) in collapseItems"
					:key="idx"
					class="collapse-item"
					@click="toggleCollapse(idx)"
				>
					<view class="collapse-header">
						<text class="collapse-icon">{{ item.icon }}</text>
						<text class="collapse-title">{{ item.title }}</text>
						<text class="collapse-arrow" :class="{ expanded: expandedIndex === idx }">›</text>
					</view>
					<view class="collapse-body" :class="{ visible: expandedIndex === idx }">
						<text class="collapse-content">{{ item.content }}</text>
					</view>
				</view>
			</view>

			<!-- 推荐药剂 -->
			<view v-if="profile.pesticides" class="pesticides-card">
				<text class="card-title">📌 推荐药剂</text>
				<view class="pesticides-list">
					<text
						v-for="(pesticide, idx) in pesticideList"
						:key="idx"
						class="pesticide-item"
					>{{ pesticide }}</text>
				</view>
			</view>
		</view>

		<EmptyState v-else-if="!loading" icon="📭" title="档案不存在" />
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getKnowledgeDetail } from '@/api/knowledge'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import EmptyState from '@/components/EmptyState.vue'

const loading = ref(true)
const profile = ref(null)
const expandedIndex = ref(0)

const pesticideList = computed(() => {
	if (!profile.value?.pesticides) return []
	return profile.value.pesticides.split(/[,，、]/).filter(p => p.trim())
})

const collapseItems = computed(() => {
	if (!profile.value) return []
	return [
		{ icon: '🌱', title: '诱因', content: profile.value.causes },
		{ icon: '✨', title: '典型症状', content: profile.value.symptoms },
		{ icon: '📅', title: '发生规律', content: profile.value.occurrence || '暂无数据' },
		{ icon: '🛡️', title: '预防措施', content: profile.value.prevention },
		{ icon: '💊', title: '治疗方案', content: profile.value.treatment }
	]
})

function toggleCollapse(idx) {
	expandedIndex.value = expandedIndex.value === idx ? -1 : idx
}

async function loadProfile() {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const id = currentPage.options?.id

	if (!id) {
		loading.value = false
		return
	}

	try {
		const data = await getKnowledgeDetail(id)
		profile.value = data
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	loadProfile()
})
</script>

<style lang="scss" scoped>
.archive-page {
	min-height: 100vh;
	background: #F5F5F5;
}

.content {
	padding: 24rpx;
	padding-bottom: 100rpx;
}

.header {
	background: linear-gradient(135deg, #E07A5F 0%, #C96247 100%);
	border-radius: 24rpx;
	padding: 36rpx;
	margin-bottom: 24rpx;
}

.disease-name {
	display: block;
	font-size: 40rpx;
	font-weight: 700;
	color: #fff;
	margin-bottom: 8rpx;
}

.disease-en {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.85);
}

.collapse-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
	margin-bottom: 24rpx;
}

.collapse-item {
	background: #fff;
	border-radius: 20rpx;
	overflow: hidden;
}

.collapse-header {
	display: flex;
	align-items: center;
	padding: 28rpx;
	gap: 16rpx;
}

.collapse-icon {
	font-size: 36rpx;
}

.collapse-title {
	flex: 1;
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
}

.collapse-arrow {
	font-size: 40rpx;
	color: #ccc;
	transition: transform 0.3s ease;
}

.collapse-arrow.expanded {
	transform: rotate(90deg);
}

.collapse-body {
	max-height: 0;
	overflow: hidden;
	transition: max-height 0.3s ease, padding 0.3s ease;
}

.collapse-body.visible {
	max-height: 800rpx;
	padding: 0 28rpx 28rpx;
}

.collapse-content {
	font-size: 28rpx;
	color: #666;
	line-height: 1.7;
}

.pesticides-card {
	background: #fff;
	border-radius: 20rpx;
	padding: 28rpx;
}

.card-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.pesticides-list {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.pesticide-item {
	background: rgba(255, 152, 0, 0.15);
	color: #FF9800;
	font-size: 28rpx;
	padding: 12rpx 24rpx;
	border-radius: 20rpx;
}
</style>
