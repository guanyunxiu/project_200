<template>
  <div class="hours-container">
    <van-nav-bar title="我的课时" left-arrow @click-left="onClickLeft" />

    <div v-loading="loading" class="content-wrapper">
      <div v-if="hoursData" class="hours-overview">
        <van-cell-group inset class="overview-card">
          <van-cell title="总课时">
            <template #right-icon>
              <span class="overview-value">{{ hoursData.total_hours }}</span>
            </template>
          </van-cell>
          <van-cell title="已用课时">
            <template #right-icon>
              <span class="used-value">{{ hoursData.used_hours }}</span>
            </template>
          </van-cell>
          <van-cell title="剩余课时">
            <template #right-icon>
              <span class="remaining-value">{{ hoursData.remaining_hours }}</span>
            </template>
          </van-cell>
          <div class="progress-wrapper">
            <van-progress
              :percentage="remainingPercentage"
              :color="#07c160"
              stroke-width="8"
            />
            <div class="progress-label">剩余 {{ remainingPercentage }}%</div>
          </div>
        </van-cell-group>

        <van-cell-group inset class="breakdown-card">
          <div class="breakdown-title">课时明细</div>
          <div class="breakdown-row">
            <div class="breakdown-item">
              <div class="breakdown-label">理论课时</div>
              <div class="breakdown-values">
                <span class="breakdown-total">总 {{ hoursData.theory_hours || 0 }}</span>
                <span class="breakdown-remaining">剩 {{ hoursData.remaining_theory_hours || 0 }}</span>
              </div>
              <van-progress
                :percentage="theoryPercentage"
                :color="#1989fa"
                stroke-width="6"
              />
            </div>
            <div class="breakdown-item">
              <div class="breakdown-label">实操课时</div>
              <div class="breakdown-values">
                <span class="breakdown-total">总 {{ hoursData.practical_hours || 0 }}</span>
                <span class="breakdown-remaining">剩 {{ hoursData.remaining_practical_hours || 0 }}</span>
              </div>
              <van-progress
                :percentage="practicalPercentage"
                :color="#ff976a"
                stroke-width="6"
              />
            </div>
          </div>
        </van-cell-group>

        <div v-if="hoursData.is_hours_low" class="warning-banner">
          <van-icon name="info-o" class="warning-icon" />
          <span class="warning-text">课时不足，请及时续课</span>
        </div>

        <van-button
          type="primary"
          block
          class="renew-button"
          @click="showRenewPopup = true"
        >
          续课
        </van-button>
      </div>

      <div class="records-section">
        <div class="section-title">课时记录</div>
        <van-list
          v-model:loading="recordsLoading"
          :finished="recordsFinished"
          finished-text="没有更多了"
          @load="loadRecords"
        >
          <van-cell-group inset v-if="hourRecords.length === 0 && !recordsLoading" class="empty-state">
            <van-empty description="暂无课时记录" />
          </van-cell-group>
          <van-cell-group inset v-for="record in hourRecords" :key="record.id" class="record-card">
            <van-cell>
              <template #title>
                <div class="record-header">
                  <van-tag :type="getOperationType(record.operation_type)">
                    {{ record.operation_type_display }}
                  </van-tag>
                  <van-tag plain :type="record.hour_type === 'theory' ? 'primary' : 'warning'">
                    {{ record.hour_type_display }}
                  </van-tag>
                </div>
              </template>
              <template #label>
                <div class="record-date">{{ record.created_at }}</div>
              </template>
              <template #right-icon>
                <span
                  class="record-hours"
                  :class="{ 'hours-add': record.hours > 0, 'hours-consume': record.hours < 0 }"
                >
                  {{ record.hours > 0 ? '+' : '' }}{{ record.hours }}
                </span>
              </template>
            </van-cell>
          </van-cell-group>
        </van-list>
      </div>
    </div>

    <van-popup
      v-model:show="showRenewPopup"
      position="bottom"
      round
      :style="{ height: '70%' }"
    >
      <div class="renew-popup">
        <div class="popup-header">
          <div class="popup-title">续课</div>
          <van-icon name="cross" @click="showRenewPopup = false" />
        </div>
        
        <van-cell-group inset class="form-group">
          <van-field
            v-model="renewForm.hour_type"
            is-link
            readonly
            label="课时类型"
            placeholder="请选择课时类型"
            @click="showHourTypePicker = true"
          />
          <van-field
            v-model="renewForm.hours"
            type="number"
            label="课时数量"
            placeholder="请输入课时数量"
            @click="showKeyboard = true"
          />
          <van-field
            v-model="renewForm.amount"
            readonly
            label="金额"
            placeholder="自动计算"
            :value="'¥' + calculatedAmount"
          />
          <van-field
            v-model="renewForm.payment_method"
            is-link
            readonly
            label="支付方式"
            placeholder="请选择支付方式"
            @click="showPaymentPicker = true"
          />
        </van-cell-group>

        <van-button
          type="primary"
          block
          class="confirm-button"
          :loading="renewing"
          @click="handleRenew"
        >
          确认续课
        </van-button>
      </div>
    </van-popup>

    <van-popup v-model:show="showHourTypePicker" position="bottom">
      <van-picker
        :columns="hourTypeColumns"
        @confirm="onHourTypeConfirm"
        @cancel="showHourTypePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showPaymentPicker" position="bottom">
      <van-picker
        :columns="paymentColumns"
        @confirm="onPaymentConfirm"
        @cancel="showPaymentPicker = false"
      />
    </van-popup>

    <van-number-keyboard
      v-model:show="showKeyboard"
      :extra-key="'.'"
      @input="onKeyboardInput"
      @delete="onKeyboardDelete"
    />

    <van-tabbar v-model="activeFooterTab" active-color="#1989fa">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/fee-query">查费</van-tabbar-item>
      <van-tabbar-item icon="bill-o" to="/installment">分期</van-tabbar-item>
      <van-tabbar-item icon="calendar-o" to="/booking">约课</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { useUserStore } from '@/store/user'
import { getStudentHoursApi, getStudentHourRecordsApi, renewCourseApi } from '@/api/hour'

const router = useRouter()
const userStore = useUserStore()
const studentInfo = computed(() => userStore.studentInfo)

const loading = ref(false)
const hoursData = ref(null)
const hourRecords = ref([])
const recordsLoading = ref(false)
const recordsFinished = ref(false)
const activeFooterTab = ref(4)
const showRenewPopup = ref(false)
const showHourTypePicker = ref(false)
const showPaymentPicker = ref(false)
const showKeyboard = ref(false)
const renewing = ref(false)

const renewForm = ref({
  hour_type: '',
  hours: '',
  amount: '',
  payment_method: ''
})

const hourTypeColumns = [
  { text: '理论', value: 'theory' },
  { text: '实操', value: 'practical' }
]

const paymentColumns = [
  { text: '微信支付', value: 'wechat' },
  { text: '支付宝', value: 'alipay' },
  { text: '现金', value: 'cash' },
  { text: '银行卡', value: 'bank' }
]

const remainingPercentage = computed(() => {
  if (!hoursData.value?.total_hours || hoursData.value.total_hours === 0) return 0
  return Math.round((hoursData.value.remaining_hours / hoursData.value.total_hours) * 100) || 0
})

const theoryPercentage = computed(() => {
  if (!hoursData.value?.theory_hours) return 0
  return Math.round((hoursData.value?.remaining_theory_hours || 0) / (hoursData.value?.theory_hours || 1) * 100)
})

const practicalPercentage = computed(() => {
  if (!hoursData.value?.practical_hours) return 0
  return Math.round((hoursData.value?.remaining_practical_hours || 0) / (hoursData.value?.practical_hours || 1) * 100)
})

const calculatedAmount = computed(() => {
  const hours = parseFloat(renewForm.value.hours) || 0
  return (hours * 100).toFixed(2)
})

const onClickLeft = () => {
  router.back()
}

const loadHoursData = async () => {
  if (!studentInfo.value?.id) return
  loading.value = true
  try {
    const res = await getStudentHoursApi(studentInfo.value.id)
    hoursData.value = res
  } catch (error) {
    console.error('Load hours error:', error)
    showToast('加载课时数据失败')
  } finally {
    loading.value = false
  }
}

const loadRecords = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getStudentHourRecordsApi(studentInfo.value.id)
    const results = Array.isArray(res) ? res : (res.results || [])
    hourRecords.value = [...hourRecords.value, ...results.slice(0, 20)]
    recordsFinished.value = true
  } catch (error) {
    console.error('Load records error:', error)
    showToast('加载记录失败')
  } finally {
    recordsLoading.value = false
  }
}

const getOperationType = (type) => {
  const typeMap = {
    'consume': 'danger',
    'add': 'success',
    'renew': 'primary'
  }
  return typeMap[type] || 'default'
}

const onHourTypeConfirm = ({ selectedOptions }) => {
  renewForm.value.hour_type = selectedOptions[0].text
  renewForm.value.hour_type_value = selectedOptions[0].value
  showHourTypePicker.value = false
}

const onPaymentConfirm = ({ selectedOptions }) => {
  renewForm.value.payment_method = selectedOptions[0].text
  renewForm.value.payment_method_value = selectedOptions[0].value
  showPaymentPicker.value = false
}

const onKeyboardInput = (value) => {
  renewForm.value.hours = value
}

const onKeyboardDelete = () => {
  renewForm.value.hours = renewForm.value.hours.slice(0, -1)
}

const handleRenew = async () => {
  if (!renewForm.value.hour_type_value) {
    showToast('请选择课时类型')
    return
  }
  if (!renewForm.value.hours || parseFloat(renewForm.value.hours) <= 0) {
    showToast('请输入有效的课时数量')
    return
  }
  if (!renewForm.value.payment_method_value) {
    showToast('请选择支付方式')
    return
  }

  try {
    await showDialog({
      title: '确认续课',
      message: `确认续购 ${renewForm.value.hours} 课时 ${renewForm.value.hour_type}，共计 ¥${calculatedAmount.value}？`,
      confirmButtonText: '确认支付',
      cancelButtonText: '取消'
    })

    renewing.value = true
    await renewCourseApi({
      student_id: studentInfo.value.id,
      hour_type: renewForm.value.hour_type_value,
      hours: parseFloat(renewForm.value.hours),
      amount: parseFloat(calculatedAmount.value),
      payment_method: renewForm.value.payment_method_value
    })

    showToast('续课成功')
    showRenewPopup.value = false
    resetRenewForm()
    loadHoursData()
    hourRecords.value = []
    recordsFinished.value = false
    loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Renew error:', error)
      showToast('续课失败')
    }
  } finally {
    renewing.value = false
  }
}

const resetRenewForm = () => {
  renewForm.value = {
    hour_type: '',
    hours: '',
    amount: '',
    payment_method: ''
  }
}

onMounted(() => {
  loadHoursData()
  loadRecords()
})
</script>

<style scoped>
.hours-container {
  padding-bottom: 60px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.content-wrapper {
  padding: 16px;
}

.overview-card {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.overview-value {
  font-size: 18px;
  font-weight: bold;
  color: #323233;
}

.used-value {
  font-size: 18px;
  font-weight: bold;
  color: #ff4d4f;
}

.remaining-value {
  font-size: 18px;
  font-weight: bold;
  color: #07c160;
}

.progress-wrapper {
  padding: 12px 16px;
  background-color: #fafafa;
}

.progress-label {
  text-align: right;
  font-size: 12px;
  color: #969799;
  margin-top: 8px;
}

.breakdown-card {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  padding: 16px;
}

.breakdown-title {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 16px;
}

.breakdown-row {
  display: flex;
  gap: 16px;
}

.breakdown-item {
  flex: 1;
}

.breakdown-label {
  font-size: 14px;
  color: #323233;
  margin-bottom: 8px;
}

.breakdown-values {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.breakdown-total {
  font-size: 12px;
  color: #969799;
}

.breakdown-remaining {
  font-size: 14px;
  font-weight: bold;
  color: #07c160;
}

.warning-banner {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.warning-icon {
  color: #ff4d4f;
  font-size: 18px;
  margin-right: 8px;
}

.warning-text {
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 500;
}

.renew-button {
  margin-bottom: 20px;
  border-radius: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 12px;
  padding-left: 4px;
}

.record-card {
  margin-bottom: 8px;
  border-radius: 8px;
  overflow: hidden;
}

.record-header {
  display: flex;
  gap: 8px;
  align-items: center;
}

.record-date {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

.record-hours {
  font-size: 18px;
  font-weight: bold;
}

.hours-add {
  color: #07c160;
}

.hours-consume {
  color: #ff4d4f;
}

.empty-state {
  padding: 40px 0;
}

.renew-popup {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #ebedf0;
}

.popup-title {
  font-size: 18px;
  font-weight: bold;
  color: #323233;
}

.form-group {
  margin-top: 16px;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.confirm-button {
  margin-top: auto;
  border-radius: 8px;
}
</style>
