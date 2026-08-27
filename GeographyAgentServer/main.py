print("这里是：main.py")

import os
from dotenv import load_dotenv

# 本地 Windows / PyCharm 环境加载 .env.local
# Docker 环境由 docker compose 注入 .env，因此不需要加载文件
if os.getenv("DOCKER_ENV") != "true":
    load_dotenv(".env.local")

from fastapi import FastAPI

# 启动和关闭要执行的操作
from contextlib import asynccontextmanager
from ai import LoadLLM
from chat.utils import AgentUtil
llm = None
agent = None
@asynccontextmanager
async def start_and_stop(app):
    global llm, agent
    app.state.username = "clover"
    print("启动项目")
    print("正在初始化大模型...")
    llm = LoadLLM.create_model()
    print("正在初始化智能体...")
    agent = AgentUtil.agent_util(llm)
    yield
    print("关闭项目")

app = FastAPI(lifespan=start_and_stop)

# 健康检查端点（Docker HEALTHCHECK 需要）
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 跨域配置
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],    # 允许的跨域访问的域名 -- 完整的客户端域名
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"],    # 允许的跨域访问请求的方法
    allow_headers=["*"],    # 允许的跨域访问请求的头部信息
)

# 注册子路由 -- 注册之后接口才能被访问

# 用户子路由
from users.controller.UsersController import users_router
app.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)

# 聊天子路由
from chat.controller.ChatController import chat_router
app.include_router(
    chat_router,
    prefix="/chat",
    tags=["chat"],
)

# 历史子路由
from chat.controller.HistoryController import history_router
app.include_router(
    history_router,
    prefix="/history",
    tags=["history"],
)



if __name__ == '__main__':
    import uvicorn as uv
    uv.run(app="main:app", host="localhost", port=8000, reload=False)
