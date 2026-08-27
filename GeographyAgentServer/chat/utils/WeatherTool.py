# 连接图数据库
from common import Neo4jUtil
conn = Neo4jUtil.get_neo4j_conn()

# 参数校验
from pydantic import BaseModel, Field
class WeatherTool(BaseModel):
    city: str = Field(..., description="城市名称")

# 创建工具
from langchain_core.tools import tool

# 创建查询天气的工具
import requests
@tool(
    name_or_callable="get_weather",
    description="""
        当用户需要查询某个城市的天气时，调用此工具
        参数：
            city：字符串类型，表示城市名称
    """
)
def get_weather(city: str):
    print(f"查询天气的城市：{city}")
    # 引入天气查询接口 --- 第三方api【高德、心知】
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": "be2c23df0824437362ed4948ecfb50d9",
        "city": city,
    }
    # 通过requests发送get请求
    result = requests.get(url=url, params=params)
    result = result.json()
    # 拼接天气数据
    live = result["lives"][0]
    return {
        "result": (
            f"{live['province']}{live['city']}当前天气{live['weather']}，"
            f"气温{live['temperature_float']}℃，湿度{live['humidity_float']}%，"
            f"{live['winddirection']}风{live['windpower']}级，"
            f"数据更新时间为{live['reporttime']}。"
        )
    }