# qing-agent Internal Module Responsibilities v1

## Layered view

```text
qing-agent/
├─ agent/           # Agent orchestration / top-level agent runtime behavior
├─ auth/            # Authentication / identity integration
├─ config/          # Runtime configuration and settings
├─ data/            # Active runtime data stores and generated active state
├─ database/        # DB bootstrap, session, engine, low-level persistence wiring
├─ migrations/      # Schema migration versions
├─ pipeline/        # Cross-platform search/enrich/score/recommend pipeline
├─ qing_platform/   # Platform adapters (zhilian / 51job / liepin ...)
├─ repositories/    # Repository layer for DB read/write abstraction
├─ routes/          # API / web routes
├─ scripts/         # Operational entrypoints / run commands
├─ services/        # Business services (apply, dedupe, notification, orchestration support)
├─ tools/           # Pure helpers: scoring, parsing, formatting, matching
├─ vectorbrain/     # Decision layer: taxonomy, gating, orchestration contracts, runtime policy
└─ tests/           # Tests
```

## Responsibilities by module

| Module | Responsibility | Inputs | Outputs | Must NOT own |
|---|---|---|---|---|
| `agent/` | 顶层 agent 行为与会话内编排入口 | user intent, runtime context | agent action plan | DB details, platform scraping logic |
| `auth/` | 登录/认证相关集成 | tokens, credentials, auth config | authenticated state | business scoring rules |
| `config/` | 运行配置、常量、环境读取 | env, config files | typed config/runtime settings | live runtime data |
| `data/` | 当前活跃数据资产与运行中产物 | job/runtime outputs | db/index/report/state files | historical archive docs |
| `database/` | 数据库连接、session、engine、基础模型接线 | db config | db session/engine/base access | business decisions |
| `migrations/` | 数据库 schema 迁移 | schema changes | migrated schema | runtime logic |
| `pipeline/` | 多平台统一流水线：搜索→详情→评分→推荐 | user profile, platform results | normalized jobs, recommendations | platform-specific browser logic |
| `qing_platform/` | 各平台适配器：搜索、详情、投递实现 | keyword/city/job url/platform context | raw jobs / detail / apply result | cross-platform scoring policy |
| `repositories/` | DB 仓储抽象 | db session, entities | CRUD/repository methods | orchestration decisions |
| `routes/` | API / UI 接口暴露 | requests | API responses | deep business logic |
| `scripts/` | 正式运行入口与运维脚本 | CLI args | run results / reports | reusable business primitives |
| `services/` | 业务服务层：投递、去重、状态收口、通知等 | pipeline outputs, repositories | applied/skipped/failed results | low-level parsing |
| `tools/` | 纯工具函数层：解析、评分、格式化、匹配 | text/jobs/profile | structured helper results | orchestration / side effects |
| `vectorbrain/` | 决策与编排层：岗位族、硬闸门、运行策略、任务分组 | titles, jd, profile, orchestration policy | decision buckets / task plans | platform scraping implementation |
| `tests/` | 测试验证 | code under test | pass/fail evidence | production runtime state |

## Key dependency direction

```text
config -> database
config -> qing_platform
repositories -> database
services -> repositories
pipeline -> qing_platform + tools + services
vectorbrain -> tools/config-like policy files
scripts -> pipeline + services + vectorbrain
routes -> services / pipeline
agent -> scripts / services / vectorbrain (high-level only)
```

## Hard boundaries

### 1. `qing_platform/` boundary
- 只负责“某个平台怎么搜 / 怎么抓 / 怎么投”
- 不负责跨平台统一评分口径
- 不负责长期记忆

### 2. `pipeline/` boundary
- 负责把多个平台结果统一成一条处理链
- 不应该承载平台细节硬编码
- 不应该替代 `vectorbrain/` 的决策规则中心

### 3. `vectorbrain/` boundary
- 负责“该不该进下一步”的规则决策
- 包括：岗位族、边界、硬闸门、分桶、编排计划
- 不负责直接抓平台页面
- 不负责数据库 CRUD 细节

### 4. `services/` boundary
- 负责“怎么执行业务动作”
- 比如 apply、dedupe、notify、status normalization
- 不负责定义岗位边界原则

### 5. `tools/` boundary
- 保持尽量纯函数/低副作用
- 只做解析、匹配、格式化、评分辅助
- 不直接承担流程编排

## Current canonical execution path

```text
scripts/run_* 
  -> build/load user profile
  -> pipeline/
  -> vectorbrain/ gating + taxonomy + bucket decision
  -> services/application_service
  -> data/ reports + state
```

## Current canonical decision path

```text
raw platform jobs
  -> normalize
  -> role/title boundary (`job_taxonomy.py`)
  -> hard gate (`gating.py`)
  -> dynamic scoring (`tools/dynamic_scorer.py`)
  -> delivery bucket/apply decision
```

## Current cleanup conclusion
- `scripts/` 已只保留正式运行入口
- 历史报告、stage 运行产物、旧备份、旧临时脚本已迁出 active tree
- 当前 `qing-agent/` 根目录只保留业务系统骨架与必要入口文件
