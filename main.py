import asyncio
import aiohttp
import time
import os
import json
import datetime
from bilibili_api import user

# ================= 配置区域 =================
TARGET_UIDS = [
    17280004,
    343093731,
    449342345,
    245604271,
    23462279,
    3546611913329493,
    219572544,
    479755595,
    110353151,
    14843708,
    12710942,
    2115870090,
    1194488958,
    78652351,
    412411578,
    2008798642,
    17919458,
    175873218,
    20366485,
    503934057,
    1450124458,
    219296,
    1840885116,
    1078072406,
    385085361,
]

KEYWORDS = ["ComfyUI", "Stable Diffusion", "Flux", "Sora", "Runway", "Luma", "AIGC", "LoRA", "工作流", "模型"]
HISTORY_DAYS = 14 # 记忆保留时间稍微拉长一点，防止周报重复
CONCURRENCY_LIMIT = 2  # 降低并发数，避免触发风控
# ===========================================

class HistoryManager:
    """记忆管理 (保持不变)"""
    def __init__(self, file_path="history.json"):
        self.file_path = file_path
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def is_processed(self, bvid):
        return bvid in self.data

    def add(self, bvid):
        self.data[bvid] = int(time.time())

    def save_and_clean(self):
        now = time.time()
        expire_time = now - (HISTORY_DAYS * 24 * 3600)
        new_data = {k: v for k, v in self.data.items() if v > expire_time}
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2)
        print(f"记忆库更新：清理后剩余 {len(new_data)} 条记录")

memory = HistoryManager()

def get_time_config():
    """【新功能】根据今天是星期几，决定抓取策略"""
    # 获取当前北京时间 (UTC+8)
    utc_now = datetime.datetime.utcnow()
    beijing_now = utc_now + datetime.timedelta(hours=8)
    weekday = beijing_now.weekday() # 0是周一, ..., 6是周日
    
    current_timestamp = time.time()
    
    if weekday == 0: # 如果是周一
        print("今天是周一，执行【周报】模式，抓取过去 7 天...")
        return {
            "title": "B站 AIGC 周报 (Past 7 Days)",
            "window": 7 * 24 * 3600,
            "now": current_timestamp
        }
    else: # 周二到周五
        print("今天是工作日，执行【日报】模式，抓取过去 1 天...")
        return {
            "title": "B站 AIGC 日报",
            "window": 26 * 3600, # 设置26小时，稍微多一点防止漏掉边界
            "now": current_timestamp
        }

async def fetch_videos_from_up(uid, semaphore, retry_count=3):
    """获取UP主视频，带重试机制"""
    async with semaphore:
        for attempt in range(retry_count):
            try:
                u = user.User(uid=uid)
                # 周报模式下，5条可能不够，改为获取最近 10 条
                videos = await u.get_videos(ps=10) 
                
                # 检查是否有错误
                if isinstance(videos, dict) and videos.get('code') == -352:
                    # 风控错误，等待更长时间后重试
                    wait_time = (attempt + 1) * 3  # 3秒、6秒、9秒
                    print(f"⚠️  UID {uid} 触发风控，等待 {wait_time} 秒后重试... (尝试 {attempt + 1}/{retry_count})")
                    await asyncio.sleep(wait_time)
                    continue
                
                # 成功获取数据
                await asyncio.sleep(1)  # 增加延迟，避免触发风控
                return videos.get('list', {}).get('vlist', [])
                
            except Exception as e:
                error_msg = str(e)
                # 检查是否是风控错误
                if '-352' in error_msg or '风控' in error_msg:
                    wait_time = (attempt + 1) * 3
                    if attempt < retry_count - 1:
                        print(f"⚠️  UID {uid} 触发风控，等待 {wait_time} 秒后重试... (尝试 {attempt + 1}/{retry_count})")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ UID {uid} 获取失败（风控限制）: {error_msg}")
                        return []
                else:
                    # 其他错误，直接返回
                    print(f"❌ UID {uid} 获取失败: {error_msg}")
                    return []
        
        # 所有重试都失败
        print(f"❌ UID {uid} 获取失败，已重试 {retry_count} 次")
        return []

async def filter_content(video_data, time_config):
    """【过滤层】增加了严格的时间判断"""
    title = video_data['title']
    # 修复简介可能为空的bug
    desc = video_data['description'] if 'description' in video_data else ""
    full_text = (title + desc).lower()
    
    # 1. 【新增】严格的时间过滤
    # created 是视频发布时间戳
    video_time = video_data['created']
    # 如果 (当前时间 - 视频时间) > 允许的时间窗口，则说明是旧视频
    if (time_config['now'] - video_time) > time_config['window']:
        return False

    # 2. 关键词硬过滤
    hit_keyword = False
    for kw in KEYWORDS:
        if kw.lower() in full_text:
            hit_keyword = True
            break
    
    if not hit_keyword:
        return False

    return True

async def send_notification(content, title_prefix):
    """发送飞书消息（修复版本：检查响应体中的 code 字段）"""
    webhook_url = os.environ.get("FEISHU_WEBHOOK")
    if not webhook_url:
        print("❌ FEISHU_WEBHOOK 未设置")
        return False
    
    # 格式化内容（text 格式，不使用 Markdown）
    formatted_content = content \
        .replace("<h3>", "").replace("</h3>", "\n") \
        .replace("<ul>", "").replace("</ul>", "") \
        .replace("<li style='margin-bottom:8px'>", "- ") \
        .replace("<li>", "- ") \
        .replace("</li>", "\n") \
        .replace("<b>", "").replace("</b>", "") \
        .replace("<a href='", "").replace("'>", ": ") \
        .replace("</a>", "")
    
    # 确保消息包含飞书机器人要求的关键词（安全设置要求）
    # 飞书机器人关键词：ComfyUI, Stable Diffusion, Flux, Sora, Runway, B站, AIGC, LoRA, 工作流, 模型
    # 在消息开头明确添加关键词，确保飞书机器人能识别
    # 注意：使用 text 格式而不是 markdown，因为 markdown 格式中关键词可能无法被识别
    # 测试发现：text 格式能正确识别关键词，markdown 格式会返回 code=19024
    text_content = f"B站 AIGC\n\n{title_prefix}\n\n" + formatted_content

    data = {
        "msg_type": "text", # 使用 text 格式确保关键词能被识别
        "content": {
            "text": text_content
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                # 1. 检查 HTTP 状态码
                http_status = resp.status
                
                # 2. 读取响应体（关键！）
                try:
                    response_data = await resp.json()
                except:
                    response_text = await resp.text()
                    print(f"❌ 响应不是有效的JSON (HTTP {http_status}): {response_text}")
                    return False
                
                # 3. 检查飞书 API 的实际状态码
                # code = 0 表示成功，code != 0 表示失败
                code = response_data.get("code", -1)
                msg = response_data.get("msg", "")
                
                if code == 0:
                    print(f"✅ 推送成功 (HTTP {http_status}, code {code})")
                    return True
                else:
                    print(f"❌ 推送失败 (HTTP {http_status}, code={code}): {msg}")
                    print(f"   响应体: {json.dumps(response_data, ensure_ascii=False)}")
                    # 如果是关键词错误，打印消息内容的前200个字符用于调试
                    if code == 19024:
                        print(f"   消息内容预览: {text_content[:200]}...")
                        print(f"   ⚠️  提示：飞书机器人要求消息包含特定关键词，请检查机器人安全设置")
                    return False
                    
    except asyncio.TimeoutError:
        print(f"❌ 推送超时")
        return False
    except Exception as e:
        print(f"❌ 推送异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    # 1. 获取今日策略 (周报 vs 日报)
    config = get_time_config()
    
    print(f"开始监控 {len(TARGET_UIDS)} 个UP主...")
    print(f"并发限制: {CONCURRENCY_LIMIT}")
    print("")
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    tasks = [fetch_videos_from_up(uid, semaphore) for uid in TARGET_UIDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_videos = []
    success_count = 0
    fail_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            fail_count += 1
            print(f"❌ UID {TARGET_UIDS[i]} 获取异常: {result}")
            continue
        
        if not result:
            fail_count += 1
            continue
        
        success_count += 1
        for v in result:
            bvid = v['bvid']
            
            # 记忆去重
            if memory.is_processed(bvid):
                continue
            
            # 传入 config 进行时间判断
            if await filter_content(v, config):
                print(f"发现新视频：{v['title']}")
                valid_videos.append(v)
                memory.add(bvid)
    
    print(f"\n监控完成：成功 {success_count} 个，失败 {fail_count} 个")

    if valid_videos:
        # 按发布时间倒序排列 (新的在前)
        valid_videos.sort(key=lambda x: x['created'], reverse=True)
        
        msg = "<ul>"
        for v in valid_videos:
            # 格式化一下时间，比如 [01-05]
            time_str = time.strftime("%m-%d", time.localtime(v['created']))
            msg += f"<li style='margin-bottom:8px'>[{time_str}] <b>{v['author']}</b>: <a href='https://www.bilibili.com/video/{v['bvid']}'>{v['title']}</a></li>"
        msg += "</ul>"
        
        success = await send_notification(msg, config['title'])
        if success:
            print(f"推送成功！共 {len(valid_videos)} 条")
        else:
            print(f"推送失败！共 {len(valid_videos)} 条（请查看上方错误信息）")
    else:
        print("没有符合条件的新视频。")

    memory.save_and_clean()

if __name__ == '__main__':
    asyncio.run(main())
