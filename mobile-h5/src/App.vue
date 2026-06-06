<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
</script>

<style>
#app {
  width: 100%;
  min-height: 100%;
  padding-bottom: 50px;
}
</style>
