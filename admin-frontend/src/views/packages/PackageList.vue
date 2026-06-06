<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">套餐管理</div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增套餐
      </el-button>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="套餐类型">
          <el-select v-model="filterForm.type" placeholder="全部" clearable style="width: 150px;">
            <el-option label="普通班" value="normal" />
            <el-option label="精品班" value="premium" />
            <el-option label="VIP班" value="vip" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用驾照">
          <el-select v-model="filterForm.license_type" placeholder="全部" clearable style="width: 150px;">
            <el-option label="C1证" value="C1" />
            <el-option label="C2证" value="C2" />
            <el-option label="D证" value="D" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_active" placeholder="全部" clearable style="width: 150px;">
            <el-option label="启用" value="true" />
            <el-option label="禁用" value="false" />
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
        <el-table-column prop="code" label="套餐编码" width="140" />
        <el-table-column prop="name" label="套餐名称" width="150" />
        <el-table-column prop="type_display" label="套餐类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ row.type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="license_type_display" label="适用驾照" width="100" />
        <el-table-column prop="base_price" label="基准报名费" width="120">
          <template #default="{ row }"><b style="color: #F56C6C;">¥{{ row.base_price }}</b></template>
        </el-table-column>
        <el-table-column prop="total_hours" label="包含课时" width="100" />
        <el-table-column label="分期付款" width="180">
          <template #default="{ row }">
            <div v-if="row.payment_type !== 'full'">
              <div>首付: ¥{{ row.down_payment }}</div>
              <div>{{ row.installment_months }}期 × ¥{{ row.installment_amount }}</div>
            </div>
            <el-tag v-else type="info">不支持分期</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="student_count" label="报名人数" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑套餐' : '新增套餐'" width="700px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="套餐名称" prop="name">
            <el-input v-model="form.name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="套餐编码" prop="code">
            <el-input v-model="form.code" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="套餐类型" prop="type">
            <el-select v-model="form.type" style="width: 100%;">
              <el-option label="普通班" value="normal" />
              <el-option label="精品班" value="premium" />
              <el-option label="VIP班" value="vip" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="适用驾照" prop="license_type">
            <el-select v-model="form.license_type" style="width: 100%;">
              <el-option label="C1证" value="C1" />
              <el-option label="C2证" value="C2" />
              <el-option label="D证" value="D" />
              <el-option label="通用" value="all" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="基准报名费" prop="base_price">
            <el-input-number v-model="form.base_price" :min="0" :precision="2" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="包含课时" prop="total_hours">
            <el-input-number v-model="form.total_hours" :min="0" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="付款方式" prop="payment_type">
            <el-select v-model="form.payment_type" style="width: 100%;">
              <el-option label="一次性付款" value="full" />
              <el-option label="分期付款" value="installment" />
              <el-option label="支持两种" value="both" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="是否启用" prop="is_active">
            <el-switch v-model="form.is_active" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider v-if="form.payment_type !== 'full'" content-position="left">分期设置</el-divider>
      <el-row :gutter="20" v-if="form.payment_type !== 'full'">
        <el-col :span="8">
          <el-form-item label="首付金额" prop="down_payment">
            <el-input-number v-model="form.down_payment" :min="0" :precision="2" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="分期期数" prop="installment_months">
            <el-input-number v-model="form.installment_months" :min="1" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="每期金额" prop="installment_amount">
            <el-input-number v-model="form.installment_amount" :min="0" :precision="2" style="width: 100%;" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="套餐描述">
        <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { getPackageList, createPackage, updatePackage, deletePackage } from '@/api/packages'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const filterForm = reactive({
  type: '',
  license_type: '',
  is_active: ''
})

const form = reactive({
  id: null,
  name: '',
  code: '',
  type: 'normal',
  license_type: 'all',
  base_price: 0,
  total_hours: 0,
  description: '',
  payment_type: 'both',
  down_payment: 0,
  installment_months: 0,
  installment_amount: 0,
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入套餐名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入套餐编码', trigger: 'blur' }],
  type: [{ required: true, message: '请选择套餐类型', trigger: 'change' }],
  license_type: [{ required: true, message: '请选择适用驾照', trigger: 'change' }],
  base_price: [{ required: true, message: '请输入基准报名费', trigger: 'blur' }]
}

const getTypeTag = (type) => {
  const types = { normal: 'info', premium: 'warning', vip: 'success' }
  return types[type] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.type) params.type = filterForm.type
    if (filterForm.license_type) params.license_type = filterForm.license_type
    if (filterForm.is_active !== '') params.is_active = filterForm.is_active
    const res = await getPackageList(params)
    tableData.value = res.results || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.type = ''
  filterForm.license_type = ''
  filterForm.is_active = ''
  loadData()
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.code = ''
  form.type = 'normal'
  form.license_type = 'all'
  form.base_price = 0
  form.total_hours = 0
  form.description = ''
  form.payment_type = 'both'
  form.down_payment = 0
  form.installment_months = 0
  form.installment_amount = 0
  form.is_active = true
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  isEdit.value = true
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await updatePackage(form.id, form)
          ElMessage.success('修改成功')
        } else {
          await createPackage(form)
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

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除套餐「${row.name}」吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deletePackage(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      console.error(e)
    }
  })
}

onMounted(() => {
  loadData()
})
</script>
