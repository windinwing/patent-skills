#!/usr/bin/env python3
"""
测试专利 API 连接（本地脚本）。打印参数时对 token 脱敏。
"""

import os
import sys
import json
import requests
from pathlib import Path


def _params_for_logging(p: dict) -> dict:
    o = dict(p)
    if o.get("t"):
        o["t"] = "<redacted>"
    return o


# 获取OpenClaw配置的token
try:
    import subprocess
    result = subprocess.run(
        ['openclaw', 'config', 'get', 'skills.entries.patent-search.apiKey'],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        token = result.stdout.strip()
        print("从 OpenClaw CLI 获取到 token（不在此打印）")
    else:
        print("无法从OpenClaw获取token")
        token = None
except Exception as e:
    print(f"获取OpenClaw配置失败: {e}")
    token = None

# 如果没有token，尝试环境变量
if not token or token == "__OPENCLAW_REDACTED__":
    token = os.environ.get('PATENT_API_TOKEN')
    if token:
        print("从环境变量 PATENT_API_TOKEN 获取到 token（不在此打印）")
    else:
        print("没有找到API Token")
        sys.exit(1)

# 测试API连接
base_url = "https://www.9235.net/api"
endpoint = "/s"

params = {
    "t": token,
    "v": 1,
    "ds": "cn",
    "q": "石墨烯",
    "p": 1,
    "ps": 5,
    "sort": "relation"
}

url = f"{base_url}/{endpoint.lstrip('/')}"
print(f"\n测试API请求...")
print(f"URL: {url}")
print(f"参数: {json.dumps(_params_for_logging(params), ensure_ascii=False, indent=2)}")

try:
    response = requests.get(url, params=params, timeout=30)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n响应JSON: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
            
            if "success" in data:
                if data["success"]:
                    print("✅ API调用成功！")
                    print(f"找到 {data.get('total', 0)} 条专利")
                else:
                    print(f"❌ API返回错误: {data.get('message', '未知错误')}")
                    print(f"错误代码: {data.get('errorCode', '未知')}")
            else:
                print("⚠️ 响应中没有success字段")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"响应内容: {response.text[:500]}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except requests.exceptions.ConnectionError as e:
    print(f"❌ 连接失败: {e}")
except Exception as e:
    print(f"❌ 请求异常: {e}")