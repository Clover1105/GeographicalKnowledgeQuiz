<template>
  <div class="signup-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration bg-circle-1"></div>
    <div class="bg-decoration bg-circle-2"></div>

    <div class="signup-card">
      <h1 class="page-title">注册页面</h1>

      <!-- 表单区域 -->
      <form class="signup-form" @submit.prevent>
        <div class="form-item">
          <label class="form-label">用户名</label>
          <input
            type="text"
            v-model="username"
            placeholder="请输入用户名"
            class="form-input"
          />
        </div>

        <div class="form-item">
          <label class="form-label">邮箱号</label>
          <input
            type="text"
            v-model="email"
            placeholder="请输入邮箱地址"
            class="form-input"
          />
        </div>

        <div class="form-item">
          <label class="form-label">密码</label>
          <input
            type="password"
            v-model="password"
            placeholder="请设置密码"
            class="form-input"
          />
        </div>

        <div class="form-item">
          <label class="form-label">确认密码</label>
          <input
            type="password"
            v-model="confirmPassword"
            placeholder="请再次输入密码"
            class="form-input"
          />
        </div>
      </form>

      <!-- 操作按钮区 -->
      <div class="action-area">
        <button class="btn-secondary" @click="goLogin">返回登陆页面</button>
        <button class="btn-primary" @click="signUp">注册</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

let router = useRouter();
let proxy = getCurrentInstance().proxy;

let username = ref("");
let email = ref("");
let password = ref("");
let confirmPassword = ref("");

function goLogin() {
  router.push("/login");
}

// 注册账号
function signUp() {
  // 验证两次密码是否一致
  if (password.value !== confirmPassword.value) {
    ElMessage.error("两次密码不一致");
    return {
      code: 500,
      msg: "两次密码不一致",
    };
  }

  // 创建用户信息对象
  let userInformation = {
    username: username.value,
    email: email.value,
    password: password.value,
  };
  proxy
    .$axios({
      url: "/users/signup",
      method: "post",
      data: userInformation,
    })
    .then((res) => {
      console.log(res.data);
      let code = res.data.code;
      if (code === 200) {
        ElMessage.success("注册成功");
        router.push("/login");
      } else {
        ElMessage.error("注册失败");
      }
    });
}
</script>

<style scoped>
/* ========== 页面容器 & 背景 ========== */
.signup-page {
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
.signup-card {
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
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin: 0 0 32px 0;
  letter-spacing: 0.5px;
}

/* ========== 表单 ========== */
.signup-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 32px;
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

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.45);
}

.btn-primary:active {
  transform: translateY(0);
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

.btn-secondary:active {
  transform: translateY(0);
}

/* ========== 响应式 ========== */
@media (max-width: 480px) {
  .signup-card {
    padding: 32px 24px 28px;
  }
  .page-title {
    font-size: 20px;
  }
}
</style>