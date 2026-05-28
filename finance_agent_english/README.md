# Finance Agent for OpenClaw

专为 [OpenClaw](https://openclaw.com) 设计的**Python金融投研Agent框架**，基于ReAct工作流与分层Prompt架构，生成美股深度分析报告并支持浏览器可视化查看。

## 架构设计

### 分层Prompt设计（核心）

```
config/
├── IDENTITY.md  ← 身份定位 - 告诉模型它是谁该做什么
├── SOUL.md      ← 核心原则 - 数据先行、交叉验证、风控规则
├── Finance.md   ← 数据源手册 - 权威数据源列表，可不断更新
└── meigu2.md    ← 输出格式 - 完整的章节模板，填空式输出
```

**设计思路**：关注点分离，改一个层不影响其他层，易于迭代维护。

### 工作流：ReAct 循环

```
Reasoning：我还需要哪些数据？
   ↓
Acting：调用工具搜索/获取网页
   ↓
Observation：拿到结果
   ↓
Repeat：直到数据足够
   ↓
Generate：生成最终报告
```

**特点**：必须先搜索再分析，从根源减少幻觉，每个关键数据都交叉验证。

## 功能特性

✅ **为OpenClaw而生** - 完全适配OpenClaw生态，纯Python实现，所有代码可修改
✅ **多后端搜索** - 支持 Serper/Exa/Brave/Bing/Google，改环境变量就切换
✅ **Prompt缓存就绪** - 节省30%~80% token成本
✅ **工具可扩展** - 添加新工具只需要新建一个文件
✅ **风控内置** - 数据优先级、缺失标注、交叉验证规则都在prompt层面卡死
✅ **Web报告渲染** - 分析完成后自动生成HTML报告，本地HTTP服务器一键在浏览器查看，无file://安全限制
✅ **交互式API Key管理** - `manage_env.py` 一键清除/替换API Key
✅ **可选飞书推送** - 生成报告自动推送到飞书群（默认注释，需要启用即可）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

```bash
# 复制模板
cp .env.example .env

# 交互式配置API Key
python manage_env.py
```

### 3. 运行分析

```bash
# 推荐：实时查看进度
PYTHONUNBUFFERED=1 python3 -u run_analysis.py

# 或直接运行
python run_analysis.py
```

报告生成后保存在 `output/` 目录，同时在终端输出 `http://` 链接。

### 4. 查看报告

```bash
# 启动本地 HTTP 服务器，查看最新报告（推荐）
python open_report.py --latest

# 交互式选择历史报告
python open_report.py

# 查看指定报告
python open_report.py <filename>
```

启动后会自动在浏览器中打开报告，终端显示 `http://127.0.0.1:xxxx` 地址。按 Ctrl+C 关闭服务器。

### 5. （可选）配置定时自动运行

编辑crontab:
```bash
crontab -e
```

添加一行（每天工作日9点运行）:
```
0 9 * * 1-5 cd /Users/cow/Desktop/finance_agent_english && /usr/bin/python3 run_analysis.py >> logs/cron.log 2>&1
```

## 项目结构

```
finance_agent_english/
├── config/                 ← 配置和prompt（纯文本，好改）
│   ├── IDENTITY.md
│   ├── SOUL.md
│   ├── Finance.md
│   └── meigu2.md
├── agent/                 ← 核心框架代码
│   ├── llm_client.py      ← LLM API封装，带prompt缓存
│   ├── prompt_builder.py  ← 拼装分层prompt
│   ├── tool_registry.py   ← 工具注册管理
│   └── workflow.py        ← ReAct工作流调度
├── tools/                 ← 工具实现
│   ├── web_search.py      ← 多后端搜索
│   └── web_fetch.py       ← 网页内容提取
├── output/                ← 生成的报告保存在这里（.md + .html）
├── data/                  ← 缓存数据
├── prompt/                ← 各阶段prompt模板
│   ├── 01_macro_collect.md
│   ├── 02_macro_analyze.md
│   ├── 03_stock_analyze.md
│   └── 04_final_compile.md
├── run_analysis.py        ← 主入口
├── open_report.py         ← 报告查看工具（按需打开链接）
├── web_renderer.py        ← Markdown→HTML渲染引擎
├── manage_env.py          ← API Key管理工具
├── requirements.txt       ← 依赖列表
├── .env.example           ← 环境变量模板
└── README.md              ← 本文档
```

## 配置说明

### LLM配置

兼容任何**OpenAI chat completions**格式的API:
- 火山方舟（默认配置，和OpenClaw一致）
- OpenAI 官方
- 通义千问
- DeepSeek
- 任何其他兼容OpenAI格式的服务

### 搜索后端配置

在 `.env` 中设置 `SEARCH_BACKEND`:

| 后端 | 免费额度 | 说明 |
|------|---------|------|
| `serper` | 1000次/月免费 | **推荐**，Google搜索结果，API稳定 |
| `exa` | 500次/月免费 | AI原生搜索，OpenClaw默认 |
| `brave` | 20次/分钟 | 免费额度大 |
| `bing` | 1000次/月免费 | 微软官方 |
| `google` | 100次/天免费 | Google Custom Search |

只需要设置对应的API Key，框架自动切换。

### 飞书推送（可选）

1. 在 `.env` 中添加:
```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=your_secret
FEISHU_CHAT_ID=oc_xxx
```

2. 在 `agent/workflow.py` 中取消注释飞书推送代码即可启用。

## API Key管理

使用 `manage_env.py` 管理API Key:

```bash
python manage_env.py
```

功能:
- 查看当前配置（掩码显示，保护隐私）
- 一键清除所有API Key（分享代码前用这个）
- 交互式替换单个/多个API Key

## 核心设计原则（金融投研场景）

| 原则 | 实现 |
|------|------|
| **数据先行** | 必须先搜索再分析，禁止跳过工具直接生成 |
| **交叉验证** | 每个关键数据至少两个来源，不一致优先官方 |
| **宁缺毋滥** | 数据拿不到标注 `[数据暂缺]`，绝不猜测 |
| **时效性第一** | 每个数据必须标注日期，禁用过时数据 |
| **板块均衡** | 十大股票必须至少2只金融龙头，避免过度集中科技 |
| **风控明确** | 每个股票都给买入区间+明确止损，严格控制风险 |

## 学习知识点

这个项目演示了生产级agent开发的最佳实践:

1. **分层Prompt工程** - 分离身份/原则/数据源/格式，易于维护
2. **ReAct工作流** - Reasoning + Acting 循环，让LLM自己控制搜索节奏
3. **可插拔工具** - 多后端搜索，切换不需要改代码
4. **Web渲染** - Markdown转自包含HTML，本地HTTP服务器提供无限制的浏览器访问
5. **成本优化** - Prompt缓存省大钱
6. **工程规范** - 环境变量存敏感信息，requirements明确依赖，结构清晰

## 授权

仅供OpenClaw内部投研使用。
