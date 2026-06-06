import request from '@/utils/request'

export function loginApi(data) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}

export function refreshTokenApi(refresh) {
  return request({
    url: '/auth/refresh/',
    method: 'post',
    data: { refresh }
  })
}

export function getUserInfoApi() {
  return request({
    url: '/auth/me/',
    method: 'get'
  })
}

export function changePasswordApi(data) {
  return request({
    url: '/auth/change_password/',
    method: 'post',
    data
  })
}

export function registerUserApi(data) {
  return request({
    url: '/auth/register/',
    method: 'post',
    data
  })
}
