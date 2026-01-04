import asyncio
import aiohttp
import time
import os
import json
from bilibili_api import user

# ================= 配置区域 =================
TARGET_UIDS = [
    20259914,  # 比如秋叶
    # 在这里填入你的 UID 列表...
]

# 第一层：硬过滤关键词
KEYWORDS = ["ComfyUI", "Stable Diffusion", "Flux", "Sora", "Runway", "Luma", "AIGC", "LoRA"]
# 记录保存天数 (7天前的记录会被自动清理)
HISTORY_DAYS = 7 
# 并发限制 (同时查 3 个，保持礼貌)
CONCURRENCY_LIMIT = 3
# ===========================================

class HistoryManager:
    """管理已处理的视频记录 (你的短期记忆)"""
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
        """判断是否已处理过"""
        return bvid in self.data

    def add(self, bvid):
        """添加新记录"""
        self.data[bvid] = int(time.time())

    def save_and_clean(self):
        """清理过期记录并保存到文件"""
        now = time.time()
        expire_time = now - (HISTORY_DAYS * 24 * 3600)
        # 字典推导式：只保留没过期的
        new_data = {k: v for k, v in self.data.items() if v > expire_time}
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2)
        print(f"记忆库更新：清理后剩余 {len(new_data)} 条记录")

# 全局记忆管理器
memory = HistoryManager()

async def fetch_videos_from_up(uid, semaphore):
    """【数据源层】获取单个 UP 主的最新视频"""
    async with semaphore: # 限制并发数
        try:
            print(f"正在检查 UP: {uid} ...")
            u = user.User(uid=uid)
            videos = await u.get_videos(ps=5) # 只看最近5个
            await asyncio.sleep(1) # 礼貌性延迟
            return videos.get('list', {}).get('vlist', [])
        except Exception as e:
            print(f"UID {uid} 获取失败: {e}")
            return []

async def filter_content(video_data):
    """【过滤层】两段式判断"""
    title = video_data['title']
    desc = video_data['description']
    full_text = (title + desc).lower()

    # --- 第一段：关键词硬过滤 ---
    hit_keyword = False
    for kw in KEYWORDS:
        if kw.lower() in full_text:
            hit_keyword = True
            break
    
    if not hit_keyword:
        return False # 关键词都没中，直接淘汰

    # --- 第二段：语义判断 (目前预留位置，暂时直接通过) ---
    # 未来在这里接入 LLM API：
    # if not await llm_check(title, desc): return False
    
    return True

async def send_notification(content):
    """【通知层】发送消息"""
    token = os.environ.get("PUSH_KEY")
    if not token: return
    
    url = "http://www.pushplus.plus/send"
    async with aiohttp.ClientSession() as session:
        await session.post(url, json={
            "token": token, 
            "title": "B站 AIGC 监控日报", 
            "content": content, 
            "template": "html"
        })

async def main():
    # 1. 初始化并发限制器
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    # 2. 并发获取所有 UP 主的数据
    tasks = [fetch_videos_from_up(uid, semaphore) for uid in TARGET_UIDS]
    results = await asyncio.gather(*tasks)
    
    # 3. 扁平化结果并去重处理
    valid_videos = []
    
    for video_list in results:
        for v in video_list:
            bvid = v['bvid']
            
            # 【重要】如果记忆里有，直接跳过
            if memory.is_processed(bvid):
                continue
            
            # 进入过滤器
            if await filter_content(v):
                print(f"发现新视频：{v['title']}")
                valid_videos.append(v)
                # 标记为已处理 (但还没存盘，防止推送失败)
                memory.add(bvid)

    # 4. 发送通知
    if valid_videos:
        msg = "<h3>今日 AIGC 新发现：</h3><ul>"
        for v in valid_videos:
            msg += f"<li style='margin-bottom:8px'><b>{v['author']}</b>: <a href='https://www.bilibili.com/video/{v['bvid']}'>{v['title']}</a></li>"
        msg += "</ul>"
        
        await send_notification(msg)
        print("推送成功！")
    else:
        print("没有符合条件的新视频。")

    # 5. 【关键】最后一步：保存记忆到文件
    memory.save_and_clean()

if __name__ == '__main__':
    asyncio.run(main())

