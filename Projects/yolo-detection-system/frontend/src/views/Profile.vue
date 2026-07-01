<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="left-section slide-in-left">
        <div class="glass-card glow-border user-info-card">
          <div class="avatar-wrapper">
            <div class="avatar">
              <el-icon :size="64"><User /></el-icon>
            </div>
            <div class="avatar-badge">
              <el-icon :size="16"><Crown v-if="userInfo?.role === 'admin'" /><User v-else /></el-icon>
            </div>
          </div>
          <h2 class="username">{{ userInfo?.username || '未登录' }}</h2>
          <p class="email text-secondary">{{ userInfo?.email || '-' }}</p>
          <div class="role-tag" :class="{ admin: userInfo?.role === 'admin' }">
            <el-icon><Crown v-if="userInfo?.role === 'admin'" /><User v-else /></el-icon>
            <span>{{ userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</span>
          </div>
          <div class="divider"></div>
          <div class="info-list">
            <div class="info-item">
              <el-icon class="info-icon"><Calendar /></el-icon>
              <div class="info-content">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ formatDate(userInfo?.created_at) }}</span>
              </div>
            </div>
            <div class="info-item">
              <el-icon class="info-icon"><Message /></el-icon>
              <div class="info-content">
                <span class="info-label">用户ID</span>
                <span class="info-value">{{ userInfo?.id || '-' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card stats-card">
          <h3 class="card-title">
            <el-icon><DataAnalysis /></el-icon>
            检测统计
          </h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon total">
                <el-icon :size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ stats.total }}</span>
                <span class="stat-label">总检测次数</span>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon today">
                <el-icon :size="24"><Sunny /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ stats.today }}</span>
                <span class="stat-label">今日检测</span>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon image">
                <el-icon :size="24"><Picture /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ stats.image }}</span>
                <span class="stat-label">图片检测</span>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon video">
                <el-icon :size="24"><VideoCamera /></el-icon>
              </div>
              <div class="stat-content">
                <span class="stat-value">{{ stats.video }}</span>
                <span class="stat-label">视频检测</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-section slide-in-right">
        <div class="glass-card glow-border password-card">
          <h3 class="card-title">
            <el-icon><Lock /></el-icon>
            修改密码
          </h3>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            class="password-form"
          >
            <el-form-item prop="oldPassword" label="旧密码">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入旧密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item prop="newPassword" label="新密码">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码 (6-50字符)"
                size="large"
                :prefix-icon="Key"
                show-password
              />
            </el-form-item>
            <el-form-item prop="confirmPassword" label="确认新密码">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                size="large"
                :prefix-icon="Key"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="w-full btn-glow"
                :loading="passwordLoading"
                @click="handleChangePassword"
              >
                确认修改
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="glass-card logout-card">
          <h3 class="card-title">
            <el-icon><SwitchButton /></el-icon>
            账号操作
          </h3>
          <p class="logout-desc text-secondary">退出当前账号，返回登录页面</p>
          <el-button
            type="danger"
            size="large"
            class="logout-btn"
            @click="handleLogout"
          >
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Lock,
  Key,
  Crown,
  Calendar,
  Message,
  DataAnalysis,
  TrendCharts,
  Sunny,
  Picture,
  VideoCamera,
  SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'
import { changePassword } from '@/api/auth'
import { getHistoryList } from '@/api/history'

const router = useRouter()
const userStore = useUserStore()

const passwordFormRef = ref(null)
const passwordLoading = ref(false)

const userInfo = computed(() => userStore.userInfo)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const stats = reactive({
  total: 0,
  today: 0,
  image: 0,
  video: 0
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为 6-50 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const fetchStats = async () => {
  try {
    const res = await getHistoryList({ page: 1, pageSize: 1000 })
    const list = res.items || res.data?.items || []
    
    stats.total = res.total || res.data?.total || list.length
    
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    stats.today = list.filter(item => {
      const itemDate = new Date(item.created_at)
      return itemDate >= today
    }).length
    
    stats.image = list.filter(item => item.type === 'image' || item.detection_type === 'image').length
    stats.video = list.filter(item => item.type === 'video' || item.detection_type === 'video').length
    
    if (stats.total === 0 && list.length > 0) {
      stats.total = list.length
    }
    if (stats.image === 0 && stats.video === 0 && list.length > 0) {
      stats.image = list.length
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    await changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    ElMessage.success('密码修改成功')
    
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    passwordFormRef.value.resetFields()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '密码修改失败，请重试')
    }
  } finally {
    passwordLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？退出后需要重新登录才能使用系统。',
      '退出确认',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'logout-message-box'
      }
    )
    
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}

onMounted(() => {
  if (!userStore.userInfo) {
    userStore.fetchUserInfo()
  }
  fetchStats()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 40px 20px;
  position: relative;
  z-index: 1;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.left-section {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.user-info-card {
  padding: 40px 30px;
  text-align: center;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 32px var(--color-accent-glow);
}

.avatar-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
  border: 2px solid var(--color-border-light);
}

.username {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--color-text-primary);
}

.email {
  font-size: 14px;
  margin-bottom: 16px;
}

.role-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 20px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
}

.role-tag.admin {
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.info-list {
  margin-top: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  font-size: 18px;
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.info-value {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.stats-card {
  padding: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text-primary);
}

.card-title .el-icon {
  color: var(--color-accent);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--color-bg-secondary);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-icon.today {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.stat-icon.image {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.stat-icon.video {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.password-card {
  padding: 32px;
}

.password-form {
  margin-top: 8px;
}

.password-form :deep(.el-form-item__label) {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.password-form :deep(.el-input__wrapper) {
  padding: 4px 15px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.password-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-accent) inset;
}

.password-form :deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px var(--color-accent-glow),
              0 0 20px var(--color-accent-glow);
}

.password-form :deep(.el-input__prefix-inner .el-icon) {
  color: var(--color-text-tertiary);
}

.logout-card {
  padding: 32px;
}

.logout-desc {
  font-size: 14px;
  margin-bottom: 20px;
}

.logout-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 77, 79, 0.3);
}

.w-full {
  width: 100%;
}

@media (max-width: 968px) {
  .profile-container {
    flex-direction: column;
  }

  .left-section {
    width: 100%;
  }

  .right-section {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .profile-page {
    padding: 20px 12px;
  }

  .user-info-card {
    padding: 30px 20px;
  }

  .password-card,
  .logout-card,
  .stats-card {
    padding: 24px 20px;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .stat-item {
    padding: 12px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-value {
    font-size: 18px;
  }

  .avatar {
    width: 100px;
    height: 100px;
  }

  .avatar .el-icon {
    font-size: 48px !important;
  }

  .username {
    font-size: 20px;
  }
}

@media (max-width: 380px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
