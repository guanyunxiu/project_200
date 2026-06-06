import request from '@/utils/request'

export function getPaymentList(params) {
  return request({
    url: '/payments/',
    method: 'get',
    params
  })
}

export function getPaymentDetail(id) {
  return request({
    url: `/payments/${id}/`,
    method: 'get'
  })
}

export function createPayment(data) {
  return request({
    url: '/payments/',
    method: 'post',
    data
  })
}

export function updatePayment(id, data) {
  return request({
    url: `/payments/${id}/`,
    method: 'put',
    data
  })
}

export function deletePayment(id) {
  return request({
    url: `/payments/${id}/`,
    method: 'delete'
  })
}

export function exportPayments(params) {
  return request({
    url: '/payments/export_excel/',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

export function getPaymentStats() {
  return request({
    url: '/payments/stats/',
    method: 'get'
  })
}

export function getPaymentSummary() {
  return request({
    url: '/payments/student_summary/',
    method: 'get'
  })
}

export function getInstallmentList(params) {
  return request({
    url: '/payments/installments/',
    method: 'get',
    params
  })
}

export function createInstallment(data) {
  return request({
    url: '/payments/installments/',
    method: 'post',
    data
  })
}

export function payInstallment(id, data) {
  return request({
    url: `/payments/installments/${id}/pay_period/`,
    method: 'post',
    data
  })
}

export function getOverdueInstallments() {
  return request({
    url: '/payments/installments/overdue_list/',
    method: 'get'
  })
}

export function getArrearsLedger() {
  return request({
    url: '/payments/installments/arrears_ledger/',
    method: 'get'
  })
}

export function calculateLateFees(id) {
  return request({
    url: `/payments/installments/${id}/calculate_late_fees/`,
    method: 'post'
  })
}

export function getInstallmentSchemeList(params) {
  return request({
    url: '/payments/schemes/',
    method: 'get',
    params
  })
}

export function createInstallmentScheme(data) {
  return request({
    url: '/payments/schemes/',
    method: 'post',
    data
  })
}

export function updateInstallmentScheme(id, data) {
  return request({
    url: `/payments/schemes/${id}/`,
    method: 'put',
    data
  })
}

export function deleteInstallmentScheme(id) {
  return request({
    url: `/payments/schemes/${id}/`,
    method: 'delete'
  })
}

export function getActiveInstallmentSchemes() {
  return request({
    url: '/payments/schemes/active_list/',
    method: 'get'
  })
}

export function getPaymentReminderList(params) {
  return request({
    url: '/payments/reminders/',
    method: 'get',
    params
  })
}

export function createPaymentReminder(data) {
  return request({
    url: '/payments/reminders/',
    method: 'post',
    data
  })
}

export function updatePaymentReminder(id, data) {
  return request({
    url: `/payments/reminders/${id}/`,
    method: 'put',
    data
  })
}

export function deletePaymentReminder(id) {
  return request({
    url: `/payments/reminders/${id}/`,
    method: 'delete'
  })
}

export function getFinancialStatsSummary(params) {
  return request({
    url: '/payments/stats/summary/',
    method: 'get',
    params
  })
}

export function getRevenueByPackage(params) {
  return request({
    url: '/payments/stats/revenue_by_package/',
    method: 'get',
    params
  })
}

export function getInstallmentRevenue(params) {
  return request({
    url: '/payments/stats/installment_revenue/',
    method: 'get',
    params
  })
}

export function getExamFeeRevenue(params) {
  return request({
    url: '/payments/stats/exam_fee_revenue/',
    method: 'get',
    params
  })
}

export function getCourseRenewalRevenue(params) {
  return request({
    url: '/payments/stats/course_renewal_revenue/',
    method: 'get',
    params
  })
}

export function getMonthlyTrend(params) {
  return request({
    url: '/payments/stats/monthly_trend/',
    method: 'get',
    params
  })
}
