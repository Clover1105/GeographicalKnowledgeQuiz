<template>
  <div>
    <h1>注册页面</h1>
  </div>
  <div>
    <form>
      <table>
        <tbody>
          <tr>
            <td>用户名：</td>
            <td><input type="text" v-model="username"></td>
          </tr>
          <tr>
            <td>邮箱号：</td>
            <td><input type="text" v-model="email"></td>
          </tr>
          <tr>
            <td>密码：</td>
            <td><input type="password" v-model="password"></td>
          </tr>
          <tr>
            <td>确认密码：</td>
            <td><input type="password" v-model="confirmPassword"></td>
          </tr>
        </tbody>
      </table>
    </form>
  </div>

  <div>
    <button @click="goLogin">返回登陆页面</button>
    <button @click="signUp">注册</button>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";

let router = useRouter();
let proxy = getCurrentInstance().proxy;

let username = ref('')
let email = ref('')
let password = ref('')
let confirmPassword = ref('')

function goLogin(){
  router.push('/login');
}


// 注册账号
function signUp(){
  // 验证两次密码是否一致
  if(password.value !== confirmPassword.value){
    ElMessage.error('两次密码不一致');
    return {
      "code": 500,
      "msg": "两次密码不一致"
    }
  }

  // 创建用户信息对象
  let userInformation = {
    username: username.value,
    email: email.value,
    password: password.value
  }
  proxy.$axios({
    url: '/users/signup',
    method: 'post',
    data: userInformation
  }).then(res => {
    console.log(res.data);
    let code = res.data.code;
    if(code === 200){
      ElMessage.success('注册成功');
      router.push('/login');
    }else{
      ElMessage.error('注册失败');
    }
  })
}

</script>

<style scoped>
</style>