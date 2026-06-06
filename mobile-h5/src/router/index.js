import { createRouter, createWebHashHistory } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', requiresAuth: true }
  },
  {
    path: '/fee-query',
    name: 'FeeQuery',
    component: () => import('@/views/FeeQuery.vue'),
    meta: { title: '查费', requiresAuth: true }
  },
  {
    path: '/installment',
    name: 'Installment',
    component: () => import('@/views/Installment.vue'),
    meta: { title: '分期还款', requiresAuth: true }
  },
  {
    path: '/booking',
    name: 'Booking',
    component: () => import('@/views/Booking.vue'),
    meta: { title: '自主约课', requiresAuth: true }
  },
  {
    path: '/exam-fee',
    name: 'ExamFee',
    component: () => import('@/views/ExamFee.vue'),
    meta: { title: '补考缴费', requiresAuth: true }
  },
  {
    path: '/hours',
    name: 'Hours',
    component: () => import('@/views/Hours.vue'),
    meta: { title: '我的课时', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '我的', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.title) {
    document.title = to.meta.title
  }
  if (to.meta.requiresAuth && !userStore.token) {
    showToast('请先登录')
    next('/login')
  } else {
    next()
  }
})

export default router
