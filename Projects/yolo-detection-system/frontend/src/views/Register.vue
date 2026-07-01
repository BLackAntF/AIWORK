<template>
  <div class="register-page">
    <div class="register-container">
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
            <h2 class="form-title">创建账号</h2>
            <p class="form-subtitle text-secondary">加入我们，开始智能检测之旅</p>
          </div>

          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="register-form"
            @keyup.enter="handleRegister"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱（选填）"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="w-full btn-glow register-btn"
                :loading="loading"
                @click="handleRegister"
              >
                注 册
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <span class="text-secondary">已有账号？</span>
            <router-link to="/login" class="login-link">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Monitor, Cpu, Lightning, DataAnalysis } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'
import { register as registerApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为 6-50 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    await registerApi({
      username: registerForm.username,
      email: registerForm.email || undefined,
      password: registerForm.password
    })
    
    ElMessage.success('注册成功，正在登录...')
    
    await userStore.login({
      username: registerForm.username,
      password: registerForm.password
    })
    
    ElMessage.success('登录成功')
    router.push('/detect')
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.register-container {
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

.register-form {
  margin-bottom: 0;
}

.register-form :deep(.el-input__wrapper) {
  padding: 4px 15px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.register-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-accent) inset;
}

.register-form :deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px var(--color-accent-glow),
              0 0 20px var(--color-accent-glow);
}

.register-form :deep(.el-input__prefix-inner .el-icon) {
  color: var(--color-text-tertiary);
}

.register-btn {
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

.login-link {
  color: var(--color-accent);
  font-weight: 500;
  margin-left: 4px;
  transition: all 0.3s ease;
}

.login-link:hover {
  color: var(--color-accent-light);
  text-shadow: 0 0 10px var(--color-accent-glow);
}

@media (max-width: 968px) {
  .register-container {
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
  .register-page {
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
