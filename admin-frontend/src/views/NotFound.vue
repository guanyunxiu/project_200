<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<script setup>
</script>

<style scoped lang="scss">
.not-found {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  
  h1 {
    font-size: 120px;
    margin: 0;
    color: #409EFF;
  }
  
  p {
    font-size: 24px;
    color: #909399;
    margin: 20px 0 30px 0;
  }
}
</style>
