import request from '@/utils/request'

export function getPackageList(params) {
  return request({
    url: '/packages/',
    method: 'get',
    params
  })
}

export function getActivePackages() {
  return request({
    url: '/packages/active_list/',
    method: 'get'
  })
}

export function getPackageDetail(id) {
  return request({
    url: `/packages/${id}/`,
    method: 'get'
  })
}

export function createPackage(data) {
  return request({
    url: '/packages/',
    method: 'post',
    data
  })
}

export function updatePackage(id, data) {
  return request({
    url: `/packages/${id}/`,
    method: 'put',
    data
  })
}

export function deletePackage(id) {
  return request({
    url: `/packages/${id}/`,
    method: 'delete'
  })
}
