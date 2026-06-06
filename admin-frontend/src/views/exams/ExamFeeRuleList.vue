<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">考试费用规则</div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增规则
      </el-button>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_active" placeholder="全部" clearable style="width: 150px;">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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
        <el-table-column label="科目" width="120">
          <template #default="{ row }">{{ getSubjectName(row.subject) }}</template>
        </el-table-column>
        <el-table-column label="费用金额" width="120">
          <template #default="{ row }">¥{{ row.fee_amount }}</template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" link @click="handleToggle(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑规则' : '新增规则'" width="600px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="科目" prop="subject">
        <el-select v-model="form.subject" placeholder="请选择科目" style="width: 100%;">
          <el-option label="科目一（理论）" :value="1" />
          <el-option label="科目二（场地）" :value="2" />
          <el-option label="科目三（道路）" :value="3" />
          <el-option label="科目四（安全）" :value="4" />
        </el-select>
      </el-form-item>
      <el-form-item label="费用金额" prop="fee_amount">
        <el-input-number v-model="form.fee_amount" :min="0" :precision="2" :step="10" style="width: 100%;" />
        <span style="color: #909399; font-size: 12px;">元</span>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
      </el-form-item>
      <el-form-item label="是否启用">
        <el-switch v-model="form.is_active" />
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
  getExamFeeRuleList, createExamFeeRule,
  updateExamFeeRule, deleteExamFeeRule
} from '@/api/exams'

const subjectMap = {
  1: '科目一（理论）',
  2: '科目二（场地）',
  3: '科目三（道路）',
  4: '科目四（安全）'
}

const getSubjectName = (subject) => {
  return subjectMap[subject] || '未知'
}

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const filterForm = reactive({
  is_active: ''
})

const form = reactive({
  id: null,
  subject: null,
  fee_amount: 0,
  description: '',
  is_active: true
})

const validateSubjectUnique = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请选择科目'))
    return
  }
  const exists = tableData.value.some(
    item => item.subject === value && item.id !== form.id
  )
  if (exists) {
    callback(new Error('该科目已存在费用规则，请选择其他科目'))
  } else {
    callback()
  }
}

const rules = {
  subject: [
    { required: true, validator: validateSubjectUnique, trigger: 'change' }
  ],
  fee_amount: [
    { required: true, message: '请输入费用金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '费用金额不能小于0', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过500个字符', trigger: 'blur' }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.is_active !== '') params.is_active = filterForm.is_active
    const res = await getExamFeeRuleList(params)
    tableData.value = res.results || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.is_active = ''
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    subject: null,
    fee_amount: 0,
    description: '',
    is_active: true
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleToggle = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? '禁用' : '启用'}该规则吗？`,
      '提示',
      { type: 'warning' }
    )
    await updateExamFeeRule(row.id, { ...row, is_active: !row.is_active })
    ElMessage.success('操作成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', { type: 'warning' })
    await deleteExamFeeRule(row.id)
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
        if (isEdit.value) {
          await updateExamFeeRule(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createExamFeeRule(form)
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
})
</script>
