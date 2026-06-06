import request from '@/utils/request'

export const getStudentListApi = (params = {}) => {
  return request({
    url: '/students/',
    method: 'get',
    params
  })
}

export const getStudentDetailApi = (id) => {
  return request({
    url: `/students/${id}/`,
    method: 'get'
  })
}

export const getStudentHoursApi = (id) => {
  return request({
    url: `/students/${id}/hours_cache/`,
    method: 'get'
  })
}

export const updateStudentHoursApi = (id, hours, operation = 'add') => {
  return request({
    url: `/students/${id}/update_hours/`,
    method: 'post',
    data: { hours, operation }
  })
}
