<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">补考费用管理</div>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #F56C6C;"><Warning /></div>
          <div class="stat-value">{{ stats.unpaid_count || 0 }}</div>
          <div class="stat-label">未缴费笔数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #E6A23C;"><Money /></div>
          <div class="stat-value">¥{{ stats.unpaid_amount || 0 }}</div>
          <div class="stat-label">未缴费总金额</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #67C23A;"><CircleCheck /></div>
          <div class="stat-value">¥{{ stats.paid_amount || 0 }}</div>
          <div class="stat-label">已缴费总金额</div>
        </el-card>
      </el-col>
    </el-row>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="学员">
          <el-input v-model="filterForm.student_name" placeholder="姓名/手机号" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="考试科目">
          <el-select v-model="filterForm.subject" placeholder="全部" clearable style="width: 150px;">
            <el-option label="科目一" :value="1" />
            <el-option label="科目二" :value="2" />
            <el-option label="科目三" :value="3" />
            <el-option label="科目四" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="费用类型">
          <el-select v-model="filterForm.fee_type" placeholder="全部" clearable style="width: 150px;">
            <el-option label="缺考补考" value="absent" />
            <el-option label="不及格补考" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px;">
            <el-option label="未缴费" value="unpaid" />
            <el-option label="已缴费" value="paid" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" border v-loading="loading" :row-style="rowStyle">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="student_name" label="学员姓名" width="100" />
        <el-table-column prop="student_phone" label="手机号" width="130" />
        <el-table-column prop="subject_display" label="考试科目" width="100" />
        <el-table-column prop="fee_type_display" label="费用类型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.fee_type === 'absent' ? 'warning' : 'danger'">
              {{ row.fee_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }"><b style="color: #F56C6C;">¥{{ row.amount }}</b></template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="缴费时间" width="170">
          <template #default="{ row }">{{ row.paid_at || '-' }}</template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="90">
          <template #default="{ row }">{{ row.operator_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              link
              @click="handlePay(row)"
              v-if="row.status === 'unpaid'"
            >
              缴费
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="margin-top: 20px; text-align: right;"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
  </div>

  <el-dialog v-model="payVisible" title="缴费" width="500px" destroy-on-close>
    <el-form :model="payForm" :rules="payRules" ref="payFormRef" label-width="100px">
      <el-form-item label="学员姓名">
        <span>{{ currentFee?.student_name }}</span>
      </el-form-item>
      <el-form-item label="考试科目">
        <span>{{ currentFee?.subject_display }}</span>
      </el-form-item>
      <el-form-item label="费用类型">
        <el-tag :type="currentFee?.fee_type === 'absent' ? 'warning' : 'danger'">
          {{ currentFee?.fee_type_display }}
        </el-tag>
      </el-form-item>
      <el-form-item label="缴费金额">
        <b style="color: #F56C6C; font-size: 18px;">¥{{ currentFee?.amount }}</b>
      </el-form-item>
      <el-form-item label="支付方式" prop="payment_method">
        <el-select v-model="payForm.payment_method" placeholder="请选择支付方式" style="width: 100%;">
          <el-option label="现金" value="cash" />
          <el-option label="微信" value="wechat" />
          <el-option label="支付宝" value="alipay" />
          <el-option label="银行转账" value="bank" />
          <el-option label="刷卡" value="card" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="payVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmPay" :loading="submitting">确认缴费</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, Money, CircleCheck } from '@element-plus/icons-vue'
import { getExamFeeList, payExamFee, getUnpaidExamFees } from '@/api/exams'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const payVisible = ref(false)
const payFormRef = ref(null)
const currentFee = ref(null)

const stats = reactive({
  unpaid_count: 0,
  unpaid_amount: 0,
  paid_amount: 0
})

const filterForm = reactive({
  student_name: '',
  subject: '',
  fee_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const payForm = reactive({
  payment_method: ''
})

const payRules = {
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const getStatusType = (status) => {
  const types = {
    unpaid: 'warning',
    paid: 'success',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const rowStyle = ({ row }) => {
  if (row.status === 'unpaid') {
    return { backgroundColor: '#FDF6EC' }
  }
  return {}
}

const loadStats = async () => {
  try {
    const [unpaidRes, paidRes] = await Promise.all([
      getUnpaidExamFees(),
      getExamFeeList({ status: 'paid', page_size: 1000 })
    ])
    stats.unpaid_count = unpaidRes.length || 0
    stats.unpaid_amount = (unpaidRes || []).reduce((sum, item) => sum + (item.amount || 0), 0)
    stats.paid_amount = (paidRes.results || []).reduce((sum, item) => sum + (item.amount || 0), 0)
  } catch (e) {
    console.error(e)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filterForm.student_name) params.student_name = filterForm.student_name
    if (filterForm.subject) params.subject = filterForm.subject
    if (filterForm.fee_type) params.fee_type = filterForm.fee_type
    if (filterForm.status) params.status = filterForm.status
    const res = await getExamFeeList(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.student_name = ''
  filterForm.subject = ''
  filterForm.fee_type = ''
  filterForm.status = ''
  pagination.page = 1
  loadData()
}

const handlePay = (row) => {
  currentFee.value = row
  payForm.payment_method = ''
  payVisible.value = true
}

const confirmPay = async () => {
  if (!payFormRef.value || !currentFee.value) return
  await payFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await ElMessageBox.confirm(
          `确定收取学员「${currentFee.value.student_name}」的补考费用 ¥${currentFee.value.amount} 吗？`,
          '提示',
          { type: 'warning' }
        )
        submitting.value = true
        await payExamFee(currentFee.value.id, { payment_method: payForm.payment_method })
        ElMessage.success('缴费成功')
        payVisible.value = false
        loadData()
        loadStats()
      } catch (e) {
        if (e !== 'cancel') console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.stat-card {
  text-align: center;
}
.stat-icon {
  font-size: 32px;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}
.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>
