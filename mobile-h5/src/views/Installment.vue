<template>
  <div class="installment-container">
    <van-nav-bar title="分期还款" left-arrow @click-left="onClickLeft" />

    <van-tabs v-model:active="activeTab" sticky offset-top="46px">
      <van-tab title="待还款" name="unpaid">
        <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="onLoad">
          <div v-if="unpaidPlans.length === 0 && !loading" class="empty-state">
            <van-empty description="暂无待还款分期" />
          </div>
          <van-cell-group inset v-for="plan in unpaidPlans" :key="plan.id" class="plan-card">
            <van-cell :title="'分期计划 #' + plan.id">
              <template #right-icon>
                <van-tag :type="plan.status === 'overdue' ? 'danger' : 'warning'">
                  {{ plan.status_display }}
                </van-tag>
              </template>
            </van-cell>
            <van-cell title="总金额" :value="'¥' + plan.total_amount" />
            <van-cell title="首付" :value="'¥' + plan.down_payment" />
            <van-cell title="月还" :value="'¥' + plan.monthly_amount + ' × ' + plan.months + '期'" />
            <van-cell title="已还" :value="'¥' + plan.paid_amount" />
            <van-cell title="待还" :value="'¥' + plan.remaining_amount">
              <template #right-icon>
                <span class="remaining-amount">¥{{ plan.remaining_amount }}</span>
              </template>
            </van-cell>
            
            <div class="period-list">
              <div class="period-title">还款明细</div>
              <div
                v-for="record in plan.records"
                :key="record.id"
                class="period-item"
                :class="{ 'is-paid': record.status === 'paid', 'is-overdue': record.status === 'overdue' }"
              >
                <div class="period-info">
                  <span class="period-no">第{{ record.period }}期</span>
                  <span class="period-date">到期日: {{ record.due_date }}</span>
                  <span v-if="record.late_fee_days > 0" class="overdue-days">
                    已逾期{{ record.late_fee_days }}天
                  </span>
                </div>
                <div class="period-amount-wrapper">
                  <div class="period-amount">¥{{ record.amount }}</div>
                  <div v-if="record.late_fee > 0" class="late-fee">
                    滞纳金: ¥{{ record.late_fee }}
                  </div>
                  <div v-if="record.late_fee > 0" class="total-due">
                    合计: ¥{{ (parseFloat(record.amount) + parseFloat(record.late_fee)).toFixed(2) }}
                  </div>
                </div>
                <div class="period-action">
                  <template v-if="record.status === 'paid'">
                    <van-tag type="success">已还款</van-tag>
                  </template>
                  <template v-else-if="record.status === 'overdue'">
                    <van-button
                      size="small"
                      type="danger"
                      :loading="payingId === record.id"
                      @click="handlePay(plan.id, record.period)"
                    >
                      立即还款
                    </van-button>
                  </template>
                  <template v-else>
                    <van-button
                      size="small"
                      type="primary"
                      :loading="payingId === record.id"
                      @click="handlePay(plan.id, record.period)"
                    >
                      立即还款
                    </van-button>
                  </template>
                </div>
              </div>
            </div>
          </van-cell-group>
        </van-list>
      </van-tab>
      <van-tab title="已还清" name="paid">
        <van-list v-model:loading="paidLoading" :finished="paidFinished" finished-text="没有更多了" @load="onLoadPaid">
          <div v-if="paidPlans.length === 0 && !paidLoading" class="empty-state">
            <van-empty description="暂无已还清分期" />
          </div>
          <van-cell-group inset v-for="plan in paidPlans" :key="plan.id" class="plan-card">
            <van-cell :title="'分期计划 #' + plan.id">
              <template #right-icon>
                <van-tag type="success">{{ plan.status_display }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="总金额" :value="'¥' + plan.total_amount" />
            <van-cell title="还款期数" :value="plan.months + '期'" />
            <van-cell title="还清日期" :value="plan.updated_at" />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { useUserStore } from '@/store/user'
import { getInstallmentListApi, payInstallmentPeriodApi } from '@/api/installment'

const router = useRouter()
const userStore = useUserStore()
const studentInfo = computed(() => userStore.studentInfo)

const activeTab = ref('unpaid')
const activeFooterTab = ref(2)
const unpaidPlans = ref([])
const paidPlans = ref([])
const loading = ref(false)
const finished = ref(false)
const paidLoading = ref(false)
const paidFinished = ref(false)
const page = ref(1)
const paidPage = ref(1)
const payingId = ref(null)

const onClickLeft = () => {
  router.back()
}

const loadUnpaidPlans = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getInstallmentListApi({
      student_id: studentInfo.value.id,
      status: 'unpaid',
      page: page.value,
      page_size: 10
    })
    const results = Array.isArray(res) ? res : (res.results || [])
    unpaidPlans.value = [...unpaidPlans.value, ...results]
    if (results.length < 10) {
      finished.value = true
    }
    page.value++
  } finally {
    loading.value = false
  }
}

const loadPaidPlans = async () => {
  if (!studentInfo.value?.id) return
  try {
    const res = await getInstallmentListApi({
      student_id: studentInfo.value.id,
      status: 'paid',
      page: paidPage.value,
      page_size: 10
    })
    const results = Array.isArray(res) ? res : (res.results || [])
    paidPlans.value = [...paidPlans.value, ...results]
    if (results.length < 10) {
      paidFinished.value = true
    }
    paidPage.value++
  } finally {
    paidLoading.value = false
  }
}

const handlePay = async (planId, period) => {
  const plan = unpaidPlans.value.find(p => p.id === planId)
  const record = plan?.records?.find(r => r.period === period)
  let message = `确定要支付第${period}期的分期还款吗？`
  if (record && record.late_fee > 0) {
    message = `第${period}期还款详情:\n本金: ¥${record.amount}\n滞纳金: ¥${record.late_fee}\n合计: ¥${(parseFloat(record.amount) + parseFloat(record.late_fee)).toFixed(2)}`
  }
  try {
    await showDialog({
      title: '确认还款',
      message: message,
      confirmButtonText: '确认支付',
      cancelButtonText: '取消'
    })
    
    payingId.value = period
    await payInstallmentPeriodApi(planId, period, 'wechat')
    showToast('还款成功')
    
    unpaidPlans.value = []
    page.value = 1
    finished.value = false
    loadUnpaidPlans()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Pay error:', error)
    }
  } finally {
    payingId.value = null
  }
}

const onLoad = () => {
  loadUnpaidPlans()
}

const onLoadPaid = () => {
  loadPaidPlans()
}

onMounted(() => {
  loadUnpaidPlans()
})
</script>

<style scoped>
.installment-container {
  padding-bottom: 60px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.plan-card {
  margin: 12px 16px;
  border-radius: 8px;
  overflow: hidden;
}

.period-list {
  padding: 12px 16px;
  background-color: #fafafa;
  border-top: 1px solid #ebedf0;
}

.period-title {
  font-size: 14px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 12px;
}

.period-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 8px;
}

.period-item.is-paid {
  opacity: 0.7;
}

.period-item.is-overdue {
  border: 1px solid #ff4d4f;
}

.period-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.period-no {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.period-date {
  font-size: 12px;
  color: #969799;
  margin-top: 2px;
}

.overdue-days {
  font-size: 12px;
  color: #ff4d4f;
  margin-top: 2px;
  font-weight: 500;
}

.period-amount-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-right: 12px;
}

.period-amount {
  font-size: 16px;
  font-weight: bold;
  color: #ff4d4f;
}

.late-fee {
  font-size: 12px;
  color: #ff9800;
  margin-top: 2px;
}

.total-due {
  font-size: 13px;
  color: #f44336;
  font-weight: bold;
  margin-top: 2px;
}

.remaining-amount {
  color: #ff4d4f;
  font-weight: bold;
}

.empty-state {
  padding: 60px 0;
}
</style>
