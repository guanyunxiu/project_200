<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title">缴费管理</div>
      <div>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon> 导出Excel
        </el-button>
        <el-button type="primary" @click="$router.push('/payments/new')">
          <el-icon><Plus /></el-icon> 新增缴费
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="学员">
          <el-input v-model="filterForm.student_name" placeholder="姓名/手机号" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="缴费类型">
          <el-select v-model="filterForm.payment_type" placeholder="全部" clearable style="width: 150px;">
            <el-option label="一次性全款" value="full" />
            <el-option label="首付" value="down" />
            <el-option label="分期还款" value="installment" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="filterForm.payment_method" placeholder="全部" clearable style="width: 150px;">
            <el-option label="现金" value="cash" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行转账" value="bank" />
            <el-option label="刷卡" value="card" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px;">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="缴费日期">
          <el-date-picker
            v-model="filterForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
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
        <el-table-column prop="receipt_no" label="凭证号" width="180" />
        <el-table-column prop="student_name" label="学员姓名" width="100" />
        <el-table-column prop="student_phone" label="手机号" width="130" />
        <el-table-column prop="package_name" label="套餐" width="150" />
        <el-table-column prop="payment_type_display" label="缴费类型" width="110" />
        <el-table-column prop="payment_method_display" label="支付方式" width="100" />
        <el-table-column prop="amount" label="缴费金额" width="120">
          <template #default="{ row }"><b style="color: #F56C6C;">¥{{ row.amount }}</b></template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余未缴" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.remaining_amount > 0 ? '#F56C6C' : '#67C23A' }">
              ¥{{ row.remaining_amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'confirmed' ? 'success' : row.status === 'pending' ? 'warning' : 'info'">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="经办人" width="90" />
        <el-table-column prop="paid_at" label="缴费时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleView(row)">详情</el-button>
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

  <el-dialog v-model="detailVisible" title="缴费详情" width="600px">
    <el-descriptions :column="2" border v-if="currentDetail">
      <el-descriptions-item label="凭证号">{{ currentDetail.receipt_no }}</el-descriptions-item>
      <el-descriptions-item label="学员">{{ currentDetail.student_name }}</el-descriptions-item>
      <el-descriptions-item label="手机号">{{ currentDetail.student_phone }}</el-descriptions-item>
      <el-descriptions-item label="套餐">{{ currentDetail.package_name }}</el-descriptions-item>
      <el-descriptions-item label="缴费类型">{{ currentDetail.payment_type_display }}</el-descriptions-item>
      <el-descriptions-item label="支付方式">{{ currentDetail.payment_method_display }}</el-descriptions-item>
      <el-descriptions-item label="缴费金额">
        <b style="color: #F56C6C;">¥{{ currentDetail.amount }}</b>
      </el-descriptions-item>
      <el-descriptions-item label="总金额">¥{{ currentDetail.total_amount }}</el-descriptions-item>
      <el-descriptions-item label="剩余未缴">
        <span :style="{ color: currentDetail.remaining_amount > 0 ? '#F56C6C' : '#67C23A' }">
          ¥{{ currentDetail.remaining_amount }}
        </span>
      </el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="currentDetail.status === 'confirmed' ? 'success' : 'warning'">
          {{ currentDetail.status_display }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="经办人">{{ currentDetail.operator_name || '-' }}</el-descriptions-item>
      <el-descriptions-item label="缴费时间">{{ currentDetail.paid_at }}</el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">{{ currentDetail.remark || '-' }}</el-descriptions-item>
    </el-descriptions>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { getPaymentList, exportPayments } from '@/api/payments'

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const currentDetail = ref(null)

const filterForm = reactive({
  student_name: '',
  payment_type: '',
  payment_method: '',
  status: '',
  date_range: []
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filterForm.payment_type) params.payment_type = filterForm.payment_type
    if (filterForm.payment_method) params.payment_method = filterForm.payment_method
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.date_range?.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }
    const res = await getPaymentList(params)
    tableData.value = res.results || []
    pagination.total = res.count || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.student_name = ''
  filterForm.payment_type = ''
  filterForm.payment_method = ''
  filterForm.status = ''
  filterForm.date_range = []
  pagination.page = 1
  loadData()
}

const handleView = (row) => {
  currentDetail.value = row
  detailVisible.value = true
}

const handleExport = async () => {
  try {
    const params = {}
    if (filterForm.payment_type) params.payment_type = filterForm.payment_type
    if (filterForm.payment_method) params.payment_method = filterForm.payment_method
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.date_range?.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }
    const blob = await exportPayments(params)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `payments_${Date.now()}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('导出成功')
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
})
</script>
