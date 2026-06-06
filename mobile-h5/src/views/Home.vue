<template>
  <div class="home-container">
    <div class="user-card">
      <van-cell>
        <template #icon>
          <div class="avatar">
            {{ studentInfo?.name?.charAt(0) || '学' }}
          </div>
        </template>
        <template #title>
          <span class="user-name">{{ studentInfo?.name || '学员' }}</span>
        </template>
        <template #label>
          <span class="user-info">{{ studentInfo?.license_type_display }} | {{ studentInfo?.status_display }}</span>
        </template>
        <van-tag type="primary" size="medium" slot="right-icon">
          {{ studentInfo?.coach_info?.real_name ? studentInfo.coach_info.real_name + '教练' : '未分配教练' }}
        </van-tag>
      </van-cell>
    </div>

    <div class="stats-card">
      <div class="stats-item">
        <div class="stats-value">{{ hoursInfo.total_hours || 0 }}</div>
        <div class="stats-label">总学时</div>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-item">
        <div class="stats-value">{{ hoursInfo.used_hours || 0 }}</div>
        <div class="stats-label">已学</div>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-item">
        <div class="stats-value remaining">{{ hoursInfo.remaining_hours || 0 }}</div>
        <div class="stats-label">剩余</div>
      </div>
    </div>

    <div class="section-title">快捷入口</div>
    <div class="quick-menu">
      <div class="menu-item" @click="goTo('/fee-query')">
        <div class="menu-icon fee">💰</div>
        <div class="menu-text">费用查询</div>
      </div>
      <div class="menu-item" @click="goTo('/installment')">
        <div class="menu-icon installment">📋</div>
        <div class="menu-text">分期还款</div>
      </div>
      <div class="menu-item" @click="goTo('/booking')">
        <div class="menu-icon booking">📅</div>
        <div class="menu-text">自主约课</div>
      </div>
      <div class="menu-item" @click="goTo('/profile')">
        <div class="menu-icon profile">👤</div>
        <div class="menu-text">个人中心</div>
      </div>
    </div>

    <div class="section-title">我的预约</div>
    <van-list v-model:loading="bookingLoading" :finished="bookingFinished" finished-text="没有更多了" @load="loadBookings">
      <div v-if="myBookings.length === 0 && !bookingLoading" class="empty-state">
        <van-empty description="暂无预约记录" />
      </div>
      <van-cell
        v-for="booking in myBookings"
        :key="booking.id"
        :title="booking.schedule_info?.subject_display"
        :label="booking.schedule_info?.exam_date + ' ' + booking.schedule_info?.start_time"
      >
        <template #right-icon>
          <van-tag :type="getBookingTagType(booking.status)">{{ booking.status_display }}</van-tag>
        </template>
      </van-cell>
    </van-list>

    <van-tabbar v-model="activeTab" active-color="#1989fa">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/fee-query">查费</van-tabbar-item>
      <van-tabbar-item icon="bill-o" to="/installment">分期</van-tabbar-item>
      <van-tabbar-item icon="calendar-o" to="/booking">约课</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getStudentHoursApi } from '@/api/student'
import { getBookingListApi } from '@/api/exam'

const router = useRouter()
const userStore = useUserStore()

const studentInfo = computed(() => userStore.studentInfo)
const activeTab = ref(0)
const hoursInfo = ref({ total_hours: 0, used_hours: 0, remaining_hours: 0 })

const myBookings = ref([])
const bookingLoading = ref(false)
const bookingFinished = ref(false)
const bookingPage = ref(1)

const loadHours = async () => {
  if (studentInfo.value?.id) {
    const res = await getStudentHoursApi(studentInfo.value.id)
    hoursInfo.value = res
  }
}

const loadBookings = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getBookingListApi({
      student_id: studentInfo.value.id,
      page: bookingPage.value,
      page_size: 10
    })
    const results = Array.isArray(res) ? res : (res.results || [])
    myBookings.value = [...myBookings.value, ...results]
    if (results.length < 10) {
      bookingFinished.value = true
    }
    bookingPage.value++
  } finally {
    bookingLoading.value = false
  }
}

const getBookingTagType = (status) => {
  const types = {
    pending: 'warning',
    approved: 'success',
    cancelled: 'info',
    passed: 'success',
    failed: 'danger',
    absent: 'danger'
  }
  return types[status] || 'default'
}

const goTo = (path) => {
  router.push(path)
}

onMounted(() => {
  loadHours()
})
</script>

<style scoped>
.home-container {
  padding-bottom: 60px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.user-card {
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  padding: 20px 16px;
  margin-bottom: 16px;
}

.user-card :deep(.van-cell) {
  background: transparent;
  color: #fff;
}

.user-card :deep(.van-cell__title) {
  color: #fff;
}

.user-card :deep(.van-cell__label) {
  color: rgba(255, 255, 255, 0.8);
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
}

.user-info {
  font-size: 13px;
}

.stats-card {
  background: #fff;
  margin: 0 16px 16px;
  border-radius: 12px;
  padding: 20px 0;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.stats-item {
  flex: 1;
  text-align: center;
}

.stats-value {
  font-size: 28px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 4px;
}

.stats-value.remaining {
  color: #07c160;
}

.stats-label {
  font-size: 13px;
  color: #969799;
}

.stats-divider {
  width: 1px;
  height: 40px;
  background-color: #ebedf0;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
  padding: 0 16px;
  margin-bottom: 12px;
}

.quick-menu {
  background: #fff;
  margin: 0 16px 16px;
  border-radius: 12px;
  padding: 20px 0;
  display: flex;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.menu-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.menu-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 8px;
}

.menu-icon.fee {
  background: #fff7e6;
}

.menu-icon.installment {
  background: #e6f7ff;
}

.menu-icon.booking {
  background: #f6ffed;
}

.menu-icon.profile {
  background: #fff0f6;
}

.menu-text {
  font-size: 13px;
  color: #323233;
}

.empty-state {
  padding: 40px 0;
}
</style>
