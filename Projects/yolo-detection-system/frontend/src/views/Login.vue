<template>
  <div class="login-page">
    <div class="login-container">
      <div class="brand-section slide-in-left">
        <div class="brand-content">
          <div class="logo-wrapper">
            <div class="logo-icon">
              <el-icon :size="48"><Monitor /></el-icon>
            </div>
          </div>
          <h1 class="brand-title font-logo glow-text">YOLO DETECT</h1>
          <p class="brand-subtitle">智能目标检测系统</p>
          <p class="brand-desc">基于深度学习的实时目标检测平台，支持多种检测模型，快速精准识别图像中的目标物体。</p>
          <div class="brand-features">
            <div class="feature-item">
              <el-icon><Cpu /></el-icon>
              <span>高性能检测</span>
            </div>
            <div class="feature-item">
              <el-icon><Lightning /></el-icon>
              <span>实时处理</span>
            </div>
            <div class="feature-item">
              <el-icon><DataAnalysis /></el-icon>
              <span>智能分析</span>
            </div>
          </div>
        </div>
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
      </div>

      <div class="form-section slide-in-right">
        <div class="form-card glass-card glow-border">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle text-secondary">请登录您的账号</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="w-full btn-glow login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <span class="text-secondary">还没有账号？</span>
            <router-link to="/register" class="register-link">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor, Cpu, Lightning, DataAnalysis } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为 6-50 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    ElMessage.success('登录成功')
    
    const redirect = route.query.redirect || '/detect'
    router.push(redirect)
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '登录失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.login-container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  align-items: center;
  gap: 60px;
}

.brand-section {
  flex: 1;
  position: relative;
  padding: 40px;
}

.brand-content {
  position: relative;
  z-index: 2;
}

.logo-wrapper {
  margin-bottom: 24px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  border-radius: 20px;
  color: white;
  box-shadow: 0 8px 32px var(--color-accent-glow);
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 8px;
}

.brand-subtitle {
  font-size: 20px;
  color: var(--color-text-secondary);
  margin-bottom: 24px;
  font-weight: 500;
}

.brand-desc {
  font-size: 15px;
  color: var(--color-text-tertiary);
  line-height: 1.8;
  margin-bottom: 40px;
  max-width: 400px;
}

.brand-features {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.feature-item .el-icon {
  color: var(--color-accent);
  font-size: 20px;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
  z-index: 1;
}

.circle-1 {
  width: 200px;
  height: 200px;
  background: var(--color-accent);
  top: -50px;
  right: -30px;
}

.circle-2 {
  width: 150px;
  height: 150px;
  background: var(--color-accent-light);
  bottom: 20px;
  left: -20px;
}

.form-section {
  width: 440px;
  flex-shrink: 0;
}

.form-card {
  padding: 40px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
}

.login-form {
  margin-bottom: 0;
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 15px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-accent) inset;
}

.login-form :deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px var(--color-accent-glow),
              0 0 20px var(--color-accent-glow);
}

.login-form :deep(.el-input__prefix-inner .el-icon) {
  color: var(--color-text-tertiary);
}

.form-options {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.login-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
}

.register-link {
  color: var(--color-accent);
  font-weight: 500;
  margin-left: 4px;
  transition: all 0.3s ease;
}

.register-link:hover {
  color: var(--color-accent-light);
  text-shadow: 0 0 10px var(--color-accent-glow);
}

@media (max-width: 968px) {
  .login-container {
    flex-direction: column;
    gap: 40px;
  }

  .brand-section {
    text-align: center;
    padding: 20px;
  }

  .brand-content {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .brand-features {
    justify-content: center;
  }

  .brand-desc {
    text-align: center;
  }

  .form-section {
    width: 100%;
    max-width: 440px;
  }
}

@media (max-width: 480px) {
  .login-page {
    padding: 10px;
  }

  .brand-title {
    font-size: 32px;
  }

  .brand-subtitle {
    font-size: 16px;
  }

  .form-card {
    padding: 30px 24px;
  }

  .form-title {
    font-size: 24px;
  }

  .brand-features {
    gap: 20px;
  }
}
</style>
