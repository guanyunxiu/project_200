<template>
  <div class="register-container">
    <div class="register-header">
      <div class="logo">🚗</div>
      <h1 class="title">学员注册</h1>
      <p class="subtitle">开启学车之旅</p>
    </div>
    <van-form @submit="onSubmit" class="register-form">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请填写用户名' }, { min: 3, message: '用户名至少3位' }]"
          left-icon="user-o"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }, { min: 6, message: '密码至少6位' }]"
          left-icon="lock"
        />
        <van-field
          v-model="form.name"
          name="name"
          label="真实姓名"
          placeholder="请输入真实姓名"
          :rules="[{ required: true, message: '请填写真实姓名' }]"
        />
        <van-field
          v-model="form.phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号"
          :rules="[{ required: true, message: '请填写手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]"
        />
        <van-field
          v-model="form.id_card"
          name="id_card"
          label="身份证号"
          placeholder="请输入身份证号"
          :rules="[{ required: true, message: '请填写身份证号' }, { len: 18, message: '身份证号为18位' }]"
        />
        <van-field
          v-model="form.gender"
          name="gender"
          label="性别"
          is-link
          readonly
          placeholder="请选择性别"
          :rules="[{ required: true, message: '请选择性别' }]"
          @click="showGenderPicker = true"
        />
        <van-field
          v-model="form.license_type"
          name="license_type"
          label="驾照类型"
          is-link
          readonly
          placeholder="请选择驾照类型"
          :rules="[{ required: true, message: '请选择驾照类型' }]"
          @click="showLicensePicker = true"
        />
        <van-field
          v-model="form.birthday"
          name="birthday"
          label="出生日期"
          is-link
          readonly
          placeholder="请选择出生日期"
          :rules="[{ required: true, message: '请选择出生日期' }]"
          @click="showBirthdayPicker = true"
        />
        <van-field
          v-model="form.address"
          name="address"
          label="住址"
          placeholder="请输入住址（选填）"
          type="textarea"
          autosize
        />
      </van-cell-group>
      <div class="register-btn">
        <van-button
          type="primary"
          native-type="submit"
          block
          :loading="loading"
          loading-text="注册中..."
        >
          注册
        </van-button>
      </div>
      <div class="login-link">
        <span>已有账号？</span>
        <span class="link" @click="goToLogin">去登录</span>
      </div>
    </van-form>

    <van-popup v-model:show="showGenderPicker" position="bottom">
      <van-picker
        :columns="genderColumns"
        @confirm="onGenderConfirm"
        @cancel="showGenderPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showLicensePicker" position="bottom">
      <van-picker
        :columns="licenseColumns"
        @confirm="onLicenseConfirm"
        @cancel="showLicensePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showBirthdayPicker" position="bottom">
      <van-date-picker
        v-model="currentBirthday"
        type="date"
        :max-date="new Date()"
        @confirm="onBirthdayConfirm"
        @cancel="showBirthdayPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const showGenderPicker = ref(false)
const showLicensePicker = ref(false)
const showBirthdayPicker = ref(false)
const currentBirthday = ref([2000, 1, 1])

const genderColumns = [
  { text: '男', value: 'male' },
  { text: '女', value: 'female' }
]

const licenseColumns = [
  { text: 'C1证（手动挡）', value: 'C1' },
  { text: 'C2证（自动挡）', value: 'C2' },
  { text: 'D证（摩托车）', value: 'D' }
]

const form = reactive({
  username: '',
  password: '',
  name: '',
  gender: '',
  phone: '',
  id_card: '',
  license_type: '',
  birthday: '',
  address: ''
})

const onGenderConfirm = ({ selectedOptions }) => {
  form.gender = selectedOptions[0].value
  showGenderPicker.value = false
}

const onLicenseConfirm = ({ selectedOptions }) => {
  form.license_type = selectedOptions[0].value
  showLicensePicker.value = false
}

const onBirthdayConfirm = ({ selectedValues }) => {
  const year = selectedValues[0]
  const month = String(selectedValues[1]).padStart(2, '0')
  const day = String(selectedValues[2]).padStart(2, '0')
  form.birthday = `${year}-${month}-${day}`
  showBirthdayPicker.value = false
}

const onSubmit = async () => {
  try {
    loading.value = true
    await userStore.register(form)
    showToast('注册成功')
    router.replace('/home')
  } catch (error) {
    console.error('Register error:', error)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  padding: 40px 20px 20px;
  box-sizing: border-box;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 60px;
  margin-bottom: 10px;
}

.title {
  color: #fff;
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.register-form {
  margin-top: 20px;
}

.register-btn {
  margin: 30px 16px 0;
}

.register-btn :deep(.van-button) {
  height: 48px;
  font-size: 18px;
  border-radius: 24px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.login-link .link {
  color: #fff;
  font-weight: bold;
  margin-left: 5px;
}
</style>
