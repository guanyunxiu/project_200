import request from '@/utils/request'

export const getStudentHoursApi = (id) => {
  return request({
    url: `/students/${id}/hours_cache/`,
    method: 'get'
  })
}

export const getStudentHourRecordsApi = (id) => {
  return request({
    url: `/students/${id}/hour_records/`,
    method: 'get'
  })
}

export const getHourRecordListApi = (params = {}) => {
  return request({
    url: '/students/hours/',
    method: 'get',
    params
  })
}

export const renewCourseApi = (data) => {
  return request({
    url: '/students/hours/renew_course/',
    method: 'post',
    data
  })
}
