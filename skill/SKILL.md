---
name: sanskrit-study
description: 基于本机部署的 OpenMAIC（多智能体 AI 互动课堂平台）开展梵语学习。当用户要求学梵语、上梵语课、打开/继续梵语课堂、生成新梵语课程、把梵语教材做成课堂，或询问 OpenMAIC 本地部署与课堂生成怎么做时使用。技能提供：OpenMAIC 服务检查与启动、已有梵语课堂打开、新课堂生成（上传教材→AI 生成→交付链接）、完整部署 SOP（references/openmaic-howto.md）。上课时一律用系统浏览器（Edge/Chrome）打开课堂（豆包内置浏览器不支持语音输入权限）。
---

# 梵语学习（基于 OpenMAIC）

## 核心对象

- **OpenMAIC 服务**：`http://localhost:3000`，项目根 `C:\OpenMAIC`（Next.js 16 + PostgreSQL 16，服务端生成课堂，单用户模式，无需登录）
- **已有梵语课堂**：「梵语入门：零基础系统教程」温润男声版 = `http://localhost:3000/classroom/stage-PWy97xeG2F2T`（25 场景，4 个 AI 智能体，中文授课+梵语术语双语；教材为《Sanskrit for Beginners》，配音=温润男声）；旧版（御姐音色，18 场景）`stage-fvL1XzATAqYN` 仍可访问
- **模型**：MiniMax Token Plan（Key 在 `C:\OpenMAIC\.env.local` 的 `MINIMAX_API_KEY`，勿外泄）；`openmaic.yml` 中 `llm` 与 `course.content` 槽位 = `minimax:MiniMax-M3`
- **教材**：本仓库 `materials/`（Sanskrit-for-Beginners.pdf 1.1MB、vyakarana-传统梵语语法.pdf 1.2MB；Intensive-course-in-Sanskrit.pdf 约 39MB，体积大按需从 Learn-sanskrit 仓库获取）；离线应用 `web/梵语学习.html`（48 字母/17 课/语法，可作内容参考）

## 工作流

### 1. 检查服务状态

访问 `GET http://localhost:3000/api/health`：
- `200 + {"success":true,"status":"ok"}` → 服务正常，进入第 2 步。
- 连接失败 → 服务未启动，按「启动服务」启动后重试。

### 2. 选择课堂

- **继续已有课堂**：用系统浏览器打开 `http://localhost:3000/classroom/stage-PWy97xeG2F2T`（温润男声版，推荐；或用户指定的课堂 ID），打开前用 GET 验证返回 200。
- **生成新课堂**：走第 3 步。常见需求：不同主题（如语法深化、佛教文献阅读、实用会话）、不同教材（换用 Intensive 或 vyakarana PDF）、不同难度、**不同配音音色**（用 `--voice` 指定，见第 3 步）。

### 2.5 打开课堂（必做：系统浏览器，非内置浏览器）

**上课必须用系统浏览器（Edge/Chrome）打开课堂 URL，绝不在豆包内置浏览器打开**——内置浏览器（webview）没有麦克风权限授权通道，语音输入必然被拒（`not-allowed`）；系统浏览器权限机制完整，首次点「允许」即可。Windows 下执行：

```powershell
# 优先 Edge（本机已装），Chrome 存在时也可用；跳过 IE（不支持语音识别）
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$browser = (Test-Path $edge) -and (Test-Path $chrome) ? $chrome : $edge
if (Test-Path $browser) { Start-Process $browser "http://localhost:3000/classroom/stage-PWy97xeG2F2T" }
# 若两者皆无，用默认浏览器打开但提示语音输入可能不可用
else { Start-Process "http://localhost:3000/classroom/stage-PWy97xeG2F2T" }
```

打开后提醒用户：页面首次使用麦克风会弹权限请求，点「允许」；误点「阻止」则到地址栏左侧站点设置改为允许。

### 3. 生成新课堂（核心）

用 `scripts/generate_classroom.py`（本机已验证可用的全自动流程）：

```bash
python scripts/generate_classroom.py --requirement "为汉语母语者设计...梵语课程..." [--material "<教材路径>"] [--voice "温润男声"] [--resume <runId>]
```

脚本自动完成：暖启动 owner cookie（持久化在 `C:\OpenMAIC\_cookie.txt`）→ 上传教材（可选，上传即提取）→ 提交生成任务 → 轮询进度 → 输出课堂 URL。参数：
- `--requirement`：教学要求（中文）。要控制场景类型时写明，如「只使用幻灯片讲解与测验场景，不要交互式模拟」。
- `--material`：教材 PDF 路径；省略则 AI 凭知识生成。
- `--voice`：配音音色中文名（可选）。**关键：想换老师声音必须传此参数**——不传时走无头接口，服务端回落到默认「御姐音色」，首页换的音色不会生效。可选值：温润男声 / 电台男主播 / 温暖少女 / 新闻女声 / 少女音色 / 精英青年 / 御姐音色。指定后新课堂全程用该音色配音（走浏览器同级接口 `/api/generation-runs`）。
- `--resume <runId>`：任务失败暂停后从中断点继续（OpenMAIC 支持 retry）。

生成耗时约 5–15 分钟（25 场景约 10 分钟），过程输出进度行。

### 4. 交付

- **按第 2.5 步用系统浏览器打开课堂**，再交付链接 `http://localhost:3000/classroom/<stageId>` 并说明课堂主题/场景数/教材。
- 上课能力：AI 教师语音讲解、白板演示、测验判分、随时提问；语音输入需在系统浏览器中使用。

## 故障排查速查

| 现象 | 处理 |
|---|---|
| health 连接失败 | PostgreSQL 服务 `postgresql-x64-16` 是否 Running；`C:\OpenMAIC` 下 `pnpm dev` 是否在跑（无则启动，见「启动服务」） |
| 生成某场景反复失败并暂停 | 多为交互式场景生成不过校验。确认 `openmaic.yml` 的 `llm`/`course.content` 指向 `MiniMax-M3`（M2.7 会失败）；改配置后重启服务，再用 `--resume` 继续 |
| 生成任务报 `ACTIVE_RUN_LIMIT` | 该 owner 有进行中任务，等待或先完成旧任务 |
| 新浏览器看不到课堂 | 已启用单用户模式（`OWNER_SINGLE_USER=true`），正常情况下所有浏览器共享课程库；若被改动过，检查 `.env.local` |
| 语音输入（麦克风）不可用 | 在豆包内置浏览器中属正常限制（webview 无麦克风授权通道，报 `not-allowed`）。按第 2.5 步改用 Edge/Chrome 打开并授权麦克风；系统层（Windows 隐私）本机已放行 |

## 启动服务

服务未运行时（如重启电脑后）按此启动（Windows，PowerShell）：

```powershell
# 1. 确认 PostgreSQL 服务
Get-Service postgresql-x64-16   # 非 Running 则 Start-Service postgresql-x64-16
# 2. 启动 OpenMAIC（在 C:\OpenMAIC，后台常驻）
Set-Location C:\OpenMAIC; pnpm dev
# 3. 等待 30–60 秒编译，然后验证
Invoke-WebRequest http://localhost:3000/api/health
```

更正规的常驻方案（计划任务/服务）见 `references/openmaic-howto.md` 的「常驻化建议」。

## OpenMAIC 是怎么做的

完整部署（从零：克隆→依赖→PostgreSQL→配置→启动）、课堂生成机制（两阶段流水线、API 契约、轮询）、本机部署现状与全部踩坑记录：**先读 `references/openmaic-howto.md`**，它是本技能的知识底座，回答「OpenMAIC 怎么做」的一切问题。

## 资源

- `scripts/generate_classroom.py` — 课堂生成全自动脚本（上传教材/提交/轮询/交付，支持断点续跑）
- `scripts/health_check.py` — 服务与数据库健康检查（含一键启动提示）
- `references/openmaic-howto.md` — OpenMAIC 完整做法：部署 SOP、配置详解、课堂生成机制、本机现状、踩坑记录
