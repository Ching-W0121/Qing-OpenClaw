## [LRN-20260317-001] correction

**Logged**: 2026-03-17T17:55:00+08:00
**Priority**: critical
**Status**: pending
**Area**: infra

### Summary
重大任务结果不能只停留在聊天上下文，必须在完成当下实时写入统一记忆主库。

### Details
用户明确指出：如果重大任务没有实时记录，就可能导致整段工作成果丢失，出现“忙了一下午却没有记住”的严重问题。此次已确认存在统一记忆写入器 `memory/unified_memory.py`，但缺少“重大任务完成后必须立即落库”的硬性执行环节，导致求职 Agent 下午运行结果没有同步进入主记忆链路，`memory/working/session_current.json` 仍停留在 2026-03-11 的旧状态。

### Suggested Action
1. 将“重大任务必须即时落库”写入 AGENTS.md / TOOLS.md 作为强制规则。
2. 提供统一脚本 `memory/record_task_completion.py`，任务完成后立即调用。
3. 执行后必须验证 working memory 和 episodic 记录都已更新，再向用户汇报。
4. 后续所有真实投递、Agent 运行结果、系统迁移、重要配置变更一律走该流程。

### Metadata
- Source: user_feedback
- Related Files: AGENTS.md, TOOLS.md, memory/unified_memory.py, memory/record_task_completion.py, memory/working/session_current.json
- Tags: memory, realtime, critical, correction
- Pattern-Key: harden.realtime_memory_recording
- Recurrence-Count: 1
- First-Seen: 2026-03-17
- Last-Seen: 2026-03-17

---

## [LRN-20260317-002] best_practice

**Logged**: 2026-03-17T22:17:00+08:00
**Priority**: critical
**Status**: pending
**Area**: infra

### Summary
统一记忆系统当前仍是“主库写入 + 兼容文件层 + 批量向量同步”的过渡态，不能误判为已经完成实时向量化。

### Details
今天复盘确认：`memory/unified_memory.py` 在写入 `episodes` 的同时，仍会追加 `memory/episodic/YYYY-MM-DD.jsonl` 作为兼容备份；`memory/vector_memory.py` 通过 `sync_from_main_db()` 批量扫描主库补入 `memory_vectors`，而不是在 `append_episode()` 后立即向量化。因此“SQLite 是唯一事实源”在事实存储层基本成立，但“实时写入即实时进向量库、且不再出现文件层产物”这一目标并未真正实现。下午求职 Agent 的 auto-apply 运行结果没被实时记住，也暴露出业务脚本产物尚未统一接入记忆写入链路。

### Suggested Action
1. 在 `append_episode()` / 统一写入入口后直接触发 `upsert_vector()`，实现逐条实时向量化。
2. 将求职 Agent 运行结果（如 auto_apply_reports 生成后）自动写入 `episodes`，不要只停留在业务 JSON 文件中。
3. 将 `memory/YYYY-MM-DD.md`、`working/*.json`、`episodic/*.jsonl` 明确定义为摘要/兼容视图，不再作为“实时真相”的替代物。
4. 对外描述系统状态时，明确区分：事实主库、兼容备份、摘要视图、向量召回层，避免自我误判“已完成”。

### Metadata
- Source: reflection
- Related Files: memory/unified_memory.py, memory/vector_memory.py, memory/README.md, memory/2026-03-17.md, qing-agent/data/auto_apply_reports/auto_apply_afternoon_20260317_160552.json
- Tags: memory, vector, realtime, architecture, jobs
- See Also: LRN-20260317-001
- Pattern-Key: clarify.memory_pipeline_realtime_gap
- Recurrence-Count: 1
- First-Seen: 2026-03-17
- Last-Seen: 2026-03-17

---
## [LRN-20260330-001] correction

**Logged**: 2026-03-30T10:33:58.5815141+08:00
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
用户已明确指出某条浏览器/投递链路有“之前成功过的方法”时，必须先复用那条已验证方法，不能继续沿用旧链接或旧失败路径死循环。

### Details
本轮用户直接纠正：assistant 一直在用旧链接跑，没有优先切回“之前成功过的方法”，同时反思/记忆系统也没有在失败后真正发挥止损作用，导致重复尝试同一路径、形成死循环。这说明当前执行虽然口头上有“记忆优先 / 3 次法则 / preflight guard”，但在实际任务切换时，没有把“上一个成功样本的方法、入口链接、验证信号”作为硬前置条件，仍然会掉回旧路径。

### Suggested Action
1. 同类任务重跑前，先检索最近一次成功样本，明确记录：成功入口链接、使用方法、验证信号。
2. 如果当前运行路径不是最近成功路径，默认停止，不直接开跑。
3. 对浏览器/投递/外部网页任务，失败达到 3 次必须终止，并向用户报告“旧路径已停用，需切回成功路径或人工确认新入口”。
4. 反思系统不只记录结论，还要把“成功方法优先于历史旧链接”提升为执行硬规则。

### Metadata
- Source: user_feedback
- Related Files: AGENTS.md, TOOLS.md, MEMORY.md, .learnings/LEARNINGS.md
- Tags: correction, browser, deadloop, successful-path, retry-control
- Pattern-Key: enforce.last_known_good_path_before_browser_retry
- Recurrence-Count: 1
- First-Seen: 2026-03-30
- Last-Seen: 2026-03-30

---
## [LRN-20260318-001] best_practice

**Logged**: 2026-03-18T04:15:45
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Memory distillation worker should not rely only on today's episodic file during date-rollover windows.

### Details
A scheduled 
un-memory-distillation was triggered at 2026-03-18 04:12 Asia/Shanghai. The existing worker in memory-cleanup-backup-20260317-095759/distillation-worker.js only loads memory/episodic/<today>.jsonl. Because the newest episodic file was still 2026-03-17.jsonl, the worker reported No episodes to distill and skipped useful recent memory. This creates a silent gap around local date rollover or when file creation lags behind runtime date.

### Suggested Action
Update distillation logic to fall back to the latest available episodic file(s), or query the SQLite main memory DB directly instead of assuming a same-day JSONL file exists.

### Metadata
- Source: reflection
- Related Files: memory-cleanup-backup-20260317-095759/distillation-worker.js, memory/episodic/2026-03-17.jsonl
- Tags: memory, distillation, rollover, fallback
- Pattern-Key: harden.memory_distillation_date_rollover

---
## [LRN-20260318-002] correction

**Logged**: 2026-03-18T10:12:46
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
For 51job apply verification, backend/user-observed application results can be more reliable than immediate in-page success heuristics.

### Details
During 51job repair, the assistant concluded the real apply loop was still blocked because page-state heuristics returned unknown / 
ot confirmed. The user then reported that two new applications were already successfully submitted. This means the execution layer likely worked while the verification layer lagged behind. Future diagnosis should prioritize authoritative downstream evidence (user-confirmed backend records / My Apply list delta) over fragile immediate page-text heuristics.

### Suggested Action
Refocus 51job repair from click-path debugging to post-submit verification and application-record persistence. Add verification based on application list delta and backend-visible applied status.

### Metadata
- Source: user_feedback
- Related Files: qing-agent/services/application_service.py, qing-agent/qing_platform/job51_adapter.py
- Tags: 51job, verification, correction, apply-loop
- Pattern-Key: harden.job51_post_submit_verification

---
## [LRN-20260318-003] best_practice

**Logged**: 2026-03-18T10:16:30
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
When browser automation appears to fail but downstream evidence exists, treat the issue as a verification-layer bug before assuming the execution-layer is broken.

### Details
In the 51job repair loop, multiple tests returned ailed or unknown, which initially suggested the apply action itself was not succeeding. After user feedback confirmed that two jobs had actually been submitted, the correct framing became clear: the apply execution likely worked, while success detection and persistence lagged. This is a recurring pattern in browser automation on dynamic sites.

### Suggested Action
For future apply-loop debugging, separate the pipeline into: (1) action execution, (2) success verification, (3) persistence/reporting. Confirm each independently and avoid collapsing all failures into the action layer.

### Metadata
- Source: reflection
- Related Files: qing-agent/services/application_service.py
- Tags: browser-automation, verification, persistence, 51job
- Pattern-Key: separate.execution_from_verification

---
## [LRN-20260318-004] correction

**Logged**: 2026-03-18T15:59:48
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
Memory system storage and job-agent storage are separate systems and must not be conflated.

### Details
User clarified that the memory system is independent from the job application agent system. The memory system uses SQLite, while the job agent system uses PostgreSQL. Prior investigation incorrectly treated qing-agent local SQLite files as if they represented the full job-agent persistence layer, which led to wrong conclusions about where authoritative application data should live.

### Suggested Action
Treat memory DB and job-agent DB as separate truth domains. When checking job application persistence, inspect the PostgreSQL-backed job-agent database first; do not infer job-agent completeness from the memory database or unrelated SQLite compatibility files.

### Metadata
- Source: user_feedback
- Related Files: qing-agent/database/db.py, memory/unified_memory.py
- Tags: database, architecture, correction, persistence
- Pattern-Key: separate.memory_db.from.job_agent_db

---
## [LRN-20260318-005] architecture

**Logged**: 2026-03-18T16:17:29
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
Memory system and job-agent system must use separate databases with separate responsibilities.

### Details
Today exposed a major architecture confusion: the memory system is intended to use SQLite (plus vector retrieval) for work-state / reflection / process memory, while the job application agent should use PostgreSQL for hard business data such as jobs, applications, matches, and platform statuses. Investigation showed runtime code still hard-bound the job-agent to local SQLite, despite PostgreSQL being configured in .env. This caused incorrect reasoning about source-of-truth and risked mixing business persistence with memory persistence.

### Suggested Action
Complete database-layer separation: keep memory on SQLite/vector, move job-agent runtime DB access to PostgreSQL, and define clear truth domains so platform totals / applications are never inferred from memory storage.

### Metadata
- Source: reflection
- Related Files: qing-agent/database/db.py, qing-agent/.env, memory/unified_memory.py, memory/vector_memory.py
- Tags: architecture, database-separation, postgresql, sqlite, memory-system
- Pattern-Key: enforce.separate.truth_domains

---
## [LRN-20260319-004] correction

**Logged**: 2026-03-19T11:52:00+08:00
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
求职 Agent 今日智联重跑轮次在用户视角上应判定为失败：虽然完成了多轮搜索/抓取/评分，但未在可接受时间内完成今日投递主目标。

### Details
用户明确指出“你这轮算失败的”。这次重跑虽然压住了上一轮的重复投递 bug，但新的主要瓶颈变成了关键词家族搜索链过重：系统在多个近义关键词之间重复执行搜索→抓详情→评分，20 分钟内仍主要停留在前置检索阶段，没有及时完成用户真正关心的‘今日份投递’。这说明成功标准不能只看链路有没有工作，而要看是否在合理时间内完成主线业务目标。

### Suggested Action
1. 把“今日投递轮次”的成功标准改成：在可接受时间内完成真实投递，而不是仅完成搜索/抓取/评分。
2. 智联重跑时收缩关键词，只保留主关键词（如品牌策划 / 品牌经理 / 品牌设计 / 视觉设计），避免家族词全量轮询。
3. 为长轮次增加阶段超时：搜索阶段超过阈值仍未进入投递，则主动停机并切换策略。
4. 结果汇报必须明确区分：搜索成功 ≠ 投递成功；链路在前置阶段打转时应直接判失败并止损。

### Metadata
- Source: user_feedback
- Related Files: qing-agent/scripts/run_auto_apply_round.py, qing-agent/services/application_service.py, .learnings/LEARNINGS.md
- Tags: jobs, correction, timeout, search-strategy, failure-criteria
- Pattern-Key: jobs.round_success_requires_actual_apply
- See Also: LRN-20260319-002

---
## [LRN-20260319-002] correction

**Logged**: 2026-03-19T09:27:00+08:00
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
在用户已完成“主动记忆 + 双端共享记忆”后，不能再把 Markdown 兼容视图当成主记忆读取路径。

### Details
用户明确指出：昨天已经在飞书侧完成主动记忆和双端共享记忆能力，但本轮问答里 assistant 仍优先读取 `memory/YYYY-MM-DD.md` 等 Markdown 文件来回答“昨天做了什么”。这说明当前会话层执行仍停留在旧习惯：把 md 文件视作主来源，而不是优先从统一记忆主库/主动记忆链路读取。即使 md 仍作为兼容视图存在，也不应再把它描述或使用成“主记忆系统已经完成后的默认读取路径”。

### Suggested Action
1. 以后涉及“昨天做了什么 / 我们记住了吗 / 最近完成了什么”时，默认先查统一记忆主库或主动记忆链路。
2. `memory/*.md`、`MEMORY.md` 只作为兼容摘要/人工整理视图，不再当成主事实源。
3. 需要把“主动记忆 + 双端共享记忆已完成，但会话层默认读取路径未切换”明确区分开，避免误报“系统没完成”或误用旧入口。
4. 后续应把这条规则提升到 AGENTS.md / TOOLS.md，防止再次回退到 md-first。

### Metadata
- Source: user_feedback
- Related Files: MEMORY.md, memory/2026-03-18.md, memory/database/optimized_memory.db, .learnings/LEARNINGS.md
- Tags: memory, correction, active-memory, shared-memory, source-of-truth
- Pattern-Key: switch.memory_reads_to_active_store
- See Also: LRN-20260317-002, LRN-20260318-006

---
## [LRN-20260319-001] best_practice

**Logged**: 2026-03-19T04:16:30+08:00
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Scheduled memory reflection must have a first-class fallback path; otherwise the reminder fires but real reflection silently degrades into manual patching.

### Details
At 2026-03-19 04:15 Asia/Shanghai, the scheduled `run-memory-reflection` reminder ran, but the active workspace no longer had `memory/reflection-worker.js`. The only executable outcome was `NO_REFLECTION_WORKER`, so reflection had to be handled manually by reading `.learnings/` and logging a new error/lesson. This repeats the broader pattern already seen on 2026-03-18: maintenance jobs should not depend on stale backup scripts or assumed file locations.

### Suggested Action
1. Reintroduce an active reflection entrypoint under `workspace/memory/`, or replace it with a Python/JS script that queries the active SQLite memory DB directly.
2. Make the scheduled reminder path explicit: worker exists → run it; worker missing → run a stable fallback script, not just ad-hoc manual reflection.
3. Track scheduled-memory job health in `memory/distillation.log` so missing-worker states are visible immediately.

### Metadata
- Source: reflection
- Related Files: memory/, memory/distillation.log, .learnings/ERRORS.md
- Tags: memory, reflection, scheduler, fallback
- See Also: ERR-20260318-001, ERR-20260319-001, LRN-20260318-001
- Pattern-Key: harden.memory_reflection_worker_fallback

---
## [LRN-20260318-006] best_practice

**Logged**: 2026-03-18T22:16:52
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
Memory reporting must use structured memory-entry counts, not vector counts.

### Details
Today the user corrected the assistant for reporting 	otal_vectors as if it were the total memory count. The intended memory-system design is: SQLite as the structured fact store, vector storage as a retrieval layer, and optional binary evidence as a separate layer. A single task can generate multiple vectorized field chunks, so vector totals and memory-entry totals are different metrics and must never be conflated in user-facing reports.

### Suggested Action
Standardize all memory-write entry points to report ������� X �� / �ܼ������� Y �� using the structured SQLite memory-entry count (for example episodes rows), while vector writes remain an internal secondary metric.

### Metadata
- Source: reflection
- Related Files: memory/record_task_completion.py, memory/unified_memory.py, memory/vector_memory.py
- Tags: memory-system, vector, sqlite, counting, reporting
- Pattern-Key: memory.counts_use_structured_entries

---
## [LRN-20260319-005] correction

**Logged**: 2026-03-19T16:34:00+08:00
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
�ؼ���������ֻ˵����ʵʱ���䡱��������ȷ����д�����ĸ��㼶��д�����������ǰ������������

### Details
�û���ȷ���������Ǹ��������Ѿ�ʵʱ���䡱������Ҫ���������ĸ��㼶д���˶��������䣬�ܼ����Ƕ��١���Ҫ����ʵʱ���ݷ������û�ͬʱָ���������÷����Դ��ڲ�ͳһ���⡪�������� A�������� B��������������������� GPT ����������ظ�������

### Suggested Action
1. �Ժ�ؼ�������ɺ�ͳһ������ָ�꣺Episodes / Knowledge / Summaries / Profile / Vectors��
2. ������ģ���������Ҽ�ס�ˡ������Ǹ�ʵʱ������
3. ������� GPT/ChatGPT �ķ�ʽ����̶���ͬһ�׳ɹ���·����ֹ����һ�֡�����һ�֡�
4. ����������ͬʱ��Ϊ��ͨ���� + ִ�й���

### Metadata
- Source: user_feedback
- Related Files: .learnings/LEARNINGS.md, memory/record_task_completion.py, memory/memory_search.py
- Tags: memory, correction, reporting, consistency, browser
- Pattern-Key: enforce.realtime_memory_counts_feedback
- See Also: LRN-20260319-002

---
## [LRN-20260319-006] correction

**Logged**: 2026-03-19T16:40:00+08:00
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
������� GPT / ChatGPT ʱ����������֤���������ʵд��ɹ�������̸�ύ��̶���·�����ܷ������ȶ������ټ���ɹ���

### Details
�û���ȷָ������û�м�鵽��ʵ״̬������ûд�뵽��������棬��ȥ�Ȼظ�����˵����ǰ����ֻ���������̬ҳ���Ѳ���������ִ��˳����ˡ���Ӧ������ͨһ����ʵ����֤�Ľ�������������ڡ��ı��ɼ����ύ�ɹ���ҳ�����ظ��������ٰ����̻�Ϊ��׼��·������������ƹ̶���·��ȥ�ܡ�����᲻���ظ���������ִ���ˣ�ʵ����û�ɹ����Ĵ���

### Suggested Action
1. �������������ĳ��Ķ���֤����λ����� -> ��֤�ı���д�� -> ��֤��Ϣ���ύ -> ��֤ҳ�����ظ�����
2. δ��֤д��ɹ�ʱ�����������ơ��Ѿ��ʵ��ˡ���
3. ��·��׼�����뽨���ڳɹ�����֮�ϣ������ȶ�������������
4. ���˹�����Ϊ������Զ���Ӳ���򣬺��������ƹ㵽��ְ Agent ���ⲿ��ѯ��·��

### Metadata
- Source: user_feedback
- Related Files: .learnings/LEARNINGS.md, TOOLS.md
- Tags: browser, correction, verification, consistency
- Pattern-Key: browser.verify_real_input_before_submit
- See Also: LRN-20260319-005

---
## [LRN-20260319-001] correction

**Logged**: 2026-03-19T17:52:11.1360993+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
�û����Ѻ��ȥ����䣬˵��������������������û������ memory_search �������м�¼��

### Details
���ֶԻ���û�˵��Gemini��GPTѯ�����⡱��assistant ֱ�����û������������⣬û���Ȱ� workspace �����ѯͳһ�������⡣�û������ȷ�������㲻������ϵͳ�𣿡�����˵���ڴ���������֮ǰ���Զ�/Gemini/GPT���⡱����ǿ������ʷ�����ĵ�����ʱ�������Ȳ� memory_search���پ����Ǽ���ִ�С��������⣬�������û�����ȷ�ϡ�

### Suggested Action
�ѡ��漰����֮ǰ������ / ���Զ� / Gemini / GPT / ��������ʲô / �㻹�ǵ��𡱵�����������������Ĭ����Ϊ�Ȳ��������Ĵ�������δ����ǰ��Ҫ�����û��ظ�������

### Metadata
- Source: user_feedback
- Related Files: AGENTS.md, TOOLS.md, MEMORY.md
- Tags: memory, correction, workflow, context-retrieval
- Pattern-Key: query.memory_before_followup

---
## [LRN-20260319-002] correction

**Logged**: 2026-03-19T18:15:26.4146298+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
�û�Ҫ�� 2026-03-19 ��������ʱ����������ʱ��assistant �����˿���ɼ��䣬����������ҡ�

### Details
�����û���ȷָ����Ҫ�ҡ�������������⡱��Ӧ�Ȱ� 2026-03-19 ��ʱ�䷶Χ��խ�����ڵ��ռ����ж�λ�������⡣assistant ֮ǰ���ֱ�������������������� 3 �� 14/15 �Ⱦɼ�¼һ������������Ȼ����������أ����������û�Ҫ��ʱ��ê���������ɻش�ɢ�����ҡ�

### Suggested Action
���û��ʡ���������/�������/�ղ�/����ĳʱ�Ρ�������ʱ������ memory_search ������/ʱ��㼶��խ��Χ���������ζ�λ�����ȷ��ظ�ʱ�䴰�ڵĵ�һ���ۣ���Ҫ�����п�����ؼ��䡣

### Metadata
- Source: user_feedback
- Related Files: AGENTS.md, TOOLS.md
- Tags: memory, correction, retrieval, timeline
- Pattern-Key: query.time_window_before_semantic_search

---
## [LRN-20260323-001] correction

**Logged**: 2026-03-23T15:24:00+08:00
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
�������ڻ㱨���û�ǰ���������ȥ�أ����ܰ�δȥ�غ�ѡ�ȱ����û���˵��������ȥ�ء���

### Details
�û���ȷ������ȥ��Ӧ�÷����������������ûؽ���Ĺ����У������ǰ�ûȥ�صĺ�ѡ�嵥��չʾ�������˴��ӻỰ����������ѡ�������������������׶��Իش�����û���Ȱѡ�ͬ��˾����ظ���/ͬһ��λ���ظ����ӡ���������ͳһѹƽ�����»㱨˳�򲻷����û�Ҫ��

### Suggested Action
�������С������� + �ӻỰ������������̱���������ȥ�� �� ��Ͷ�ж� �� �ٻ㱨����ֹ��δȥ�غ�ѡֱ�ӱ�¶���û���

### Metadata
- Source: user_feedback
- Related Files: qing-agent/scripts/run_dual_platform_apply_strict.py
- Tags: jobs, dedupe, orchestration, correction

---
## [LRN-20260323-002] correction

**Logged**: 2026-03-23T15:50:00+08:00
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
����Ͷ�ݳɹ��жϲ���ֻ�� alreadyApplied�����֡���ϲ����Ͷ�ݳɹ��������ڡ���ְ�������г����¼�¼��ҲӦ�ж�Ϊ�ɹ���

### Details
�û���ȷ����������������λʵ�����Ѿ�Ͷ�ݳɹ��������ж������Ƿ�Ͷ�ݳɹ�������ҳ����� alreadyApplied �ź��⣬��Ӧ���ȼ���Ƿ���֡���ϲ����Ͷ�ݳɹ������İ�����ҳ���İ����ȶ�������롰��ְ������ҳ��˶��Ƿ������Ͷ�ݳɹ��б���������Ϊ confirm_button_not_found �Ͳ������ failed��

### Suggested Action
���� ZhilianAdapter.apply / ApplicationService._apply_zhilian �ĳɹ��ж����ȼ���ҳ��ɹ��İ� > ��ְ�����б����� > alreadyApplied�����������඼ӳ�䵽�ɹ���״̬���� failed��

### Metadata
- Source: user_feedback
- Related Files: qing-agent/qing_platform/zhilian_adapter.py, qing-agent/services/application_service.py
- Tags: zhilian, apply, verification, correction

---
## [LRN-20260323-003] correction

**Logged**: 2026-03-23T16:13:00+08:00
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
���Խ׶�Ҳ���밴����������һ���Խ�����������ƥ���ȥ�ء����ر����м䲽�費Ӧ�����û�ֱ�������ǳ��ִ���

### Details
�û���ȷ��������ǰ��·��Ȼ�ڲ��ԣ������幤������ƫ�ˡ��û�Ҫ���������ջ�����������ǡ�������ʲô����һ����ô�����Ĺ����Ի㱨��������ƥ�䡢ȥ����Щ�м䲽��Ĭ�ϲ���Ҫ���û��𲽻㱨��ֻ���ڳ��ִ����쳣��ֹ������Ҫ�˹�����ʱ��Ӧ��ϻر���

### Suggested Action
������ְ��·Ĭ�ϲ��þ�Ĭִ�У��ڲ��������/ƥ��/ȥ��/ɸѡ�����һ���Է��ؽṹ�����񣻽��ڴ�����֤�롢��·�жϡ����˹�����ʱ��ʱ�㱨��

### Metadata
- Source: user_feedback
- Related Files: qing-agent/scripts/run_dual_platform_apply_strict.py
- Tags: workflow, jobs, correction, reporting

---

## [LRN-20260325-001] best_practice

**Logged**: 2026-03-25T11:04:31.2285510+08:00
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
长链路“搜索+补详情+评分+去重+自动投递”在单主进程浏览器串行执行时过慢，应拆成分阶段可落盘的正式跑法。

### Details
本次用户要求按智联/前程无忧、品牌策划/品牌设计、1-10 页完整跑完。实际执行时发现，真正慢的核心不是双平台概念本身，而是当前实现把搜索、详情补全、评分、去重、投递串成一条超重主链，并依赖浏览器逐页/逐职位交互，导致：1) 前半段没有阶段性落盘；2) 一旦卡在首个平台或页面等待，用户看起来像“停了”；3) 全程跑完前难以及时给出中间结果。正确认知应是：用户可以一次性下达“全程跑完”的命令，但系统实现上仍应先筛选再投递，并在阶段间落盘/汇报，而不是把所有工作都堵在单条无检查点长链里。

### Suggested Action
把正式主跑改成分阶段：先搜索与候选落盘，再详情补全/评分去重落盘，最后单独投递；每阶段输出可见进度与中间结果，并优先按平台单跑以便定位阻塞点。

### Metadata
- Source: conversation
- Related Files: qing-agent/scripts/run_dual_platform_brand_apply_full.py, qing-agent/scripts/run_zhilian_brand_apply_full.py
- Tags: performance, browser-automation, pipeline, job-agent
- Pattern-Key: split.long_browser_pipeline

---
## [LRN-20260326-001] correction

**Logged**: 2026-03-26T10:07:00.4352880+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
������λ��������ʱ�����ˡ�10ҳ���ؼ��ʽ������˫�ؼ��ʽ������ͬ�ļ�˫�����ظ�չ�������ֿھ����������û��㱨�˴����������

### Details
�û�ָ�� 10 ҳÿҳ 20 ��������Ӧ�Ȱ� 200 �������Ų��ȷ�ϣ�1) ��ǰ���������������ؼ��ʣ�Ʒ�Ʋ߻���Ʒ����ƣ������ǵ��ؼ��� 10 ҳ��2) 4-6 ҳ�ļ�ͬʱ���� page_results.raw_jobs �� all_raw_jobs��pipeline ��ǰ������߶�չ����������һ�� 120 ���ظ���� 240��3) �����֮ǰ������ 400 / 241 ����ֱ����������10 ҳ���������Ľ���ھ���

### Suggested Action
�����㱨�����������ھ������ؼ���/˫�ؼ��ʡ�ҳ��λ����ԭʼ������ȥ�����������޸� pipeline �� all_raw_jobs �� page_results.raw_jobs ���ظ�չ����

### Metadata
- Source: user_feedback
- Related Files: qing-agent/data/zhilian_candidate_pipeline_20260325.py
- Tags: zhilian, counting, correction
- Pattern-Key: harden.reporting.scope

---
## [LRN-20260326-001] correction

**Logged**: 2026-03-26T11:49:30+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
�� browser tool ��ʱ�����󣬴���ذѡ����� gateway��������һ��Ĭ�Ϸ�����û���Ⱥ�ʵ�Ƿ������Ҫ�ö�����

### Details
�û�ָ���������������ء�����δ���ĸ����ǰѹ��ߴ�����ʾ��е���Ƴ�ִ�з�����û��������ϸ���жϣ�Ҳû����ͣ����ȷ�ϸ�С����ֱ�ӵ����·������ģʽ���ǰ���ȳ�ŵͨ·������֤ͨ·������ͬ��ִ��ȱ�ݡ�

### Suggested Action
���� browser/gateway �౨��ʱ�������֣�browser control �Ự��ʱ��ҳ��/��ǩ�쳣������ gateway �������ϣ�δȷ��ǰ����Ĭ�Ͻ����ִ�� gateway restart������ѡ���С�Ļָ�������ֱ�Ӹ��߷������·����

### Metadata
- Source: user_feedback
- Related Files: .learnings/LEARNINGS.md
- Tags: correction, gateway, browser, verification, recurring-error
- Pattern-Key: verify.channel_before_recovery_action

---
## [LRN-20260327-001] correction

**Logged**: 2026-03-27T10:45:00+08:00
**Priority**: critical
**Status**: pending
**Area**: infra

### Summary
ʵʱ���ϵͳ�����У���û�аѡ����ͨ��/�������������Զ�ת������������⶯����������������ֻ�䵽����ժҪ�ͼ�ر��棬û�н��� SQLite ���� episodes��

### Details
�û�ָ����ר�����˼����ʵʱ�ල������·���� 2026-03-26 ����������δ�ܴ���������������˲鷢�֣�1) memory/watchdog_report.json��monitor_report_latest.json��watchdog_last_preflight.json ��������������£�˵�����/�Ž����ܣ�2) monitor_report_latest.json ֻ��¼ PASS/WARN/BLOCK��memory_checked��reflection_logged��is_subsession ��״̬�������� append_episode��3) preflight_guard.py ������/mark watchdog��Ҳ������д�� task_completion��4) ����д������� memory/record_task_completion.py��append_episode + upsert_working + upsert_vector����5) 2026-03-26 ������̱�д���� memory/2026-03-26.md ����ժҪ����û��ͬ���� SQLite episodes������������ͣ������ 09:57��˵�������ϵͳ���ڡ��١�ʵʱ�����ѱջ�����

### Suggested Action
�Ѽ��/ִ��բ���������·�ջ����� slow/external/subsession ������ɲ�������ȷ���ʱ������ǿ�ƴ���ͳһ�� record_task_completion ��ȼ� append_episode д�룬������ֻ���� monitor/watchdog/markdown����������ƣ������ N Сʱ�ļ��� git ������ҵ�������µ� episodes ��������ֱ�ӱ�����

### Metadata
- Source: user_feedback
- Related Files: memory/sentinel_monitor.py, memory/preflight_guard.py, memory/record_task_completion.py, memory/2026-03-26.md, memory/watchdog_report.json, memory/monitor_report_latest.json
- Tags: memory, monitoring, sqlite, realtime-memory, correction
- Pattern-Key: harden.memory-monitoring-closed-loop

---
## [LRN-20260330-001] correction

**Logged**: 2026-03-30T10:20:33.7401197+08:00
**Priority**: critical
**Status**: pending
**Area**: backend

### Summary
For modern dynamic job sites, search entry must start from the homepage UI and input box, not from handcrafted result-page URLs.

### Details
The user explicitly corrected the search approach: directly constructing old search-result URLs is no longer reliable for current dynamic job platforms. The correct path is homepage -> wait for UI render -> locate the live search input -> type keyword -> trigger search -> then snapshot and continue. Reusing old URL-entry habits caused the agent to enter outdated or invalid pages and misdiagnose the problem as a generic platform failure.

### Suggested Action
1. Update job-platform adapters so search starts from homepage UI instead of handcrafted URLs.
2. For browser automation on dynamic sites, treat input-box interaction as the primary stable entry path.
3. Keep URL entry only as a verified fallback when the platform still supports it.
4. Promote this rule into the job-agent/browser workflow guidance to avoid repeating the same failure mode.

### Metadata
- Source: user_feedback
- Related Files: qing-agent/qing_platform/zhilian_adapter.py, qing-agent/pipeline/multi_platform_pipeline.py, AGENTS.md, TOOLS.md
- Tags: jobs, browser, dynamic-site, correction, search-entry
- Pattern-Key: harden.dynamic_job_site_homepage_entry
- Recurrence-Count: 1
- First-Seen: 2026-03-30
- Last-Seen: 2026-03-30

---
