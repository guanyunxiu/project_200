<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">学员管理</div>
      <el-button type="primary" @click="handleAdd" v-if="canEdit">
        <el-icon><Plus /></el-icon> 新增学员
      </el-button>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="姓名">
          <el-input v-model="filterForm.name" placeholder="请输入姓名" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="filterForm.phone" placeholder="请输入手机号" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="驾照类型">
          <el-select v-model="filterForm.license_type" placeholder="全部" clearable style="width: 150px;">
            <el-option label="C1证" value="C1" />
            <el-option label="C2证" value="C2" />
            <el-option label="D证" value="D" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px;">
            <el-option label="学习中" value="studying" />
            <el-option label="已毕业" value="graduated" />
            <el-option label="已休学" value="suspended" />
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
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender_display" label="性别" width="70" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="id_card" label="身份证号" width="180" />
        <el-table-column prop="license_type_display" label="驾照类型" width="120" />
        <el-table-column prop="package_name" label="报名套餐" width="120" />
        <el-table-column label="教练" width="100">
          <template #default="{ row }">{{ row.coach_info?.real_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="课时" width="140">
          <template #default="{ row }">
            {{ row.used_hours }}/{{ row.total_hours }}
            <el-tag size="small" :type="row.remaining_hours > 10 ? 'success' : 'warning'">
              剩余{{ row.remaining_hours }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enroll_date" label="报名日期" width="120" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'studying' ? 'success' : 'info'">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" link @click="handleEdit(row)" v-if="canEdit">编辑</el-button>
            <el-button size="small" type="success" link @click="handleHours(row)" v-if="canEdit">课时</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)" v-if="canEdit">删除</el-button>
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

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="form.gender">
              <el-radio value="male">男</el-radio>
              <el-radio value="female">女</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="身份证号" prop="id_card">
            <el-input v-model="form.id_card" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾照类型" prop="license_type">
            <el-select v-model="form.license_type" style="width: 100%;">
              <el-option label="C1证（手动挡）" value="C1" />
              <el-option label="C2证（自动挡）" value="C2" />
              <el-option label="D证（摩托车）" value="D" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出生日期" prop="birthday">
            <el-date-picker v-model="form.birthday" type="date" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="报名套餐" prop="package">
            <el-select v-model="form.package" style="width: 100%;">
              <el-option v-for="p in packages" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="所属教练" prop="coach">
            <el-select v-model="form.coach" style="width: 100%;" clearable>
              <el-option v-for="c in coaches" :key="c.id" :label="c.real_name || c.username" :value="c.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="总课时" prop="total_hours">
            <el-input-number v-model="form.total_hours" :min="0" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" style="width: 100%;">
              <el-option label="学习中" value="studying" />
              <el-option label="已毕业" value="graduated" />
              <el-option label="已休学" value="suspended" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="住址">
            <el-input v-model="form.address" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="3" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting" v-if="!isView">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="hoursDialogVisible" title="课时管理" width="400px">
    <div class="hours-info">
      <div class="hours-item"><span>总课时：</span><b>{{ currentStudent?.total_hours || 0 }}</b></div>
      <div class="hours-item"><span>已用课时：</span><b>{{ currentStudent?.used_hours || 0 }}</b></div>
      <div class="hours-item"><span>剩余课时：</span><b class="remaining">{{ (currentStudent?.total_hours || 0) - (currentStudent?.used_hours || 0) }}</b></div>
    </div>
    <el-form label-width="80px" style="margin-top: 20px;">
      <el-form-item label="操作">
        <el-radio-group v-model="hoursForm.operation">
          <el-radio value="add">增加已用</el-radio>
          <el-radio value="subtract">减少已用</el-radio>
          <el-radio value="set_total">设置总课时</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="课时数">
        <el-input-number v-model="hoursForm.hours" :min="0" style="width: 100%;" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="hoursDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleUpdateHours">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import {
  getStudentList, createStudent, updateStudent, deleteStudent, updateStudentHours
} from '@/api/students'
import { getActivePackages } from '@/api/packages'
import { getCoachList } from '@/api/users'

const router = useRouter()
const userStore = useUserStore()
const canEdit = computed(() => ['admin', 'coach'].includes(userStore.userInfo?.role))

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const hoursDialogVisible = ref(false)
const formRef = ref(null)
const isView = ref(false)
const isEdit = ref(false)
const currentStudent = ref(null)

const packages = ref([])
const coaches = ref([])

const filterForm = reactive({
  name: '',
  phone: '',
  license_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const form = reactive({
  id: null,
  name: '',
  gender: 'male',
  phone: '',
  id_card: '',
  license_type: 'C1',
  birthday: '',
  address: '',
  package: null,
  coach: null,
  total_hours: 0,
  status: 'studying',
  remark: ''
})

const hoursForm = reactive({
  operation: 'add',
  hours: 1
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  id_card: [{ required: true, message: '请输入身份证号', trigger: 'blur' }],
  license_type: [{ required: true, message: '请选择驾照类型', trigger: 'change' }],
  birthday: [{ required: true, message: '请选择出生日期', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '学员详情'
  if (isEdit.value) return '编辑学员'
  return '新增学员'
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { ...filterForm, page: pagination.page, page_size: pagination.page_size }
    const res = await getStudentList(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.name = ''
  filterForm.phone = ''
  filterForm.license_type = ''
  filterForm.status = ''
  pagination.page = 1
  loadData()
}

const loadOptions = async () => {
  try {
    const [pRes, cRes] = await Promise.all([
      getActivePackages(),
      getCoachList()
    ])
    packages.value = pRes
    coaches.value = cRes.results || []
  } catch (e) {
    console.error(e)
  }
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.gender = 'male'
  form.phone = ''
  form.id_card = ''
  form.license_type = 'C1'
  form.birthday = ''
  form.address = ''
  form.package = null
  form.coach = null
  form.total_hours = 0
  form.status = 'studying'
  form.remark = ''
}

const handleAdd = () => {
  resetForm()
  isView.value = false
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  form.package = row.package
  form.coach = row.coach
  isView.value = false
  isEdit.value = true
  dialogVisible.value = true
}

const handleView = (row) => {
  Object.assign(form, row)
  form.package = row.package
  form.coach = row.coach
  isView.value = true
  isEdit.value = false
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
          await updateStudent(form.id, submitData)
          ElMessage.success('修改成功')
        } else {
          await createStudent(submitData)
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
  ElMessageBox.confirm(`确定要删除学员「${row.name}」吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteStudent(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      console.error(e)
    }
  })
}

const handleHours = (row) => {
  currentStudent.value = row
  hoursForm.operation = 'add'
  hoursForm.hours = 1
  hoursDialogVisible.value = true
}

const handleUpdateHours = async () => {
  try {
    await updateStudentHours(currentStudent.value.id, hoursForm)
    ElMessage.success('操作成功')
    hoursDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>

<style scoped lang="scss">
.hours-info {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 5px;
  
  .hours-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    
    b.remaining {
      color: #67C23A;
      font-size: 18px;
    }
  }
}
</style>
