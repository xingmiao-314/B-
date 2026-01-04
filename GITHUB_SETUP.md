# GitHub 仓库配置指南

## 步骤 1：在 GitHub 上创建新仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 **+** 号，选择 **New repository**
3. 填写仓库信息：
   - **Repository name**: `bilibili-monitor` (或你喜欢的名字)
   - **Description**: B站UP主视频监控系统
   - **Visibility**: 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 **Create repository**

## 步骤 2：连接本地仓库到 GitHub

在本地项目目录下运行以下命令（将 `YOUR_USERNAME` 和 `YOUR_REPO_NAME` 替换为你的实际信息）：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

**或者使用 SSH（如果你配置了SSH密钥）：**

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 步骤 3：配置 GitHub Secrets（重要！）

这是让推送功能正常工作的关键步骤：

1. 在 GitHub 仓库页面，点击 **Settings**（设置）
2. 在左侧菜单中找到 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写信息：
   - **Name**: `FEISHU_WEBHOOK`
   - **Secret**: 你的飞书机器人 Webhook URL（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/...`）
5. 点击 **Add secret**

### 如何配置飞书机器人？

1. 在飞书群聊中，点击右上角设置 → **群机器人** → **添加机器人**
2. 选择 **自定义机器人**
3. 设置机器人名称和头像
4. **重要**：在"安全设置"中，选择"自定义关键词"，添加关键词：`AIGC`（必须包含，否则消息无法发送）
5. 复制生成的 Webhook URL
6. 将 Webhook URL 填入 GitHub Secrets 的 `FEISHU_WEBHOOK` 中

## 步骤 4：验证配置

1. 在 GitHub 仓库页面，点击 **Actions** 标签
2. 你应该能看到 "每日抓取" workflow
3. 点击 workflow，然后点击右侧的 **Run workflow** 按钮
4. 选择分支（通常是 `main`），点击 **Run workflow**
5. 等待运行完成，检查是否有错误

## 步骤 5：查看运行结果

- 在 **Actions** 页面可以看到每次运行的日志
- 如果配置正确，运行后会自动创建 `history.json` 文件
- 如果有新视频符合条件，你会收到飞书机器人推送

## 常见问题

### Q: 推送失败怎么办？
A: 检查以下几点：
- `FEISHU_WEBHOOK` secret 是否正确配置
- 飞书机器人 Webhook URL 是否有效
- 飞书机器人安全设置中是否包含 "AIGC" 关键词（必须包含）
- 网络连接是否正常

### Q: history.json 没有被自动提交？
A: 检查：
- GitHub Actions 是否有 `contents: write` 权限（已在 workflow 中配置）
- 是否有文件变化（如果没有新视频，文件不会变化）

### Q: 如何修改运行时间？
A: 编辑 `.github/workflows/daily.yml` 文件中的 cron 表达式：
```yaml
- cron: '0 1 * * *'  # 每天北京时间 9:00
```
cron 格式：`分钟 小时 日 月 星期`（UTC时间）

## 下一步

配置完成后，系统会：
- ✅ 每天自动运行（北京时间 9:00）
- ✅ 自动检测新视频
- ✅ 自动发送推送通知
- ✅ 自动保存运行记录到仓库

享受自动化监控的便利吧！🎉


