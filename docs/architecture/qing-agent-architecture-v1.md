# qing-agent Architecture v1

## Core runtime modules
- agent/ : agent orchestration entry logic
- auth/ : auth integration
- config/ : runtime/app config
- data/ : active runtime data/report output
- database/ : db bootstrap/session/alembic support
- migrations/ : schema migration versions
- pipeline/ : multi-platform pipeline orchestration
- qing_platform/ : platform adapters (zhilian/51job/liepin...)
- repositories/ : repository layer
- routes/ : API/web routes
- services/ : application/business services
- tools/ : scoring/parsing/formatting helpers
- vectorbrain/ : orchestration/gating/taxonomy/runtime policy
- tests/ : tests
- scripts/ : qing-agent scoped operational scripts

## Root files kept
- .env / .env.example
- alembic.ini
- main.py
- openclaw.py
- README.md
- requirements.txt
- run.ps1
- schemas.py
- __init__.py

## Moved out of root
Historical docs, old reports, temp scripts, old dbs, backups, session cache, logs.
