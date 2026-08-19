<template>
  <div>
    <h1>欢迎来到地理知识问答系统</h1>
  </div>
  <div>
    <button @click="goLogin">进入系统 ==> 去登陆/注册</button>
  </div>
</template>

<script setup>
import {useRouter} from "vue-router";

function goLogin() {
  router.push('/login');
}

// 创建路由跳转对象
let router = useRouter();
</script>

<style scoped>
</style>
