<template>
  <div class="login-container">
    <div class="login-header">
      <div class="logo">🚗</div>
      <h1 class="title">驾校学员端</h1>
      <p class="subtitle">学车更轻松</p>
    </div>
    <van-form @submit="onSubmit" class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="username"
          label="账号"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请填写用户名' }]"
          left-icon="user-o"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }]"
          left-icon="lock"
        />
      </van-cell-group>
      <div class="login-btn">
        <van-button
          type="primary"
          native-type="submit"
          block
          :loading="loading"
          loading-text="登录中..."
        >
          登录
        </van-button>
      </div>
    </van-form>
    <div class="login-footer">
      <p>如有疑问请联系客服</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

const onSubmit = async (values) => {
  try {
    loading.value = true
    await userStore.login(values.username, values.password)
    showToast('登录成功')
    router.replace('/home')
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  padding: 60px 20px 20px;
  box-sizing: border-box;
}

.login-header {
  text-align: center;
  margin-bottom: 50px;
}

.logo {
  font-size: 80px;
  margin-bottom: 20px;
}

.title {
  color: #fff;
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

.login-form {
  margin-top: 40px;
}

.login-btn {
  margin: 40px 16px 0;
}

.login-btn :deep(.van-button) {
  height: 48px;
  font-size: 18px;
  border-radius: 24px;
}

.login-footer {
  position: fixed;
  bottom: 30px;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}
</style>
