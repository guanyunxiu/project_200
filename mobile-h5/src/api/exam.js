import request from '@/utils/request'

export const getExamRoomListApi = (params = {}) => {
  return request({
    url: '/exams/rooms/',
    method: 'get',
    params
  })
}

export const getExamScheduleListApi = (params = {}) => {
  return request({
    url: '/exams/schedules/',
    method: 'get',
    params
  })
}

export const getAvailableSchedulesApi = (params = {}) => {
  return request({
    url: '/exams/schedules/available_list/',
    method: 'get',
    params
  })
}

export const getScheduleQuotaApi = (id) => {
  return request({
    url: `/exams/schedules/${id}/quota_cache/`,
    method: 'get'
  })
}

export const getBookingListApi = (params = {}) => {
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

export const cancelBookingApi = (id) => {
  return request({
    url: `/exams/bookings/${id}/cancel/`,
    method: 'post'
  })
}
