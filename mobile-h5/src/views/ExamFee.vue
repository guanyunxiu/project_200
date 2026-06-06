<template>
  <div class="exam-fee-container">
    <van-nav-bar title="补考缴费" left-arrow @click-left="onClickLeft" />

    <van-tabs v-model:active="activeTab" sticky offset-top="46px">
      <van-tab title="待缴费" name="unpaid">
        <div class="stats-bar">
          <div class="stats-item">
            <div class="stats-label">待缴费笔数</div>
            <div class="stats-value">{{ unpaidCount }}</div>
          </div>
          <div class="stats-divider"></div>
          <div class="stats-item">
            <div class="stats-label">待缴费金额</div>
            <div class="stats-value amount">¥{{ unpaidTotalAmount }}</div>
          </div>
        </div>

        <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad">
          <div v-if="unpaidFees.length === 0 && !loading" class="empty-state">
            <van-empty description="暂无待缴费记录" />
          </div>
          <van-cell-group inset v-for="fee in unpaidFees" :key="fee.id" class="fee-card">
            <van-cell :title="fee.subject_name">
              <template #right-icon>
                <van-tag type="danger">{{ fee.status_display }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="费用类型" :value="fee.fee_type_display" />
            <van-cell title="缴费金额">
              <template #right-icon>
                <span class="fee-amount">¥{{ fee.amount }}</span>
              </template>
            </van-cell>
            <van-cell title="创建时间" :value="fee.created_at" />
            <div class="card-footer">
              <van-button
                type="danger"
                block
                :loading="payingId === fee.id"
                @click="handlePay(fee)"
              >
                立即缴费
              </van-button>
            </div>
          </van-cell-group>
        </van-list>
      </van-tab>

      <van-tab title="已缴费" name="paid">
        <van-list v-model:loading="paidLoading" :finished="paidFinished" finished-text="没有更多了" @load="onLoadPaid">
          <div v-if="paidFees.length === 0 && !paidLoading" class="empty-state">
            <van-empty description="暂无已缴费记录" />
          </div>
          <van-cell-group inset v-for="fee in paidFees" :key="fee.id" class="fee-card">
            <van-cell :title="fee.subject_name">
              <template #right-icon>
                <van-tag type="success">{{ fee.status_display }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="费用类型" :value="fee.fee_type_display" />
            <van-cell title="缴费金额">
              <template #right-icon>
                <span class="fee-amount paid">¥{{ fee.amount }}</span>
              </template>
            </van-cell>
            <van-cell title="创建时间" :value="fee.created_at" />
            <van-cell title="支付时间" :value="fee.paid_at" />
            <van-cell title="支付方式" :value="fee.payment_method_display" />
          </van-cell-group>
        </van-list>
      </van-tab>
    </van-tabs>

    <van-tabbar v-model="activeFooterTab" active-color="#1989fa">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/exam-fee">查费</van-tabbar-item>
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
import { getUnpaidExamFeesApi, getExamFeeListApi, payExamFeeApi } from '@/api/exam'

const router = useRouter()
const userStore = useUserStore()
const studentInfo = computed(() => userStore.studentInfo)

const activeTab = ref('unpaid')
const activeFooterTab = ref(1)
const unpaidFees = ref([])
const paidFees = ref([])
const loading = ref(false)
const finished = ref(false)
const paidLoading = ref(false)
const paidFinished = ref(false)
const page = ref(1)
const paidPage = ref(1)
const payingId = ref(null)

const unpaidCount = computed(() => unpaidFees.value.length)
const unpaidTotalAmount = computed(() => {
  return unpaidFees.value.reduce((sum, fee) => sum + parseFloat(fee.amount || 0), 0).toFixed(2)
})

const onClickLeft = () => {
  router.back()
}

const loadUnpaidFees = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getUnpaidExamFeesApi(studentInfo.value.id)
    const results = Array.isArray(res) ? res : (res.results || [])
    unpaidFees.value = [...unpaidFees.value, ...results]
    if (results.length < 10) {
      finished.value = true
    }
    page.value++
  } finally {
    loading.value = false
  }
}

const loadPaidFees = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getExamFeeListApi({
      student_id: studentInfo.value.id,
      status: 'paid',
      page: paidPage.value,
      page_size: 10
    })
    const results = Array.isArray(res) ? res : (res.results || [])
    paidFees.value = [...paidFees.value, ...results]
    if (results.length < 10) {
      paidFinished.value = true
    }
    paidPage.value++
  } finally {
    paidLoading.value = false
  }
}

const handlePay = async (fee) => {
  try {
    await showDialog({
      title: '确认缴费',
      message: `缴费详情:\n科目: ${fee.subject_name}\n类型: ${fee.fee_type_display}\n金额: ¥${fee.amount}\n支付方式: 微信支付`,
      confirmButtonText: '确认支付',
      cancelButtonText: '取消'
    })

    payingId.value = fee.id
    await payExamFeeApi(fee.id, 'wechat')
    showToast('缴费成功')

    unpaidFees.value = []
    page.value = 1
    finished.value = false
    loadUnpaidFees()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Pay error:', error)
    }
  } finally {
    payingId.value = null
  }
}

const onLoad = () => {
  loadUnpaidFees()
}

const onLoadPaid = () => {
  loadPaidFees()
}

onMounted(() => {
  loadUnpaidFees()
})
</script>

<style scoped>
.exam-fee-container {
  padding-bottom: 60px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.stats-bar {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: linear-gradient(135deg, #1989fa 0%, #4facfe 100%);
  padding: 20px 16px;
  margin: 12px 16px;
  border-radius: 12px;
  color: #fff;
}

.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stats-label {
  font-size: 13px;
  opacity: 0.9;
  margin-bottom: 6px;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
}

.stats-value.amount {
  font-size: 22px;
}

.stats-divider {
  width: 1px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.3);
}

.fee-card {
  margin: 12px 16px;
  border-radius: 8px;
  overflow: hidden;
}

.fee-amount {
  color: #ff4d4f;
  font-weight: bold;
  font-size: 16px;
}

.fee-amount.paid {
  color: #07c160;
}

.card-footer {
  padding: 12px 16px;
  background-color: #fafafa;
  border-top: 1px solid #ebedf0;
}

.empty-state {
  padding: 60px 0;
}
</style>
