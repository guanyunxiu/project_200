import request from '@/utils/request'

export const loginApi = (username, password) => {
  return request({
    url: '/auth/login',
    method: 'post',
    data: { username, password }
  })
}

export const refreshTokenApi = (refresh) => {
  return request({
    url: '/auth/refresh',
    method: 'post',
    data: { refresh }
  })
}

export const getCurrentUserApi = () => {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}

export const changePasswordApi = (oldPassword, newPassword) => {
  return request({
    url: '/auth/change_password',
    method: 'post',
    data: { old_password: oldPassword, new_password: newPassword }
  })
}
