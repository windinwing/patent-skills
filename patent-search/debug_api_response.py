#!/usr/bin/env python3
"""
调试API返回的数据结构
"""

import sys
import os
import json
import requests

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from patent_api import PatentAPI
except ImportError as e:
    print(f"❌ 无法导入patent_api模块: {e}")
    sys.exit(1)

def debug_api_response():
    """调试API返回的数据结构"""
    
    try:
        # 初始化API客户端
        api = PatentAPI()
        
        print("🔍 测试API搜索响应数据结构")
        print("=" * 60)
        
        # 发送搜索请求
        params = {
            "ds": "cn",
            "q": "锂电池",
            "p": 1,
            "ps": 2,
            "sort": "relation",
            "t": api.token,
            "v": 1
        }
        
        url = f"{api.base_url}/s"
        print(f"📡 请求URL: {url}")
        print(f"🔑 使用Token: {api.token[:8]}...{api.token[-8:]}")
        print(f"📋 请求参数: {json.dumps(params, ensure_ascii=False)}")
        print("-" * 60)
        
        # 发送请求
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📡 响应状态: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应成功: {result.get('success', False)}")
            print(f"📊 总条数: {result.get('total', 0)}")
            
            # 显示完整的响应结构
            print("\n📋 完整响应结构:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 检查patents字段
            patents = result.get('patents', [])
            if patents:
                print(f"\n📄 找到 {len(patents)} 条专利")
                print("\n🔍 第一条专利的完整结构:")
                print(json.dumps(patents[0], ensure_ascii=False, indent=2))
                
                print("\n🔑 第一条专利的所有字段:")
                for key, value in patents[0].items():
                    print(f"  • {key}: {repr(value)[:100]}{'...' if len(repr(value)) > 100 else ''}")
                
                # 检查我们代码中使用的字段
                print("\n🔍 检查代码中使用的字段:")
                code_fields = ['ti', 'id', 'ap', 'ab', 'ad', 'pd', 'ipc']
                for field in code_fields:
                    if field in patents[0]:
                        print(f"  ✅ {field}: {repr(patents[0][field])[:80]}{'...' if len(repr(patents[0][field])) > 80 else ''}")
                    else:
                        print(f"  ❌ {field}: 字段不存在")
            
            # 检查其他可能的字段名
            print("\n🔍 检查其他可能的标题字段:")
            possible_title_fields = ['title', 'ti', 'patentName', 'name', '专利名称', '名称']
            for field in possible_title_fields:
                if patents and field in patents[0]:
                    print(f"  ✅ {field}: {repr(patents[0][field])}")
            
            print("\n🔍 检查其他可能的申请人字段:")
            possible_applicant_fields = ['applicant', 'ap', '申请人', '申请单位', 'assignee']
            for field in possible_applicant_fields:
                if patents and field in patents[0]:
                    print(f"  ✅ {field}: {repr(patents[0][field])}")
                    
        else:
            print(f"❌ 响应失败: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")

def test_format_function():
    """测试格式化函数"""
    print("\n🔧 测试格式化函数")
    print("=" * 60)
    
    try:
        api = PatentAPI()
        
        # 模拟API响应
        mock_result = {
            "success": True,
            "total": 262995,
            "patents": [
                {
                    "ti": "锂电池外壳、锂电池正极盖板及锂电池",
                    "id": "CN112968234A",
                    "ap": "比亚迪股份有限公司",
                    "ab": "本发明的一种锂电池外壳，包括柱形管、正极盖板和负极盖板...",
                    "ad": "2021-01-22",
                    "pd": "2021-04-30",
                    "ipc": "H01M50/147"
                },
                {
                    "ti": "一种锂电池正极材料及其制备方法",
                    "id": "CN113161555A",
                    "ap": "宁德时代新能源科技股份有限公司",
                    "ab": "本发明公开了一种锂电池正极材料及其制备方法...",
                    "ad": "2021-05-10",
                    "pd": "2021-08-13",
                    "ipc": "H01M4/525"
                }
            ]
        }
        
        print("📋 模拟数据:")
        print(json.dumps(mock_result, ensure_ascii=False, indent=2))
        
        # 测试格式化函数
        formatted = api.format_search_result(mock_result)
        print("\n📄 格式化输出:")
        print(formatted)
        
    except Exception as e:
        print(f"❌ 测试格式化函数失败: {e}")

def main():
    """主函数"""
    print("🔧 API响应数据结构调试工具")
    print("=" * 60)
    
    # 调试实际API响应
    debug_api_response()
    
    # 测试格式化函数
    test_format_function()
    
    print("\n" + "=" * 60)
    print("💡 根据调试结果，可能需要修改patent_api.py中的字段名")

if __name__ == "__main__":
    main()