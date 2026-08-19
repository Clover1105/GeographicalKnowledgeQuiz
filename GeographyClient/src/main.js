import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 创建对象
const app = createApp(App)

// 注册路由
import router from './router'
app.use(router)

// 美化页面全局配置 -- 全局注册 Element-Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
app.use(ElementPlus)

// axios 全局配置
import axios from 'axios'   // 导入 axios 包
axios.defaults.baseURL = 'http://localhost:8000/'   // 服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json'    // post 请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json'     // put 请求发送json数据给服务器
app.config.globalProperties.$axios = axios      // 将 axios 对象挂载到 vue 对象上，使用 $axios 替代原生的 axios

// 导航守卫
router.beforeEach((to, from, next) => {
    if (to.meta.login){
        let username = sessionStorage.getItem('username')
        if (username){
            console.log('已登录，跳转到聊天页面')
            next()
        } else {
            console.log('未登录，跳转到登录页面')
            next('/')
        }
    } else {
        console.log('非对话页面，直接访问')
        next()
    }
})

app.mount('#app')
