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
