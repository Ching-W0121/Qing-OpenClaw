# Target Structure v2 Mapping

## Workspace-level mapping

| Current | Target semantic role | Immediate action | Future optional rename |
|---|---|---|---|
| `qing-agent/` | Core application | keep | no immediate rename |
| `memory/` | Memory middleware | keep | no immediate rename |
| `integrations/feishu/` | Integration endpoint | done | none |
| `integrations/skills/` | Integration skills layer | done | none |
| `scripts/` | Global ops scripts | keep | none |
| `archive/` | Cold archive | keep | none |
| `docs/` | Governance/docs | keep | none |
| `.openclaw/` | Runtime environment | keep | none |
| `node_modules/` | Dependency layer | keep | none |

## qing-agent semantic mapping

| Current | Target semantic role | Immediate action | Future optional rename |
|---|---|---|---|
| `database/` | core persistence | keep | `core/persistence/` |
| `repositories/` | core data access | keep | `core/repositories/` |
| `services/` | core business logic | keep | `core/services/` |
| `pipeline/` | flow orchestration | keep | `core/pipeline/` or `flow/` |
| `qing_platform/` | platform adapters | keep | `adapters/platforms/` |
| `tools/` | helper toolkit | keep | `adapters/tools/` or `shared/tools/` |
| `vectorbrain/` | decision brain | keep | `brain/` |
| `scripts/` | business run entrypoints | keep | `scripts/` |
| `routes/` | API boundary | keep | `interfaces/routes/` |
| `auth/` | auth boundary | keep | `interfaces/auth/` |
| `config/` | app config | keep | `config/` |
| `data/` | runtime data area | keep | `data/` |
| `tests/` | verification | keep | `tests/` |

## memory semantic mapping

| Current | Target semantic role | Immediate action | Future optional rename |
|---|---|---|---|
| `database/` | physical store | keep | `store/database/` |
| `semantic/` | vector/semantic store | keep | `store/semantic/` |
| `working/` | active working context | keep | `engine/working/` |
| `episodic/` | compatibility event view | keep but de-emphasize | `store/episodic/` |
| `compat/` | compatibility entry layer | keep | `engine/compat/` |
| `summaries/` | compressed summary layer | keep | `engine/summaries/` |
| `weekly_summary/` | periodic summary layer | keep | `engine/weekly/` |
| `archive/` | memory cold archive | keep | `archive/` |
| `unified_memory.py` | single write/read middleware entry | keep | `engine/unified_memory.py` |
| `memory_search.py` | default retrieval entry | keep | `engine/memory_search.py` |
| `vector_memory.py` | semantic retrieval/write support | keep | `engine/vector_memory.py` |
| `watchdog.py` | monitoring/auto-backfill | keep | `monitor/watchdog.py` |
| `sentinel_monitor.py` | monitoring | keep | `monitor/sentinel_monitor.py` |
| `preflight_guard.py` | execution gate | keep | `monitor/preflight_guard.py` |
| `reflection-worker.js` | reflection runtime | keep | `monitor/reflection-worker.js` |

## Hard migration rule
- For now: semantic mapping only.
- Do NOT mass-rename qing-agent/ or memory/ directories until import graph and runtime entrypoints are exhaustively updated.
- Safe changes now = docs, integration-layer moves, archive cleanup, root cleanup, script ownership cleanup.
- Risky changes later = package/module renames (`core/`, `adapters/`, `brain/`, `engine/`, `store/`, `monitor/`).
