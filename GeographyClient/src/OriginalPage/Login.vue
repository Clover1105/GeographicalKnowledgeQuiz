<template>
  <div>
    <h1>请选择邮箱或者验证码登陆</h1>
    <!-- 无论是邮箱还是密码登陆都要发送验证码验证-->
    <button @click="loginChange" :disabled="!isDisabled" v-show="method">用户名登陆</button>
    <button @click="loginChange" :disabled="isDisabled" v-show="method">邮箱登陆</button>
  </div>

  <div>
    <form>
      <table>
        <tbody>
          <tr  v-show="!isShow">
            <td>用户名：</td>
            <td><input type="text" v-model="username"  :disabled="isAvailable"></td>
          </tr>
          <tr v-show="isShow">
            <td>邮箱号：</td>
            <td><input type="text" v-model="email"  :disabled="isAvailable"></td>
          </tr>
          <tr>
            <td>密码：</td>
            <td><input type="password" v-model="password"  :disabled="isAvailable"></td>
          </tr>
          <tr>
            <td>验证码：</td>
            <td><input type="text" v-model="captcha"></td>
          </tr>
        </tbody>
      </table>
    </form>
  </div>
  <div>
    <button @click="goSignUp">注册</button>
    <button v-show="!iscaptcha" @click="goChat" :disabled="captcha.length === 0">登陆</button>
    <button v-show="iscaptcha" @click="captchaEmail">发送验证码</button>
  </div>


</template>

<script setup>
import {ref, getCurrentInstance} from "vue";
import {useRouter} from "vue-router"
import {ElMessage} from "element-plus";

// 创建路由跳转对象
function goSignUp(){
  router.push('/signup');
}
let router = useRouter();

// 登陆方式切换
let isDisabled = ref(true)
let isShow = ref(true)
function loginChange(){
  username.value = ''
  email.value = ''
  password.value = ''
  captcha.value = ''
  isAvailable.value = false
  isDisabled.value = !isDisabled.value
  isShow.value = !isShow.value
}

// 创建当前实例对象 -- 通过这个对象才可以访问到 main.js 中定义的 $axios 变量
let proxy = getCurrentInstance().proxy
console.log(getCurrentInstance())

// 登陆验证
let username = ref('')
let email = ref('')
let password = ref('')
let captcha = ref('')
let iscaptcha = ref(true)
let method = ref(true)
let isAvailable = ref(false)

// 判断登陆方式
function loginMethod(){
  if (isShow.value) {
    // 邮箱登录模式：只传 email，username留空
    return {
      username:'',
      email:email.value,
      password:password.value
    }
  } else {
    // 用户名登录模式：只传 username，email留空
    return {
      username:username.value,
      email:'',
      password:password.value
    }
  }
}

// 发送验证码邮件函数 -- 向服务器发送请求，验证用户信息
function captchaEmail(){
  console.log("开始验证用户信息：")
  let userInformation = loginMethod()
    proxy.$axios({
    url:'users/captchaEmail',
    method:'post',
    data:userInformation
  }).then(res=>{
    console.log("邮件的发送结果：", res.data)
    let code = res.data.code
    let message = res.data.msg
    if(code === 200){
      method.value = false
      iscaptcha.value = !iscaptcha.value
      ElMessage.info(message)
    } else {
      ElMessage.error(message)
    }
  })
  isAvailable.value = true
}

// 验证验证码是否正确
function goChat(){
  console.log("开始验证验证码是否正确：")
  let userInformation = {
    username:username.value,
    email:email.value,
    password:password.value,
    captcha:captcha.value
  }
  proxy.$axios({
    url:'users/verifyCaptcha',
    method:'post',
    data:userInformation
  }).then(res => {
    console.log("验证的返回结果：", res.data)
    let code = res.data.code
    let message = res.data.msg
    let data = res.data.data
    if(code === 200){
      sessionStorage.setItem("username", data);
      ElMessage.success(message)
      setTimeout(() =>{
        router.push('/chat')
      },1000)
    } else {
      ElMessage.error(message)
    }
  })
}
</script>

<style scoped>

</style>