// 引入路由配置文件
import {createRouter, createWebHistory} from 'vue-router';

// 定义路由配置对象 -- 数组
const routes = [
    {
        path: '',
        meta: {
            title: '首页',
            login: false,
        },
        component: () => import('../components/Home.vue')
    },
    {
        path: '/login',
        meta: {
            title: '登录与注册',
            login: false,
        },
        component: () => import('../components/Login.vue')
    },
    {
        path: '/signup',
        meta: {
            title: '注册',
            login: false,
        },
        component: () => import('../components/SignUp.vue')
    },
    {
        path: '/chat',
        meta: {
            title: '聊天',
            login: true,
        },
        component: () => import('../components/Chat.vue')
    },
]

// 设置路由模式为 history 模式 -- 默认 hash 模式，访问路径中间有一个 # 号
const router = createRouter({
    history: createWebHistory(),
    routes
})

// 导出路由实例
export default router