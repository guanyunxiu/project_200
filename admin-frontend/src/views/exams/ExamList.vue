<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">约考管理</div>
      <div>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 代约考试
        </el-button>
      </div>
    </div>

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
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px;">
            <el-option label="待审核" value="pending" />
            <el-option label="已约考" value="approved" />
            <el-option label="缺考" value="absent" />
            <el-option label="已通过" value="passed" />
            <el-option label="未通过" value="failed" />
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
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="student_name" label="学员姓名" width="100" />
        <el-table-column prop="student_phone" label="手机号" width="130" />
        <el-table-column label="考试信息" width="280">
          <template #default="{ row }">
            <div><b>{{ row.schedule_info?.subject_display }}</b></div>
            <div style="color: #909399; font-size: 12px;">{{ row.schedule_info?.exam_date }} {{ row.schedule_info?.start_time }}-{{ row.schedule_info?.end_time }}</div>
            <div style="color: #909399; font-size: 12px;">考场: {{ row.schedule_info?.room_name }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="booking_type_display" label="预约类型" width="100" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分数" width="80">
          <template #default="{ row }">{{ row.score !== null ? row.score : '-' }}</template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="90" />
        <el-table-column prop="booked_at" label="预约时间" width="170" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleApprove(row)" v-if="row.status === 'pending'">审核通过</el-button>
            <el-button size="small" type="warning" link @click="handleAbsent(row)" v-if="row.status === 'approved'">缺考</el-button>
            <el-button size="small" type="success" link @click="handleResult(row, true)" v-if="row.status === 'approved'">通过</el-button>
            <el-button size="small" type="danger" link @click="handleResult(row, false)" v-if="row.status === 'approved'">未通过</el-button>
            <el-button size="small" type="info" link @click="handleCancel(row)" v-if="['pending', 'approved'].includes(row.status)">取消</el-button>
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

  <el-dialog v-model="addVisible" title="代约考试" width="600px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="选择学员" prop="student">
        <el-select v-model="form.student" filterable placeholder="请选择学员" style="width: 100%;">
          <el-option
            v-for="s in students"
            :key="s.id"
            :label="`${s.name} - ${s.phone} - ${s.license_type_display}`"
            :value="s.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="考试安排" prop="schedule">
        <el-select v-model="form.schedule" filterable placeholder="请选择考试安排" style="width: 100%;">
          <el-option
            v-for="s in schedules"
            :key="s.id"
            :label="`${s.subject_display} - ${s.exam_date} ${s.start_time} - ${s.room_name} (余${s.remaining_quota}名额)`"
            :value="s.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio value="pending">待审核</el-radio>
          <el-radio value="approved">直接通过</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="addVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="resultVisible" title="录入成绩" width="400px">
    <el-form label-width="80px">
      <el-form-item label="分数">
        <el-input-number v-model="resultForm.score" :min="0" :max="100" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="是否通过">
        <el-tag :type="resultForm.passed ? 'success' : 'danger'">
          {{ resultForm.passed ? '通过' : '未通过' }}
        </el-tag>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="resultVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmResult">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getExamBookingList, createExamBooking, approveExamBooking,
  markExamAbsent, markExamResult, cancelExamBooking
} from '@/api/exams'
import { getAvailableSchedules } from '@/api/exams'
import { getStudentSimpleList } from '@/api/students'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const addVisible = ref(false)
const resultVisible = ref(false)
const formRef = ref(null)
const students = ref([])
const schedules = ref([])
const currentBooking = ref(null)

const filterForm = reactive({
  student_name: '',
  subject: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const form = reactive({
  student: null,
  schedule: null,
  status: 'approved',
  remark: ''
})

const resultForm = reactive({
  score: 90,
  passed: true
})

const rules = {
  student: [{ required: true, message: '请选择学员', trigger: 'change' }],
  schedule: [{ required: true, message: '请选择考试安排', trigger: 'change' }]
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    approved: 'primary',
    absent: 'info',
    passed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filterForm.subject) params.subject = filterForm.subject
    if (filterForm.status) params.status = filterForm.status
    const res = await getExamBookingList(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [sRes, eRes] = await Promise.all([
      getStudentSimpleList(),
      getAvailableSchedules()
    ])
    students.value = sRes
    schedules.value = eRes
  } catch (e) {
    console.error(e)
  }
}

const resetFilter = () => {
  filterForm.student_name = ''
  filterForm.subject = ''
  filterForm.status = ''
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  form.student = null
  form.schedule = null
  form.status = 'approved'
  form.remark = ''
  loadOptions()
  addVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await createExamBooking(form)
        ElMessage.success('预约成功')
        addVisible.value = false
        loadData()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleApprove = async (row) => {
  try {
    await approveExamBooking(row.id)
    ElMessage.success('审核通过')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const handleAbsent = async (row) => {
  ElMessageBox.confirm(`确定标记学员「${row.student_name}」为缺考吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await markExamAbsent(row.id)
      ElMessage.success('已标记缺考')
      loadData()
    } catch (e) {
      console.error(e)
    }
  })
}

const handleResult = (row, passed) => {
  currentBooking.value = row
  resultForm.passed = passed
  resultForm.score = passed ? 90 : 70
  resultVisible.value = true
}

const confirmResult = async () => {
  try {
    await markExamResult(currentBooking.value.id, resultForm)
    ElMessage.success('成绩已录入')
    resultVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const handleCancel = async (row) => {
  ElMessageBox.confirm(`确定取消学员「${row.student_name}」的考试预约吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await cancelExamBooking(row.id)
      ElMessage.success('已取消')
      loadData()
    } catch (e) {
      console.error(e)
    }
  })
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>
