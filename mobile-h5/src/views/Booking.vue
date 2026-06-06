<template>
  <div class="booking-container">
    <van-nav-bar title="自主约课" left-arrow @click-left="onClickLeft" />

    <van-tabs v-model:active="activeTab" sticky offset-top="46px">
      <van-tab title="可预约" name="available">
        <div class="filter-bar">
          <van-dropdown-menu>
            <van-dropdown-item v-model="subjectFilter" :options="subjectOptions" />
          </van-dropdown-menu>
        </div>
        <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad">
          <div v-if="availableSchedules.length === 0 && !loading" class="empty-state">
            <van-empty description="暂无可预约考试" />
          </div>
          <van-cell-group inset v-for="schedule in availableSchedules" :key="schedule.id" class="schedule-card">
            <van-cell :title="schedule.subject_display">
              <template #right-icon>
                <van-tag type="primary">{{ schedule.room_name }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="考试日期" :value="schedule.exam_date" />
            <van-cell title="考试时间" :value="schedule.start_time + ' - ' + schedule.end_time" />
            <van-cell title="名额">
              <template #right-icon>
                <span :class="{ 'few-left': schedule.remaining_quota <= 5 }">
                  剩余 {{ schedule.remaining_quota }} / {{ schedule.total_quota }}
                </span>
              </template>
            </van-cell>
            <div class="booking-action">
              <van-button
                type="primary"
                block
                :disabled="schedule.remaining_quota <= 0"
                :loading="bookingId === schedule.id"
                @click="handleBook(schedule)"
              >
                {{ schedule.remaining_quota <= 0 ? '名额已满' : '立即预约' }}
              </van-button>
            </div>
          </van-cell-group>
        </van-list>
      </van-tab>
      <van-tab title="我的预约" name="mine">
        <van-list v-model:loading="myLoading" :finished="myFinished" finished-text="没有更多了" @load="onLoadMyBookings">
          <div v-if="myBookings.length === 0 && !myLoading" class="empty-state">
            <van-empty description="暂无预约记录" />
          </div>
          <van-cell-group inset v-for="booking in myBookings" :key="booking.id" class="booking-card">
            <van-cell :title="booking.schedule_info?.subject_display">
              <template #right-icon>
                <van-tag :type="getBookingTagType(booking.status)">{{ booking.status_display }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="考试日期" :value="booking.schedule_info?.exam_date" />
            <van-cell title="考试时间" :value="booking.schedule_info?.start_time + ' - ' + booking.schedule_info?.end_time" />
            <van-cell title="考场" :value="booking.schedule_info?.room_name" />
            <van-cell v-if="booking.score !== null" title="成绩" :value="booking.score + '分'" />
            <div v-if="booking.status === 'pending' || booking.status === 'approved'" class="booking-action">
              <van-button
                type="danger"
                plain
                block
                :loading="cancelingId === booking.id"
                @click="handleCancel(booking.id)"
              >
                取消预约
              </van-button>
            </div>
          </van-cell-group>
        </van-list>
      </van-tab>
    </van-tabs>

    <van-tabbar v-model="activeFooterTab" active-color="#1989fa">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/fee-query">查费</van-tabbar-item>
      <van-tabbar-item icon="bill-o" to="/installment">分期</van-tabbar-item>
      <van-tabbar-item icon="calendar-o" to="/booking">约课</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>

    <van-popup v-model:show="showBookPopup" round position="bottom" :style="{ height: '60%' }">
      <div class="book-popup">
        <div class="popup-header">
          <div class="popup-title">确认预约信息</div>
          <van-icon name="cross" @click="showBookPopup = false" />
        </div>
        <div class="popup-content">
          <van-form @submit="submitBooking">
            <van-cell-group inset>
              <van-cell title="考试科目" :value="selectedSchedule?.subject_display" />
              <van-cell title="考试日期" :value="selectedSchedule?.exam_date" />
              <van-cell title="考试时间" :value="selectedSchedule?.start_time + ' - ' + selectedSchedule?.end_time" />
              <van-cell title="考场" :value="selectedSchedule?.room_name" />
              <van-field
                v-model="phone"
                name="phone"
                label="手机号"
                placeholder="请输入手机号"
                :rules="[{ required: true, message: '请输入手机号' }]"
              />
            </van-cell-group>
            <div class="popup-actions">
              <van-button native-type="submit" type="primary" block :loading="submitting">
                确认预约
              </van-button>
            </div>
          </van-form>
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
import { getAvailableSchedulesApi, getBookingListApi, selfBookExamApi, cancelBookingApi } from '@/api/exam'

const router = useRouter()
const userStore = useUserStore()
const studentInfo = computed(() => userStore.studentInfo)

const activeTab = ref('available')
const activeFooterTab = ref(3)
const subjectFilter = ref('')
const subjectOptions = [
  { text: '全部科目', value: '' },
  { text: '科目一', value: 'subject1' },
  { text: '科目二', value: 'subject2' },
  { text: '科目三', value: 'subject3' },
  { text: '科目四', value: 'subject4' }
]

const availableSchedules = ref([])
const myBookings = ref([])
const loading = ref(false)
const finished = ref(false)
const myLoading = ref(false)
const myFinished = ref(false)
const page = ref(1)
const myPage = ref(1)
const bookingId = ref(null)
const cancelingId = ref(null)

const showBookPopup = ref(false)
const selectedSchedule = ref(null)
const phone = ref('')
const submitting = ref(false)

const onClickLeft = () => {
  router.back()
}

const loadAvailableSchedules = async () => {
  try {
    const params = {
      page: page.value,
      page_size: 10
    }
    if (subjectFilter.value) {
      params.subject = subjectFilter.value
    }
    const res = await getAvailableSchedulesApi(params)
    const results = Array.isArray(res) ? res : (res.results || [])
    availableSchedules.value = [...availableSchedules.value, ...results]
    if (results.length < 10) {
      finished.value = true
    }
    page.value++
  } finally {
    loading.value = false
  }
}

const loadMyBookings = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getBookingListApi({
      student_id: studentInfo.value.id,
      page: myPage.value,
      page_size: 10
    })
    const results = Array.isArray(res) ? res : (res.results || [])
    myBookings.value = [...myBookings.value, ...results]
    if (results.length < 10) {
      myFinished.value = true
    }
    myPage.value++
  } finally {
    myLoading.value = false
  }
}

const handleBook = (schedule) => {
  if (!studentInfo.value) {
    showToast('请先登录')
    return
  }
  selectedSchedule.value = schedule
  phone.value = studentInfo.value.phone || ''
  showBookPopup.value = true
}

const submitBooking = async () => {
  if (!selectedSchedule.value || !studentInfo.value) return
  try {
    submitting.value = true
    await selfBookExamApi({
      student_id: studentInfo.value.id,
      schedule_id: selectedSchedule.value.id,
      phone: phone.value
    })
    showToast('预约成功，等待审核')
    showBookPopup.value = false
    
    availableSchedules.value = []
    page.value = 1
    finished.value = false
    loadAvailableSchedules()
  } catch (error) {
    console.error('Booking error:', error)
  } finally {
    submitting.value = false
  }
}

const handleCancel = async (bookingId) => {
  try {
    await showDialog({
      title: '确认取消',
      message: '确定要取消该预约吗？',
      confirmButtonText: '确认取消',
      cancelButtonText: '再想想'
    })
    
    cancelingId.value = bookingId
    await cancelBookingApi(bookingId)
    showToast('取消成功')
    
    myBookings.value = []
    myPage.value = 1
    myFinished.value = false
    loadMyBookings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Cancel error:', error)
    }
  } finally {
    cancelingId.value = null
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

const onLoad = () => {
  loadAvailableSchedules()
}

const onLoadMyBookings = () => {
  loadMyBookings()
}

onMounted(() => {
  loadAvailableSchedules()
})
</script>

<style scoped>
.booking-container {
  padding-bottom: 60px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.filter-bar {
  padding: 12px 16px;
  background: #fff;
}

.schedule-card,
.booking-card {
  margin: 12px 16px;
  border-radius: 8px;
  overflow: hidden;
}

.booking-action {
  padding: 12px 16px;
  background: #fff;
}

.few-left {
  color: #ff4d4f;
  font-weight: bold;
}

.empty-state {
  padding: 60px 0;
}

.book-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
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

.popup-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.popup-actions {
  padding: 16px;
}
</style>
