<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">分期方案配置</div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增方案
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
        <el-table-column prop="name" label="方案名称" width="150" />
        <el-table-column label="首付比例" width="120">
          <template #default="{ row }">{{ row.down_payment_ratio }}%</template>
        </el-table-column>
        <el-table-column prop="periods" label="分期期数" width="100">
          <template #default="{ row }">{{ row.periods }}期</template>
        </el-table-column>
        <el-table-column prop="due_day" label="每期还款日" width="120">
          <template #default="{ row }">每月{{ row.due_day }}日</template>
        </el-table-column>
        <el-table-column label="滞纳金比例" width="150">
          <template #default="{ row }">每日{{ row.late_fee_ratio }}%</template>
        </el-table-column>
        <el-table-column prop="description" label="方案描述" min-width="200" show-overflow-tooltip />
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

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑方案' : '新增方案'" width="600px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="方案名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入方案名称" />
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="首付比例" prop="down_payment_ratio">
            <el-input-number v-model="form.down_payment_ratio" :min="0" :max="100" :precision="2" style="width: 100%;" />
            <span style="color: #909399; font-size: 12px;">%</span>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="分期期数" prop="periods">
            <el-input-number v-model="form.periods" :min="1" :max="36" style="width: 100%;" />
            <span style="color: #909399; font-size: 12px;">期</span>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="每期还款日" prop="due_day">
            <el-input-number v-model="form.due_day" :min="1" :max="28" style="width: 100%;" />
            <span style="color: #909399; font-size: 12px;">日</span>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="滞纳金比例" prop="late_fee_ratio">
            <el-input-number v-model="form.late_fee_ratio" :min="0" :max="1" :precision="4" :step="0.01" style="width: 100%;" />
            <span style="color: #909399; font-size: 12px;">% / 日</span>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="方案描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入方案描述" />
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
  getInstallmentSchemeList, createInstallmentScheme,
  updateInstallmentScheme, deleteInstallmentScheme
} from '@/api/payments'

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
  name: '',
  down_payment_ratio: 30,
  periods: 6,
  due_day: 15,
  late_fee_ratio: 0.05,
  description: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入方案名称', trigger: 'blur' }],
  down_payment_ratio: [{ required: true, message: '请输入首付比例', trigger: 'blur' }],
  periods: [{ required: true, message: '请输入分期期数', trigger: 'blur' }],
  due_day: [{ required: true, message: '请输入还款日', trigger: 'blur' }],
  late_fee_ratio: [{ required: true, message: '请输入滞纳金比例', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.is_active !== '') params.is_active = filterForm.is_active
    const res = await getInstallmentSchemeList(params)
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
    name: '',
    down_payment_ratio: 30,
    periods: 6,
    due_day: 15,
    late_fee_ratio: 0.05,
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
      `确定要${row.is_active ? '禁用' : '启用'}该方案吗？`,
      '提示',
      { type: 'warning' }
    )
    await updateInstallmentScheme(row.id, { ...row, is_active: !row.is_active })
    ElMessage.success('操作成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该方案吗？', '提示', { type: 'warning' })
    await deleteInstallmentScheme(row.id)
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
          await updateInstallmentScheme(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createInstallmentScheme(form)
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
