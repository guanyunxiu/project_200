import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'House', roles: ['admin', 'finance', 'coach'] }
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('@/views/students/StudentList.vue'),
        meta: { title: '学员管理', icon: 'User', roles: ['admin', 'coach'] }
      },
      {
        path: 'packages',
        name: 'Packages',
        component: () => import('@/views/packages/PackageList.vue'),
        meta: { title: '套餐管理', icon: 'Goods', roles: ['admin'] }
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/payments/PaymentList.vue'),
        meta: { title: '缴费管理', icon: 'Wallet', roles: ['admin', 'finance'] }
      },
      {
        path: 'payments/new',
        name: 'PaymentNew',
        component: () => import('@/views/payments/PaymentNew.vue'),
        meta: { title: '新增缴费', icon: 'Wallet', roles: ['admin', 'finance'], hidden: true }
      },
      {
        path: 'installments',
        name: 'Installments',
        component: () => import('@/views/payments/InstallmentList.vue'),
        meta: { title: '分期管理', icon: 'Calendar', roles: ['admin', 'finance'] }
      },
      {
        path: 'exams',
        name: 'Exams',
        component: () => import('@/views/exams/ExamList.vue'),
        meta: { title: '约考管理', icon: 'Calendar', roles: ['admin', 'coach'] }
      },
      {
        path: 'exams/schedule',
        name: 'ExamSchedule',
        component: () => import('@/views/exams/ExamSchedule.vue'),
        meta: { title: '考试安排', icon: 'Setting', roles: ['admin'] }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/UserList.vue'),
        meta: { title: '用户管理', icon: 'UserFilled', roles: ['admin'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  document.title = to.meta.title ? `${to.meta.title} - 驾校管理系统` : '驾校管理系统'
  
  if (to.meta.requiresAuth) {
    if (!userStore.token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else {
      if (to.meta.roles && !to.meta.roles.includes(userStore.userInfo?.role)) {
        next('/dashboard')
      } else {
        next()
      }
    }
  } else {
    if (to.path === '/login' && userStore.token) {
      next('/')
    } else {
      next()
    }
  }
})

export default router
