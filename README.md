# B站UP主视频监控系统

自动监控B站UP主的新视频，检测AIGC相关内容并推送通知。

## 功能特性

- 🔍 **并发监控**：同时监控多个UP主，智能控制并发数
- 🎯 **智能过滤**：关键词硬过滤 + 预留LLM语义判断
- 💾 **持久化记忆**：使用 `history.json` 记录已处理视频，避免重复推送
- 🧹 **自动清理**：7天前的记录自动过期删除
- 📱 **推送通知**：通过 PushPlus 发送HTML格式消息
- 🤖 **自动化运行**：GitHub Actions 每天自动运行

## 快速开始

### 1. 配置 GitHub Secrets

在 GitHub 仓库中配置 PushPlus token：

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 名称填写：`PUSH_KEY`
5. 值填写：你的 PushPlus token（在 [PushPlus官网](http://www.pushplus.plus/) 获取）
6. 点击 **Add secret**

### 2. 配置监控的UP主

编辑 `main.py` 文件，修改 `TARGET_UIDS` 列表：

```python
TARGET_UIDS = [
    20259914,  # 秋叶
    # 添加更多UP主的UID...
]
```

### 3. 配置关键词（可选）

编辑 `main.py` 文件，修改 `KEYWORDS` 列表：

```python
KEYWORDS = ["ComfyUI", "Stable Diffusion", "Flux", "Sora", "Runway", "Luma", "AIGC", "LoRA"]
```

### 4. 运行方式

#### 方式一：GitHub Actions 自动运行（推荐）

- 每天北京时间 9:00 自动运行
- 也可以在 **Actions** 页面手动触发

#### 方式二：本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export PUSH_KEY=your_pushplus_token  # Linux/Mac
# 或
set PUSH_KEY=your_pushplus_token  # Windows

# 运行脚本
python main.py
```

## 项目结构

```
.
├── main.py                    # 主程序
├── history.json               # 已处理视频记录（自动生成）
├── requirements.txt           # Python依赖
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions配置
└── README.md                  # 本文件
```

## 工作原理

1. **Memory (记忆层)**：`HistoryManager` 类管理 `history.json`，记录已处理的视频
2. **Fetcher (数据源)**：并发获取UP主的最新视频列表
3. **Filter (过滤器)**：关键词过滤 → (预留)LLM语义判断
4. **Notifier (通知器)**：发送推送消息

## 注意事项

- `history.json` 会自动提交到仓库，实现跨运行周期的持久化
- 首次运行会创建 `history.json` 文件
- GitHub Actions 会自动提交更新后的 `history.json`
- 7天前的记录会自动清理

## 未来扩展

- [ ] 接入LLM API实现语义判断
- [ ] 支持更多推送渠道
- [ ] 添加视频分类功能

## License

MIT

