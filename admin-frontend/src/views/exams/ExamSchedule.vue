<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">考试安排</div>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-button type="primary" @click="handleAddRoom">
            <el-icon><Plus /></el-icon> 新增考场
          </el-button>
          <el-button type="success" @click="handleAddSchedule">
            <el-icon><CalendarPlus /></el-icon> 新增考试安排
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>考场列表</span>
            </div>
          </template>
          <el-table :data="rooms" border v-loading="roomsLoading">
            <el-table-column prop="name" label="考场名称" />
            <el-table-column prop="capacity" label="容量" width="80" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="handleEditRoom(row)">编辑</el-button>
                <el-button size="small" type="danger" link @click="handleDeleteRoom(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>考试安排</span>
            </div>
          </template>
          <div class="filter-bar" style="margin-bottom: 10px;">
            <el-form :inline="true" :model="filterForm" size="small">
              <el-form-item label="科目">
                <el-select v-model="filterForm.subject" placeholder="全部" clearable style="width: 120px;">
                  <el-option label="科目一" :value="1" />
                  <el-option label="科目二" :value="2" />
                  <el-option label="科目三" :value="3" />
                  <el-option label="科目四" :value="4" />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px;">
                  <el-option label="预约开放" value="open" />
                  <el-option label="预约关闭" value="locked" />
                  <el-option label="考试完成" value="completed" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="small" @click="loadSchedules">查询</el-button>
                <el-button size="small" @click="resetFilter">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          <el-table :data="schedules" border v-loading="schedulesLoading">
            <el-table-column prop="subject_display" label="科目" width="120" />
            <el-table-column prop="room_name" label="考场" width="150" />
            <el-table-column label="考试时间" width="220">
              <template #default="{ row }">
                <div>{{ row.exam_date }}</div>
                <div style="color: #909399; font-size: 12px;">{{ row.start_time }} - {{ row.end_time }}</div>
              </template>
            </el-table-column>
            <el-table-column label="名额" width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round(row.booked_quota / row.total_quota * 100)"
                  :format="() => `${row.booked_quota}/${row.total_quota}`"
                />
              </template>
            </el-table-column>
            <el-table-column prop="status_display" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'open' ? 'success' : row.status === 'locked' ? 'warning' : 'info'" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="success" link @click="handleUnlock(row)" v-if="row.status === 'locked'">开放预约</el-button>
                <el-button size="small" type="warning" link @click="handleLock(row)" v-if="row.status === 'open'">关闭预约</el-button>
                <el-button size="small" type="primary" link @click="handleEditSchedule(row)">编辑</el-button>
                <el-button size="small" type="danger" link @click="handleDeleteSchedule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>

  <el-dialog v-model="roomDialogVisible" :title="isEditRoom ? '编辑考场' : '新增考场'" width="500px" destroy-on-close>
    <el-form :model="roomForm" :rules="roomRules" ref="roomFormRef" label-width="80px">
      <el-form-item label="考场名称" prop="name">
        <el-input v-model="roomForm.name" />
      </el-form-item>
      <el-form-item label="考场地址" prop="address">
        <el-input v-model="roomForm.address" />
      </el-form-item>
      <el-form-item label="容纳人数" prop="capacity">
        <el-input-number v-model="roomForm.capacity" :min="1" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="是否启用" prop="is_active">
        <el-switch v-model="roomForm.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="roomDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSaveRoom" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="scheduleDialogVisible" :title="isEditSchedule ? '编辑考试安排' : '新增考试安排'" width="600px" destroy-on-close>
    <el-form :model="scheduleForm" :rules="scheduleRules" ref="scheduleFormRef" label-width="100px">
      <el-form-item label="考试科目" prop="subject">
        <el-select v-model="scheduleForm.subject" style="width: 100%;">
          <el-option label="科目一（理论）" :value="1" />
          <el-option label="科目二（场地）" :value="2" />
          <el-option label="科目三（道路）" :value="3" />
          <el-option label="科目四（安全文明）" :value="4" />
        </el-select>
      </el-form-item>
      <el-form-item label="考场" prop="exam_room">
        <el-select v-model="scheduleForm.exam_room" style="width: 100%;">
          <el-option v-for="r in rooms" :key="r.id" :label="r.name" :value="r.id" />
        </el-select>
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="考试日期" prop="exam_date">
            <el-date-picker v-model="scheduleForm.exam_date" type="date" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="开始时间" prop="start_time">
            <el-time-picker v-model="scheduleForm.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="结束时间" prop="end_time">
            <el-time-picker v-model="scheduleForm.end_time" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="总名额" prop="total_quota">
        <el-input-number v-model="scheduleForm.total_quota" :min="1" style="width: 200px;" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="scheduleForm.status">
          <el-radio value="open">预约开放</el-radio>
          <el-radio value="locked">预约关闭</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="scheduleForm.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="scheduleDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSaveSchedule" :loading="submitting">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, CalendarPlus } from '@element-plus/icons-vue'
import {
  getExamRoomList, createExamRoom, updateExamRoom, deleteExamRoom,
  getExamScheduleList, createExamSchedule, updateExamSchedule, deleteExamSchedule,
  lockExamSchedule, unlockExamSchedule
} from '@/api/exams'

const roomsLoading = ref(false)
const schedulesLoading = ref(false)
const submitting = ref(false)
const rooms = ref([])
const schedules = ref([])
const roomDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const roomFormRef = ref(null)
const scheduleFormRef = ref(null)
const isEditRoom = ref(false)
const isEditSchedule = ref(false)

const filterForm = reactive({
  subject: '',
  status: ''
})

const roomForm = reactive({
  id: null,
  name: '',
  address: '',
  capacity: 50,
  is_active: true
})

const scheduleForm = reactive({
  id: null,
  subject: 1,
  exam_room: null,
  exam_date: '',
  start_time: '09:00',
  end_time: '11:00',
  total_quota: 50,
  status: 'open',
  remark: ''
})

const roomRules = {
  name: [{ required: true, message: '请输入考场名称', trigger: 'blur' }],
  address: [{ required: true, message: '请输入考场地址', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容纳人数', trigger: 'blur' }]
}

const scheduleRules = {
  subject: [{ required: true, message: '请选择考试科目', trigger: 'change' }],
  exam_room: [{ required: true, message: '请选择考场', trigger: 'change' }],
  exam_date: [{ required: true, message: '请选择考试日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  total_quota: [{ required: true, message: '请输入总名额', trigger: 'blur' }]
}

const loadRooms = async () => {
  roomsLoading.value = true
  try {
    const res = await getExamRoomList()
    rooms.value = res.results || []
  } catch (e) {
    console.error(e)
  } finally {
    roomsLoading.value = false
  }
}

const loadSchedules = async () => {
  schedulesLoading.value = true
  try {
    const params = {}
    if (filterForm.subject) params.subject = filterForm.subject
    if (filterForm.status) params.status = filterForm.status
    const res = await getExamScheduleList(params)
    schedules.value = res.results || []
  } catch (e) {
    console.error(e)
  } finally {
    schedulesLoading.value = false
  }
}

const resetFilter = () => {
  filterForm.subject = ''
  filterForm.status = ''
  loadSchedules()
}

const handleAddRoom = () => {
  isEditRoom.value = false
  roomForm.id = null
  roomForm.name = ''
  roomForm.address = ''
  roomForm.capacity = 50
  roomForm.is_active = true
  roomDialogVisible.value = true
}

const handleEditRoom = (row) => {
  isEditRoom.value = true
  Object.assign(roomForm, row)
  roomDialogVisible.value = true
}

const handleSaveRoom = async () => {
  if (!roomFormRef.value) return
  await roomFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditRoom.value) {
          await updateExamRoom(roomForm.id, roomForm)
          ElMessage.success('修改成功')
        } else {
          await createExamRoom(roomForm)
          ElMessage.success('创建成功')
        }
        roomDialogVisible.value = false
        loadRooms()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDeleteRoom = (row) => {
  ElMessageBox.confirm(`确定删除考场「${row.name}」吗？`, '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteExamRoom(row.id)
      ElMessage.success('删除成功')
      loadRooms()
    } catch (e) {
      console.error(e)
    }
  })
}

const handleAddSchedule = () => {
  isEditSchedule.value = false
  scheduleForm.id = null
  scheduleForm.subject = 1
  scheduleForm.exam_room = rooms[0]?.id || null
  scheduleForm.exam_date = ''
  scheduleForm.start_time = '09:00'
  scheduleForm.end_time = '11:00'
  scheduleForm.total_quota = 50
  scheduleForm.status = 'open'
  scheduleForm.remark = ''
  scheduleDialogVisible.value = true
}

const handleEditSchedule = (row) => {
  isEditSchedule.value = true
  Object.assign(scheduleForm, row)
  scheduleForm.exam_room = row.exam_room
  scheduleDialogVisible.value = true
}

const handleSaveSchedule = async () => {
  if (!scheduleFormRef.value) return
  await scheduleFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditSchedule.value) {
          await updateExamSchedule(scheduleForm.id, scheduleForm)
          ElMessage.success('修改成功')
        } else {
          await createExamSchedule(scheduleForm)
          ElMessage.success('创建成功')
        }
        scheduleDialogVisible.value = false
        loadSchedules()
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDeleteSchedule = (row) => {
  ElMessageBox.confirm(`确定删除该考试安排吗？`, '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteExamSchedule(row.id)
      ElMessage.success('删除成功')
      loadSchedules()
    } catch (e) {
      console.error(e)
    }
  })
}

const handleLock = async (row) => {
  try {
    await lockExamSchedule(row.id)
    ElMessage.success('已关闭预约')
    loadSchedules()
  } catch (e) {
    console.error(e)
  }
}

const handleUnlock = async (row) => {
  try {
    await unlockExamSchedule(row.id)
    ElMessage.success('已开放预约')
    loadSchedules()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadRooms()
  loadSchedules()
})
</script>
