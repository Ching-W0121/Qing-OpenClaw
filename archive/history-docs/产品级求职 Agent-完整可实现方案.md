# 产品级求职 Agent · 完整可实现方案

**版本：** v1.0  
**日期：** 2026-03-08 00:30  
**状态：** ✅ 可立即执行  
**责任人：** 青（OpenClaw Agent）

---

## 一、方案概述

基于《产品级求职 agent》文档设计，结合当前实际能力，**去除 Docker/Redis 依赖**，采用**轻量级替代方案**，实现 80%+ 核心功能。

### 1.1 核心目标

| 目标 | 说明 |
|------|------|
| 简历解析 | 用户上传简历 → 结构化候选人画像 |
| 职位搜索 | BOSS 直聘/智联招聘 → 获取职位列表 |
| JD 解析 | 职位描述 → 结构化数据 |
| 匹配引擎 | 6 维度匹配算法 → 计算匹配度 |
| 推荐系统 | 按匹配度排序 → 输出 Top N |
| 自动投递 | 用户确认 → 执行投递动作 |

### 1.2 技术栈调整

| 原方案 | 替代方案 | 说明 |
|--------|----------|------|
| FastAPI + Docker | **FastAPI 本地运行** | 无需容器化 |
| Redis 缓存 | **SQLite + 内存缓存** | 轻量级持久化 |
| PostgreSQL | **SQLite（开发）→ PostgreSQL（生产）** | 渐进式迁移 |
| Playwright | **OpenClaw browser 工具** | 已有能力 |

---

## 二、系统架构（简化版）

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│  (微信/Telegram/Discord/命令行/Web UI)                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Agent 控制层（青）                         │
│  - 用户交互                                                  │
│  - 任务规划                                                  │
│  - 工具调度                                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 服务层                          │
│  - REST API                                                  │
│  - 请求验证                                                  │
│  - 响应格式化                                                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      工具调度层                              │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │简历解析工具   │职位搜索工具   │JD 解析工具     │            │
│  └──────────────┴──────────────┴──────────────┘            │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │匹配引擎       │推荐引擎       │投递执行器     │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据持久层                              │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │SQLite 数据库  │JSON 文件缓存  │内存缓存       │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、目录结构

```
qing-agent/
├── main.py                 # FastAPI 入口
├── agent/
│   ├── agent_core.py       # Agent 核心逻辑
│   └── planner.py          # 任务规划器
├── tools/
│   ├── resume_parser.py    # 简历解析
│   ├── job_search.py       # 职位搜索
│   ├── jd_parser.py        # JD 解析
│   ├── matcher.py          # 匹配引擎
│   ├── recommender.py      # 推荐引擎
│   └── apply_executor.py   # 投递执行
├── database/
│   ├── db.py               # 数据库连接
│   ├── models.py           # 数据模型
│   └── cache.py            # 缓存管理
├── services/
│   ├── job_service.py      # 职位服务
│   └── match_service.py    # 匹配服务
├── config/
│   └── settings.py         # 配置文件
├── data/                   # 数据文件（SQLite + JSON）
├── logs/                   # 日志文件
├── requirements.txt        # Python 依赖
└── README.md               # 说明文档
```

---

## 四、环境搭建

### 4.1 基础要求

| 组件 | 版本 | 安装命令 |
|------|------|----------|
| Python | 3.11+ | 已安装 |
| Node.js | 18+ | 已安装 |
| pip | 最新 | 已安装 |

### 4.2 Python 依赖

**requirements.txt：**
```txt
# Web 框架
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# 数据处理
pydantic>=2.5.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# AI/ML
openai>=1.10.0
sentence-transformers>=2.2.0
numpy>=1.24.0
pandas>=2.0.0

# 浏览器自动化
playwright>=1.40.0

# 工具
python-dotenv>=1.0.0
tqdm>=4.66.0
python-docx>=1.1.0
PyPDF2>=3.0.0

# 缓存（替代 Redis）
cachetools>=5.3.0

# 日志
loguru>=0.7.0
```

**安装命令：**
```bash
cd qing-agent
pip install -r requirements.txt
playwright install  # 安装浏览器
```

### 4.3 配置文件

**config/settings.py：**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# API 配置
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# 数据库配置（SQLite 替代 PostgreSQL）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/qing_agent.db")

# 缓存配置（内存缓存替代 Redis）
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 小时
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 1000))

# AI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh")

# 业务配置
MAX_RECOMMEND = int(os.getenv("MAX_RECOMMEND", 10))
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", 0.7))

# BOSS 直聘配置
BOSS_CITY_CODE = os.getenv("BOSS_CITY_CODE", "101280600")  # 深圳
BOSS_EXCLUDE_DISTRICTS = os.getenv("BOSS_EXCLUDE_DISTRICTS", "宝安区").split(",")
```

**.env 示例：**
```bash
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True

DATABASE_URL=sqlite:///./data/qing_agent.db

OPENAI_API_KEY=sk-xxx
EMBEDDING_MODEL=BAAI/bge-large-zh

MAX_RECOMMEND=10
MATCH_THRESHOLD=0.7

BOSS_CITY_CODE=101280600
BOSS_EXCLUDE_DISTRICTS=宝安区
```

---

## 五、数据库设计（SQLite 版）

### 5.1 数据模型

**database/models.py：**
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户信息表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    education = Column(String(50))  # 学历
    major = Column(String(100))  # 专业
    experience_years = Column(Integer)  # 工作年限
    skills = Column(JSON)  # 技能列表
    tools = Column(JSON)  # 工具/软件
    industry = Column(String(100))  # 行业
    target_jobs = Column(JSON)  # 目标职位
    expected_city = Column(String(100))  # 期望城市
    expected_salary_min = Column(Integer)  # 期望薪资下限
    expected_salary_max = Column(Integer)  # 期望薪资上限
    resume_file = Column(String(255))  # 简历文件路径
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Job(Base):
    """职位信息表"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))  # 职位名称
    company = Column(String(200))  # 公司
    city = Column(String(100))  # 城市
    district = Column(String(100))  # 区域
    salary_min = Column(Integer)  # 薪资下限
    salary_max = Column(Integer)  # 薪资上限
    experience = Column(String(50))  # 经验要求
    education = Column(String(50))  # 学历要求
    industry = Column(String(100))  # 行业
    skills = Column(JSON)  # 技能要求
    tools = Column(JSON)  # 工具要求
    platform = Column(String(50))  # 平台（BOSS/智联）
    url = Column(String(500))  # 职位链接
    jd_text = Column(Text)  # JD 原文
    created_at = Column(DateTime, default=datetime.now)

class Match(Base):
    """匹配记录表"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float)  # 总匹配度
    industry_score = Column(Float)  # 行业匹配
    skill_score = Column(Float)  # 技能匹配
    experience_score = Column(Float)  # 经验匹配
    salary_score = Column(Float)  # 薪资匹配
    location_score = Column(Float)  # 地点匹配
    education_score = Column(Float)  # 学历匹配
    created_at = Column(DateTime, default=datetime.now)

class Application(Base):
    """投递记录表"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String(50))  # pending/submitted/interview/offer/rejected
    applied_at = Column(DateTime)  # 投递时间
    hr_reply = Column(Text)  # HR 回复
    notes = Column(Text)  # 备注
    created_at = Column(DateTime, default=datetime.now)
```

### 5.2 数据库初始化

**database/db.py：**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库（创建表）"""
    from database import models
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 六、缓存设计（替代 Redis）

### 6.1 内存缓存实现

**database/cache.py：**
```python
from cachetools import TTLCache, LRUCache
from datetime import datetime
import json

class CacheManager:
    """缓存管理器（替代 Redis）"""
    
    def __init__(self, ttl=3600, max_size=1000):
        # TTL 缓存：自动过期
        self.ttl_cache = TTLCache(maxsize=max_size, ttl=ttl)
        # LRU 缓存：最近最少使用淘汰
        self.lru_cache = LRUCache(maxsize=max_size)
        # 文件缓存：持久化
        self.file_cache_dir = "data/cache"
    
    def get(self, key):
        """获取缓存"""
        return self.ttl_cache.get(key) or self.lru_cache.get(key)
    
    def set(self, key, value, use_ttl=True):
        """设置缓存"""
        if use_ttl:
            self.ttl_cache[key] = value
        else:
            self.lru_cache[key] = value
    
    def delete(self, key):
        """删除缓存"""
        self.ttl_cache.pop(key, None)
        self.lru_cache.pop(key, None)
    
    def clear(self):
        """清空缓存"""
        self.ttl_cache.clear()
        self.lru_cache.clear()
    
    def get_stats(self):
        """获取缓存统计"""
        return {
            "ttl_cache_size": len(self.ttl_cache),
            "lru_cache_size": len(self.lru_cache),
            "ttl_cache_hits": self.ttl_cache.currsize,
        }

# 全局缓存实例
cache = CacheManager(ttl=3600, max_size=1000)
```

### 6.2 缓存使用场景

| 场景 | 缓存类型 | 过期时间 |
|------|----------|----------|
| 职位搜索结果 | TTL | 1 小时 |
| JD 解析结果 | TTL | 24 小时 |
| 用户画像 | LRU | 持久 |
| 匹配结果 | TTL | 30 分钟 |

---

## 七、核心模块实现

### 7.1 FastAPI 入口

**main.py：**
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.db import init_db, get_db
from config.settings import API_HOST, API_PORT, DEBUG

app = FastAPI(
    title="求职 Agent API",
    description="产品级求职 Agent 系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    init_db()
    print(f"🚀 服务启动：http://{API_HOST}:{API_PORT}")
    print(f"📚 API 文档：http://{API_HOST}:{API_PORT}/docs")

@app.get("/")
async def root():
    return {"message": "求职 Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# 导入路由
from routes import users, jobs, matches, applications

app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["职位"])
app.include_router(matches.router, prefix="/api/matches", tags=["匹配"])
app.include_router(applications.router, prefix="/api/applications", tags=["投递"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=DEBUG)
```

### 7.2 简历解析工具

**tools/resume_parser.py：**
```python
from docx import Document
import PyPDF2
import json

class ResumeParser:
    """简历解析器"""
    
    def parse_docx(self, file_path):
        """解析 Word 简历"""
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return self.extract_info(text)
    
    def parse_pdf(self, file_path):
        """解析 PDF 简历"""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages])
        return self.extract_info(text)
    
    def extract_info(self, text):
        """提取简历信息（使用 AI 或规则）"""
        # 简化版：规则提取
        # 完整版：调用 OpenAI API
        
        info = {
            "name": self._extract_name(text),
            "education": self._extract_education(text),
            "major": self._extract_major(text),
            "experience_years": self._extract_experience(text),
            "skills": self._extract_skills(text),
            "tools": self._extract_tools(text),
            "industry": self._extract_industry(text),
            "target_jobs": self._extract_target_jobs(text),
        }
        
        return info
    
    def _extract_name(self, text):
        # 实现姓名提取逻辑
        pass
    
    def _extract_education(self, text):
        # 实现学历提取逻辑
        pass
    
    # ... 其他提取方法
```

### 7.3 职位搜索工具

**tools/job_search.py：**
```python
from openclaw import browser
import asyncio

class JobSearchTool:
    """职位搜索工具"""
    
    def __init__(self, city_code="101280600"):
        self.city_code = city_code
        self.base_url = "https://www.zhipin.com/web/geek/job"
    
    async def search_boss(self, keyword, page=1):
        """搜索 BOSS 直聘职位"""
        url = f"{self.base_url}?city={self.city_code}&query={keyword}&page={page}"
        
        # 使用 OpenClaw browser 工具
        await browser.open(url)
        await asyncio.sleep(5)  # 等待加载
        
        # 获取快照
        snapshot = await browser.snapshot(refs="aria")
        
        # 解析职位列表
        jobs = self._parse_job_list(snapshot)
        
        return jobs
    
    def _parse_job_list(self, snapshot):
        """解析职位列表"""
        jobs = []
        # 实现解析逻辑
        return jobs
    
    async def search_zhilian(self, keyword):
        """搜索智联招聘职位"""
        # 类似实现
        pass
```

### 7.4 匹配引擎

**tools/matcher.py：**
```python
class MatchingEngine:
    """匹配引擎"""
    
    def __init__(self):
        self.weights = {
            "industry": 0.20,
            "skill": 0.25,
            "experience": 0.20,
            "salary": 0.15,
            "location": 0.10,
            "education": 0.10
        }
    
    def calculate_match(self, user_profile, job_profile):
        """计算匹配度"""
        scores = {
            "industry": self._match_industry(user_profile, job_profile),
            "skill": self._match_skills(user_profile, job_profile),
            "experience": self._match_experience(user_profile, job_profile),
            "salary": self._match_salary(user_profile, job_profile),
            "location": self._match_location(user_profile, job_profile),
            "education": self._match_education(user_profile, job_profile)
        }
        
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        
        return {
            "total": total_score,
            "details": scores
        }
    
    def _match_skills(self, user, job):
        """技能匹配（Jaccard 相似度）"""
        user_skills = set(user.get("skills", []))
        job_skills = set(job.get("skills", []))
        
        if not job_skills:
            return 1.0
        
        intersection = len(user_skills & job_skills)
        union = len(user_skills | job_skills)
        
        return intersection / union if union > 0 else 0.0
    
    # ... 其他匹配方法
```

### 7.5 推荐引擎

**tools/recommender.py：**
```python
class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self, matcher):
        self.matcher = matcher
    
    def recommend(self, user_profile, jobs, top_n=10):
        """推荐 Top N 职位"""
        # 计算所有职位的匹配度
        scored_jobs = []
        
        for job in jobs:
            match_result = self.matcher.calculate_match(user_profile, job)
            scored_jobs.append({
                "job": job,
                "match_score": match_result["total"],
                "details": match_result["details"]
            })
        
        # 按匹配度排序
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 返回 Top N
        return scored_jobs[:top_n]
```

### 7.6 投递执行器

**tools/apply_executor.py：**
```python
from openclaw import browser
import asyncio

class ApplyExecutor:
    """投递执行器"""
    
    async def apply_boss(self, job_url, user_profile):
        """BOSS 直聘投递"""
        await browser.open(job_url)
        await asyncio.sleep(3)
        
        # 点击"立即沟通"
        # 发送消息
        # 上传简历
        
        return {"status": "submitted", "job_url": job_url}
    
    async def apply_zhilian(self, job_url, user_profile):
        """智联招聘投递"""
        # 类似实现
        pass
```

---

## 八、API 路由设计

### 8.1 用户相关

**routes/users.py：**
```python
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database.db import get_db
from database import models
from tools.resume_parser import ResumeParser

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传简历并解析"""
    parser = ResumeParser()
    
    # 保存文件
    file_path = f"data/resumes/{file.filename}"
    
    # 解析简历
    if file.filename.endswith(".docx"):
        profile = parser.parse_docx(file_path)
    elif file.filename.endswith(".pdf"):
        profile = parser.parse_pdf(file_path)
    else:
        raise HTTPException(400, "不支持的文件格式")
    
    # 保存到数据库
    user = models.User(**profile, resume_file=file_path)
    db.add(user)
    db.commit()
    
    return {"user_id": user.id, "profile": profile}

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user

@router.put("/{user_id}")
async def update_user(user_id: int, profile: dict, db: Session = Depends(get_db)):
    """更新用户画像"""
    # 实现更新逻辑
    pass
```

### 8.2 职位相关

**routes/jobs.py：**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from tools.job_search import JobSearchTool

router = APIRouter()

@router.get("/search")
async def search_jobs(keyword: str, platform: str = "boss", db: Session = Depends(get_db)):
    """搜索职位"""
    search_tool = JobSearchTool()
    
    if platform == "boss":
        jobs = await search_tool.search_boss(keyword)
    elif platform == "zhilian":
        jobs = await search_tool.search_zhilian(keyword)
    else:
        raise HTTPException(400, "不支持的平台")
    
    return {"jobs": jobs, "count": len(jobs)}

@router.get("/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取职位详情"""
    # 实现获取逻辑
    pass
```

### 8.3 匹配相关

**routes/matches.py：**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from tools.matcher import MatchingEngine

router = APIRouter()

@router.post("/calculate")
async def calculate_match(user_id: int, job_id: int, db: Session = Depends(get_db)):
    """计算匹配度"""
    # 获取用户和职位数据
    # 计算匹配度
    # 保存到数据库
    
    return {"match_score": 0.85, "details": {...}}

@router.get("/user/{user_id}")
async def get_user_matches(user_id: int, db: Session = Depends(get_db)):
    """获取用户的所有匹配记录"""
    # 实现查询逻辑
    pass
```

### 8.4 推荐相关

**routes/recommendations.py：**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from tools.recommender import RecommendationEngine
from tools.matcher import MatchingEngine

router = APIRouter()

@router.get("/user/{user_id}")
async def get_recommendations(user_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    """获取推荐职位"""
    # 获取用户画像
    # 获取职位列表
    # 计算推荐
    
    matcher = MatchingEngine()
    recommender = RecommendationEngine(matcher)
    
    recommendations = recommender.recommend(user_profile, jobs, top_n)
    
    return {"recommendations": recommendations}
```

### 8.5 投递相关

**routes/applications.py：**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from tools.apply_executor import ApplyExecutor

router = APIRouter()

@router.post("/submit")
async def submit_application(user_id: int, job_id: int, db: Session = Depends(get_db)):
    """提交投递"""
    executor = ApplyExecutor()
    
    # 获取职位 URL
    # 执行投递
    
    result = await executor.apply_boss(job_url, user_profile)
    
    # 保存投递记录
    
    return result

@router.get("/{application_id}")
async def get_application(application_id: int, db: Session = Depends(get_db)):
    """获取投递状态"""
    # 实现查询逻辑
    pass

@router.put("/{application_id}/status")
async def update_application_status(application_id: int, status: str, db: Session = Depends(get_db)):
    """更新投递状态"""
    # 实现更新逻辑
    pass
```

---

## 九、启动与运行

### 9.1 启动 FastAPI 服务

```bash
# 方式 1：开发模式（自动重载）
cd qing-agent
fastapi dev main.py

# 方式 2：生产模式
fastapi run main.py

# 方式 3：直接使用 uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 9.2 访问服务

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8000 | API 根路径 |
| http://127.0.0.1:8000/docs | Swagger UI 文档 |
| http://127.0.0.1:8000/redoc | ReDoc 文档 |
| http://127.0.0.1:8000/health | 健康检查 |

### 9.3 与 OpenClaw 集成

**作为 OpenClaw 工具注册：**

```python
# 在 OpenClaw 中注册工具
@tool
def search_jobs(keyword: str, city: str = "深圳") -> list:
    """搜索职位"""
    response = requests.get(f"http://127.0.0.1:8000/api/jobs/search", params={
        "keyword": keyword,
        "city": city
    })
    return response.json()["jobs"]

@tool
def calculate_match(user_id: int, job_id: int) -> dict:
    """计算匹配度"""
    response = requests.get(f"http://127.0.0.1:8000/api/matches/calculate", params={
        "user_id": user_id,
        "job_id": job_id
    })
    return response.json()
```

---

## 十、测试计划

### 10.1 单元测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/ -v
```

### 10.2 集成测试

| 测试场景 | 预期结果 |
|----------|----------|
| 上传简历 → 解析 → 保存 | 用户画像正确提取 |
| 搜索职位 → 解析 JD → 保存 | 职位数据完整 |
| 计算匹配度 | 分数合理（0-1） |
| 推荐 Top10 | 按匹配度降序 |
| 执行投递 | 投递成功并记录 |

---

## 十一、部署方案

### 11.1 本地部署（开发）

```bash
# 直接运行
python main.py
```

### 11.2 服务器部署（生产）

**使用 systemd 服务：**

`/etc/systemd/system/qing-agent.service`：
```ini
[Unit]
Description=Qing Agent API
After=network.target

[Service]
Type=simple
User=tr
WorkingDirectory=/home/tr/qing-agent
Environment="PATH=/home/tr/.venv/bin"
ExecStart=/home/tr/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable qing-agent
sudo systemctl start qing-agent
sudo systemctl status qing-agent
```

### 11.3 反向代理（Nginx）

`/etc/nginx/sites-available/qing-agent`：
```nginx
server {
    listen 80;
    server_name agent.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 十二、时间规划

| 阶段 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| 1 | 环境搭建 + 依赖安装 | 30 分钟 | ⏳ 待执行 |
| 2 | 数据库模型 + 初始化 | 1 小时 | ⏳ 待执行 |
| 3 | FastAPI 路由开发 | 3 小时 | ⏳ 待执行 |
| 4 | 简历解析工具 | 2 小时 | ⏳ 待执行 |
| 5 | 职位搜索工具 | 2 小时 | ⏳ 待执行 |
| 6 | 匹配引擎 + 推荐引擎 | 2 小时 | ⏳ 待执行 |
| 7 | 投递执行器 | 3 小时 | ⏳ 待执行 |
| 8 | 集成测试 | 2 小时 | ⏳ 待执行 |
| 9 | 文档完善 | 1 小时 | ⏳ 待执行 |

**总计：约 16 小时**

---

## 十三、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| BOSS 直聘封号 | 高 | 严格遵循防封禁方案，阶梯式放量 |
| 简历解析准确率低 | 中 | 人工校对 + AI 辅助 |
| 匹配算法不准 | 中 | 用户反馈调优 |
| 自动投递失败 | 高 | 人工确认 + 手动备选 |
| 性能瓶颈 | 低 | SQLite → PostgreSQL 迁移 |

---

## 十四、总结

### 14.1 可实现功能清单

| 功能 | 可实现度 | 说明 |
|------|----------|------|
| FastAPI 服务 | ✅ 100% | 本地运行，无需 Docker |
| SQLite 数据库 | ✅ 100% | 替代 PostgreSQL |
| 内存缓存 | ✅ 100% | cachetools 替代 Redis |
| 简历解析 | ✅ 80% | Word/PDF 解析 |
| 职位搜索 | ✅ 80% | BOSS/智联 |
| JD 解析 | ✅ 85% | 结构化提取 |
| 匹配引擎 | ✅ 90% | 6 维度算法 |
| 推荐系统 | ✅ 95% | Top N 排序 |
| 自动投递 | ✅ 60% | 需人工确认 |

### 14.2 核心优势

1. **轻量级** — 无需 Docker/Redis，开箱即用
2. **易部署** — FastAPI 本地运行，systemd 管理
3. **可扩展** — 后续可迁移 PostgreSQL/Redis
4. **与 OpenClaw 无缝集成** — 直接调用 browser 工具

### 14.3 下一步行动

1. **立即执行：** 创建项目目录 + 安装依赖
2. **04:09 后：** 测试 BOSS 直聘搜索（账号已恢复）
3. **本周内：** 完成核心模块开发
4. **下周：** 集成测试 + 优化

---

**文档版本：** v1.0  
**创建时间：** 2026-03-08 00:30  
**下次审查：** 完成阶段 1 后

---

*庆，这份方案已去除所有不可行依赖，采用最优替代方案。请审查，如无异议我立即开始执行。*
