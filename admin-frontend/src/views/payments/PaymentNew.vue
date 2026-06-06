<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">新增缴费</div>
      <el-button @click="$router.push('/payments')">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
    </div>

    <div class="form-container">
      <el-card>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
          <el-form-item label="选择学员" prop="student">
            <el-select
              v-model="form.student"
              filterable
              placeholder="请选择学员"
              style="width: 100%;"
              @change="onStudentChange"
            >
              <el-option
                v-for="s in students"
                :key="s.id"
                :label="`${s.name} - ${s.phone} - ${s.license_type_display}`"
                :value="s.id"
              />
            </el-select>
          </el-form-item>

          <div v-if="selectedStudent" class="student-info">
            <el-descriptions :column="3" border size="small">
              <el-descriptions-item label="姓名">{{ selectedStudent.name }}</el-descriptions-item>
              <el-descriptions-item label="手机号">{{ selectedStudent.phone }}</el-descriptions-item>
              <el-descriptions-item label="驾照类型">{{ selectedStudent.license_type_display }}</el-descriptions-item>
              <el-descriptions-item label="报名套餐">{{ selectedStudent.package_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="总学费">¥{{ selectedStudent.package?.base_price || 0 }}</el-descriptions-item>
              <el-descriptions-item label="已缴学费">¥{{ paidAmount }}</el-descriptions-item>
              <el-descriptions-item label="待缴学费" :span="3">
                <b style="color: #F56C6C; font-size: 18px;">¥{{ remainingAmount }}</b>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <el-form-item label="缴费类型" prop="payment_type">
            <el-radio-group v-model="form.payment_type">
              <el-radio value="full">一次性全款</el-radio>
              <el-radio value="down">首付</el-radio>
              <el-radio value="installment">分期还款</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="分期期次" prop="installment_no" v-if="form.payment_type === 'installment'">
            <el-input-number v-model="form.installment_no" :min="1" style="width: 200px;" />
          </el-form-item>

          <el-form-item label="支付方式" prop="payment_method">
            <el-select v-model="form.payment_method" style="width: 200px;">
              <el-option label="现金" value="cash" />
              <el-option label="微信" value="wechat" />
              <el-option label="支付宝" value="alipay" />
              <el-option label="银行转账" value="bank" />
              <el-option label="刷卡" value="card" />
            </el-select>
          </el-form-item>

          <el-form-item label="缴费金额" prop="amount">
            <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 200px;" />
            <el-button type="text" @click="autoFillAmount" style="margin-left: 10px;">
              自动填充剩余金额
            </el-button>
          </el-form-item>

          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="3" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">确认缴费</el-button>
            <el-button @click="$router.push('/payments')">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getStudentSimpleList } from '@/api/students'
import { getPaymentList, createPayment } from '@/api/payments'
import { getActivePackages } from '@/api/packages'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const students = ref([])
const packages = ref([])
const studentPayments = ref([])

const form = reactive({
  student: null,
  package: null,
  payment_type: 'full',
  payment_method: 'wechat',
  amount: 0,
  total_amount: 0,
  remaining_amount: 0,
  installment_no: 0,
  remark: ''
})

const rules = {
  student: [{ required: true, message: '请选择学员', trigger: 'change' }],
  payment_type: [{ required: true, message: '请选择缴费类型', trigger: 'change' }],
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }],
  amount: [{ required: true, message: '请输入缴费金额', trigger: 'blur' }]
}

const selectedStudent = computed(() => {
  return students.value.find(s => s.id === form.student)
})

const paidAmount = computed(() => {
  return studentPayments.value
    .filter(p => p.status === 'confirmed')
    .reduce((sum, p) => sum + Number(p.amount), 0)
})

const remainingAmount = computed(() => {
  const total = selectedStudent.value?.package?.base_price || 0
  return Math.max(0, total - paidAmount.value)
})

const loadStudents = async () => {
  try {
    const res = await getStudentSimpleList()
    students.value = res
  } catch (e) {
    console.error(e)
  }
}

const loadPackages = async () => {
  try {
    const res = await getActivePackages()
    packages.value = res
  } catch (e) {
    console.error(e)
  }
}

const loadStudentPayments = async (studentId) => {
  try {
    const res = await getPaymentList({ student_id: studentId, page_size: 100 })
    studentPayments.value = res.results || []
  } catch (e) {
    console.error(e)
  }
}

const onStudentChange = (studentId) => {
  if (studentId) {
    loadStudentPayments(studentId)
    const student = students.value.find(s => s.id === studentId)
    if (student?.package_id) {
      form.package = student.package_id
      const pkg = packages.value.find(p => p.id === student.package_id)
      if (pkg) {
        form.total_amount = Number(pkg.base_price)
      }
    }
  }
}

const autoFillAmount = () => {
  form.amount = remainingAmount.value
  form.remaining_amount = 0
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        form.remaining_amount = Math.max(0, form.total_amount - paidAmount.value - form.amount)
        await createPayment(form)
        ElMessage.success('缴费成功')
        router.push('/payments')
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadStudents()
  loadPackages()
})
</script>

<style scoped lang="scss">
.student-info {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 5px;
}
</style>
