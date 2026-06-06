import request from '@/utils/request'

export function getExamRoomList(params) {
  return request({
    url: '/exams/rooms/',
    method: 'get',
    params
  })
}

export function createExamRoom(data) {
  return request({
    url: '/exams/rooms/',
    method: 'post',
    data
  })
}

export function updateExamRoom(id, data) {
  return request({
    url: `/exams/rooms/${id}/`,
    method: 'put',
    data
  })
}

export function deleteExamRoom(id) {
  return request({
    url: `/exams/rooms/${id}/`,
    method: 'delete'
  })
}

export function getExamScheduleList(params) {
  return request({
    url: '/exams/schedules/',
    method: 'get',
    params
  })
}

export function getAvailableSchedules() {
  return request({
    url: '/exams/schedules/available_list/',
    method: 'get'
  })
}

export function createExamSchedule(data) {
  return request({
    url: '/exams/schedules/',
    method: 'post',
    data
  })
}

export function updateExamSchedule(id, data) {
  return request({
    url: `/exams/schedules/${id}/`,
    method: 'put',
    data
  })
}

export function deleteExamSchedule(id) {
  return request({
    url: `/exams/schedules/${id}/`,
    method: 'delete'
  })
}

export function lockExamSchedule(id) {
  return request({
    url: `/exams/schedules/${id}/lock_quota/`,
    method: 'post'
  })
}

export function unlockExamSchedule(id) {
  return request({
    url: `/exams/schedules/${id}/unlock_quota/`,
    method: 'post'
  })
}

export function getExamStats() {
  return request({
    url: '/exams/schedules/stats/',
    method: 'get'
  })
}

export function getExamBookingList(params) {
  return request({
    url: '/exams/bookings/',
    method: 'get',
    params
  })
}

export function createExamBooking(data) {
  return request({
    url: '/exams/bookings/',
    method: 'post',
    data
  })
}

export function updateExamBooking(id, data) {
  return request({
    url: `/exams/bookings/${id}/`,
    method: 'put',
    data
  })
}

export function deleteExamBooking(id) {
  return request({
    url: `/exams/bookings/${id}/`,
    method: 'delete'
  })
}

export function approveExamBooking(id) {
  return request({
    url: `/exams/bookings/${id}/approve/`,
    method: 'post'
  })
}

export function markExamAbsent(id) {
  return request({
    url: `/exams/bookings/${id}/mark_absent/`,
    method: 'post'
  })
}

export function markExamResult(id, data) {
  return request({
    url: `/exams/bookings/${id}/mark_result/`,
    method: 'post',
    data
  })
}

export function cancelExamBooking(id) {
  return request({
    url: `/exams/bookings/${id}/cancel/`,
    method: 'post'
  })
}

export function selfBookExam(data) {
  return request({
    url: '/exams/bookings/self_book/',
    method: 'post',
    data
  })
}
