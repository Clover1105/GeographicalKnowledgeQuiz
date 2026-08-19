<template>
  <div class="app-container">
    <!-- 左侧 历史记录 -->
    <div class="sidebar">
      <div class="logo-area">
        <div class="logo-icon">🌍</div>
        <h2>地理知识问答</h2>
      </div>

      <div class="action-area">
        <button class="new-chat-btn" @click="new_chat">
          <el-icon style="margin-right: 6px;"><Plus /></el-icon> 新建对话
        </button>
      </div>

      <div class="search-area">
        <el-input
          v-model="searchInput"
          placeholder="搜索历史记录..."
          :prefix-icon="Search"
          clearable
          @keyup.enter="fuzzySearch"
          @blur="cleraSearch"
          class="custom-search-input"
        />
      </div>

      <!-- 普通历史记录栏 -->
      <div v-show="isSearch" class="history-section">
        <div class="section-title">历史记录</div>
        <div class="history-list-container">
          <div
            v-for="(item, index) in historyList"
            :key="item.historyId"
            class="history-item"
            :class="{ active: item.historyId === currentChatId || (item.parentId !== 0 && item.parentId === currentChatId) }"
            @click="history_Dialogue(item.historyId, item.parentId)"
          >
            <div class="item-content">
              <div class="item-question">{{ item.question }}</div>
              <div class="item-time">{{ item.createTime }}</div>
            </div>
            <div class="item-actions">
              <el-popconfirm
                title="确定删除该历史记录吗?"
                confirm-button-text="删除"
                cancel-button-text="取消"
                @confirm="confirmEvent(item.historyId)"
                @cancel="cancelEvent"
              >
                <template #reference>
                  <button class="delete-btn" @click.stop>
                    <el-icon><Delete /></el-icon>
                  </button>
                </template>
              </el-popconfirm>
            </div>
          </div>
          <div v-if="historyList.length === 0" class="empty-tip">暂无历史记录</div>
        </div>
      </div>

      <!-- 模糊搜索历史记录栏 -->
      <div v-show="!isSearch" class="history-section">
        <div class="section-title">搜索结果</div>
        <div class="history-list-container">
          <div
            v-for="(item, index) in searchList"
            :key="index"
            class="history-item search-result-item"
            @mousedown="isClickingSearch = true"
            @click="history_Dialogue(item.historyId, item.parentId)"
          >
            <div class="item-content">
              <div class="item-question">{{ item.question }}</div>
              <div class="item-answer-preview">{{ item.answer }}</div>
            </div>
          </div>
          <div v-if="searchList.length === 0" class="empty-tip">未找到相关记录</div>
        </div>
      </div>

      <div class="user-info">
        <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <span class="username">{{ username || '未登录' }}</span>
      </div>
    </div>

    <!-- 右侧 聊天区域 -->
    <div class="chat-area">
      <div class="chat-header">
        <span class="header-title">
          当前对话：{{ messages.find(m => m.role === 'user')?.content || '新会话' }}
        </span>
      </div>

      <!-- 聊天消息展示区 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="welcome-icon">🌏</div>
          <h1>欢迎使用地理知识问答系统</h1>
          <p>请输入您的问题，我将为您提供专业的地理知识解答。</p>
        </div>

        <div
          v-for="(item, index) in messages"
          :key="index"
          class="message-row"
          :class="item.role"
        >
          <div class="avatar" :class="item.role">
            <span v-if="item.role === 'user'">🐻</span>
            <span v-else>🤖</span>
          </div>
          <div class="bubble" :class="item.role">
            <div v-html="formatContent(item.content)"></div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="question"
            placeholder="输入问题，按 Enter 发送..."
            @keyup.enter.exact="sendQuestion"
            class="custom-chat-input"
          />
          <button
            class="send-btn"
            :disabled="isSendQuestion"
            @click="sendQuestion"
          >
            <el-icon v-if="isSendQuestion" class="is-loading"><Loading /></el-icon>
            <span v-else>发送</span>
          </button>
        </div>
        <div class="disclaimer">注：AI 生成内容仅供参考，请核实重要信息。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance, onMounted, nextTick } from 'vue';
import { ElMessage } from "element-plus";
import { Plus, Delete, Search, Loading } from '@element-plus/icons-vue';

let proxy = getCurrentInstance().proxy;

let isSendQuestion = ref(false);
let username = ref('');
let question = ref('');
let messages = ref([]);
const messagesContainer = ref(null);

const currentChatId = ref(0);

let token = sessionStorage.getItem('token');

// 简单的格式化函数，处理换行符
function formatContent(text) {
  if (!text) return '';
  return text.replace(/\n/g, '<br>');
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

// 聊天
function sendQuestion() {
  let que = question.value.trim();
  if (que.length === 0) {
    ElMessage.warning("请输入有效内容！");
    return;
  }

  isSendQuestion.value = true;
  question.value = '';

  messages.value.push({ role: 'user', content: que });
  messages.value.push({ role: 'system', content: '思考中，请耐心等待^3^......' });
  scrollToBottom();


  let urlSearchParams = new URLSearchParams({
    question: que,
    historyId: currentChatId.value,
  });

  let ans = '';

  fetch("http://localhost:8000/chat/chat?" + urlSearchParams.toString(), {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(async (response) => {
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let parts = buffer.split('\n\n');
      buffer = parts.pop();
      for (let part of parts) {
        let line = part.split('\n').find(l => l.startsWith('data:'));
        if (!line) continue;
        let data = JSON.parse(line.slice(5).trim()).content;
        if (data === "end_end") {
          isSendQuestion.value = false;
          save_new_dialogue(que, ans);
          scrollToBottom();
          return;
        }
        ans += data;
        messages.value[messages.value.length - 1].content = ans;
        scrollToBottom();
      }
    }
  }).catch((e) => {
    console.log("SSE获取数据失败", e);
    isSendQuestion.value = false;
    ElMessage.error("连接服务器失败");
  });
}

// 历史记录栏
const historyList = ref([]);
function get_history() {
  proxy
    .$axios({
      url: '/history/getHistory',
      method: 'get',
      headers: { 'Authorization':`Bearer ${token}` },
    })
    .then((res) => {
      console.log(res.data);
      historyList.value = res.data.data;
    });
}

// 某对话框历史对话详情
function history_Dialogue(historyId, parentId) {
  console.log("当前点击对话id：", historyId, "当前对话的父对话id：", parentId);
  let rootId = parentId !== 0 ? parentId : historyId;
  currentChatId.value = rootId;

  if (!isSearch.value) {
    isSearch.value = true;
    searchInput.value = '';
    isClickingSearch.value = false;
    get_history();
  }

  proxy
    .$axios({
      url: '/history/historyDialogue',
      method: 'get',
      params: { historyId: rootId },
      headers: { 'Authorization':`Bearer ${token}` },
    })
    .then((res) => {
      console.log(res.data);
      messages.value = res.data.data;
      scrollToBottom();
    });
}

// 存储新对话
function save_new_dialogue(question, answer) {
  let dialogueInformation = {
    question: question,
    answer: answer,
    parentId: currentChatId.value,
  };
  proxy
    .$axios({
      url: '/chat/saveNewDialogue',
      method: 'post',
      data: dialogueInformation,
      headers: { 'Authorization':`Bearer ${token}` },
    })
    .then((res) => {
      console.log('对话存储结果：', res.data);
      if (currentChatId.value === 0) {
        currentChatId.value = res.data.data;
        const newItem = historyList.value.find(
          (item) => item.historyId === res.data.data
        );
        if (newItem && (!newItem.question || newItem.question === '新会话')) {
          newItem.question = question;
        }
      }
      get_history();
    });
}

// 新建对话框
function new_chat() {
  currentChatId.value = 0;
  messages.value = [];
  console.log('新建对话框，当前对话id：', currentChatId.value);
}

// 删除历史记录
const confirmEvent = (historyId) => {
  console.log('confirm!');
  proxy
    .$axios({
      url: '/history/deleteHistory',
      method: 'delete',
      params: { historyId: historyId },
      headers: { 'Authorization':`Bearer ${token}` },
    })
    .then((res) => {
      console.log('删除历史记录结果：', res.data);
      if (historyId === currentChatId.value) {
        currentChatId.value = 0;
        messages.value = [];
      }
      get_history();
    });
};
const cancelEvent = () => {
  console.log('cancel!');
};

// 模糊搜索
let searchInput = ref('');
let isSearch = ref(true);
let searchList = ref([]);
function fuzzySearch() {
  let si = searchInput.value.trim();
  if (si.length === 0) {
    ElMessage.warning("请输入有效内容！");
    return;
  }
  proxy
    .$axios({
      url: '/history/fuzzySearch',
      method: 'get',
      params: {searchInput: searchInput.value},
      headers: { 'Authorization':`Bearer ${token}` },
    })
    .then((res) => {
      console.log('模糊搜索结果：', res.data);
      isSearch.value = false;
      searchList.value = res.data.data;
    });
}

let isClickingSearch = ref(false);
function cleraSearch() {
  if (isClickingSearch.value) return;
  searchInput.value = '';
  isSearch.value = true;
  get_history();
}

onMounted(() => {
  username.value = sessionStorage.getItem("username");
  get_history();
});
</script>

<style scoped>
/* ========== 全局容器 ========== */
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 50%, #ecfeff 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', sans-serif;
  overflow: hidden;
}

/* ========== 左侧侧边栏 ========== */
.sidebar {
  width: 300px;
  min-width: 300px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(14, 165, 233, 0.08);
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  z-index: 10;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 0 4px;
}

.logo-icon {
  font-size: 28px;
  line-height: 1;
}

.logo-area h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #0ea5e9, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 新建对话按钮 */
.action-area {
  margin-bottom: 14px;
}

.new-chat-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
}

.new-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
}

.new-chat-btn:active {
  transform: translateY(0);
}

/* 搜索框 */
.search-area {
  margin-bottom: 16px;
}

.custom-search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f8fafc;
  box-shadow: none;
  border: 1.5px solid #e2e8f0;
  transition: all 0.25s ease;
}

.custom-search-input :deep(.el-input__wrapper:focus-within) {
  border-color: #0ea5e9;
  background: white;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

/* 历史记录区域 */
.history-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 10px;
  padding-left: 6px;
}

.history-list-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.history-list-container::-webkit-scrollbar {
  width: 4px;
}

.history-list-container::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
}

.history-list-container::-webkit-scrollbar-track {
  background: transparent;
}

.history-item {
  background: #f8fafc;
  border: 1.5px solid transparent;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.history-item:hover {
  background: rgba(14, 165, 233, 0.06);
  border-color: rgba(14, 165, 233, 0.15);
}

.history-item.active {
  background: rgba(14, 165, 233, 0.08);
  border-color: #0ea5e9;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.12);
}

.item-content {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}

.item-question {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 3px;
}

.item-time {
  font-size: 11px;
  color: #94a3b8;
}

.item-answer-preview {
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 3px;
}

.delete-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  opacity: 0;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.empty-tip {
  text-align: center;
  color: #cbd5e1;
  font-size: 13px;
  margin-top: 40px;
}

/* 用户信息 */
.user-info {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

/* ========== 右侧聊天区 ========== */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  position: relative;
}

.chat-header {
  height: 60px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(14, 165, 233, 0.08);
  display: flex;
  align-items: center;
  padding: 0 28px;
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  max-width: 300px;          /* 限制最大宽度，按需调整 */
  white-space: nowrap;       /* 不换行 */
  overflow: hidden;          /* 超出隐藏 */
  text-overflow: ellipsis;   /* 超出部分显示 ... */
}

/* 消息容器 */
.messages-container {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.messages-container::-webkit-scrollbar {
  width: 5px;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
}

/* 欢迎屏 */
.welcome-screen {
  margin: auto;
  text-align: center;
  animation: fadeIn 0.8s ease forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.welcome-screen h1 {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #0ea5e9, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-screen p {
  font-size: 15px;
  color: #64748b;
  margin: 0;
}

/* 消息气泡 */
.message-row {
  display: flex;
  width: 100%;
  animation: msgIn 0.3s ease forwards;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.avatar.user {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  box-shadow: 0 3px 10px rgba(14, 165, 233, 0.3);
}

.avatar.system {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 3px 10px rgba(16, 185, 129, 0.3);
}

.bubble {
  max-width: 68%;
  padding: 14px 18px;
  font-size: 14px;
  line-height: 1.7;
  word-wrap: break-word;
  position: relative;
}

.bubble.system {
  background: white;
  color: #1e293b;
  margin-left: 12px;
  border-radius: 4px 16px 16px 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.1);
}

.bubble.user {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  margin-right: 12px;
  border-radius: 16px 4px 16px 16px;
  box-shadow: 0 2px 12px rgba(14, 165, 233, 0.25);
}

/* 输入区域 */
.input-area {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 18px 28px 14px;
  border-top: 1px solid rgba(14, 165, 233, 0.08);
}

.input-wrapper {
  display: flex;
  gap: 10px;
  max-width: 860px;
  margin: 0 auto;
  align-items: center;
}

.custom-chat-input :deep(.el-input__wrapper) {
  border-radius: 14px;
  background: #f8fafc;
  box-shadow: none;
  border: 1.5px solid #e2e8f0;
  padding: 4px 16px;
  height: 48px;
  font-size: 15px;
  transition: all 0.25s ease;
}

.custom-chat-input :deep(.el-input__wrapper:focus-within) {
  border-color: #0ea5e9;
  background: white;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.send-btn {
  height: 48px;
  padding: 0 28px;
  font-size: 15px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.disclaimer {
  text-align: center;
  font-size: 11px;
  color: #cbd5e1;
  margin-top: 10px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .sidebar {
    width: 240px;
    min-width: 240px;
    padding: 16px 12px;
  }
  .bubble {
    max-width: 82%;
  }
  .messages-container {
    padding: 16px;
  }
  .input-area {
    padding: 14px 16px 10px;
  }
}
</style>