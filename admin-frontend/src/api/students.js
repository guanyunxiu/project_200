import request from '@/utils/request'

export function getStudentList(params) {
  return request({
    url: '/students/',
    method: 'get',
    params
  })
}

export function getStudentSimpleList() {
  return request({
    url: '/students/simple_list/',
    method: 'get'
  })
}

export function getStudentDetail(id) {
  return request({
    url: `/students/${id}/`,
    method: 'get'
  })
}

export function createStudent(data) {
  return request({
    url: '/students/',
    method: 'post',
    data
  })
}

export function updateStudent(id, data) {
  return request({
    url: `/students/${id}/`,
    method: 'put',
    data
  })
}

export function deleteStudent(id) {
  return request({
    url: `/students/${id}/`,
    method: 'delete'
  })
}

export function getStudentStats() {
  return request({
    url: '/students/stats/',
    method: 'get'
  })
}

export function getStudentHours(id) {
  return request({
    url: `/students/${id}/hours_cache/`,
    method: 'get'
  })
}

export function updateStudentHours(id, data) {
  return request({
    url: `/students/${id}/update_hours/`,
    method: 'post',
    data
  })
}

export function bindCoach(id, coachId) {
  return request({
    url: `/students/${id}/bind_coach/`,
    method: 'post',
    data: { coach_id: coachId }
  })
}
