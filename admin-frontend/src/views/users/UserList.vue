<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">用户管理</div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增用户
      </el-button>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="角色">
          <el-select v-model="filterForm.role" placeholder="全部" clearable style="width: 150px;">
            <el-option label="管理员" value="admin" />
            <el-option label="财务" value="finance" />
            <el-option label="教练" value="coach" />
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
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="role_display" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTag(row.role)">{{ row.role_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)" v-if="row.id !== currentUserId">删除</el-button>
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

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="密码" prop="password" v-if="!isEdit">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="真实姓名" prop="real_name">
        <el-input v-model="form.real_name" />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="form.role" style="width: 100%;">
          <el-option label="管理员" value="admin" />
          <el-option label="财务" value="finance" />
          <el-option label="教练" value="coach" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否启用" prop="is_active">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/users'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userInfo?.id)

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const filterForm = reactive({
  role: '',
  is_active: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const form = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  role: 'coach',
  is_active: true
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码长度至少6位', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const getRoleTag = (role) => {
  const types = { admin: 'danger', finance: 'warning', coach: 'success' }
  return types[role] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filterForm.role) params.role = filterForm.role
    if (filterForm.is_active) params.is_active = filterForm.is_active
    const res = await getUserList(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.role = ''
  filterForm.is_active = ''
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  form.id = null
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.phone = ''
  form.email = ''
  form.role = 'coach'
  form.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  form.password = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = { ...form }
        if (isEdit.value) {
          delete submitData.password
          await updateUser(form.id, submitData)
          ElMessage.success('修改成功')
        } else {
          await createUser(submitData)
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
  ElMessageBox.confirm(`确定删除用户「${row.real_name || row.username}」吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteUser(row.id)
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
