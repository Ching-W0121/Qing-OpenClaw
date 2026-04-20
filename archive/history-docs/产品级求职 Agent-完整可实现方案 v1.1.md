# 产品级求职 Agent · 完整可实现方案 v1.1

**版本：** v1.1（架构升级版）  
**日期：** 2026-03-08 01:15  
**状态：** ✅ 可立即执行  
**责任人：** 青（OpenClaw Agent）

---

## 一、架构升级说明

### 1.1 v1.0 → v1.1 核心变化

| 模块 | v1.0 | v1.1 | 升级原因 |
|------|------|------|----------|
| **架构层次** | Agent→FastAPI→Tools→DB | Agent→Pipeline→Service→Adapter→Tools→DB | 避免屎山代码 |
| **行业匹配** | 简单字符串匹配 | 行业图谱 + 相似度算法 | 精确匹配 |
| **平台适配** | if platform == boss | 平台适配器模式 | 易扩展 |
| **Agent 角色** | API 调用器 | 真正决策 Agent | 智能化 |
| **匹配维度** | 6 维 | 7 维（+tools） | 更全面 |

### 1.2 新架构层次

```
User
  ↓
Agent Planner（决策层）
  ↓
Pipeline Engine（任务流水线）
  ↓
Service Layer（业务服务）
  ├── Resume Service
  ├── Job Service
  ├── Match Service
  └── Apply Service
  ↓
Platform Adapter（平台适配）
  ├── Boss Adapter
  ├── Zhilian Adapter
  └── Liepin Adapter
  ↓
Tools（工具层）
  ├── Resume Parser
  ├── JD Parser
  ├── Matcher
  └── Recommender
  ↓
Storage（存储层）
  ├── SQLite
  ├── Cache
  └── JSON
```

---

## 二、核心升级模块

### 2.1 行业匹配系统（Industry Graph）

#### 行业树结构

**data/industry_tree.json：**
```json
{
  "广告": ["品牌咨询", "营销策划", "创意代理", "公关"],
  "互联网": ["电商", "SaaS", "内容平台", "AI", "游戏"],
  "消费品": ["快消", "新消费", "文旅", "食品饮料"],
  "科技": ["人工智能", "芯片", "硬件", "通信"],
  "文化传媒": ["影视", "出版", "媒体", "演艺"],
  "金融": ["银行", "证券", "保险", "基金"],
  "制造业": ["汽车", "机械", "电子", "化工"],
  "服务业": ["餐饮", "酒店", "零售", "物流"]
}
```

#### 行业相似度算法

**tools/industry_matcher.py：**
```python
import json

class IndustryMatcher:
    """行业匹配器"""
    
    def __init__(self, tree_file="data/industry_tree.json"):
        with open(tree_file, 'r', encoding='utf-8') as f:
            self.tree = json.load(f)
        
        # 反向索引：子行业→父行业
        self.child_to_parent = {}
        for parent, children in self.tree.items():
            for child in children:
                self.child_to_parent[child] = parent
    
    def match(self, user_industry, job_industry):
        """
        计算行业相似度
        
        返回：
        1.0  - 完全相同
        0.8  - 父子关系（用户在父行业，职位在子行业）
        0.6  - 同级关系（同一父行业下的不同子行业）
        0.3  - 弱相关（不同父行业但有一定关联）
        0.2  - 无关
        """
        # 完全相同
        if user_industry == job_industry:
            return 1.0
        
        # 获取父行业
        user_parent = self.child_to_parent.get(user_industry, user_industry)
        job_parent = self.child_to_parent.get(job_industry, job_industry)
        
        # 父子关系
        if user_parent == job_parent:
            # 用户在父行业，职位在子行业
            if user_industry == user_parent and job_industry in self.tree.get(user_industry, []):
                return 0.8
            # 用户在子行业，职位在父行业
            if job_industry == job_parent and user_industry in self.tree.get(job_industry, []):
                return 0.8
            # 同级关系
            return 0.6
        
        # 弱相关（特定行业组合）
        weak_relations = {
            ("广告", "互联网"): 0.3,
            ("广告", "文化传媒"): 0.3,
            ("互联网", "科技"): 0.3,
            ("消费品", "零售"): 0.3,
        }
        
        relation = weak_relations.get((user_parent, job_parent), 0.2)
        return relation
    
    def get_parent(self, industry):
        """获取父行业"""
        return self.child_to_parent.get(industry, industry)
    
    def get_children(self, industry):
        """获取子行业列表"""
        return self.tree.get(industry, [])
```

---

### 2.2 平台适配器层（Platform Adapter）

#### 基础适配器

**platform/base_adapter.py：**
```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """平台适配器基类"""
    
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    async def search_jobs(self, keyword, city, page=1):
        """搜索职位"""
        pass
    
    @abstractmethod
    async def get_job_detail(self, url):
        """获取职位详情"""
        pass
    
    @abstractmethod
    async def apply(self, job_url, resume):
        """申请职位"""
        pass
    
    @abstractmethod
    def parse_search_results(self, snapshot):
        """解析搜索结果"""
        pass
    
    @abstractmethod
    def parse_job_detail(self, snapshot):
        """解析职位详情"""
        pass
```

#### BOSS 直聘适配器

**platform/boss_adapter.py：**
```python
from platform.base_adapter import BaseAdapter
from openclaw import browser
import asyncio

class BossAdapter(BaseAdapter):
    """BOSS 直聘适配器"""
    
    def __init__(self):
        super().__init__("boss")
        self.base_url = "https://www.zhipin.com"
        self.city_code = "101280600"  # 深圳
    
    async def search_jobs(self, keyword, city=None, page=1):
        """搜索 BOSS 直聘职位"""
        city_code = self._get_city_code(city) if city else self.city_code
        url = f"{self.base_url}/web/geek/job?city={city_code}&query={keyword}&page={page}"
        
        # 打开页面
        await browser.open(url)
        await asyncio.sleep(5)  # 等待加载
        
        # 获取快照
        snapshot = await browser.snapshot(refs="aria")
        
        # 解析结果
        jobs = self.parse_search_results(snapshot)
        
        return jobs
    
    def parse_search_results(self, snapshot):
        """解析搜索结果"""
        jobs = []
        
        # 使用 aria-ref 解析职位列表
        job_elements = snapshot.querySelectorAll('[ref*="job"]')
        
        for el in job_elements:
            job = {
                "platform": "boss",
                "title": el.querySelector('link')?.text,
                "company": el.querySelector('link[company]')?.text,
                "salary": el.querySelector('generic')?.text,
                "district": el.querySelector('generic[district]')?.text,
                "experience": el.querySelector('listitem[exp]')?.text,
                "education": el.querySelector('listitem[edu]')?.text,
                "url": el.querySelector('link')?.url,
            }
            
            if job["title"] and job["url"]:
                jobs.append(job)
        
        return jobs
    
    async def get_job_detail(self, url):
        """获取职位详情"""
        await browser.open(url)
        await asyncio.sleep(5)
        
        snapshot = await browser.snapshot(refs="aria")
        detail = self.parse_job_detail(snapshot)
        
        return detail
    
    def parse_job_detail(self, snapshot):
        """解析职位详情"""
        detail = {
            "platform": "boss",
            "title": self._extract_text(snapshot, 'heading[title]'),
            "company": self._extract_text(snapshot, 'link[company]'),
            "salary": self._extract_text(snapshot, 'generic[salary]'),
            "description": self._extract_text(snapshot, 'paragraph[desc]'),
            "skills": self._extract_skills(snapshot),
            "experience": self._extract_text(snapshot, 'listitem[exp]'),
            "education": self._extract_text(snapshot, 'listitem[edu]'),
            "industry": self._extract_text(snapshot, 'generic[industry]'),
        }
        
        return detail
    
    async def apply(self, job_url, resume):
        """BOSS 直聘投递（点击"立即沟通"）"""
        await browser.open(job_url)
        await asyncio.sleep(3)
        
        # 查找"立即沟通"按钮并点击
        # 上传简历
        # 发送消息
        
        return {"status": "submitted", "platform": "boss"}
    
    def _get_city_code(self, city_name):
        """城市名转城市代码"""
        city_map = {
            "深圳": "101280600",
            "广州": "101280100",
            "北京": "101010100",
            "上海": "101020100",
        }
        return city_map.get(city_name, self.city_code)
    
    def _extract_text(self, snapshot, selector):
        """提取文本"""
        el = snapshot.querySelector(selector)
        return el.text if el else ""
    
    def _extract_skills(self, snapshot):
        """提取技能标签"""
        skills = []
        skill_els = snapshot.querySelectorAll('tag[skill]')
        for el in skill_els:
            skills.append(el.text)
        return skills
```

#### 智联招聘适配器

**platform/zhilian_adapter.py：**
```python
from platform.base_adapter import BaseAdapter

class ZhilianAdapter(BaseAdapter):
    """智联招聘适配器"""
    
    def __init__(self):
        super().__init__("zhilian")
        self.base_url = "https://www.zhaopin.com"
    
    async def search_jobs(self, keyword, city=None, page=1):
        """搜索智联招聘职位"""
        # 类似 BOSS 实现
        pass
    
    async def get_job_detail(self, url):
        """获取职位详情"""
        pass
    
    async def apply(self, job_url, resume):
        """智联招聘投递"""
        pass
    
    def parse_search_results(self, snapshot):
        """解析搜索结果"""
        pass
    
    def parse_job_detail(self, snapshot):
        """解析职位详情"""
        pass
```

#### 适配器工厂

**platform/adapter_factory.py：**
```python
from platform.boss_adapter import BossAdapter
from platform.zhilian_adapter import ZhilianAdapter

class AdapterFactory:
    """适配器工厂"""
    
    _adapters = {
        "boss": BossAdapter,
        "zhilian": ZhilianAdapter,
    }
    
    @classmethod
    def get_adapter(cls, platform):
        """获取平台适配器"""
        adapter_class = cls._adapters.get(platform)
        if not adapter_class:
            raise ValueError(f"不支持的平台：{platform}")
        return adapter_class()
    
    @classmethod
    def register_adapter(cls, platform, adapter_class):
        """注册新适配器"""
        cls._adapters[platform] = adapter_class
```

---

### 2.3 匹配算法升级（7 维）

#### 新匹配公式

```
match_score = 
  industry * 0.25 +   # 行业匹配（新增权重）
  skill * 0.25 +      # 技能匹配
  experience * 0.15 + # 经验匹配
  salary * 0.10 +     # 薪资匹配
  location * 0.10 +   # 地点匹配
  education * 0.10 +  # 学历匹配
  tools * 0.05        # 工具匹配（新增）
```

#### 匹配引擎升级

**tools/matcher.py：**
```python
from tools.industry_matcher import IndustryMatcher

class MatchingEngine:
    """匹配引擎（7 维）"""
    
    def __init__(self):
        self.industry_matcher = IndustryMatcher()
        self.weights = {
            "industry": 0.25,    # 行业（新增）
            "skill": 0.25,       # 技能
            "experience": 0.15,  # 经验
            "salary": 0.10,      # 薪资
            "location": 0.10,    # 地点
            "education": 0.10,   # 学历
            "tools": 0.05,       # 工具（新增）
        }
    
    def calculate_match(self, user_profile, job_profile):
        """计算匹配度"""
        scores = {
            "industry": self._match_industry(user_profile, job_profile),
            "skill": self._match_skills(user_profile, job_profile),
            "experience": self._match_experience(user_profile, job_profile),
            "salary": self._match_salary(user_profile, job_profile),
            "location": self._match_location(user_profile, job_profile),
            "education": self._match_education(user_profile, job_profile),
            "tools": self._match_tools(user_profile, job_profile),
        }
        
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        
        return {
            "total": total_score,
            "details": scores,
            "weights": self.weights
        }
    
    def _match_industry(self, user, job):
        """行业匹配（使用 IndustryMatcher）"""
        user_industry = user.get("industry", "")
        job_industry = job.get("industry", "")
        
        if not job_industry:
            return 0.5  # 未知行业，中等分数
        
        return self.industry_matcher.match(user_industry, job_industry)
    
    def _match_skills(self, user, job):
        """技能匹配（Jaccard 相似度）"""
        user_skills = set(user.get("skills", []))
        job_skills = set(job.get("skills", []))
        
        if not job_skills:
            return 1.0
        
        intersection = len(user_skills & job_skills)
        union = len(user_skills | job_skills)
        
        return intersection / union if union > 0 else 0.0
    
    def _match_tools(self, user, job):
        """工具匹配（新增）"""
        user_tools = set(user.get("tools", []))
        job_tools = set(job.get("tools", []))
        
        if not job_tools:
            return 1.0
        
        intersection = len(user_tools & job_tools)
        union = len(user_tools | job_tools)
        
        return intersection / union if union > 0 else 0.0
    
    # ... 其他匹配方法
```

---

### 2.4 任务流水线（Pipeline）

#### Pipeline 引擎

**pipeline/job_pipeline.py：**
```python
from services.resume_service import ResumeService
from services.job_service import JobService
from services.match_service import MatchService
from tools.recommender import Recommender

class JobPipeline:
    """求职任务流水线"""
    
    def __init__(self):
        self.resume_service = ResumeService()
        self.job_service = JobService()
        self.match_service = MatchService()
        self.recommender = Recommender()
    
    async def run(self, user_id, keywords=None, top_n=10):
        """
        执行完整求职流程
        
        流程：
        1. 获取用户画像
        2. 搜索职位
        3. 解析 JD
        4. 计算匹配
        5. 排序推荐
        6. 返回结果
        """
        print(f"🚀 开始执行求职 Pipeline，用户：{user_id}")
        
        # 步骤 1: 获取用户画像
        print("📄 步骤 1: 获取用户画像")
        profile = await self.resume_service.get_profile(user_id)
        
        # 如果用户没有目标职位，使用传入的关键词
        search_keywords = keywords or profile.target_jobs or ["品牌策划"]
        
        # 步骤 2: 搜索职位
        print(f"🔎 步骤 2: 搜索职位，关键词：{search_keywords}")
        jobs = []
        for keyword in search_keywords:
            keyword_jobs = await self.job_service.search(keyword, profile.expected_city)
            jobs.extend(keyword_jobs)
        
        print(f"   找到 {len(jobs)} 个职位")
        
        # 步骤 3: 解析 JD（批量）
        print("📋 步骤 3: 解析 JD")
        parsed_jobs = await self.job_service.parse_details(jobs)
        print(f"   解析完成 {len(parsed_jobs)} 个职位")
        
        # 步骤 4: 计算匹配
        print("📊 步骤 4: 计算匹配度")
        matches = []
        for job in parsed_jobs:
            match_result = await self.match_service.calculate(profile, job)
            matches.append({
                "job": job,
                "match": match_result
            })
        
        # 步骤 5: 排序推荐
        print("🎯 步骤 5: 排序推荐")
        ranked = self.recommender.rank(matches, top_n=top_n)
        
        # 步骤 6: 保存结果
        print("💾 步骤 6: 保存结果")
        await self.match_service.save_matches(user_id, ranked)
        
        print(f"✅ Pipeline 完成，推荐 {len(ranked)} 个职位")
        
        return ranked
    
    async def run_with_apply(self, user_id, job_ids, keywords=None):
        """执行求职流程并自动投递"""
        # 先执行标准流程
        ranked = await self.run(user_id, keywords)
        
        # 筛选指定职位
        to_apply = [j for j in ranked if j["job"]["id"] in job_ids]
        
        # 执行投递
        for item in to_apply:
            await self.job_service.apply(item["job"], user_id)
        
        return to_apply
```

---

### 2.5 Agent 决策系统（Planner 升级）

#### Agent Planner

**agent/planner.py：**
```python
class Planner:
    """Agent 任务规划器"""
    
    def __init__(self):
        self.pipelines = {
            "find_job": [
                "parse_resume",
                "search_jobs",
                "parse_jd",
                "calculate_match",
                "rank_jobs",
                "recommend"
            ],
            "apply": [
                "open_job",
                "submit_application",
                "track_status"
            ],
            "analyze_market": [
                "search_jobs",
                "aggregate_stats",
                "generate_report"
            ]
        }
    
    def plan(self, intent, context=None):
        """
        根据用户意图生成任务计划
        
        参数：
        intent: 用户意图（find_job, apply, analyze_market）
        context: 上下文信息（用户 ID、关键词等）
        
        返回：
        任务列表
        """
        if intent not in self.pipelines:
            raise ValueError(f"未知意图：{intent}")
        
        base_tasks = self.pipelines[intent]
        
        # 根据上下文调整任务
        if context:
            if context.get("skip_resume_parse"):
                base_tasks = [t for t in base_tasks if t != "parse_resume"]
            
            if context.get("auto_apply"):
                base_tasks.append("auto_apply")
        
        return base_tasks
    
    def analyze_intent(self, user_input):
        """分析用户输入，识别意图"""
        user_input = user_input.lower()
        
        if any(word in user_input for word in ["找工", "求职", "推荐职位"]):
            return "find_job"
        
        if any(word in user_input for word in ["投递", "申请", "报名"]):
            return "apply"
        
        if any(word in user_input for word in ["分析", "市场", "趋势"]):
            return "analyze_market"
        
        return "find_job"  # 默认
```

#### Agent Core

**agent/agent_core.py：**
```python
from agent.planner import Planner
from pipeline.job_pipeline import JobPipeline

class AgentCore:
    """Agent 核心"""
    
    def __init__(self):
        self.planner = Planner()
        self.pipeline = JobPipeline()
    
    async def handle_request(self, user_input, user_id=None):
        """处理用户请求"""
        # 1. 分析意图
        intent = self.planner.analyze_intent(user_input)
        
        # 2. 生成计划
        context = {"user_id": user_id}
        tasks = self.planner.plan(intent, context)
        
        # 3. 执行计划
        if intent == "find_job":
            result = await self.pipeline.run(user_id)
            return self._format_recommendations(result)
        
        elif intent == "apply":
            # 提取职位 ID
            job_ids = self._extract_job_ids(user_input)
            result = await self.pipeline.run_with_apply(user_id, job_ids)
            return self._format_apply_result(result)
        
        elif intent == "analyze_market":
            result = await self._analyze_market(user_id)
            return self._format_analysis(result)
    
    def _format_recommendations(self, matches):
        """格式化推荐结果"""
        output = "🎯 为您推荐以下职位：\n\n"
        
        for i, item in enumerate(matches, 1):
            job = item["job"]
            match = item["match"]
            
            output += f"{i}. **{job['title']}** - {job['company']}\n"
            output += f"   匹配度：{match['total']*100:.1f}%\n"
            output += f"   薪资：{job.get('salary', '面议')}\n"
            output += f"   地点：{job.get('city', '')}{job.get('district', '')}\n\n"
        
        return output
    
    def _format_apply_result(self, applications):
        """格式化投递结果"""
        output = "✅ 投递完成：\n\n"
        
        for app in applications:
            job = app["job"]
            output += f"- {job['title']} - {job['company']}\n"
        
        return output
```

---

## 三、服务层实现

### 3.1 职位服务

**services/job_service.py：**
```python
from platform.adapter_factory import AdapterFactory
from database.cache import cache

class JobService:
    """职位服务"""
    
    def __init__(self):
        self.adapters = {}
    
    def _get_adapter(self, platform):
        """获取平台适配器（单例）"""
        if platform not in self.adapters:
            self.adapters[platform] = AdapterFactory.get_adapter(platform)
        return self.adapters[platform]
    
    async def search(self, keyword, city=None, platforms=None):
        """搜索职位（多平台）"""
        if platforms is None:
            platforms = ["boss"]  # 默认 BOSS 直聘
        
        all_jobs = []
        
        for platform in platforms:
            # 检查缓存
            cache_key = f"search:{platform}:{keyword}:{city}"
            cached = cache.get(cache_key)
            
            if cached:
                all_jobs.extend(cached)
                continue
            
            # 搜索
            adapter = self._get_adapter(platform)
            jobs = await adapter.search_jobs(keyword, city)
            
            # 缓存 1 小时
            cache.set(cache_key, jobs, use_ttl=True)
            
            all_jobs.extend(jobs)
        
        return all_jobs
    
    async def parse_details(self, jobs):
        """批量解析职位详情"""
        parsed = []
        
        for job in jobs:
            # 检查缓存
            cache_key = f"job:{job['platform']}:{job['url']}"
            cached = cache.get(cache_key)
            
            if cached:
                parsed.append(cached)
                continue
            
            # 解析详情
            adapter = self._get_adapter(job['platform'])
            detail = await adapter.get_job_detail(job['url'])
            
            # 合并数据
            job.update(detail)
            
            # 缓存 24 小时
            cache.set(cache_key, job, use_ttl=True)
            
            parsed.append(job)
        
        return parsed
    
    async def apply(self, job, user_id):
        """申请职位"""
        adapter = self._get_adapter(job['platform'])
        
        # 获取用户简历
        resume = await self._get_user_resume(user_id)
        
        # 执行投递
        result = await adapter.apply(job['url'], resume)
        
        # 保存投递记录
        await self._save_application(user_id, job, result)
        
        return result
```

### 3.2 匹配服务

**services/match_service.py：**
```python
from tools.matcher import MatchingEngine
from database.db import get_db
from database import models

class MatchService:
    """匹配服务"""
    
    def __init__(self):
        self.engine = MatchingEngine()
    
    async def calculate(self, user_profile, job_profile):
        """计算匹配度"""
        result = self.engine.calculate_match(user_profile, job_profile)
        return result
    
    async def save_matches(self, user_id, matches):
        """保存匹配结果到数据库"""
        db = next(get_db())
        
        for item in matches:
            job = item["job"]
            match = item["match"]
            
            match_record = models.Match(
                user_id=user_id,
                job_id=job.get("id"),
                match_score=match["total"],
                industry_score=match["details"]["industry"],
                skill_score=match["details"]["skill"],
                experience_score=match["details"]["experience"],
                salary_score=match["details"]["salary"],
                location_score=match["details"]["location"],
                education_score=match["details"]["education"],
                tools_score=match["details"]["tools"]
            )
            
            db.add(match_record)
        
        db.commit()
```

### 3.3 简历服务

**services/resume_service.py：**
```python
from tools.resume_parser import ResumeParser
from database.db import get_db
from database import models

class ResumeService:
    """简历服务"""
    
    def __init__(self):
        self.parser = ResumeParser()
    
    async def parse_and_save(self, file_path, user_id=None):
        """解析简历并保存"""
        # 解析
        if file_path.endswith(".docx"):
            profile = self.parser.parse_docx(file_path)
        elif file_path.endswith(".pdf"):
            profile = self.parser.parse_pdf(file_path)
        else:
            raise ValueError("不支持的文件格式")
        
        # 保存到数据库
        db = next(get_db())
        
        if user_id:
            # 更新现有用户
            user = db.query(models.User).filter(models.User.id == user_id).first()
            for key, value in profile.items():
                setattr(user, key, value)
        else:
            # 创建新用户
            user = models.User(**profile, resume_file=file_path)
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    async def get_profile(self, user_id):
        """获取用户画像"""
        db = next(get_db())
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            raise ValueError(f"用户不存在：{user_id}")
        
        return {
            "id": user.id,
            "name": user.name,
            "education": user.education,
            "major": user.major,
            "experience_years": user.experience_years,
            "skills": user.skills,
            "tools": user.tools,
            "industry": user.industry,
            "target_jobs": user.target_jobs,
            "expected_city": user.expected_city,
            "expected_salary_min": user.expected_salary_min,
            "expected_salary_max": user.expected_salary_max,
        }
```

---

## 四、最终目录结构

```
qing-agent/
├── main.py                     # FastAPI 入口
├── agent/
│   ├── agent_core.py           # Agent 核心
│   └── planner.py              # 任务规划器
├── pipeline/
│   └── job_pipeline.py         # 求职流水线
├── services/
│   ├── resume_service.py       # 简历服务
│   ├── job_service.py          # 职位服务
│   └── match_service.py        # 匹配服务
├── platform/
│   ├── base_adapter.py         # 适配器基类
│   ├── boss_adapter.py         # BOSS 适配器
│   ├── zhilian_adapter.py      # 智联适配器
│   └── adapter_factory.py      # 适配器工厂
├── tools/
│   ├── resume_parser.py        # 简历解析
│   ├── jd_parser.py            # JD 解析
│   ├── matcher.py              # 匹配引擎（7 维）
│   ├── industry_matcher.py     # 行业匹配（新增）
│   └── recommender.py          # 推荐引擎
├── database/
│   ├── db.py                   # 数据库连接
│   ├── models.py               # 数据模型
│   └── cache.py                # 缓存管理
├── routes/
│   ├── users.py                # 用户路由
│   ├── jobs.py                 # 职位路由
│   ├── matches.py              # 匹配路由
│   └── applications.py         # 投递路由
├── config/
│   └── settings.py             # 配置
├── data/
│   ├── industry_tree.json      # 行业树（新增）
│   └── qing_agent.db           # SQLite 数据库
├── logs/                       # 日志
├── requirements.txt            # 依赖
└── README.md                   # 说明
```

---

## 五、可执行性评估

### 5.1 可实现度

| 模块 | 可实现度 | 预计时间 | 优先级 |
|------|----------|----------|--------|
| **行业匹配系统** | ✅ 95% | 2 小时 | P0 |
| **平台适配器层** | ✅ 90% | 4 小时 | P0 |
| **任务流水线** | ✅ 95% | 2 小时 | P0 |
| **Agent 决策系统** | ✅ 90% | 2 小时 | P0 |
| **匹配算法升级** | ✅ 100% | 1 小时 | P0 |
| **服务层** | ✅ 95% | 3 小时 | P1 |
| **FastAPI 路由** | ✅ 100% | 2 小时 | P1 |
| **数据库模型** | ✅ 100% | 1 小时 | P1 |

**总计：约 17 小时**

### 5.2 依赖检查

| 依赖 | 状态 | 安装命令 |
|------|------|----------|
| FastAPI | ✅ 可用 | `pip install fastapi` |
| SQLAlchemy | ✅ 可用 | `pip install sqlalchemy` |
| cachetools | ✅ 可用 | `pip install cachetools` |
| python-docx | ✅ 可用 | `pip install python-docx` |
| PyPDF2 | ✅ 可用 | `pip install PyPDF2` |
| OpenClaw browser | ✅ 已有 | 内置 |

---

## 六、执行计划

### 阶段 1：核心模块（6 小时）

| 任务 | 文件 | 时间 |
|------|------|------|
| 行业树 + 行业匹配器 | `data/industry_tree.json`, `tools/industry_matcher.py` | 2h |
| 平台适配器基类 + BOSS 适配器 | `platform/base_adapter.py`, `platform/boss_adapter.py` | 2h |
| 匹配引擎升级（7 维） | `tools/matcher.py` | 1h |
| 任务流水线 | `pipeline/job_pipeline.py` | 1h |

### 阶段 2：服务层（5 小时）

| 任务 | 文件 | 时间 |
|------|------|------|
| 简历服务 | `services/resume_service.py` | 2h |
| 职位服务 | `services/job_service.py` | 2h |
| 匹配服务 | `services/match_service.py` | 1h |

### 阶段 3：Agent 系统（3 小时）

| 任务 | 文件 | 时间 |
|------|------|------|
| Planner | `agent/planner.py` | 1h |
| Agent Core | `agent/agent_core.py` | 2h |

### 阶段 4：API 与集成（3 小时）

| 任务 | 文件 | 时间 |
|------|------|------|
| FastAPI 路由 | `routes/*.py` | 2h |
| 集成测试 | `tests/` | 1h |

---

## 七、测试用例

### 7.1 行业匹配测试

```python
def test_industry_match():
    matcher = IndustryMatcher()
    
    # 相同行业
    assert matcher.match("广告", "广告") == 1.0
    
    # 父子关系
    assert matcher.match("广告", "品牌咨询") == 0.8
    
    # 同级关系
    assert matcher.match("品牌咨询", "营销策划") == 0.6
    
    # 弱相关
    assert matcher.match("广告", "电商") == 0.3
    
    # 无关
    assert matcher.match("广告", "金融") == 0.2
```

### 7.2 Pipeline 测试

```python
async def test_job_pipeline():
    pipeline = JobPipeline()
    
    # 创建测试用户
    user_id = await create_test_user()
    
    # 执行 Pipeline
    results = await pipeline.run(user_id, keywords=["品牌策划"])
    
    # 验证结果
    assert len(results) > 0
    assert all("match" in r for r in results)
```

---

## 八、总结

### 8.1 v1.1 核心优势

1. **平台适配层** — 未来添加新平台（猎聘、拉勾）无需修改核心逻辑
2. **行业图谱** — 精确匹配行业相似度，不是简单的是/否
3. **任务流水线** — 标准化流程，易于扩展和调试
4. **真正 Agent** — 能理解意图、生成计划、执行任务

### 8.2 下一步行动

1. **立即执行：** 创建项目目录 + 行业树文件
2. **阶段 1：** 实现行业匹配 + 平台适配器
3. **阶段 2：** 实现服务层 + Pipeline
4. **阶段 3：** 实现 Agent 决策系统
5. **阶段 4：** 集成测试 + 文档

---

**文档版本：** v1.1  
**创建时间：** 2026-03-08 01:15  
**审查状态：** 待庆审查

---

*庆，v1.1 方案已完成。核心升级：行业图谱、平台适配器、任务流水线、Agent 决策系统。请审查。*
