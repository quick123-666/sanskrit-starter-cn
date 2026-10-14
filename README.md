# sanskrit-starter-cn

给中文用户的梵语入门学习项目：**AI 互动课堂 + 生成工具 + 离线学习应用** 三合一。

以《Sanskrit for Beginners》为内容依据，面向零基础汉语母语者，系统覆盖：天城体字母、罗马转写（IAST）、发音规则（送气音/卷舌音/连音）、常用词汇短语、名词性数格与动词变化基础、简单句子读写、梵语文化背景。

## 特性

- **AI 互动课堂**（OpenMAIC 驱动）：25 个场景循序渐进，AI 教师语音讲解 + 白板演示 + 测验判分 + 随时提问，全程中文授课、梵语双语术语
- **音色可选**：7 种中文配音音色（温润男声 / 电台男主播 / 温暖少女 / 新闻女声 / 少女音色 / 精英青年 / 御姐音色），生成课堂时用 `--voice` 指定
- **一键生成新课堂**：给定需求（+可选教材 PDF），自动完成 大纲→场景→配音 全流程（`skill/scripts/generate_classroom.py`）
- **离线学习应用**：`web/` 单文件 HTML（48 字母表 / 17 课 / 语法），双击即用
- **Skill 封装**：`skill/` 是可直接挂载给 AI Agent 的「梵语学习」技能（含完整部署手册与脚本）

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
