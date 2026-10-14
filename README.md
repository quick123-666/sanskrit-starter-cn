# sanskrit-starter-cn

给中文用户的梵语入门学习项目：**AI 互动课堂 + 生成工具 + 离线学习应用** 三合一。

以《Sanskrit for Beginners》为内容依据，面向零基础汉语母语者，系统覆盖：天城体字母、罗马转写（IAST）、发音规则（送气音/卷舌音/连音）、常用词汇短语、名词性数格与动词变化基础、简单句子读写、梵语文化背景。

## 特性

- **AI 互动课堂**（OpenMAIC 驱动）：25 个场景循序渐进，AI 教师语音讲解 + 白板演示 + 测验判分 + 随时提问，全程中文授课、梵语双语术语
- **音色可选**：7 种中文配音音色（温润男声 / 电台男主播 / 温暖少女 / 新闻女声 / 少女音色 / 精英青年 / 御姐音色），生成课堂时用 `--voice` 指定
- **一键生成新课堂**：给定需求（+可选教材 PDF），自动完成 大纲→场景→配音 全流程（`skill/scripts/generate_classroom.py`）
- **离线学习应用**：`web/` 单文件 HTML（48 字母表 / 17 课 / 语法），双击即用
- **Skill 封装**：`skill/` 是可直接挂载给 AI Agent 的「梵语学习」技能（含完整部署手册与脚本）

## 技术特点

### 课堂平台（OpenMAIC）

- **技术栈**：Next.js 16（React 19 / TypeScript 5）+ LangGraph 多智能体编排 + pnpm workspace + Tailwind 4，数据存储于 PostgreSQL 16
- **两阶段课堂生成流水线**：先由 AI 产出结构化课堂大纲（outline），再逐场景生成内容 / 动作脚本 / TTS 配音；全程在服务端常驻进程运行，关页面不中断，进程崩溃可断点续跑（`retry`）
- **多智能体课堂**：课堂内有 AI 教师 + AI 同学智能体，支持幻灯片讲解（语音 + 聚光灯 / 白板）、交互式模拟、测验判分、项目制学习（PBL）、随时提问
- **模型服务商中立**：通过 `openmaic.yml` 的槽位（slot）机制声明各环节模型——`llm` / `course.content` / `image` / `tts` / `webSearch`；本项目使用 MiniMax Token Plan（MiniMax-M2.7 / M3），一个 Key 覆盖对话、图像、TTS 与搜索
- **单用户模式**（`OWNER_SINGLE_USER=true`）：所有浏览器共享同一课程库，无需登录、无 cookie 隔离问题

### 语音方案

- 课堂配音使用 **MiniMax TTS**，内置 7 种中文音色映射（温润男声 / 电台男主播 / 温暖少女 / 新闻女声 / 少女音色 / 精英青年 / 御姐音色）
- 音频在**课堂生成时合成**并固化到场景中，因此换音色必须重新生成课堂，而非在界面切换（页面设置仅影响后续新生成任务）
- 语音输入依赖浏览器原生 ASR，需在支持麦克风授权的系统浏览器（Edge/Chrome）中使用

### 自动化脚本（`skill/scripts/`）

- **纯 Python 标准库实现**（urllib / http.cookiejar），零第三方依赖
- `generate_classroom.py`：cookie 暖启动 → 教材上传（原始字节体 + 后台提取）→ 提交生成任务 → 轮询进度 → 输出课堂 URL；支持 `--voice` 指定音色、`--resume` 断点续跑
- `health_check.py`：一键检查服务 / 数据库 / 模型配置状态

### 离线学习应用（`web/`）

- **单文件 HTML**：纯原生 JS + CSS，无任何外部依赖与网络请求，双击即用
- 数据模型：48 个基础字母（13 元音 + 33 辅音 + 2 辅助符号）卡片，含天城体 / IAST 转写 / 中文释义 / 发音部位分组
- 学习功能：字母掌握标记、发音规则（五发音部位、清浊送气、长短元音、复合元音）、17 课核心课程、波你尼语法概览、学习打卡
- **本地持久化**：字母掌握进度与打卡日志存于浏览器 `localStorage`，无需账号

## 目录结构

```
sanskrit-starter-cn/
├── README.md
├── LICENSE                 MIT
├── docs/
│   ├── 部署与使用指南.md     OpenMAIC 完整部署 SOP（脱敏版）
│   └── 课堂说明.md           课堂链接、语音输入、换音色说明
├── skill/                  梵语学习 Agent 技能（SKILL.md + scripts + references）
├── web/                    离线学习应用（梵语学习.html + assets）
└── materials/              教材 PDF（公开开源教材）
```

## 快速开始

### 方式一：直接上 AI 课堂（需要本机部署 OpenMAIC）

```powershell
# 1. 部署（详见 docs/部署与使用指南.md）：Node 22+/pnpm 10+/PostgreSQL 16
git clone https://github.com/THU-MAIC/OpenMAIC.git C:\OpenMAIC
cd C:\OpenMAIC && pnpm install
# 配置 .env.local（模型 Key、DATABASE_URL、OWNER_SINGLE_USER=true）与 openmaic.yml
pnpm dev
# 2. 打开课堂
start msedge http://localhost:3000/classroom/stage-PWy97xeG2F2T
```

课堂默认链接：`http://localhost:3000/classroom/stage-PWy97xeG2F2T`（25 场景 · 温润男声配音）。

### 方式二：生成自己的新课堂

```bash
python skill/scripts/generate_classroom.py \
  --requirement "为零基础汉语母语者设计...梵语课程..." \
  --material "materials/Sanskrit-for-Beginners.pdf" \
  --voice "温润男声"
```

### 方式三：离线学习

直接双击打开 `web/梵语学习.html`，无需任何服务。

## 安全说明

- 本仓库**不含任何密钥**：模型 API Key 请自行填写在部署机的 `.env.local`，数据库密码在文档中为占位符 `<YOUR_DB_PASSWORD>`
- 课堂数据存储在部署机本地 PostgreSQL，不随仓库分发

## 致谢

- 课堂平台：OpenMAIC（THU-MAIC，MIT 协议）
- 教材：Sanskrit for Beginners / Vyakarana 传统梵语语法（公开学习资料）
