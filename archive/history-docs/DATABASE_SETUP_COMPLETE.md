# PostgreSQL 数据库配置完成报告

**配置日期**: 2026-03-14 16:53  
**状态**: ✅ 已完成并验证

---

## 📊 数据库信息

| 项目 | 值 |
|------|-----|
| **主机** | localhost:5432 |
| **数据库** | qing_jobs_db |
| **用户** | qing_admin |
| **密码** | Qing2026 |
| **版本** | PostgreSQL 16.13 |

---

## 📁 已创建的表（5 张）

### 1. jobs - 职位表

**字段**（19 个）:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| platform | varchar(50) | 招聘平台 |
| source_platform_id | varchar(100) | 平台原始 ID |
| title | varchar(200) | 职位名称 |
| company | varchar(200) | 公司名称 |
| city | varchar(100) | 城市 |
| district | varchar(100) | 区域 |
| salary_min | integer | 最低薪资 |
| salary_max | integer | 最高薪资 |
| experience | varchar(50) | 经验要求 |
| education | varchar(50) | 学历要求 |
| industry | varchar(100) | 行业 |
| skills | json | 技能要求 |
| tools | json | 工具要求 |
| url | varchar(500) | 职位 URL |
| jd_text | text | 原始 JD |
| requirements | json | 任职要求 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

**索引**（10 个）:
- idx_jobs_location (city, district)
- idx_jobs_salary (salary_min, salary_max)
- idx_jobs_title (title)
- idx_jobs_unique (platform, source_platform_id) - 唯一索引
- ix_jobs_city, ix_jobs_created_at, ix_jobs_id, ix_jobs_industry, ix_jobs_salary_min

---

### 2. users - 用户表

**字段**（15 个）:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| name | varchar(100) | 姓名 |
| education | varchar(50) | 学历 |
| major | varchar(100) | 专业 |
| experience_years | integer | 工作年限 |
| skills | json | 技能 |
| tools | json | 工具 |
| industry | varchar(100) | 行业 |
| target_jobs | json | 目标职位 |
| expected_city | varchar(100) | 期望城市 |
| expected_salary_min | integer | 期望最低薪资 |
| expected_salary_max | integer | 期望最高薪资 |
| resume_file | varchar(255) | 简历文件 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

---

### 3. matches - 匹配表

**字段**（16 个）:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| user_id | integer | 用户 ID（外键） |
| job_id | integer | 职位 ID（外键） |
| match_score | float | 匹配分数 |
| match_vector | json | 匹配向量 |
| match_details | json | 匹配详情 |
| industry_score | float | 行业匹配分 |
| skill_score | float | 技能匹配分 |
| experience_score | float | 经验匹配分 |
| salary_score | float | 薪资匹配分 |
| location_score | float | 地点匹配分 |
| education_score | float | 学历匹配分 |
| tools_score | float | 工具匹配分 |
| is_viewed | integer | 是否已查看 |
| is_applied | integer | 是否已投递 |
| rank | integer | 排名 |
| created_at | timestamp | 创建时间 |

---

### 4. applications - 投递记录表

**字段**（11 个）:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| user_id | integer | 用户 ID（外键） |
| job_id | integer | 职位 ID（外键） |
| match_id | integer | 匹配 ID（外键） |
| status | varchar(50) | 投递状态 |
| platform_status | varchar(50) | 平台状态 |
| applied_at | timestamp | 投递时间 |
| hr_reply | text | HR 回复 |
| notes | text | 备注 |
| updated_at | timestamp | 更新时间 |
| created_at | timestamp | 创建时间 |

**外键约束**:
- job_id → jobs(id)
- user_id → users(id)
- match_id → matches(id)

---

### 5. alembic_version - 数据库版本管理

| 字段 | 类型 | 说明 |
|------|------|------|
| version_num | varchar(32) | Alembic 版本号 |

**当前版本**: 64ed1241be8c (Initial migration - v1.4 schema)

---

## 🔧 配置文件

### .env
```ini
DATABASE_URL=postgresql+asyncpg://qing_admin:Qing2026@localhost:5432/qing_jobs_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600
```

### alembic.ini
```ini
sqlalchemy.url = postgresql://qing_admin:Qing2026@localhost:5432/qing_jobs_db
```

---

## ✅ 验证命令

```bash
# 查看表列表
psql -U qing_admin -h localhost -d qing_jobs_db -c "\dt"

# 查看 jobs 表结构
psql -U qing_admin -h localhost -d qing_jobs_db -c "\d jobs"

# 查看 applications 表结构
psql -U qing_admin -h localhost -d qing_jobs_db -c "\d applications"

# 测试连接
psql -U qing_admin -h localhost -d qing_jobs_db -c "SELECT current_user, current_database();"
```

---

## 📝 数据库关系图

```
users (1) ──< matches >── (N) jobs
                │
                │ (1)
                │
                ▼ (N)
          applications
```

---

**配置完成时间**: 2026-03-14 16:53  
**验证状态**: ✅ 所有表已创建并验证
