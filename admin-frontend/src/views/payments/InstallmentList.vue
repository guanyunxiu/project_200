<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">分期管理</div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增分期
      </el-button>
    </div>

    <el-alert
      title="逾期提醒"
      :description="`当前有 ${overdueCount} 笔分期已逾期，请及时处理`"
      type="warning"
      show-icon
      style="margin-bottom: 20px;"
      v-if="overdueCount > 0"
    />

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="学员">
          <el-input v-model="filterForm.student_name" placeholder="姓名/手机号" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px;">
            <el-option label="未还款" value="unpaid" />
            <el-option label="还款中" value="unpaid" />
            <el-option label="已还清" value="paid" />
            <el-option label="已逾期" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="student_name" label="学员姓名" width="100" />
        <el-table-column prop="student_phone" label="手机号" width="130" />
        <el-table-column prop="total_amount" label="分期总金额" width="120">
          <template #default="{ row }"><b>¥{{ row.total_amount }}</b></template>
        </el-table-column>
        <el-table-column prop="down_payment" label="首付" width="100">
          <template #default="{ row }">¥{{ row.down_payment }}</template>
        </el-table-column>
        <el-table-column label="分期信息" width="180">
          <template #default="{ row }">
            <div>{{ row.months }}期 × ¥{{ row.monthly_amount }}</div>
            <div style="color: #909399; font-size: 12px;">开始: {{ row.start_date }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="已还" width="100" />
        <el-table-column prop="remaining_amount" label="剩余" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.remaining_amount > 0 ? '#F56C6C' : '#67C23A' }">
              ¥{{ row.remaining_amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleView(row)">详情</el-button>
            <el-button size="small" type="success" link @click="handlePay(row)" v-if="row.status !== 'paid'">还款</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>

  <el-dialog v-model="detailVisible" title="分期详情" width="700px">
    <div v-if="currentDetail">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="学员">{{ currentDetail.student_name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentDetail.student_phone }}</el-descriptions-item>
        <el-descriptions-item label="分期总金额"><b>¥{{ currentDetail.total_amount }}</b></el-descriptions-item>
        <el-descriptions-item label="首付金额">¥{{ currentDetail.down_payment }}</el-descriptions-item>
        <el-descriptions-item label="分期期数">{{ currentDetail.months }}期</el-descriptions-item>
        <el-descriptions-item label="每期金额">¥{{ currentDetail.monthly_amount }}</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentDetail.start_date }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDetail.status)">{{ currentDetail.status_display }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">还款明细</el-divider>
      <el-table :data="currentDetail.records || []" border>
        <el-table-column prop="period" label="期次" width="80" />
        <el-table-column prop="amount" label="应还金额" width="120" />
        <el-table-column prop="due_date" label="到期日" width="120" />
        <el-table-column prop="paid_date" label="实际还款" width="120" />
        <el-table-column prop="status_display" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'paid' ? 'success' : row.status === 'overdue' ? 'danger' : 'warning'">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" v-if="currentDetail.status !== 'paid'">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              link
              @click="handlePayPeriod(row)"
              v-if="row.status === 'unpaid' || row.status === 'overdue'"
            >
              还款
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-dialog>

  <el-dialog v-model="payDialogVisible" title="还款" width="400px">
    <el-form label-width="80px">
      <el-form-item label="期次">
        <el-select v-model="payForm.period" style="width: 100%;" v-if="!payForm.period">
          <el-option
            v-for="r in unpaidRecords"
            :key="r.period"
            :label="`第${r.period}期 - ¥${r.amount} - 到期: ${r.due_date}`"
            :value="r.period"
          />
        </el-select>
        <span v-else>第{{ payForm.period }}期</span>
      </el-form-item>
      <el-form-item label="还款金额">
        <el-input-number v-model="payForm.amount" :min="0" :precision="2" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="支付方式">
        <el-select v-model="payForm.payment_method" style="width: 100%;">
          <el-option label="现金" value="cash" />
          <el-option label="微信" value="wechat" />
          <el-option label="支付宝" value="alipay" />
          <el-option label="银行转账" value="bank" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="payDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmPay" :loading="paying">确认还款</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="addDialogVisible" title="新增分期" width="600px" destroy-on-close>
    <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-width="100px">
      <el-form-item label="学员" prop="student">
        <el-select v-model="addForm.student" filterable placeholder="请选择学员" style="width: 100%;">
          <el-option
            v-for="s in students"
            :key="s.id"
            :label="`${s.name} - ${s.phone}`"
            :value="s.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="分期总金额" prop="total_amount">
        <el-input-number v-model="addForm.total_amount" :min="0" :precision="2" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="首付金额" prop="down_payment">
        <el-input-number v-model="addForm.down_payment" :min="0" :precision="2" style="width: 100%;" />
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="分期期数" prop="months">
            <el-input-number v-model="addForm.months" :min="1" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="每期金额" prop="monthly_amount">
            <el-input-number v-model="addForm.monthly_amount" :min="0" :precision="2" style="width: 100%;" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker v-model="addForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="addDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleAddSubmit" :loading="adding">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getInstallmentList, getOverdueInstallments, createInstallment, payInstallment
} from '@/api/payments'
import { getStudentSimpleList } from '@/api/students'

const loading = ref(false)
const paying = ref(false)
const adding = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const payDialogVisible = ref(false)
const addDialogVisible = ref(false)
const addFormRef = ref(null)
const currentDetail = ref(null)
const students = ref([])
const overdueCount = ref(0)

const filterForm = reactive({
  student_name: '',
  status: ''
})

const payForm = reactive({
  period: null,
  amount: 0,
  payment_method: 'wechat'
})

const addForm = reactive({
  student: null,
  total_amount: 0,
  down_payment: 0,
  months: 6,
  monthly_amount: 0,
  start_date: ''
})

const addRules = {
  student: [{ required: true, message: '请选择学员', trigger: 'change' }],
  total_amount: [{ required: true, message: '请输入分期总金额', trigger: 'blur' }],
  months: [{ required: true, message: '请输入分期期数', trigger: 'blur' }],
  monthly_amount: [{ required: true, message: '请输入每期金额', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

const unpaidRecords = computed(() => {
  return currentDetail.value?.records?.filter(r => r.status !== 'paid') || []
})

const getStatusType = (status) => {
  const types = { unpaid: 'warning', paid: 'success', overdue: 'danger' }
  return types[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.status) params.status = filterForm.status
    const res = await getInstallmentList(params)
    tableData.value = res.results || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadOverdue = async () => {
  try {
    const res = await getOverdueInstallments()
    overdueCount.value = res.length || 0
  } catch (e) {
    console.error(e)
  }
}

const loadStudents = async () => {
  try {
    const res = await getStudentSimpleList()
    students.value = res
  } catch (e) {
    console.error(e)
  }
}

const resetFilter = () => {
  filterForm.student_name = ''
  filterForm.status = ''
  loadData()
}

const handleAdd = () => {
  addForm.student = null
  addForm.total_amount = 0
  addForm.down_payment = 0
  addForm.months = 6
  addForm.monthly_amount = 0
  addForm.start_date = ''
  addDialogVisible.value = true
}

const handleAddSubmit = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      adding.value = true
      try {
        addForm.remaining_amount = addForm.total_amount - addForm.down_payment
        addForm.paid_amount = 0
        addForm.status = 'unpaid'
        await createInstallment(addForm)
        ElMessage.success('创建成功')
        addDialogVisible.value = false
        loadData()
      } catch (e) {
        console.error(e)
      } finally {
        adding.value = false
      }
    }
  })
}

const handleView = (row) => {
  currentDetail.value = row
  detailVisible.value = true
}

const handlePay = (row) => {
  currentDetail.value = row
  payForm.period = null
  const nextUnpaid = row.records?.find(r => r.status !== 'paid')
  if (nextUnpaid) {
    payForm.amount = Number(nextUnpaid.amount)
  }
  payDialogVisible.value = true
}

const handlePayPeriod = (record) => {
  payForm.period = record.period
  payForm.amount = Number(record.amount)
  payDialogVisible.value = true
}

const confirmPay = async () => {
  if (!payForm.period || !payForm.amount) {
    ElMessage.warning('请填写完整信息')
    return
  }
  paying.value = true
  try {
    await payInstallment(currentDetail.value.id, payForm)
    ElMessage.success('还款成功')
    payDialogVisible.value = false
    detailVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    paying.value = false
  }
}

onMounted(() => {
  loadData()
  loadOverdue()
  loadStudents()
})
</script>
