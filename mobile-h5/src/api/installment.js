import request from '@/utils/request'

export const getInstallmentListApi = (params = {}) => {
  return request({
    url: '/payments/installments/',
    method: 'get',
    params
  })
}

export const getInstallmentDetailApi = (id) => {
  return request({
    url: `/payments/installments/${id}/`,
    method: 'get'
  })
}

export const payInstallmentPeriodApi = (id, period, paymentMethod = 'wechat') => {
  return request({
    url: `/payments/installments/${id}/pay_period/`,
    method: 'post',
    data: { period, payment_method: paymentMethod }
  })
}

export const getOverdueInstallmentApi = () => {
  return request({
    url: '/payments/installments/overdue_list/',
    method: 'get'
  })
}
