<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="28"><Van /></el-icon>
        <span>驾校管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#1f2d3d"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item :index="'/' + route.path" v-if="!route.meta.hidden && checkRole(route.meta.roles)">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <span>{{ route.meta.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="user-info">
          <el-dropdown @command="handleCommand">
            <span class="user-name">
              <el-icon><UserFilled /></el-icon>
              {{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
              <el-tag size="small" :type="getRoleTagType(userStore.userInfo?.role)">
                {{ getRoleName(userStore.userInfo?.role) }}
              </el-tag>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
    <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
      <el-form-item label="原密码" prop="old_password">
        <el-input v-model="passwordForm.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="passwordForm.new_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closePasswordDialog">取消</el-button>
      <el-button type="primary" @click="handleChangePassword">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Van } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { changePasswordApi } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const passwordFormRef = ref(null)
const passwordDialogVisible = ref(false)

const activeMenu = computed(() => route.path)
const menuRoutes = computed(() => router.options.routes.find(r => r.path === '/')?.children || [])

const passwordForm = reactive({
  old_password: '',
  new_password: ''
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, min: 6, message: '密码长度至少6位', trigger: 'blur' }]
}

const checkRole = (roles) => {
  if (!roles) return true
  return roles.includes(userStore.userInfo?.role)
}

const getRoleName = (role) => {
  const roles = { admin: '管理员', finance: '财务', coach: '教练' }
  return roles[role] || role
}

const getRoleTagType = (role) => {
  const types = { admin: 'danger', finance: 'warning', coach: 'success' }
  return types[role] || 'info'
}

const closePasswordDialog = () => {
  passwordDialogVisible.value = false
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    })
  } else if (command === 'password') {
    passwordDialogVisible.value = true
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await changePasswordApi(passwordForm)
        ElMessage.success('密码修改成功')
        passwordDialogVisible.value = false
        passwordForm.old_password = ''
        passwordForm.new_password = ''
      } catch (e) {
        console.error(e)
      }
    }
  })
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #1f2d3d;
  overflow-y: auto;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid #2d4054;
    
    span {
      margin-left: 10px;
    }
  }
  
  .el-menu {
    border-right: none;
  }
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .user-info {
    .user-name {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .el-icon {
        margin-right: 5px;
      }
      
      .el-tag {
        margin-left: 10px;
      }
    }
  }
}

.main-content {
  background: #f0f2f5;
  overflow-y: auto;
}
</style>
