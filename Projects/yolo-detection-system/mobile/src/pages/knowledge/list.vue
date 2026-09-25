<template>
	<view class="knowledge-page">
		<PageHeader title="知识库" :show-back="true" />

		<view class="search-section">
			<view class="search-box">
				<AppIcon class="search-icon" name="search" :size="32" color="#ADB5BD" />
				<input
					class="search-input"
					v-model="keyword"
					placeholder="搜索病害知识..."
					confirm-type="search"
					@confirm="onSearch"
				/>
				<view v-if="keyword" class="search-clear" @click="clearSearch">
					<AppIcon name="close" :size="28" color="#ADB5BD" />
				</view>
			</view>
		</view>

		<scroll-view
			class="knowledge-content"
			scroll-y
			@refresherrefresh="onRefresh"
			@scrolltolower="onLoadMore"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
			:show-scrollbar="false"
		>
			<view class="category-bar">
				<text
					v-for="cat in categories"
					:key="cat.id"
					class="category-item"
					:class="{ active: selectedCategory === cat.id }"
					@click="selectCategory(cat.id)"
				>{{ cat.name }}</text>
			</view>

			<view v-if="loading && !refreshing" class="loading-row">
				<text class="loading-text">加载中...</text>
			</view>

			<EmptyState v-else-if="list.length === 0" name="book" title="暂无知识" desc="没有找到相关内容" />

			<view v-else class="knowledge-list">
				<view
					v-for="item in list"
					:key="item.id"
					class="knowledge-item"
					@click="goDetail(item.id)"
				>
					<text class="item-title">{{ item.title }}</text>
					<text class="item-summary">{{ item.summary }}</text>
					<view class="item-footer">
						<text class="item-category">{{ item.category || '未分类' }}</text>
						<text class="item-time">{{ formatTime(item.created_at) }}</text>
					</view>
				</view>
			</view>

			<view v-if="hasMore && !loading" class="load-more">
				<text class="load-more-text">加载更多...</text>
			</view>
			<view v-if="!hasMore && list.length > 0" class="no-more">
				<text class="no-more-text">- 已加载全部 -</text>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getKnowledgeList, getCategories } from '@/api/knowledge'
import AppIcon from '@/components/AppIcon.vue'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'

const keyword = ref('')
const categories = ref([])
const selectedCategory = ref('')
const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = ref(10)
const hasMore = ref(true)

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}/${date.getDate()}`
}

async function loadCategories() {
	try {
		const data = await getCategories()
		const names = data.categories || []
		categories.value = [{ id: '', name: '全部' }, ...names.map(name => ({ id: name, name }))]
	} catch (e) {
		categories.value = [{ id: '', name: '全部' }]
	}
}

async function loadList(isRefresh = false) {
	if (loading.value) return

	loading.value = true
	try {
		const params = { page: page.value, page_size: pageSize.value }
		if (keyword.value) params.keyword = keyword.value
		if (selectedCategory.value) params.category = selectedCategory.value

		const data = await getKnowledgeList(params)
		if (isRefresh) {
			list.value = data.items || []
		} else {
			list.value = [...list.value, ...(data.items || [])]
		}
		hasMore.value = (data.items || []).length >= pageSize.value
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onSearch() {
	page.value = 1
	hasMore.value = true
	loadList(true)
}

function clearSearch() {
	keyword.value = ''
	onSearch()
}

function selectCategory(id) {
	selectedCategory.value = id
	page.value = 1
	hasMore.value = true
	loadList(true)
}

function onRefresh() {
	refreshing.value = true
	page.value = 1
	hasMore.value = true
	loadList(true)
}

function onLoadMore() {
	if (hasMore.value && !loading.value) {
		page.value++
		loadList()
	}
}

function goDetail(id) {
	uni.navigateTo({ url: `/pages/knowledge/detail?id=${id}` })
}

onMounted(() => {
	loadCategories()
	loadList()
})
</script>

<style lang="scss" scoped>
.knowledge-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.search-section {
	padding: 20rpx 24rpx;
	background: var(--bg-1);
}

.search-box {
	display: flex;
	align-items: center;
	background: var(--bg-2);
	border-radius: 40rpx;
	padding: 0 24rpx;
	height: 72rpx;
}

.search-icon {
	font-size: 28rpx;
	margin-right: 12rpx;
}

.search-input {
	flex: 1;
	font-size: 28rpx;
	background: transparent;
}

.search-clear {
	width: 36rpx;
	height: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--text-3);
	font-size: 24rpx;
}

.knowledge-content {
	height: calc(100vh - 200rpx);
}

.category-bar {
	display: flex;
	gap: 16rpx;
	padding: 20rpx 24rpx;
	overflow-x: auto;
	white-space: nowrap;
	background: var(--bg-1);
	border-bottom: 1rpx solid var(--border-light);
}

.category-item {
	padding: 12rpx 28rpx;
	border-radius: 24rpx;
	font-size: 26rpx;
	color: var(--text-2);
	background: var(--bg-2);
	flex-shrink: 0;
}

.category-item.active {
	background: rgba(224, 122, 95, 0.1);
	color: var(--brand);
	font-weight: 600;
}

.loading-row {
	padding: 60rpx;
	text-align: center;
}

.loading-text {
	font-size: 28rpx;
	color: var(--text-3);
}

.knowledge-list {
	padding: 24rpx;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.knowledge-item {
	background: var(--bg-1);
	border-radius: 20rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.item-title {
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-1);
	margin-bottom: 12rpx;
	display: block;
}

.item-summary {
	font-size: 26rpx;
	color: var(--text-2);
	line-height: 1.5;
	margin-bottom: 16rpx;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.item-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.item-category {
	font-size: 24rpx;
	color: var(--brand);
	background: rgba(224, 122, 95, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.item-time {
	font-size: 24rpx;
	color: var(--text-3);
}

.load-more {
	padding: 32rpx;
	text-align: center;
}

.load-more-text {
	font-size: 26rpx;
	color: var(--text-3);
}

.no-more {
	padding: 24rpx;
	text-align: center;
}

.no-more-text {
	font-size: 24rpx;
	color: var(--text-disabled);
}
</style>