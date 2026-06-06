import request from '@/utils/request'

export const getPaymentListApi = (params = {}) => {
  return request({
    url: '/payments/',
    method: 'get',
    params
  })
}

export const getPaymentDetailApi = (id) => {
  return request({
    url: `/payments/${id}/`,
    method: 'get'
  })
}

export const getStudentPaymentSummaryApi = () => {
  return request({
    url: '/payments/student_summary/',
    method: 'get'
  })
}

export const createPaymentApi = (data) => {
  return request({
    url: '/payments/',
    method: 'post',
    data
  })
}
