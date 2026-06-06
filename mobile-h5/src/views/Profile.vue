<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="avatar">
        {{ studentInfo?.name?.charAt(0) || '学' }}
      </div>
      <div class="user-info">
        <div class="user-name">{{ studentInfo?.name || '学员' }}</div>
        <div class="user-phone">{{ userInfo?.phone || studentInfo?.phone || '-' }}</div>
      </div>
    </div>

    <van-cell-group inset class="info-group">
      <van-cell title="学员编号" :value="studentInfo?.id || '-'" />
      <van-cell title="身份证号" :value="maskIdCard(studentInfo?.id_card)" />
      <van-cell title="准驾车型" :value="studentInfo?.license_type_display || '-'" />
      <van-cell title="学员状态" :value="studentInfo?.status_display || '-'" />
      <van-cell title="报名日期" :value="studentInfo?.enroll_date || '-'" />
      <van-cell title="所属驾校" :value="studentInfo?.school_name || '-'">
        <template #right-icon>
          <van-icon name="arrow" />
        </template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset class="info-group">
      <van-cell title="套餐名称" :value="studentInfo?.package_name || '-'" />
      <van-cell title="总学时" :value="hoursInfo.total_hours || 0" />
      <van-cell title="已用学时" :value="hoursInfo.used_hours || 0" />
      <van-cell title="剩余学时" :value="hoursInfo.remaining_hours || 0">
        <template #right-icon>
          <span class="remaining-hours">{{ hoursInfo.remaining_hours || 0 }}</span>
        </template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset class="menu-group">
      <van-cell title="缴费记录" is-link @click="goTo('/fee-query')">
        <template #icon>💰</template>
      </van-cell>
      <van-cell title="分期还款" is-link @click="goTo('/installment')">
        <template #icon>📋</template>
      </van-cell>
      <van-cell title="我的预约" is-link @click="goTo('/booking')">
        <template #icon>📅</template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset class="menu-group">
      <van-cell title="修改密码" is-link @click="showPasswordPopup = true">
        <template #icon>🔒</template>
      </van-cell>
      <van-cell title="联系客服" is-link @click="contactService">
        <template #icon>📞</template>
      </van-cell>
      <van-cell title="关于我们" is-link @click="showAboutPopup = true">
        <template #icon>ℹ️</template>
      </van-cell>
    </van-cell-group>

    <div class="logout-btn">
      <van-button type="danger" block @click="handleLogout">
        退出登录
      </van-button>
    </div>

    <van-tabbar v-model="activeTab" active-color="#1989fa">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/fee-query">查费</van-tabbar-item>
      <van-tabbar-item icon="bill-o" to="/installment">分期</van-tabbar-item>
      <van-tabbar-item icon="calendar-o" to="/booking">约课</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>

    <van-popup v-model:show="showPasswordPopup" round position="bottom" :style="{ height: 'auto' }">
      <div class="password-popup">
        <div class="popup-header">
          <div class="popup-title">修改密码</div>
          <van-icon name="cross" @click="showPasswordPopup = false" />
        </div>
        <van-form @submit="submitPassword">
          <van-cell-group inset>
            <van-field
              v-model="oldPassword"
              type="password"
              name="oldPassword"
              label="原密码"
              placeholder="请输入原密码"
              :rules="[{ required: true, message: '请输入原密码' }]"
            />
            <van-field
              v-model="newPassword"
              type="password"
              name="newPassword"
              label="新密码"
              placeholder="请输入新密码"
              :rules="[
                { required: true, message: '请输入新密码' },
                { min: 6, message: '密码至少6位' }
              ]"
            />
            <van-field
              v-model="confirmPassword"
              type="password"
              name="confirmPassword"
              label="确认密码"
              placeholder="请再次输入新密码"
              :rules="[{ required: true, message: '请再次输入新密码' }]"
            />
          </van-cell-group>
          <div class="popup-actions">
            <van-button native-type="submit" type="primary" block :loading="passwordLoading">
              确认修改
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <van-popup v-model:show="showAboutPopup" round position="bottom" :style="{ height: '60%' }">
      <div class="about-popup">
        <div class="popup-header">
          <div class="popup-title">关于我们</div>
          <van-icon name="cross" @click="showAboutPopup = false" />
        </div>
        <div class="about-content">
          <div class="about-logo">🚗</div>
          <h3 class="about-title">驾校学员端</h3>
          <p class="about-version">版本 1.0.0</p>
          <div class="about-desc">
            <p>驾校学员端是一款为驾校学员打造的移动应用，提供便捷的学车服务。</p>
            <p>主要功能：</p>
            <ul>
              <li>• 费用查询：随时查看缴费记录和欠费情况</li>
              <li>• 分期还款：灵活的分期还款方式</li>
              <li>• 自主约课：在线预约考试，省时省力</li>
              <li>• 个人中心：管理个人信息</li>
            </ul>
          </div>
          <div class="about-footer">
            <p>© 2024 驾校管理系统 版权所有</p>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { useUserStore } from '@/store/user'
import { getStudentHoursApi } from '@/api/student'
import { changePasswordApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const studentInfo = computed(() => userStore.studentInfo)

const activeTab = ref(4)
const hoursInfo = ref({ total_hours: 0, used_hours: 0, remaining_hours: 0 })
const showPasswordPopup = ref(false)
const showAboutPopup = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordLoading = ref(false)

const maskIdCard = (idCard) => {
  if (!idCard) return '-'
  return idCard.substring(0, 6) + '********' + idCard.substring(14)
}

const loadHours = async () => {
  if (studentInfo.value?.id) {
    const res = await getStudentHoursApi(studentInfo.value.id)
    hoursInfo.value = res
  }
}

const goTo = (path) => {
  router.push(path)
}

const contactService = () => {
  showToast('客服电话：400-888-8888')
}

const submitPassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    showToast('两次输入的密码不一致')
    return
  }
  try {
    passwordLoading.value = true
    await changePasswordApi(oldPassword.value, newPassword.value)
    showToast('密码修改成功')
    showPasswordPopup.value = false
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (error) {
    console.error('Change password error:', error)
  } finally {
    passwordLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await showDialog({
      title: '确认退出',
      message: '确定要退出登录吗？',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    userStore.logout()
    showToast('已退出登录')
    router.replace('/login')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Logout error:', error)
    }
  }
}

onMounted(() => {
  loadHours()
})
</script>

<style scoped>
.profile-container {
  padding-bottom: 80px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.profile-header {
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  color: #fff;
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  margin-right: 16px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 6px;
}

.user-phone {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.info-group {
  margin: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.menu-group {
  margin: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.menu-group :deep(.van-cell__icon) {
  font-size: 20px;
  margin-right: 12px;
}

.remaining-hours {
  color: #07c160;
  font-weight: bold;
  font-size: 16px;
}

.logout-btn {
  margin: 24px 16px;
}

.password-popup {
  padding-bottom: 20px;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #ebedf0;
}

.popup-title {
  font-size: 16px;
  font-weight: bold;
}

.popup-actions {
  padding: 16px;
}

.about-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.about-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px 20px;
  text-align: center;
}

.about-logo {
  font-size: 80px;
  margin-bottom: 16px;
}

.about-title {
  font-size: 22px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 8px;
}

.about-version {
  font-size: 14px;
  color: #969799;
  margin-bottom: 24px;
}

.about-desc {
  text-align: left;
  color: #646566;
  font-size: 14px;
  line-height: 1.8;
}

.about-desc ul {
  margin-top: 12px;
  padding-left: 0;
}

.about-desc li {
  list-style: none;
  margin-bottom: 8px;
}

.about-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebedf0;
  color: #969799;
  font-size: 12px;
}
</style>
