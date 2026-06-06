import request from '@/utils/request'

export function getUserList(params) {
  return request({
    url: '/auth/users/',
    method: 'get',
    params
  })
}

export function getUserDetail(id) {
  return request({
    url: `/auth/users/${id}/`,
    method: 'get'
  })
}

export function createUser(data) {
  return request({
    url: '/auth/users/',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/auth/users/${id}/`,
    method: 'put',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/auth/users/${id}/`,
    method: 'delete'
  })
}

export function getCoachList() {
  return request({
    url: '/auth/users/?role=coach',
    method: 'get'
  })
}
