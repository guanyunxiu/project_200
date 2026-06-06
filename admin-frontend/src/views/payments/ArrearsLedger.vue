<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">欠费台账</div>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #F56C6C;"><Warning /></div>
          <div class="stat-value">¥{{ stats.overdue_amount || 0 }}</div>
          <div class="stat-label">逾期总金额</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #E6A23C;"><Bell /></div>
          <div class="stat-value">{{ stats.overdue_count || 0 }}</div>
          <div class="stat-label">逾期笔数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #409EFF;"><Money /></div>
          <div class="stat-value">¥{{ stats.unpaid_amount || 0 }}</div>
          <div class="stat-label">欠费总金额</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="color: #909399;"><Document /></div>
          <div class="stat-value">{{ stats.unpaid_count || 0 }}</div>
          <div class="stat-label">欠费笔数</div>
        </el-card>
      </el-col>
    </el-row>

    <div class="table-container">
      <el-table :data="tableData" border v-loading="loading" :row-class-name="tableRowClassName">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="student_name" label="学员姓名" width="100" />
        <el-table-column prop="student_phone" label="手机号" width="130" />
        <el-table-column prop="installment_id" label="分期ID" width="100" />
        <el-table-column prop="period" label="期次" width="80">
          <template #default="{ row }">第{{ row.period }}期</template>
        </el-table-column>
        <el-table-column prop="principal_amount" label="本金" width="110">
          <template #default="{ row }">¥{{ row.principal_amount }}</template>
        </el-table-column>
        <el-table-column prop="late_fee" label="滞纳金" width="110">
          <template #default="{ row }">
            <span :style="{ color: row.late_fee > 0 ? '#F56C6C' : '' }">¥{{ row.late_fee || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_due" label="应还总额" width="120">
          <template #default="{ row }">
            <b>¥{{ row.total_due }}</b>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="到期日" width="120" />
        <el-table-column prop="is_overdue" label="是否逾期" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_overdue ? 'danger' : 'info'">
              {{ row.is_overdue ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="late_fee_days" label="逾期天数" width="100">
          <template #default="{ row }">
            <span v-if="row.late_fee_days > 0" style="color: #F56C6C;">{{ row.late_fee_days }}天</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" link @click="handleReminder(row)">催缴登记</el-button>
            <el-button size="small" type="primary" link @click="handlePay(row)">立即还款</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>

  <el-dialog v-model="reminderDialogVisible" title="催缴登记" width="500px" destroy-on-close>
    <el-form :model="reminderForm" :rules="reminderRules" ref="reminderFormRef" label-width="100px">
      <el-form-item label="学员">
        <span>{{ reminderForm.student_name }}</span>
      </el-form-item>
      <el-form-item label="期次">
        <span>第{{ reminderForm.period }}期</span>
      </el-form-item>
      <el-form-item label="应还金额">
        <span style="color: #F56C6C; font-weight: bold;">¥{{ reminderForm.total_due }}</span>
      </el-form-item>
      <el-form-item label="催缴方式" prop="reminder_type">
        <el-select v-model="reminderForm.reminder_type" style="width: 100%;">
          <el-option label="电话" value="phone" />
          <el-option label="短信" value="sms" />
          <el-option label="微信" value="wechat" />
          <el-option label="上门" value="visit" />
        </el-select>
      </el-form-item>
      <el-form-item label="催缴内容" prop="content">
        <el-input v-model="reminderForm.content" type="textarea" :rows="4" placeholder="请输入催缴内容" />
      </el-form-item>
      <el-form-item label="下次催缴日期" prop="next_reminder_date">
        <el-date-picker v-model="reminderForm.next_reminder_date" type="date" style="width: 100%;" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="reminderDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitReminder" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="payDialogVisible" title="立即还款" width="450px" destroy-on-close>
    <el-form :model="payForm" :rules="payRules" ref="payFormRef" label-width="100px">
      <el-form-item label="学员">
        <span>{{ payForm.student_name }}</span>
      </el-form-item>
      <el-form-item label="期次">
        <span>第{{ payForm.period }}期</span>
      </el-form-item>
      <el-form-item label="应还本金">
        <span>¥{{ payForm.principal_amount }}</span>
      </el-form-item>
      <el-form-item label="滞纳金">
        <span style="color: #F56C6C;">¥{{ payForm.late_fee || 0 }}</span>
      </el-form-item>
      <el-form-item label="应还总额">
        <span style="color: #F56C6C; font-weight: bold; font-size: 18px;">¥{{ payForm.total_due }}</span>
      </el-form-item>
      <el-form-item label="还款金额" prop="amount">
        <el-input-number v-model="payForm.amount" :min="0" :precision="2" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="支付方式" prop="payment_method">
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
      <el-button type="primary" @click="submitPay" :loading="paying">确认还款</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Warning, Bell, Money, Document } from '@element-plus/icons-vue'
import { getArrearsLedger, createPaymentReminder, payInstallment } from '@/api/payments'

const loading = ref(false)
const submitting = ref(false)
const paying = ref(false)
const tableData = ref([])
const reminderDialogVisible = ref(false)
const payDialogVisible = ref(false)
const reminderFormRef = ref(null)
const payFormRef = ref(null)

const stats = reactive({
  overdue_amount: 0,
  overdue_count: 0,
  unpaid_amount: 0,
  unpaid_count: 0
})

const reminderForm = reactive({
  installment_id: null,
  period: null,
  student_name: '',
  total_due: 0,
  reminder_type: 'phone',
  content: '',
  next_reminder_date: ''
})

const reminderRules = {
  reminder_type: [{ required: true, message: '请选择催缴方式', trigger: 'change' }],
  content: [{ required: true, message: '请输入催缴内容', trigger: 'blur' }]
}

const payForm = reactive({
  installment_id: null,
  period: null,
  student_name: '',
  principal_amount: 0,
  late_fee: 0,
  total_due: 0,
  amount: 0,
  payment_method: 'wechat'
})

const payRules = {
  amount: [{ required: true, message: '请输入还款金额', trigger: 'blur' }],
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const getStatusType = (status) => {
  const types = { unpaid: 'warning', overdue: 'danger', paid: 'success' }
  return types[status] || 'info'
}

const tableRowClassName = ({ row }) => {
  if (row.is_overdue) {
    return 'overdue-row'
  }
  return ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getArrearsLedger()
    tableData.value = res.records || []
    stats.overdue_amount = res.overdue_amount || 0
    stats.overdue_count = res.overdue_count || 0
    stats.unpaid_amount = res.unpaid_amount || 0
    stats.unpaid_count = res.unpaid_count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleReminder = (row) => {
  Object.assign(reminderForm, {
    installment_id: row.installment_id,
    period: row.period,
    student_name: row.student_name,
    total_due: row.total_due,
    reminder_type: 'phone',
    content: '',
    next_reminder_date: ''
  })
  reminderDialogVisible.value = true
}

const submitReminder = async () => {
  if (!reminderFormRef.value) return
  await reminderFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data = {
          installment: reminderForm.installment_id,
          period: reminderForm.period,
          reminder_type: reminderForm.reminder_type,
          content: reminderForm.content,
          next_reminder_date: reminderForm.next_reminder_date
        }
        await createPaymentReminder(data)
        ElMessage.success('催缴登记成功')
        reminderDialogVisible.value = false
        loadData()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handlePay = (row) => {
  Object.assign(payForm, {
    installment_id: row.installment_id,
    period: row.period,
    student_name: row.student_name,
    principal_amount: row.principal_amount,
    late_fee: row.late_fee || 0,
    total_due: row.total_due,
    amount: row.total_due,
    payment_method: 'wechat'
  })
  payDialogVisible.value = true
}

const submitPay = async () => {
  if (!payFormRef.value) return
  await payFormRef.value.validate(async (valid) => {
    if (valid) {
      paying.value = true
      try {
        const data = {
          period: payForm.period,
          amount: payForm.amount,
          payment_method: payForm.payment_method
        }
        await payInstallment(payForm.installment_id, data)
        ElMessage.success('还款成功')
        payDialogVisible.value = false
        loadData()
      } catch (e) {
        console.error(e)
      } finally {
        paying.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.stat-card {
  text-align: center;

  .stat-icon {
    font-size: 36px;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    margin: 8px 0;
  }

  .stat-label {
    color: #909399;
    font-size: 14px;
  }
}

:deep(.overdue-row) {
  --el-table-tr-bg-color: #fef0f0;
  background-color: #fef0f0;
}
</style>
