<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">学时管理</div>
      <div class="header-actions">
        <el-button type="success" @click="openCoachConsumeDialog">
          <el-icon><Wallet /></el-icon> 教练核销
        </el-button>
        <el-button type="primary" @click="openAddTheoryDialog">
          <el-icon><DocumentAdd /></el-icon> 录入理论
        </el-button>
        <el-button type="warning" @click="openRenewCourseDialog">
          <el-icon><Money /></el-icon> 续课缴费
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-item">
            <div class="stats-label">今日消耗学时</div>
            <div class="stats-value primary">{{ stats.today_consumed_hours || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-item">
            <div class="stats-label">今日消耗记录</div>
            <div class="stats-value success">{{ stats.today_consumed_records || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-item">
            <div class="stats-label">累计消耗学时</div>
            <div class="stats-value warning">{{ stats.total_consumed_hours || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stats-card" @click="showLowHoursStudents">
          <div class="stats-item">
            <div class="stats-label">低学时学员</div>
            <div class="stats-value danger">{{ stats.low_hours_students_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="学员">
          <el-input v-model="filterForm.keyword" placeholder="姓名/手机号" clearable @keyup.enter="loadData" style="width: 180px;" />
        </el-form-item>
        <el-form-item label="学时类型">
          <el-select v-model="filterForm.hour_type" placeholder="全部" clearable style="width: 130px;">
            <el-option label="理论" value="theory" />
            <el-option label="实操" value="practical" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="filterForm.operation_type" placeholder="全部" clearable style="width: 130px;">
            <el-option label="教练核销" value="coach_consume" />
            <el-option label="录入理论" value="add_theory" />
            <el-option label="续课缴费" value="renew" />
            <el-option label="系统调整" value="adjust" />
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
            style="width: 260px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" border v-loading="loading" max-height="600">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="student_name" label="学员姓名" width="100" />
        <el-table-column prop="hour_type_display" label="学时类型" width="90">
          <template #default="{ row }">
            <el-tag :type="row.hour_type === 'theory' ? 'primary' : 'success'" size="small">
              {{ row.hour_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operation_type_display" label="操作类型" width="110">
          <template #default="{ row }">
            <el-tag :type="getOperationTypeTag(row.operation_type)" size="small">
              {{ row.operation_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hours" label="学时" width="80" align="center">
          <template #default="{ row }">
            <span :class="row.hours > 0 ? 'text-success' : 'text-danger'">
              {{ row.hours > 0 ? '+' : '' }}{{ row.hours }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="hours_before" label="操作前" width="80" align="center" />
        <el-table-column prop="hours_after" label="操作后" width="80" align="center" />
        <el-table-column prop="coach_name" label="教练" width="100">
          <template #default="{ row }">{{ row.coach_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="100" />
        <el-table-column prop="sign_in_time" label="签到时间" width="160">
          <template #default="{ row }">{{ row.sign_in_time || '-' }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
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

  <el-dialog v-model="coachConsumeDialogVisible" title="教练核销" width="500px" destroy-on-close>
    <el-form :model="coachConsumeForm" :rules="coachConsumeRules" ref="coachConsumeFormRef" label-width="100px">
      <el-form-item label="学员" prop="student_id">
        <el-select v-model="coachConsumeForm.student_id" placeholder="请选择学员" style="width: 100%;" filterable>
          <el-option v-for="s in studentOptions" :key="s.id" :label="`${s.name} (${s.phone})`" :value="s.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="学时类型" prop="hour_type">
        <el-select v-model="coachConsumeForm.hour_type" style="width: 100%;">
          <el-option label="实操" value="practical" />
          <el-option label="理论" value="theory" />
        </el-select>
      </el-form-item>
      <el-form-item label="核销学时" prop="hours">
        <el-input-number v-model="coachConsumeForm.hours" :min="0.5" :step="0.5" :precision="1" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="coachConsumeForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="coachConsumeDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleCoachConsume" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="addTheoryDialogVisible" title="录入理论学时" width="500px" destroy-on-close>
    <el-form :model="addTheoryForm" :rules="addTheoryRules" ref="addTheoryFormRef" label-width="100px">
      <el-form-item label="学员" prop="student_id">
        <el-select v-model="addTheoryForm.student_id" placeholder="请选择学员" style="width: 100%;" filterable>
          <el-option v-for="s in studentOptions" :key="s.id" :label="`${s.name} (${s.phone})`" :value="s.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="理论学时" prop="hours">
        <el-input-number v-model="addTheoryForm.hours" :min="0.5" :step="0.5" :precision="1" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="addTheoryForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="addTheoryDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleAddTheory" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="renewCourseDialogVisible" title="续课缴费" width="500px" destroy-on-close>
    <el-form :model="renewCourseForm" :rules="renewCourseRules" ref="renewCourseFormRef" label-width="100px">
      <el-form-item label="学员" prop="student_id">
        <el-select v-model="renewCourseForm.student_id" placeholder="请选择学员" style="width: 100%;" filterable>
          <el-option v-for="s in studentOptions" :key="s.id" :label="`${s.name} (${s.phone})`" :value="s.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="学时类型" prop="hour_type">
        <el-select v-model="renewCourseForm.hour_type" style="width: 100%;">
          <el-option label="实操" value="practical" />
          <el-option label="理论" value="theory" />
        </el-select>
      </el-form-item>
      <el-form-item label="续课学时" prop="hours">
        <el-input-number v-model="renewCourseForm.hours" :min="1" :step="1" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="缴费金额" prop="amount">
        <el-input-number v-model="renewCourseForm.amount" :min="0" :step="100" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="支付方式" prop="payment_method">
        <el-select v-model="renewCourseForm.payment_method" style="width: 100%;">
          <el-option label="微信支付" value="wechat" />
          <el-option label="支付宝" value="alipay" />
          <el-option label="现金" value="cash" />
          <el-option label="银行卡" value="bank" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="renewCourseForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="renewCourseDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleRenewCourse" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="lowHoursDialogVisible" title="低学时学员列表" width="600px">
    <el-table :data="lowHoursStudents" border v-loading="lowHoursLoading">
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="license_type_display" label="驾照类型" width="100" />
      <el-table-column label="剩余学时" width="120">
        <template #default="{ row }">
          <el-tag type="danger" size="small">{{ row.remaining_hours || 0 }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Wallet, DocumentAdd, Money } from '@element-plus/icons-vue'
import {
  getHourRecordList,
  coachConsumeHours,
  addTheoryHours,
  renewCourse,
  getHourStats,
  getLowHoursStudents,
  getStudentSimpleList
} from '@/api/students'

const loading = ref(false)
const submitting = ref(false)
const lowHoursLoading = ref(false)
const tableData = ref([])
const studentOptions = ref([])
const lowHoursStudents = ref([])

const stats = reactive({
  today_consumed_hours: 0,
  today_consumed_records: 0,
  total_consumed_hours: 0,
  low_hours_students_count: 0
})

const filterForm = reactive({
  keyword: '',
  hour_type: '',
  operation_type: '',
  date_range: []
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const coachConsumeDialogVisible = ref(false)
const coachConsumeFormRef = ref(null)
const coachConsumeForm = reactive({
  student_id: null,
  hour_type: 'practical',
  hours: 1,
  remark: ''
})

const addTheoryDialogVisible = ref(false)
const addTheoryFormRef = ref(null)
const addTheoryForm = reactive({
  student_id: null,
  hours: 1,
  remark: ''
})

const renewCourseDialogVisible = ref(false)
const renewCourseFormRef = ref(null)
const renewCourseForm = reactive({
  student_id: null,
  hour_type: 'practical',
  hours: 10,
  amount: 0,
  payment_method: 'wechat',
  remark: ''
})

const lowHoursDialogVisible = ref(false)

const coachConsumeRules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  hour_type: [{ required: true, message: '请选择学时类型', trigger: 'change' }],
  hours: [{ required: true, message: '请输入核销学时', trigger: 'blur' }]
}

const addTheoryRules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  hours: [{ required: true, message: '请输入理论学时', trigger: 'blur' }]
}

const renewCourseRules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  hour_type: [{ required: true, message: '请选择学时类型', trigger: 'change' }],
  hours: [{ required: true, message: '请输入续课学时', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入缴费金额', trigger: 'blur' }],
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const getOperationTypeTag = (type) => {
  const tagMap = {
    coach_consume: 'success',
    add_theory: 'primary',
    renew: 'warning',
    adjust: 'info'
  }
  return tagMap[type] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filterForm.keyword) params.keyword = filterForm.keyword
    if (filterForm.hour_type) params.hour_type = filterForm.hour_type
    if (filterForm.operation_type) params.operation_type = filterForm.operation_type
    if (filterForm.date_range && filterForm.date_range.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }
    const res = await getHourRecordList(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await getHourStats()
    Object.assign(stats, res)
  } catch (e) {
    console.error(e)
  }
}

const loadStudentOptions = async () => {
  try {
    const res = await getStudentSimpleList()
    studentOptions.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.hour_type = ''
  filterForm.operation_type = ''
  filterForm.date_range = []
  pagination.page = 1
  loadData()
}

const resetCoachConsumeForm = () => {
  coachConsumeForm.student_id = null
  coachConsumeForm.hour_type = 'practical'
  coachConsumeForm.hours = 1
  coachConsumeForm.remark = ''
}

const resetAddTheoryForm = () => {
  addTheoryForm.student_id = null
  addTheoryForm.hours = 1
  addTheoryForm.remark = ''
}

const resetRenewCourseForm = () => {
  renewCourseForm.student_id = null
  renewCourseForm.hour_type = 'practical'
  renewCourseForm.hours = 10
  renewCourseForm.amount = 0
  renewCourseForm.payment_method = 'wechat'
  renewCourseForm.remark = ''
}

const openCoachConsumeDialog = () => {
  resetCoachConsumeForm()
  coachConsumeDialogVisible.value = true
}

const openAddTheoryDialog = () => {
  resetAddTheoryForm()
  addTheoryDialogVisible.value = true
}

const openRenewCourseDialog = () => {
  resetRenewCourseForm()
  renewCourseDialogVisible.value = true
}

const handleCoachConsume = async () => {
  if (!coachConsumeFormRef.value) return
  await coachConsumeFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const res = await coachConsumeHours(coachConsumeForm)
        ElMessage.success('核销成功')
        if (res.hours_low) {
          ElMessage.warning('该学员剩余学时不足，请提醒学员续课')
        }
        coachConsumeDialogVisible.value = false
        loadData()
        loadStats()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleAddTheory = async () => {
  if (!addTheoryFormRef.value) return
  await addTheoryFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await addTheoryHours(addTheoryForm)
        ElMessage.success('录入成功')
        addTheoryDialogVisible.value = false
        loadData()
        loadStats()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleRenewCourse = async () => {
  if (!renewCourseFormRef.value) return
  await renewCourseFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await renewCourse(renewCourseForm)
        ElMessage.success('续课成功')
        renewCourseDialogVisible.value = false
        loadData()
        loadStats()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const showLowHoursStudents = async () => {
  lowHoursLoading.value = true
  try {
    const res = await getLowHoursStudents()
    lowHoursStudents.value = res || []
    lowHoursDialogVisible.value = true
  } catch (e) {
    console.error(e)
  } finally {
    lowHoursLoading.value = false
  }
}

onMounted(() => {
  loadData()
  loadStats()
  loadStudentOptions()
})
</script>

<style scoped lang="scss">
.stats-cards {
  margin-bottom: 20px;

  .stats-card {
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-2px);
    }
  }

  .stats-item {
    text-align: center;

    .stats-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 8px;
    }

    .stats-value {
      font-size: 28px;
      font-weight: bold;

      &.primary {
        color: #409eff;
      }

      &.success {
        color: #67c23a;
      }

      &.warning {
        color: #e6a23c;
      }

      &.danger {
        color: #f56c6c;
      }
    }
  }
}

.text-success {
  color: #67c23a;
  font-weight: bold;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
