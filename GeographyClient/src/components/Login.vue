<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration bg-circle-1"></div>
    <div class="bg-decoration bg-circle-2"></div>

    <div class="login-card">
      <h1 class="page-title">登陆页面</h1>

      <!-- 登录方式切换按钮组 -->
      <div class="method-switch" v-show="method">
        <button
          class="switch-btn"
          :class="{ active: !isDisabled }"
          @click="loginChange"
          :disabled="!isDisabled"
        >
          用户名登陆
        </button>
        <button
          class="switch-btn"
          :class="{ active: isDisabled }"
          @click="loginChange"
          :disabled="isDisabled"
        >
          邮箱登陆
        </button>
      </div>

      <!-- 表单区域 -->
      <form class="login-form" @submit.prevent>
        <div class="form-item" v-show="!isShow">
          <label class="form-label">用户名</label>
          <input
            type="text"
            v-model="username"
            placeholder="请输入用户名"
            class="form-input"
          />
        </div>

        <div class="form-item" v-show="isShow">
          <label class="form-label">邮箱号</label>
          <input
            type="text"
            v-model="email"
            :disabled="isAvailable"
            placeholder="请输入邮箱地址"
            class="form-input"
          />
        </div>

        <div class="form-item" v-show="!isShow">
          <label class="form-label">密码</label>
          <input
            type="password"
            v-model="password"
            placeholder="请输入密码"
            class="form-input"
          />
        </div>

        <div class="form-item" v-show="isShow">
          <label class="form-label">验证码</label>
          <input
            type="text"
            v-model="captcha"
            placeholder="请输入验证码"
            class="form-input captcha-input"
          />
        </div>
      </form>

      <!-- 操作按钮区 -->
      <div class="action-area">
        <button class="btn-secondary" @click="goSignUp">注册</button>

        <button
          v-show="!isShow || (isShow && !iscaptcha)"
          class="btn-primary"
          @click="goChat"
          :disabled="password.length === 0 && captcha.length === 0"
        >
          登陆
        </button>

        <button
          v-show="isShow && iscaptcha"
          class="btn-primary btn-captcha"
          @click="captchaEmail"
        >
          发送验证码
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

// 创建路由跳转对象
function goSignUp() {
  router.push("/signup");
}
let router = useRouter();

// 登陆方式切换
let isDisabled = ref(true);
let isShow = ref(true);
function loginChange() {
  username.value = "";
  email.value = "";
  password.value = "";
  captcha.value = "";
  isAvailable.value = false;
  isDisabled.value = !isDisabled.value;
  isShow.value = !isShow.value;
}

// 创建当前实例对象 -- 通过这个对象才可以访问到 main.js 中定义的 $axios 变量
let proxy = getCurrentInstance().proxy;
console.log(getCurrentInstance());

// 登陆验证
let username = ref("");
let email = ref("");
let password = ref("");
let captcha = ref("");
let iscaptcha = ref(true);
let method = ref(true);
let isAvailable = ref(false);

// 判断登陆方式
function loginMethod() {
  if (isShow.value) {
    // 邮箱登录模式：只传 email，则username和password留空
    return {
      username: "",
      email: email.value,
      password: "",
    };
  } else {
    // 用户名登录模式：只传 username，则email留空
    return {
      username: username.value,
      email: "",
      password: password.value,
    };
  }
}

// 邮箱登录模式：发送验证码邮件函数 -- 向服务器发送请求，验证用户信息
function captchaEmail() {
  console.log("开始验证用户信息：");
  let userInformation = loginMethod();
  proxy
    .$axios({
      url: "users/captchaEmail",
      method: "post",
      data: userInformation,
    })
    .then((res) => {
      console.log("邮件的发送结果：", res.data);
      let code = res.data.code;
      let message = res.data.msg;
      if (code === 200) {
        method.value = false;
        iscaptcha.value = !iscaptcha.value;
        ElMessage.info(message);
      } else {
        ElMessage.error(message);
      }
    });
  isAvailable.value = true;
}

function goChat(){
  if (!isShow.value) {
    // 用户名模式：直接用户名+密码登录
    loginByUsername();
  } else {
    // 邮箱模式：验证验证码
    loginByEmail();
  }
}

// 用户名模式：直接用户名+密码登录
function loginByUsername() {
  console.log("开始验证密码是否正确：");
  let userInformation = loginMethod();  // 用户名+密码
  proxy
    .$axios({
      url: "users/verifyPassword",
      method: "post",
      data: userInformation,
    })
    .then((res) => {
      console.log("登录的返回结果：", res.data);
      let code = res.data.code;
      let message = res.data.msg;
      let data = res.data.data;
      if (code === 200) {
        sessionStorage.setItem("username", data.username);
        sessionStorage.setItem("token", data.token);
        ElMessage.success(message);
        setTimeout(() => {
          router.push("/chat");
        }, 1000);
      } else {
        ElMessage.error(message);
      }
    });
}

// 邮箱模式：验证验证码
function loginByEmail() {
  console.log("开始验证验证码是否正确：");
  let userInformation = {
    email: email.value,
    captcha: captcha.value,
  };
  proxy
    .$axios({
      url: "users/verifyCaptcha",
      method: "post",
      data: userInformation,
    })
    .then((res) => {
      console.log("验证的返回结果：", res.data);
      let code = res.data.code;
      let message = res.data.msg;
      let data = res.data.data;
      if (code === 200) {
        sessionStorage.setItem("username", data.username);
        sessionStorage.setItem("token", data.token);
        ElMessage.success(message);
        setTimeout(() => {
          router.push("/chat");
        }, 1000);
      } else {
        ElMessage.error(message);
      }
    });
}
</script>

<style scoped>
/* ========== 页面容器 & 背景 ========== */
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 50%, #ecfeff 100%);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', sans-serif;
  padding: 20px;
}

.bg-decoration {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  pointer-events: none;
}

.bg-circle-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #0ea5e9, transparent 70%);
  top: -200px;
  right: -150px;
  animation: float 8s ease-in-out infinite;
}

.bg-circle-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #10b981, transparent 70%);
  bottom: -100px;
  left: -100px;
  animation: float 10s ease-in-out infinite reverse;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(30px, -20px) scale(1.05);
  }
}

/* ========== 卡片 ========== */
.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
  padding: 44px 40px 36px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 20px 50px -12px rgba(14, 165, 233, 0.15);
  animation: cardEnter 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(30px);
}

@keyframes cardEnter {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========== 标题 ========== */
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin: 0 0 28px 0;
  letter-spacing: 0.5px;
}

/* ========== 登录方式切换 ========== */
.method-switch {
  display: flex;
  gap: 10px;
  margin-bottom: 28px;
  background: #f1f5f9;
  border-radius: 12px;
  padding: 4px;
}

.switch-btn {
  flex: 1;
  padding: 10px 0;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #64748b;
  background: transparent;
}

.switch-btn.active {
  color: white;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.switch-btn:disabled {
  cursor: default;
  opacity: 1;
}

.switch-btn:not(.active):not(:disabled):hover {
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.08);
}

/* ========== 表单 ========== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 28px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  padding-left: 2px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  color: #0f172a;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  outline: none;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #94a3b8;
}

.form-input:focus {
  border-color: #0ea5e9;
  background: white;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f1f5f9;
}

.captcha-input {
  letter-spacing: 4px;
  font-weight: 600;
}

/* ========== 操作按钮 ========== */
.action-area {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 14px 0;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: 1px;
}

.btn-primary {
  color: white;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.35);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.45);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-captcha {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
}

.btn-captcha:hover:not(:disabled) {
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.45);
}

.btn-secondary {
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.08);
  border: 1.5px solid rgba(14, 165, 233, 0.2);
}

.btn-secondary:hover {
  background: rgba(14, 165, 233, 0.14);
  border-color: rgba(14, 165, 233, 0.35);
  transform: translateY(-2px);
}

/* ========== 响应式 ========== */
@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px 28px;
  }
  .page-title {
    font-size: 19px;
  }
}
</style>