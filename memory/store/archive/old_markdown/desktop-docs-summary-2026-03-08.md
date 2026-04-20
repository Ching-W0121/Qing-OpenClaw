# 桌面 Word 文档读取记录 - 产品级求职 Agent

## 📄 文档信息

### 文档 1：产品级求职 agent.docx
- **创建时间**: 2026-03-08 00:08
- **内容**: 完整的求职 Agent 系统架构设计 v1.0

### 文档 2：求职 agent 补充.docx
- **创建时间**: 2026-03-08 00:58
- **内容**: v1.1 架构升级建议

---

## 📋 文档 1：产品级求职 agent v1.0

### 一、系统定位
**产品级逻辑驱动求职系统**，不是简单脚本，而是完整系统架构。
- 用户：庆
- Agent：青（OpenClaw Agent）
- 目标：AI 求职系统 + 产品级结构

### 二、系统分层架构

```
用户 (庆)
  ↓
Agent 决策层 (青)
  ↓
工具调度层
  ↓
数据处理层
  ↓
推荐匹配层
  ↓
自动执行层
  ↓
数据库层
```

**详细结构**：
```
User
  ↓
OpenClaw Agent (青)
  ↓
Tools Layer
  ├── Job Search Tool
  ├── Resume Parser Tool
  ├── JD Parser Tool
  ├── Matching Engine
  ├── Recommendation Engine
  ↓
Database Layer
  ├── Jobs DB
  ├── Users DB
  ├── Match DB
  ↓
Automation Layer
  ├── Playwright Browser
  ├── Apply Executor
```

### 三、Agent 核心职责
**青不直接执行代码，而是调度工具**

**职责**：
1. 理解用户意图
2. 调用 Resume Parser 解析用户简历
3. 调用 Job Search Tool 搜索职位
4. 调用 JD Parser 解析 JD
5. 调用 Matching Engine 计算匹配
6. 调用 Recommendation Engine 推荐职位

**Agent 只做**：
- 理解
- 调度工具
- 呈现结果

### 四、系统模块划分（7 大模块）

1. **Agent 决策**
2. **简历解析**
3. **职位搜索**
4. **JD 解析**
5. **匹配引擎**
6. **推荐系统**
7. **自动投递**

### 五、数据流转

```
用户上传简历
  ↓
Resume Parser
  ↓
Candidate Profile
  ↓
Job Search Tool
  ↓
Job List
  ↓
JD Parser
  ↓
Structured Job Data
  ↓
Matching Engine
  ↓
Match Score
  ↓
Recommendation Engine
  ↓
Top Jobs
  ↓
用户选择
  ↓
Apply Executor
```

### 六、数据库结构（PostgreSQL）

**users 表**：
- id, name, education, experience_years
- skills, tools, industry
- target_jobs, expected_city, expected_salary

**jobs 表**：
- id, title, company, city
- salary_min, salary_max
- experience, education, industry
- skills, tools, platform, url, created_at

**matches 表**：
- id, user_id, job_id
- match_score, industry_score, skill_score, experience_score

**applications 表**：
- id, user_id, job_id, status, applied_at, hr_reply

### 七、匹配引擎结构

**4 个核心模块**：
1. Industry Matcher（行业匹配）
2. Skill Matcher（技能匹配）
3. Rule Matcher（规则匹配）

**匹配流程**：
```
行业匹配 → 技能匹配 → 经验匹配 → 岗位匹配 → 薪资匹配 → 学历匹配
  ↓
match_score
```

### 八、推荐系统结构

**排序维度**：
- 匹配度
- 薪资
- 经验
- 行业

**流程**：
```
Job List → 过滤 → 打分 → 排序 → Top N
```

**推荐数量**：Top 10

### 九、自动执行系统

**技术栈**：Playwright

**执行流程**：
```
登录招聘网站 → 搜索职位 → 抓取职位 → 解析 JD → 自动投递 → 发送消息
```

**当前目标平台**：https://landing.zhipin.com

### 十、项目目录结构

```
qing-agent/
├── agent/
│   ├── agent_core.py
│   └── planner.py
├── tools/
│   ├── resume_parser.py
│   ├── job_search.py
│   ├── jd_parser.py
│   ├── matcher.py
│   └── recommender.py
├── automation/
│   ├── browser.py
│   └── apply_executor.py
├── database/
│   ├── models.py
│   └── db.py
├── services/
│   ├── job_service.py
│   └── match_service.py
├── config/
│   └── settings.py
├── prompts/
│   ├── resume_prompt.txt
│   └── jd_prompt.txt
└── main.py
```

### 十一、技术栈

**基础环境**：
- Python 3.11
- Node.js
- PostgreSQL
- Redis

**Python 依赖**：
```
fastapi, uvicorn, pydantic, sqlalchemy
psycopg2-binary, redis, openai
sentence-transformers, numpy, pandas
playwright, python-dotenv, tqdm
```

**Embedding 模型**：bge-large-zh

### 十二、OpenClaw 工具注册

需要注册的工具：
- ResumeParserTool
- JobSearchTool
- JDParserTool
- MatchTool
- RecommendTool
- ApplyTool

### 十三、Prompt 模板

**简历解析 Prompt**：提取学历、专业、工作年限、行业、技能、工具、目标职位等

**JD 解析 Prompt**：提取职位名称、公司、技能要求、经验要求、学历要求、工具要求、薪资范围、行业

### 十四、推荐话术模板

```
匹配度 92%

行业匹配：✓
经验：3-5 年
技能：品牌策划、营销推广
薪资：10k-15k

已根据您的需求匹配到该职位
```

---

## 📋 文档 2：求职 agent 补充 v1.1 架构升级

### 核心问题（v1.0 的 3 个结构性问题）

1. ❌ **行业匹配没有真正进入算法核心**
2. ❌ **招聘平台适配层不够抽象**（未来扩展难）
3. ❌ **Agent 调度逻辑还停留在"API 调用"**，没有形成真正 Agent

### 升级方案：4 个关键模块

#### 1️⃣ 行业匹配系统（Industry Graph）

**行业树结构**：
```json
{
  "广告": ["品牌咨询", "营销策划", "创意代理"],
  "互联网": ["电商", "SaaS", "内容平台", "AI"],
  "消费品": ["快消", "新消费", "文旅"],
  "科技": ["人工智能", "芯片", "SaaS"]
}
```

**行业相似度算法**：
- 相同行业 = 1.0
- 父子行业 = 0.8
- 同级行业 = 0.6
- 无关行业 = 0.2

**示例**：
- 用户：广告 → 职位：品牌咨询 = 0.8
- 用户：广告 → 职位：电商 = 0.3

#### 2️⃣ 平台适配器层（Platform Adapter）

**问题**：避免未来出现大量 if-else

**结构**：
```
platform/
├── base_adapter.py
├── boss_adapter.py
├── zhilian_adapter.py
└── liepin_adapter.py
```

**Base Adapter**：
```python
class BaseAdapter:
    async def search_jobs(self, keyword):
        raise NotImplementedError
    
    async def get_job_detail(self, url):
        raise NotImplementedError
    
    async def apply(self, job_url):
        raise NotImplementedError
```

#### 3️⃣ 任务流水线（Pipeline）

**现在的问题**：所有操作是散的

**完整流程**：
```
Resume Upload
  ↓
Parse Resume
  ↓
Create User Profile
  ↓
Search Jobs
  ↓
Parse JD
  ↓
Calculate Match
  ↓
Rank Jobs
  ↓
Recommend
  ↓
Apply
```

#### 4️⃣ Agent 决策系统（Planner 升级）

**从 API orchestrator 升级为真正的 Agent**

**决策逻辑**：
```
用户上传简历
  ↓
Agent 解析用户意图
  ↓
启动 Pipeline
  ↓
结果分析
  ↓
策略推荐
```

**Planner 示例**：
```python
class Planner:
    def plan(self, intent):
        if intent == "find_job":
            return [
                "parse_resume",
                "search_jobs",
                "calculate_match",
                "recommend_jobs"
            ]
        
        if intent == "apply":
            return [
                "open_job",
                "submit_application"
            ]
```

### 五、匹配算法升级（7 维）

**原来 6 维 → 升级 7 维**

**公式**：
```
match_score = 
  industry * 0.25 +  # 行业 25%
  skill * 0.25 +     # 技能 25%
  experience * 0.15 + # 经验 15%
  salary * 0.10 +    # 薪资 10%
  location * 0.10 +  # 地点 10%
  education * 0.10 + # 学历 10%
  tools * 0.05       # 工具 5%
```

**核心**：行业 + 技能 = 50%

### 六、最终目录结构（v1.1）

```
qing-agent/
├── agent/
│   ├── planner.py
│   └── agent_core.py
├── pipeline/
│   └── job_pipeline.py
├── services/
│   ├── job_service.py
│   ├── match_service.py
│   └── resume_service.py
├── platform/
│   ├── base_adapter.py
│   ├── boss_adapter.py
│   └── zhilian_adapter.py
├── tools/
│   ├── resume_parser.py
│   ├── jd_parser.py
│   ├── matcher.py
│   ├── industry_matcher.py
│   └── recommender.py
├── database/
│   ├── db.py
│   ├── models.py
│   └── cache.py
├── config/
│   └── settings.py
├── data/
│   └── industry_tree.json
├── routes/
│   ├── users.py
│   ├── jobs.py
│   ├── matches.py
│   └── applications.py
└── main.py
```

### 七、系统能力

**当前能力**：
1. 解析简历
2. 理解职业
3. 搜索岗位
4. 评估岗位
5. 推荐岗位
6. 自动投递
7. 追踪进度

**未来扩展**：
- 自动改简历
- 自动写求职信
- 自动回复 HR
- 自动跟进面试

### 八、下一步最关键

**JD 解析器（JD Parser）** 是核心缺失模块

**JD 解析要提取**：
- 技能
- 工具
- 经验
- 学历
- 行业
- 岗位类型

**这个模块决定匹配准确率 80% 以上**

---

## 📊 与昨天 HEARTBEAT 任务的关联

### 当前执行的任务（HEARTBEAT.md）
- ✅ 每天 10:00 搜索 BOSS 直聘
- ✅ 按匹配标准筛选
- ✅ 推送给用户
- ✅ 30 天去重

### 与产品级 Agent 的关系

**当前任务** = 产品级 Agent 的 **Job Search + Match + Recommend** 模块的简化版

**差异**：
| 维度 | 当前 HEARTBEAT 任务 | 产品级 Agent v1.1 |
|------|-------------------|------------------|
| 架构 | 简单脚本 | 分层架构 |
| 匹配 | 规则匹配 | 7 维算法 + 行业图谱 |
| 平台 | BOSS 直聘 only | 多平台适配 |
| 执行 | 人工投递 | 自动投递 |
| 数据 | Markdown 记录 | PostgreSQL |

**演进路径**：
1. 当前：验证匹配逻辑和推送流程
2. 短期：完善 JD 解析器
3. 中期：实现行业匹配系统
4. 长期：完整产品级 Agent

---

## 📝 读取时间
2026-03-08 12:03 (Asia/Shanghai)
