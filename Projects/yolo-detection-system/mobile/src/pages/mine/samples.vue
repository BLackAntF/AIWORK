<template>
	<view class="samples-page">
		<PageHeader title="我的样本" subtitle="检测反馈与审核进度" eyebrow="SAMPLE FEEDBACK" :show-back="true" />
		<view v-if="loading && page === 1" class="loading-row">
			<text class="loading-text">加载中...</text>
		</view>
		<EmptyState v-else-if="list.length === 0" name="inbox" title="暂无样本反馈" desc="可在检测详情中提交检测反馈" />
		<view v-else class="sample-list">
			<view v-for="item in list" :key="item.id" class="sample-card" @click="goHistory(item.history_id)">
				<image
					v-if="getFullUrl(item.image_path)"
					:src="getFullUrl(item.image_path)"
					mode="aspectFill"
					class="sample-image"
				/>
				<view class="sample-body">
					<view class="sample-head">
						<text class="mark-text" :class="item.mark_type">{{ markLabel(item.mark_type) }}</text>
						<text class="status-text" :class="item.status">{{ statusLabel(item.status) }}</text>
					</view>
					<text class="sample-line">预测：{{ item.predicted_class || '—' }}{{ confidenceText(item.predicted_confidence) }}</text>
					<text v-if="item.corrected_class" class="sample-line corrected">纠正为：{{ item.corrected_class }}</text>
					<text v-if="item.note" class="sample-note">{{ item.note }}</text>
					<text v-if="item.review_note" class="sample-note review">审核说明：{{ item.review_note }}</text>
					<view class="sample-footer">
						<text v-if="item.auto_created" class="auto-text">低置信度自动收录</text>
						<text class="time-text">{{ formatTime(item.created_at) }}</text>
					</view>
				</view>
			</view>
			<view v-if="loading" class="loading-row"><text class="loading-text">加载更多...</text></view>
			<view v-else-if="!hasMore" class="no-more"><text class="no-more-text">- 已加载全部 -</text></view>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { getMySamples } from '@/api/history'
import { getFullUrl } from '@/utils/format'
import { showError } from '@/utils/error'
import PageHeader from '@/components/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'

const MARK_LABELS = { correct: '标注正确', misclassified: '识别错误', missed: '漏检', uncertain: '不确定' }
const STATUS_LABELS = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
const list = ref([])
const page = ref(1)
const pageSize = 10
const hasMore = ref(true)
const loading = ref(false)

function markLabel(type) {
	return MARK_LABELS[type] || '未知反馈'
}

function statusLabel(status) {
	return STATUS_LABELS[status] || '未知状态'
}

function confidenceText(value) {
	return value == null ? '' : `（${(value * 100).toFixed(1)}%）`
}

function formatTime(value) {
	if (!value) return ''
	const date = new Date(value)
	return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

async function loadList(refresh = false) {
	if (loading.value) return
	loading.value = true
	if (refresh) page.value = 1
	const requestedPage = page.value
	try {
		const data = await getMySamples({ page: requestedPage, page_size: pageSize })
		const items = data.list || []
		list.value = refresh ? items : [...list.value, ...items]
		hasMore.value = list.value.length < (data.total || 0)
	} catch (e) {
		if (!refresh) page.value = requestedPage - 1
		showError(e, '加载失败')
	} finally {
		loading.value = false
		uni.stopPullDownRefresh()
	}
}

function goHistory(id) {
	uni.navigateTo({ url: `/pages/history/detail?id=${id}` })
}

onLoad(() => loadList(true))
onPullDownRefresh(() => loadList(true))
onReachBottom(() => {
	if (!hasMore.value || loading.value) return
	page.value += 1
	loadList()
})
</script>

<style lang="scss" scoped>
.samples-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.sample-list {
	padding: 24rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.sample-card {
	display: flex;
	gap: 20rpx;
	padding: 20rpx;
	border-radius: 20rpx;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
}

.sample-image {
	width: 160rpx;
	height: 160rpx;
	flex-shrink: 0;
	border-radius: 14rpx;
	background: var(--bg-2);
}

.sample-body {
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.sample-head,
.sample-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12rpx;
}

.mark-text,
.status-text {
	font-size: 24rpx;
	font-weight: 600;
}

.mark-text { color: var(--brand); }
.mark-text.correct { color: var(--forest-2); }
.status-text { color: var(--warning); }
.status-text.approved { color: var(--forest-2); }
.status-text.rejected { color: var(--error); }

.sample-line,
.sample-note {
	font-size: 25rpx;
	line-height: 1.5;
	color: var(--text-2);
	word-break: break-all;
}

.sample-line.corrected { color: var(--brand); }
.sample-note.review { color: var(--text-1); }
.auto-text,
.time-text {
	font-size: 22rpx;
	color: var(--text-3);
}

.loading-row,
.no-more {
	padding: 40rpx;
	text-align: center;
}

.loading-text,
.no-more-text {
	font-size: 25rpx;
	color: var(--text-3);
}
</style>
