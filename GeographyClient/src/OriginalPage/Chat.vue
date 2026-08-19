<template>
  <!-- 左侧 历史记录 -->
  <div>
    <div>
      地理知识问答系统
    </div>
    <div>
      <div style="border: 3px solid green;height: 30px;width: 10%"  @click="new_chat">+新建对话</div>
    </div>
    <div>
      <div >
        <input v-model="searchInput" type="text" placeholder="搜索历史记录" @keyup.enter="fuzzySearch" @blur="cleraSearch">
      </div>
    </div>
    <!-- 普通历史记录栏 -->
    <div v-show="isSearch">
      历史记录栏（普通）
      <div style="border: 3px solid green;min-height: 300px;width: 100%" >
        <div v-for="(item,index) in historyList" style="border: 3px solid orange;min-height: 50px;width: 40%; box-sizing: border-box;">
          <div @click="history_Dialogue(item.historyId,item.parentId)">
            {{item.question}}<br>
            {{item.createTime}}
            <el-popconfirm title="确定删除该历史记录吗?" @confirm="confirmEvent(item.historyId)" @cancel="cancelEvent">
              <template #reference>
                <el-button @click.stop>Delete</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>
    <!-- 模糊搜索历史记录栏 -->
    <div v-show="!isSearch">
      历史记录栏（模糊搜索）
      <div style="border: 3px solid green;min-height: 300px;width: 100%" >
        <div @mousedown="isClickingSearch = true" @click="history_Dialogue(item.historyId,item.parentId)" v-for="(item,index) in searchList" :key='index' style="border: 3px solid orange;min-height: 60px;width: 40%; box-sizing: border-box;">
          <div>
            {{item.question}}
          </div>
          <div style="font-size: 10px; color: gray;">
            {{item.answer}}
          </div>
        </div>
      </div>
    </div>
    <div>
      用户：{{username}}
    </div>
  </div>

  <!-- 右侧 聊天区域 -->
  <div>
    <div>
      当前对话为：
    </div>
    <div>
      聊天框
    </div>
    <div>
      <div style="border: 3px solid green;min-height: 100px;width: 100%" >
        <div v-for="(item,index) in messages">
          <div v-if="item.role === 'user'">{{item.content}}</div>
          <div v-else>{{item.content}}</div>
        </div>
      </div>
      问题：<input v-model="question" type="text" @keyup.enter="sendQuestion">
      <button :disabled="isSendQuestion" @click="sendQuestion">发送</button>
    </div>
    <div>
      注释：仅供参考
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance, onMounted} from 'vue';
import {ElMessage} from "element-plus";

let proxy = getCurrentInstance().proxy

let isSendQuestion = ref(false)
let username = ref('')
let question = ref('')
let messages = ref([])

const currentChatId = ref(0); // 当前对话窗口ID -- const 禁止的是重新赋值（改变绑定），不是禁止修改内容


// 聊天
function sendQuestion(){
  // 判断用户输入内容是否有效
  let que = question.value.trim();
  if(que.length === 0){
    ElMessage.warning("请输入有效内容！");
    return
  }

  // 禁用发送按钮
  isSendQuestion = true;

  // 清空输入框
  question.value = '';

  // 将发送的问题和回复内容渲染到页面 -- 往聊天列表末尾加消息
  messages.value.push({role: 'user', content: que});
  messages.value.push({role: 'geo', content: '思考中，请耐心等待^3^......'});

  // 构造SSE请求 -- 发送问题给服务器，流式接收服务器传递的内容
  let urlSearchParams = new URLSearchParams({
    question: que,
    historyId: currentChatId.value
  });
  let es = new EventSource("http://localhost:8000/chat/chat?"+urlSearchParams.toString());
  let ans = '';

  // 监听服务器
  es.onmessage = (e) => {
    let data = JSON.parse(e.data).content;
    if (data === "end_end"){
      es.close();
      isSendQuestion = false;
      save_new_dialogue(que,ans);
      return
    }
    ans += data;
    messages.value[messages.value.length - 1].content = ans;  // 更新数据，替换思考中
  };
  es.onerror = (e) => {
    console.log("SSE获取数据失败",e);
    es.close();
  }
}

// 历史记录栏
const historyList = ref([]);
function get_history(){
  proxy.$axios({
    url: '/history/getHistory',
    method: 'get',
    params: {
      username:username.value
    }
  }).then(res => {
    console.log(res.data)
    historyList.value = res.data.data;
  })
}

// 某对话框历史对话详情
function history_Dialogue(historyId,parentId){
  console.log("当前点击对话id：",historyId,'当前对话的父对话id：',parentId);
  // 模糊搜索历史记录栏
  let rootId = (parentId !== 0) ? parentId : historyId;
  // 普通历史记录栏
  currentChatId.value = rootId;
  // 从模糊搜索进入对话框的同时切回普通历史栏并重置标志
  if (!isSearch.value) {  // 如果当前为模糊搜索历史记录栏
    isSearch.value = true;
    searchInput.value = '';
    isClickingSearch.value = false;
    get_history();
  }
  proxy.$axios({
    url: '/history/historyDialogue',
    method: 'get',
    params: {
      historyId:rootId
    }
  }).then(res => {
    console.log(res.data);
    messages.value = res.data.data;
  })
}

// 存储新对话
function save_new_dialogue(question,answer){
  let dialogueInformation = {
    username:username.value,
    question:question,
    answer:answer,
    parentId:currentChatId.value
  }
  proxy.$axios({
    url: '/chat/saveNewDialogue',
    method: 'post',
    data: dialogueInformation
  }).then(res => {
    console.log('对话存储结果：',res.data);
    if (currentChatId.value === 0){
      currentChatId.value = res.data.data
    }
    get_history();
  })

}

// 新建对话框
function new_chat(){
  currentChatId.value = 0;
  messages.value = [];
  console.log('新建对话框，当前对话id：',currentChatId.value)
}

// 删除历史记录 -- 点击确认按钮时触发
const confirmEvent = (historyId) => {
  console.log('confirm!')
  proxy.$axios({
    url: '/history/deleteHistory',
    method: 'delete',
    params: {
      historyId:historyId
    }
  }).then(res => {
    console.log('删除历史记录结果：',res.data);
    if (historyId === currentChatId.value){
      currentChatId.value = 0;
      messages.value = [];
    }
    get_history();
  })
}
// 删除历史记录 -- 点击取消按钮时触发
const cancelEvent = () => {
  console.log('cancel!')
}


// 模糊搜索
let searchInput = ref('')
let isSearch = ref(true)
let searchList = ref([])
function fuzzySearch(){
  // 判断输入是否有效
  let si = searchInput.value.trim();
  if (si.length === 0){
    ElMessage.warning("请输入有效内容！");
    return
  }
  proxy.$axios({
    url: '/history/fuzzySearch',
    method: 'get',
    params: {
      username:username.value,
      searchInput:searchInput.value
    }
  }).then(res => {
    console.log('模糊搜索结果：',res.data);
    isSearch.value = false;
    searchList.value = res.data.data;
  })
}
// 取消模糊搜索
let isClickingSearch = ref(false) // 默认没有点击搜索结果
function cleraSearch(){
  // 如果在点击搜索结果，则不切换历史记录栏
  if (isClickingSearch.value) return
  searchInput.value = '';
  isSearch.value = true;
  get_history();
}

// 加载页面后自动执行功能
onMounted(() => {
  username.value = sessionStorage.getItem("username");
  get_history();
})
</script>

<style scoped>
</style>