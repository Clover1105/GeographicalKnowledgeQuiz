<template>
  <div class="welcome-container">
    <!-- 背景装饰元素 -->
    <div class="bg-decoration bg-circle-1"></div>
    <div class="bg-decoration bg-circle-2"></div>

    <div class="content-card">
      <!-- 图标/Logo区域 -->
      <div class="icon-wrapper">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="geo-icon">
          <circle cx="12" cy="12" r="10" />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
      </div>

      <!-- 标题区域 -->
      <h1 class="main-title">地理知识问答系统</h1>
      <p class="sub-title">探索世界 · 发现未知 · 智答万象</p>

      <!-- 按钮区域 -->
      <button class="enter-btn" @click="goLogin">
        <span>进入系统</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="arrow-icon">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

function goLogin() {
  router.push('/login');
}
</script>

<style scoped>
/* ========== 全局容器 ========== */
.welcome-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 50%, #ecfeff 100%);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
}

/* ========== 背景装饰圆 ========== */
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
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -20px) scale(1.05); }
}

/* ========== 内容卡片 ========== */
.content-card {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 60px 50px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 20px 50px -12px rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.6);
  max-width: 480px;
  width: 90%;
  animation: cardEnter 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(30px);
}

@keyframes cardEnter {
  to { opacity: 1; transform: translateY(0); }
}

/* ========== 图标 ========== */
.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9, #10b981);
  margin-bottom: 28px;
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.3);
}

.geo-icon {
  width: 40px;
  height: 40px;
  color: white;
}

/* ========== 文字 ========== */
.main-title {
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 12px 0;
  letter-spacing: 1px;
}

.sub-title {
  font-size: 15px;
  color: #64748b;
  margin: 0 0 40px 0;
  letter-spacing: 2px;
}

/* ========== 按钮 ========== */
.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 40px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.35);
  letter-spacing: 1px;
}

.enter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.45);
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
}

.enter-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(14, 165, 233, 0.3);
}

.arrow-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.enter-btn:hover .arrow-icon {
  transform: translateX(4px);
}

/* ========== 响应式 ========== */
@media (max-width: 640px) {
  .content-card {
    padding: 40px 30px;
  }
  .main-title {
    font-size: 22px;
  }
  .enter-btn {
    padding: 14px 32px;
    font-size: 15px;
  }
}
</style>