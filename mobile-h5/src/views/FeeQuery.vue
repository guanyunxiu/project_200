<template>
  <div class="fee-query-container">
    <van-nav-bar title="费用查询" left-arrow @click-left="onClickLeft" />

    <div class="summary-card" v-if="paymentSummary">
      <div class="summary-item">
        <div class="summary-label">应缴总额</div>
        <div class="summary-value total">¥{{ paymentSummary.total_due }}</div>
      </div>
      <div class="summary-item">
        <div class="summary-label">已缴金额</div>
        <div class="summary-value paid">¥{{ paymentSummary.total_paid }}</div>
      </div>
      <div class="summary-item">
        <div class="summary-label">待缴金额</div>
        <div class="summary-value remaining">¥{{ paymentSummary.remaining }}</div>
      </div>
      <div class="payment-status">
        <van-tag :type="getStatusTagType(paymentSummary.payment_status)" size="medium">
          {{ paymentSummary.payment_status }}
        </van-tag>
      </div>
    </div>

    <van-tabs v-model:active="activeTab" sticky offset-top="46px">
      <van-tab title="全部" name="all">
        <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad">
          <div v-if="payments.length === 0 && !loading" class="empty-state">
            <van-empty description="暂无缴费记录" />
          </div>
          <van-cell-group inset v-for="payment in payments" :key="payment.id" class="payment-card">
            <van-cell :title="payment.payment_type_display" :value="'¥' + payment.amount">
              <template #label>
                <span class="payment-no">{{ payment.receipt_no }}</span>
              </template>
              <template #right-icon>
                <van-tag :type="payment.status === 'confirmed' ? 'success' : 'warning'">
                  {{ payment.status_display }}
                </van-tag>
              </template>
            </van-cell>
            <van-cell title="套餐" :value="payment.package_name || '-'" />
            <van-cell title="支付方式" :value="payment.payment_method_display" />
            <van-cell title="缴费时间" :value="payment.paid_at || '-'" />
            <van-cell v-if="payment.remark" title="备注" :value="payment.remark" />
          </van-cell-group>
        </van-list>
      </van-tab>
      <van-tab title="欠费" name="unpaid">
        <div v-if="unpaidRecords.length === 0" class="empty-state">
          <van-empty description="暂无欠费记录" />
        </div>
        <van-cell-group inset v-for="record in unpaidRecords" :key="record.id" class="payment-card">
          <van-cell title="分期还款" :value="'¥' + record.amount">
            <template #label>
              <span>第{{ record.period }}期</span>
            </template>
            <template #right-icon>
              <van-tag type="danger">待还款</van-tag>
            </template>
          </van-cell>
          <van-cell title="应还日期" :value="record.due_date" />
          <van-cell v-if="record.status === 'overdue'" title="状态" value="已逾期">
            <template #right-icon>
              <van-tag type="danger">逾期</van-tag>
            </template>
          </van-cell>
        </van-cell-group>
      </van-tab>
    </van-tabs>

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
import { useUserStore } from '@/store/user'
import { getPaymentListApi, getStudentPaymentSummaryApi } from '@/api/payment'
import { getOverdueInstallmentApi } from '@/api/installment'

const router = useRouter()
const userStore = useUserStore()
const studentInfo = computed(() => userStore.studentInfo)

const activeTab = ref('all')
const activeFooterTab = ref(1)
const payments = ref([])
const unpaidRecords = ref([])
const paymentSummary = ref(null)
const loading = ref(false)
const finished = ref(false)
const page = ref(1)

const onClickLeft = () => {
  router.back()
}

const loadSummary = async () => {
  if (!studentInfo.value?.id) return
  const list = await getStudentPaymentSummaryApi()
  const summary = list.find(s => s.student?.id === studentInfo.value.id)
  if (summary) {
    paymentSummary.value = summary
  }
}

const loadPayments = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getPaymentListApi({
      student_id: studentInfo.value.id,
      page: page.value,
      page_size: 10
    })
    const results = Array.isArray(res) ? res : (res.results || [])
    payments.value = [...payments.value, ...results]
    if (results.length < 10) {
      finished.value = true
    }
    page.value++
  } finally {
    loading.value = false
  }
}

const loadUnpaid = async () => {
  if (!studentInfo.value?.id) return
  const installments = await getOverdueInstallmentApi()
  const myInstallments = installments.filter(p => p.student_id === studentInfo.value.id)
  const records = []
  myInstallments.forEach(plan => {
    if (plan.records) {
      plan.records.forEach(r => {
        if (r.status === 'unpaid' || r.status === 'overdue') {
          records.push(r)
        }
      })
    }
  })
  unpaidRecords.value = records
}

const onLoad = () => {
  loadPayments()
}

const getStatusTagType = (status) => {
  if (status === '已缴清') return 'success'
  if (status === '未缴费') return 'danger'
  return 'warning'
}

onMounted(() => {
  loadSummary()
  loadUnpaid()
})
</script>

<style scoped>
.fee-query-container {
  padding-bottom: 60px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.summary-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 16px;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  color: #fff;
}

.summary-item {
  width: 33.33%;
  text-align: center;
}

.summary-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 6px;
}

.summary-value {
  font-size: 20px;
  font-weight: bold;
}

.summary-value.total {
  color: #fff;
}

.summary-value.paid {
  color: #52c41a;
}

.summary-value.remaining {
  color: #ffd666;
}

.payment-status {
  width: 100%;
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.payment-card {
  margin: 12px 16px;
  border-radius: 8px;
  overflow: hidden;
}

.payment-no {
  font-size: 12px;
  color: #969799;
}

.empty-state {
  padding: 60px 0;
}
</style>
