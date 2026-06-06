import request from '@/utils/request'

export const getExamScheduleListApi = (params = {}) => {
  return request({
    url: '/exams/schedules/',
    method: 'get',
    params
  })
}

export const getAvailableSchedulesApi = () => {
  return request({
    url: '/exams/schedules/available_list/',
    method: 'get'
  })
}

export const getExamBookingListApi = (params = {}) => {
  return request({
    url: '/exams/bookings/',
    method: 'get',
    params
  })
}

export const selfBookExamApi = (data) => {
  return request({
    url: '/exams/bookings/self_book/',
    method: 'post',
    data
  })
}

export const cancelExamBookingApi = (id) => {
  return request({
    url: `/exams/bookings/${id}/cancel/`,
    method: 'post'
  })
}

export const getExamFeeListApi = (params = {}) => {
  return request({
    url: '/exams/fees/',
    method: 'get',
    params
  })
}

export const getUnpaidExamFeesApi = (studentId) => {
  return request({
    url: '/exams/fees/unpaid_by_student/',
    method: 'get',
    params: { student_id: studentId }
  })
}

export const payExamFeeApi = (id, paymentMethod = 'wechat') => {
  return request({
    url: `/exams/fees/${id}/pay/`,
    method: 'post',
    data: { payment_method: paymentMethod }
  })
}

export const checkExamBookingPermissionApi = (studentId, subject) => {
  return request({
    url: '/exams/fees/check_booking_permission/',
    method: 'post',
    data: { student_id: studentId, subject }
  })
}
