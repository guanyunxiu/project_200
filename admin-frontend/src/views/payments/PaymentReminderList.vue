<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">催缴记录管理</div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增催缴
      </el-button>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="学员信息">
          <el-input v-model="filterForm.keyword" placeholder="姓名/手机号" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item label="催缴方式">
          <el-select v-model="filterForm.reminder_type" placeholder="全部" clearable style="width: 150px;">
            <el-option label="电话" value="phone" />
            <el-option label="短信" value="sms" />
            <el-option label="微信" value="wechat" />
            <el-option label="上门" value="visit" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="催缴结果">
          <el-select v-model="filterForm.result" placeholder="全部" clearable style="width: 150px;">
            <el-option label="承诺还款" value="promised" />
            <el-option label="部分还款" value="partial" />
            <el-option label="无人接听" value="no_answer" />
            <el-option label="拒绝还款" value="refused" />
            <el-option label="待跟进" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 300px;"
          />
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
        <el-table-column prop="student_name" label="学员姓名" width="120" />
        <el-table-column prop="student_phone" label="手机号" width="130" />
        <el-table-column label="分期计划" min-width="200">
          <template #default="{ row }">
            {{ row.installment_plan?.student_name || '-' }} - {{ row.installment_plan?.months || '-' }}期
          </template>
        </el-table-column>
        <el-table-column prop="reminder_type_display" label="催缴方式" width="100" />
        <el-table-column prop="reminder_date" label="催缴日期" width="120" />
        <el-table-column prop="amount" label="催缴金额" width="120">
          <template #default="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="催缴结果" width="110">
          <template #default="{ row }">
            <el-tag :type="getResultTagType(row.result)">
              {{ row.result_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="promised_date" label="承诺还款日" width="120" />
        <el-table-column prop="operator_name" label="经办人" width="100" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑催缴记录' : '新增催缴记录'" width="600px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="学员" prop="student">
        <el-select
          v-model="form.student"
          placeholder="请选择学员"
          filterable
          style="width: 100%;"
          @change="handleStudentChange"
        >
          <el-option
            v-for="item in studentList"
            :key="item.id"
            :label="`${item.name} - ${item.phone}`"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="分期计划" prop="installment_plan">
        <el-select v-model="form.installment_plan" placeholder="请选择分期计划" filterable style="width: 100%;">
          <el-option
            v-for="item in installmentList"
            :key="item.id"
            :label="`${item.months}期 - ¥${Number(item.monthly_amount).toFixed(2)}/期"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="催缴方式" prop="reminder_type">
            <el-select v-model="form.reminder_type" placeholder="请选择" style="width: 100%;">
              <el-option label="电话" value="phone" />
              <el-option label="短信" value="sms" />
              <el-option label="微信" value="wechat" />
              <el-option label="上门" value="visit" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="催缴金额" prop="amount">
            <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%;" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="催缴结果" prop="result">
            <el-select v-model="form.result" placeholder="请选择" style="width: 100%;">
              <el-option label="承诺还款" value="promised" />
              <el-option label="部分还款" value="partial" />
              <el-option label="无人接听" value="no_answer" />
              <el-option label="拒绝还款" value="refused" />
              <el-option label="待跟进" value="pending" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="承诺还款日" prop="promised_date">
            <el-date-picker
              v-model="form.promised_date"
              type="date"
              placeholder="请选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%;"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getPaymentReminderList, createPaymentReminder,
  updatePaymentReminder, deletePaymentReminder,
  getInstallmentList
} from '@/api/payments'
import { getStudentSimpleList } from '@/api/students'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const studentList = ref([])
const installmentList = ref([])

const filterForm = reactive({
  keyword: '',
  reminder_type: '',
  result: '',
  date_range: []
})

const form = reactive({
  id: null,
  student: null,
  installment_plan: null,
  reminder_type: '',
  amount: 0,
  result: '',
  promised_date: '',
  remark: ''
})

const rules = {
  student: [{ required: true, message: '请选择学员', trigger: 'change' }],
  installment_plan: [{ required: true, message: '请选择分期计划', trigger: 'change' }],
  reminder_type: [{ required: true, message: '请选择催缴方式', trigger: 'change' }],
  amount: [{ required: true, message: '请输入催缴金额', trigger: 'blur' }],
  result: [{ required: true, message: '请选择催缴结果', trigger: 'change' }]
}

const reminderTypeMap = {
  phone: '电话',
  sms: '短信',
  wechat: '微信',
  visit: '上门',
  other: '其他'
}

const resultMap = {
  promised: '承诺还款',
  partial: '部分还款',
  no_answer: '无人接听',
  refused: '拒绝还款',
  pending: '待跟进'
}

const getResultTagType = (result) => {
  const typeMap = {
    promised: 'success',
    partial: 'warning',
    no_answer: 'info',
    refused: 'danger',
    pending: 'primary'
  }
  return typeMap[result] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.keyword) params.keyword = filterForm.keyword
    if (filterForm.reminder_type) params.reminder_type = filterForm.reminder_type
    if (filterForm.result) params.result = filterForm.result
    if (filterForm.date_range && filterForm.date_range.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }
    const res = await getPaymentReminderList(params)
    tableData.value = res.results || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.reminder_type = ''
  filterForm.result = ''
  filterForm.date_range = []
  loadData()
}

const loadStudentList = async () => {
  try {
    const res = await getStudentSimpleList()
    studentList.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const loadInstallmentList = async (studentId = null) => {
  try {
    const params = {}
    if (studentId) params.student_id = studentId
    const res = await getInstallmentList(params)
    installmentList.value = res.results || []
  } catch (e) {
    console.error(e)
  }
}

const handleStudentChange = (studentId) => {
  form.installment_plan = null
  loadInstallmentList(studentId)
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    student: null,
    installment_plan: null,
    reminder_type: '',
    amount: 0,
    result: '',
    promised_date: '',
    remark: ''
  })
  installmentList.value = []
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    student: row.student,
    installment_plan: row.installment_plan?.id,
    reminder_type: row.reminder_type,
    amount: Number(row.amount),
    result: row.result,
    promised_date: row.promised_date,
    remark: row.remark
  })
  loadInstallmentList(row.student)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该催缴记录吗？', '提示', { type: 'warning' })
    await deletePaymentReminder(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = {
          student: form.student,
          installment_plan: form.installment_plan,
          reminder_type: form.reminder_type,
          amount: form.amount,
          result: form.result,
          promised_date: form.promised_date || null,
          remark: form.remark
        }
        if (isEdit.value) {
          await updatePaymentReminder(form.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createPaymentReminder(submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
  loadStudentList()
})
</script>
