<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">财务统计</div>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="营收概览" name="overview">
        <div class="filter-bar">
          <el-form :inline="true" :model="overviewFilter">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="overviewFilter.date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadOverviewData">查询</el-button>
              <el-button @click="resetOverviewFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-loading="overviewLoading">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #409EFF;"><Wallet /></div>
                <div class="stat-value">¥{{ overviewData.total_revenue || 0 }}</div>
                <div class="stat-label">总营收</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #67C23A;"><Document /></div>
                <div class="stat-value">{{ overviewData.payment_count || 0 }}</div>
                <div class="stat-label">缴费笔数</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #E6A23C;"><Money /></div>
                <div class="stat-value">¥{{ overviewData.by_type?.full || 0 }}</div>
                <div class="stat-label">一次性全款</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #F56C6C;"><CreditCard /></div>
                <div class="stat-value">¥{{ overviewData.by_type?.down || 0 }}</div>
                <div class="stat-label">首付</div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #909399;"><Calendar /></div>
                <div class="stat-value">¥{{ overviewData.by_type?.installment || 0 }}</div>
                <div class="stat-label">分期还款</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #67C23A;"><Reading /></div>
                <div class="stat-value">¥{{ overviewData.by_type?.makeup_exam || 0 }}</div>
                <div class="stat-label">补考收入</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #409EFF;"><Refresh /></div>
                <div class="stat-value">¥{{ overviewData.by_type?.course_renewal || 0 }}</div>
                <div class="stat-label">续课收入</div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="班型营收" name="package">
        <div class="filter-bar">
          <el-form :inline="true" :model="packageFilter">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="packageFilter.date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadPackageData">查询</el-button>
              <el-button @click="resetPackageFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="table-container">
          <el-table :data="packageData" border v-loading="packageLoading">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="package_name" label="班型名称" min-width="150" />
            <el-table-column prop="package_type" label="班型类型" width="120" />
            <el-table-column prop="license_type" label="驾照类型" width="100" />
            <el-table-column prop="base_price" label="基础价格" width="120">
              <template #default="{ row }">¥{{ row.base_price || 0 }}</template>
            </el-table-column>
            <el-table-column prop="total_revenue" label="总营收" width="120">
              <template #default="{ row }"><b style="color: #F56C6C;">¥{{ row.total_revenue || 0 }}</b></template>
            </el-table-column>
            <el-table-column prop="student_count" label="学员数" width="100" />
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="分期回款" name="installment">
        <div class="filter-bar">
          <el-form :inline="true" :model="installmentFilter">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="installmentFilter.date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadInstallmentData">查询</el-button>
              <el-button @click="resetInstallmentFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-loading="installmentLoading">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #409EFF;"><Wallet /></div>
                <div class="stat-value">¥{{ installmentData.total_installment_revenue || 0 }}</div>
                <div class="stat-label">分期总营收</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #67C23A;"><Money /></div>
                <div class="stat-value">¥{{ installmentData.total_down_payments || 0 }}</div>
                <div class="stat-label">首付总额</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #E6A23C;"><CreditCard /></div>
                <div class="stat-value">¥{{ installmentData.total_installment_paid || 0 }}</div>
                <div class="stat-label">已还分期</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #F56C6C;"><Warning /></div>
                <div class="stat-value">¥{{ installmentData.total_late_fee || 0 }}</div>
                <div class="stat-label">滞纳金总额</div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #909399;"><Document /></div>
                <div class="stat-value">{{ installmentData.total_plans || 0 }}</div>
                <div class="stat-label">分期方案总数</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #E6A23C;"><Clock /></div>
                <div class="stat-value">{{ installmentData.active_plans || 0 }}</div>
                <div class="stat-label">进行中方案</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #67C23A;"><CircleCheck /></div>
                <div class="stat-value">{{ installmentData.paid_plans || 0 }}</div>
                <div class="stat-label">已结清方案</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #F56C6C;"><Promotion /></div>
                <div class="stat-value">¥{{ installmentData.total_remaining || 0 }}</div>
                <div class="stat-label">待收金额</div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="补考收入" name="exam">
        <div class="filter-bar">
          <el-form :inline="true" :model="examFilter">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="examFilter.date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadExamData">查询</el-button>
              <el-button @click="resetExamFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-loading="examLoading">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #409EFF;"><Wallet /></div>
                <div class="stat-value">¥{{ examData.total_exam_fee || 0 }}</div>
                <div class="stat-label">补考费总营收</div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #F56C6C;"><Clock /></div>
                <div class="stat-value">{{ examData.unpaid_count || 0 }}</div>
                <div class="stat-label">未缴费人次</div>
              </el-card>
            </el-col>
          </el-row>

          <div class="table-container" style="margin-top: 20px;">
            <el-card>
              <template #header><span>按科目统计</span></template>
              <el-table :data="examData.by_subject || []" border>
                <el-table-column type="index" label="序号" width="60" />
                <el-table-column prop="subject_name" label="科目名称" min-width="150" />
                <el-table-column prop="count" label="人次" width="100" />
                <el-table-column prop="total" label="总金额" width="150">
                  <template #default="{ row }"><b style="color: #F56C6C;">¥{{ row.total || 0 }}</b></template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="续课收入" name="renewal">
        <div class="filter-bar">
          <el-form :inline="true" :model="renewalFilter">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="renewalFilter.date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadRenewalData">查询</el-button>
              <el-button @click="resetRenewalFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-loading="renewalLoading">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #409EFF;"><Wallet /></div>
                <div class="stat-value">¥{{ renewalData.total_renewal_revenue || 0 }}</div>
                <div class="stat-label">续课总营收</div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="stat-card">
                <div class="stat-icon" style="color: #67C23A;"><User /></div>
                <div class="stat-value">{{ renewalData.renewal_count || 0 }}</div>
                <div class="stat-label">续课人次</div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="月度趋势" name="trend">
        <div class="filter-bar">
          <el-form :inline="true" :model="trendFilter">
            <el-form-item label="最近月份">
              <el-select v-model="trendFilter.months" style="width: 120px;">
                <el-option label="3个月" :value="3" />
                <el-option label="6个月" :value="6" />
                <el-option label="12个月" :value="12" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadTrendData">查询</el-button>
              <el-button @click="resetTrendFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-loading="trendLoading">
          <el-card>
            <template #header><span>月度营收趋势</span></template>
            <div class="trend-chart">
              <div class="chart-container">
                <div class="chart-bars">
                  <div
                    v-for="(item, index) in trendData"
                    :key="index"
                    class="bar-item"
                  >
                    <div class="bar-wrapper">
                      <div
                        class="bar"
                        :style="{ height: getBarHeight(item.total_revenue) + '%' }"
                      >
                        <div class="bar-value">¥{{ item.total_revenue || 0 }}</div>
                      </div>
                    </div>
                    <div class="bar-label">{{ item.month }}</div>
                  </div>
                </div>
                <div class="chart-legend">
                  <span class="legend-item">
                    <span class="legend-color" style="background: #409EFF;"></span>
                    总营收
                  </span>
                </div>
              </div>
            </div>

            <el-table :data="trendData" border style="margin-top: 20px;">
              <el-table-column prop="month" label="月份" width="120" />
              <el-table-column prop="total_revenue" label="总营收" width="150">
                <template #default="{ row }"><b style="color: #409EFF;">¥{{ row.total_revenue || 0 }}</b></template>
              </el-table-column>
              <el-table-column prop="full_payment" label="一次性全款" width="150">
                <template #default="{ row }">¥{{ row.full_payment || 0 }}</template>
              </el-table-column>
              <el-table-column prop="installment_payment" label="分期还款" width="150">
                <template #default="{ row }">¥{{ row.installment_payment || 0 }}</template>
              </el-table-column>
              <el-table-column prop="exam_fee" label="补考收入" width="150">
                <template #default="{ row }">¥{{ row.exam_fee || 0 }}</template>
              </el-table-column>
              <el-table-column prop="course_renewal" label="续课收入" width="150">
                <template #default="{ row }">¥{{ row.course_renewal || 0 }}</template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import {
  Wallet, Document, Money, CreditCard, Calendar,
  Reading, Refresh, Warning, Clock, CircleCheck,
  Promotion, User
} from '@element-plus/icons-vue'
import {
  getFinancialStatsSummary,
  getRevenueByPackage,
  getInstallmentRevenue,
  getExamFeeRevenue,
  getCourseRenewalRevenue,
  getMonthlyTrend
} from '@/api/payments'

const activeTab = ref('overview')

const overviewLoading = ref(false)
const overviewData = ref({})
const overviewFilter = reactive({
  date_range: []
})

const packageLoading = ref(false)
const packageData = ref([])
const packageFilter = reactive({
  date_range: []
})

const installmentLoading = ref(false)
const installmentData = ref({})
const installmentFilter = reactive({
  date_range: []
})

const examLoading = ref(false)
const examData = ref({})
const examFilter = reactive({
  date_range: []
})

const renewalLoading = ref(false)
const renewalData = ref({})
const renewalFilter = reactive({
  date_range: []
})

const trendLoading = ref(false)
const trendData = ref([])
const trendFilter = reactive({
  months: 6
})

const maxTrendValue = computed(() => {
  if (!trendData.value || trendData.value.length === 0) return 1
  return Math.max(...trendData.value.map(item => item.total_revenue || 0), 1)
})

const getBarHeight = (value) => {
  if (!value) return 0
  return (value / maxTrendValue.value) * 100
}

const buildDateParams = (filter) => {
  const params = {}
  if (filter.date_range?.length === 2) {
    params.start_date = filter.date_range[0]
    params.end_date = filter.date_range[1]
  }
  return params
}

const loadOverviewData = async () => {
  overviewLoading.value = true
  try {
    const params = buildDateParams(overviewFilter)
    const res = await getFinancialStatsSummary(params)
    overviewData.value = res || {}
  } catch (e) {
    console.error(e)
  } finally {
    overviewLoading.value = false
  }
}

const resetOverviewFilter = () => {
  overviewFilter.date_range = []
  loadOverviewData()
}

const loadPackageData = async () => {
  packageLoading.value = true
  try {
    const params = buildDateParams(packageFilter)
    const res = await getRevenueByPackage(params)
    packageData.value = res.results || res || []
  } catch (e) {
    console.error(e)
  } finally {
    packageLoading.value = false
  }
}

const resetPackageFilter = () => {
  packageFilter.date_range = []
  loadPackageData()
}

const loadInstallmentData = async () => {
  installmentLoading.value = true
  try {
    const params = buildDateParams(installmentFilter)
    const res = await getInstallmentRevenue(params)
    installmentData.value = res || {}
  } catch (e) {
    console.error(e)
  } finally {
    installmentLoading.value = false
  }
}

const resetInstallmentFilter = () => {
  installmentFilter.date_range = []
  loadInstallmentData()
}

const loadExamData = async () => {
  examLoading.value = true
  try {
    const params = buildDateParams(examFilter)
    const res = await getExamFeeRevenue(params)
    examData.value = res || {}
  } catch (e) {
    console.error(e)
  } finally {
    examLoading.value = false
  }
}

const resetExamFilter = () => {
  examFilter.date_range = []
  loadExamData()
}

const loadRenewalData = async () => {
  renewalLoading.value = true
  try {
    const params = buildDateParams(renewalFilter)
    const res = await getCourseRenewalRevenue(params)
    renewalData.value = res || {}
  } catch (e) {
    console.error(e)
  } finally {
    renewalLoading.value = false
  }
}

const resetRenewalFilter = () => {
  renewalFilter.date_range = []
  loadRenewalData()
}

const loadTrendData = async () => {
  trendLoading.value = true
  try {
    const params = {
      months: trendFilter.months
    }
    const res = await getMonthlyTrend(params)
    trendData.value = res.results || res || []
  } catch (e) {
    console.error(e)
  } finally {
    trendLoading.value = false
  }
}

const resetTrendFilter = () => {
  trendFilter.months = 6
  loadTrendData()
}

const handleTabChange = (tabName) => {
  switch (tabName) {
    case 'overview':
      if (!overviewData.value.total_revenue) loadOverviewData()
      break
    case 'package':
      if (packageData.value.length === 0) loadPackageData()
      break
    case 'installment':
      if (!installmentData.value.total_installment_revenue) loadInstallmentData()
      break
    case 'exam':
      if (!examData.value.total_exam_fee) loadExamData()
      break
    case 'renewal':
      if (!renewalData.value.total_renewal_revenue) loadRenewalData()
      break
    case 'trend':
      if (trendData.value.length === 0) loadTrendData()
      break
  }
}

onMounted(() => {
  loadOverviewData()
})
</script>

<style scoped lang="scss">
.page-container {
  .stat-card {
    text-align: center;

    .stat-icon {
      font-size: 32px;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      margin: 8px 0;
      color: #303133;
    }

    .stat-label {
      color: #909399;
      font-size: 14px;
    }
  }

  .trend-chart {
    .chart-container {
      padding: 20px;

      .chart-bars {
        display: flex;
        align-items: flex-end;
        justify-content: space-around;
        height: 300px;
        border-bottom: 1px solid #ebeef5;
        border-left: 1px solid #ebeef5;
        padding: 20px 10px;

        .bar-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex: 1;
          margin: 0 5px;

          .bar-wrapper {
            height: 240px;
            display: flex;
            align-items: flex-end;
            justify-content: center;

            .bar {
              width: 50px;
              background: linear-gradient(180deg, #409EFF 0%, #66b1ff 100%);
              border-radius: 4px 4px 0 0;
              position: relative;
              min-height: 2px;
              transition: height 0.3s ease;

              .bar-value {
                position: absolute;
                top: -25px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 12px;
                color: #606266;
                white-space: nowrap;
              }
            }
          }

          .bar-label {
            margin-top: 10px;
            font-size: 14px;
            color: #606266;
          }
        }
      }

      .chart-legend {
        display: flex;
        justify-content: center;
        margin-top: 20px;

        .legend-item {
          display: flex;
          align-items: center;
          margin: 0 10px;
          font-size: 14px;
          color: #606266;

          .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 2px;
            margin-right: 6px;
          }
        }
      }
    }
  }
}
</style>
