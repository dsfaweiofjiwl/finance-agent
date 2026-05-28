# 美股深度分析 Agent

基于 LLM 的美股投资研究自动化系统，从数据采集到报告生成的全流程 Agent 编排。

## 核心能力

- **多阶段流水线**：宏观数据采集 → 宏观分析 → 动态选股 → 个股分析 → 报告整合
- **Agent 自主搜索**：LLM + 工具调用（Web Search / Web Fetch），Agent 自主搜索并验证最新市场数据
- **断点续跑**：每个阶段独立 checkpoint，中断后从断点恢复，不重复消耗 token
- **并行调度**：ThreadPoolExecutor 最多 5 路并发搜索 + 2 路并发个股分析
- **动态选股**：LLM 根据宏观环境动态筛选标的 + 历史推荐冷却机制 + 预处理轮换
- **双格式输出**：Markdown + HTML 报告

## 快速开始

```bash
pip install -r requirements.txt
# 配置 .env 文件（参考 .env.example）
# 至少需要一个搜索 API Key（Serper/Brave/Bing/Google 任选其一）
python run_analysis.py
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | LLM API Key（兼容 OpenAI 格式） |
| `OPENAI_BASE_URL` | LLM API 地址 |
| `SEARCH_BACKEND` | 搜索后端：serper / brave / bing / google / exa |
| `SERPER_API_KEY` | Serper 搜索 Key（推荐，1000 次/月免费） |

## 架构

```
agent/
  workflow.py      # 五阶段流水线编排
  llm_client.py    # LLM 调用封装
  tool_registry.py  # 工具注册中心
  stock_selector.py # 动态选股 + 冷却机制
  history_tracker.py # 历史推荐追踪
tools/
  web_search.py    # 多后端搜索（Serper/Brave/Bing/Google/Exa）
  web_fetch.py     # 网页内容抓取
prompt/            # 各阶段 Prompt 模板
data/checkpoints/  # 断点续跑数据
output/            # 生成的分析报告
```

## 技术栈

Python / OpenAI API / ThreadPoolExecutor / Markdown / HTML
