"""
测试飞书 Webhook 消息格式
验证关键词是否能被正确识别
"""

import os
import json
import aiohttp
import asyncio

# 飞书机器人 Webhook 地址
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/971ca8a4-d314-4af6-ac07-52a0749fa44f"

# 飞书机器人关键词列表
REQUIRED_KEYWORDS = ["ComfyUI", "Stable Diffusion", "Flux", "Sora", "Runway", "B站", "AIGC", "LoRA", "工作流", "模型"]


async def test_message_format(message_text: str, description: str):
    """测试消息格式"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"{'='*60}")
    print(f"消息内容:\n{message_text}\n")
    
    payload = {
        "msg_type": "markdown",
        "content": {
            "text": message_text
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                WEBHOOK_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                http_status = resp.status
                
                try:
                    response_data = await resp.json()
                except:
                    response_text = await resp.text()
                    print(f"❌ 响应不是有效的JSON (HTTP {http_status}): {response_text}")
                    return False
                
                code = response_data.get("code", -1)
                msg = response_data.get("msg", "")
                
                if code == 0:
                    print(f"✅ 测试成功 (HTTP {http_status}, code {code})")
                    return True
                else:
                    print(f"❌ 测试失败 (HTTP {http_status}, code={code}): {msg}")
                    print(f"   响应体: {json.dumps(response_data, ensure_ascii=False)}")
                    return False
                    
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False


async def main():
    """测试不同的消息格式"""
    print("开始测试飞书 Webhook 消息格式...")
    print(f"关键词列表: {', '.join(REQUIRED_KEYWORDS)}")
    
    # 测试 1: 当前代码使用的格式
    test1 = """**B站 AIGC 周报 (Past 7 Days)**

B站 AIGC 相关内容：

- [01-05] 作者: ComfyUI 测试视频标题"""
    
    await test_message_format(test1, "当前代码格式（B站 AIGC 在开头）")
    
    # 测试 2: 在标题中包含关键词
    test2 = """**B站 AIGC 周报 (Past 7 Days)**

- [01-05] 作者: ComfyUI 测试视频标题"""
    
    await test_message_format(test2, "标题包含 B站 AIGC")
    
    # 测试 3: 在消息开头单独一行关键词
    test3 = """B站 AIGC

**B站 AIGC 周报 (Past 7 Days)**

- [01-05] 作者: ComfyUI 测试视频标题"""
    
    await test_message_format(test3, "关键词单独一行在开头")
    
    # 测试 4: 使用纯文本格式（不使用 markdown）
    test4_payload = {
        "msg_type": "text",
        "content": {
            "text": "B站 AIGC 相关内容：\n\n**B站 AIGC 周报 (Past 7 Days)**\n\n- [01-05] 作者: ComfyUI 测试视频标题"
        }
    }
    
    print(f"\n{'='*60}")
    print(f"测试: 纯文本格式（text）")
    print(f"{'='*60}")
    print(f"消息内容:\n{test4_payload['content']['text']}\n")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                WEBHOOK_URL,
                json=test4_payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                response_data = await resp.json()
                code = response_data.get("code", -1)
                msg = response_data.get("msg", "")
                
                if code == 0:
                    print(f"✅ 测试成功 (HTTP {resp.status}, code {code})")
                else:
                    print(f"❌ 测试失败 (HTTP {resp.status}, code={code}): {msg}")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
    
    # 测试 5: 确保关键词在消息的最开始
    test5 = """B站 AIGC 相关内容

**B站 AIGC 周报 (Past 7 Days)**

- [01-05] 作者: ComfyUI 测试视频标题"""
    
    await test_message_format(test5, "关键词在消息最开始（无 Markdown 格式）")
    
    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}")
    print("\n建议：")
    print("1. 查看哪个测试通过了")
    print("2. 如果都失败了，可能需要检查飞书机器人的安全设置")
    print("3. 确认关键词是否需要完全匹配（大小写敏感）")


if __name__ == "__main__":
    asyncio.run(main())

