<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #409EFF;"><UserFilled /></div>
          <div class="stat-value">{{ studentStats.total || 0 }}</div>
          <div class="stat-label">学员总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #67C23A;"><School /></div>
          <div class="stat-value">{{ studentStats.studying || 0 }}</div>
          <div class="stat-label">学习中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #E6A23C;"><Wallet /></div>
          <div class="stat-value">¥{{ paymentStats.today_total || 0 }}</div>
          <div class="stat-label">今日收费</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #F56C6C;"><Calendar /></div>
          <div class="stat-value">{{ examStats.today_exams || 0 }}</div>
          <div class="stat-label">今日考试</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header><span>学员驾照类型分布</span></template>
          <div ref="licenseChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>本月收费统计</span></template>
          <div class="month-stats">
            <div class="month-item">
              <span class="label">本月收费总额</span>
              <span class="value primary">¥{{ paymentStats.month_total || 0 }}</span>
            </div>
            <div class="month-item">
              <span class="label">累计缴费笔数</span>
              <span class="value success">{{ paymentStats.total_count || 0 }}</span>
            </div>
            <div class="month-item">
              <span class="label">待确认缴费</span>
              <span class="value warning">{{ paymentStats.pending_count || 0 }}</span>
            </div>
            <div class="month-item">
              <span class="label">开放考试场次</span>
              <span class="value info">{{ examStats.open_schedules || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header><span>最近缴费记录</span></template>
          <el-table :data="recentPayments" border>
            <el-table-column prop="receipt_no" label="凭证号" width="180" />
            <el-table-column prop="student_name" label="学员姓名" />
            <el-table-column prop="payment_type_display" label="缴费类型" />
            <el-table-column prop="payment_method_display" label="支付方式" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥{{ row.amount }}</template>
            </el-table-column>
            <el-table-column prop="status_display" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'confirmed' ? 'success' : 'warning'">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="paid_at" label="缴费时间" width="180" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, markRaw } from 'vue'
import * as echarts from 'echarts'
import { UserFilled, School, Wallet, Calendar } from '@element-plus/icons-vue'
import { getStudentStats } from '@/api/students'
import { getPaymentStats, getPaymentList } from '@/api/payments'
import { getExamStats } from '@/api/exams'

const licenseChartRef = ref(null)
let licenseChart = null

const studentStats = ref({})
const paymentStats = ref({})
const examStats = ref({})
const recentPayments = ref([])

const initChart = () => {
  if (!licenseChartRef.value) return
  licenseChart = echarts.init(licenseChartRef.value)
  const data = [
    { value: studentStats.value.by_license?.C1 || 0, name: 'C1证' },
    { value: studentStats.value.by_license?.C2 || 0, name: 'C2证' },
    { value: studentStats.value.by_license?.D || 0, name: 'D证' }
  ]
  licenseChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: '10px', left: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: '16', fontWeight: 'bold' }
      },
      labelLine: { show: false },
      data: data,
      color: ['#409EFF', '#67C23A', '#E6A23C']
    }]
  })
}

const loadData = async () => {
  try {
    const [sRes, pRes, eRes, payRes] = await Promise.all([
      getStudentStats(),
      getPaymentStats(),
      getExamStats(),
      getPaymentList({ page_size: 5 })
    ])
    studentStats.value = sRes
    paymentStats.value = pRes
    examStats.value = eRes
    recentPayments.value = payRes.results || []
    initChart()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => licenseChart?.resize())
})
</script>

<style scoped lang="scss">
.dashboard {
  .stat-card {
    text-align: center;
    
    .stat-icon {
      font-size: 40px;
      margin-bottom: 10px;
    }
    
    .stat-value {
      font-size: 32px;
      font-weight: 600;
      margin: 10px 0;
    }
    
    .stat-label {
      color: #909399;
      font-size: 14px;
    }
  }
  
  .month-stats {
    .month-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        color: #606266;
        font-size: 14px;
      }
      
      .value {
        font-size: 20px;
        font-weight: 600;
        
        &.primary { color: #409EFF; }
        &.success { color: #67C23A; }
        &.warning { color: #E6A23C; }
        &.info { color: #909399; }
      }
    }
  }
}
</style>
