## [ERR-20260329-002] git_memory_sync_github_connection_reset

**Logged**: 2026-03-29T20:03:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
本次记忆同步已本地提交成功，但 `git push origin master` 访问 GitHub 时连接被远端重置，未完成远程同步。

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Recv failure: Connection was reset
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Result: local commit succeeded (`0a9e5e5`), push failed during HTTPS transfer
- Environment: OpenClaw exec on Windows PowerShell
- Related pattern: 与 ERR-20260329-001 / ERR-20260328-002 / ERR-20260327-001 同类，属于 GitHub 网络连通性异常复发

### Suggested Fix
后续继续直接执行 `git push origin master` 重试；若重复发生，检查当前网络、代理/VPN、防火墙，必要时测试 `github.com` HTTPS 连通性。

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260329-001, ERR-20260328-002, ERR-20260327-001

---
## [ERR-20260329-001] git_memory_sync_github_connection_reset

**Logged**: 2026-03-29T05:03:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
本次记忆同步已本地提交成功，但 `git push origin master` 访问 GitHub 时连接被远端重置，未完成远程同步。

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Recv failure: Connection was reset
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Result: local commit succeeded (`118da07`), push failed during HTTPS transfer
- Environment: OpenClaw exec on Windows PowerShell
- Related pattern: 与 ERR-20260328-002 / ERR-20260327-001 同类，属于 GitHub 网络连通性异常复发

### Suggested Fix
后续继续直接执行 `git push origin master` 重试；若重复发生，检查当前网络、代理/VPN、防火墙，必要时测试 `github.com` HTTPS 连通性。

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260328-002, ERR-20260327-001

---
## [ERR-20260328-002] git_memory_sync_github_connect_timeout

**Logged**: 2026-03-28T10:04:55+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
本次记忆同步已本地提交成功，但 `git push origin master` 因无法连接 GitHub 443 端口失败。

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Failed to connect to github.com port 443 after 21091 ms: Could not connect to server
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Result: local commit succeeded (`0c29318`), push failed during HTTPS connection establishment
- Environment: OpenClaw exec on Windows PowerShell
- Related pattern: 与 ERR-20260327-001 相同，属于 GitHub 网络连通性问题复发

### Suggested Fix
下次继续直接执行 `git push origin master`；若仍失败，检查当前网络、代理/VPN、防火墙或 GitHub 连通性。

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260327-001

---
## [ERR-20260317-001] git_auto_sync_powershell

**Logged**: 2026-03-17T13:04:29.9758766+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
记忆同步 cron 首次执行失败，因为在 PowerShell 中错误使用了 `&&` shell 连接符。

### Error
```
����λ�� ��:1 �ַ�: 29
+ git add memory/ .learnings/ && $ts = Get-Date -Format 'yyyy-MM-dd HH: ...
+                             ~~
��ǡ�&&�����Ǵ˰汾�е���Ч���ָ�����
����λ�� ��:1 �ַ�: 32
+ git add memory/ .learnings/ && $ts = Get-Date -Format 'yyyy-MM-dd HH: ...
+                                ~~~
ֻ����������ʽ��Ϊ�ܵ��ĵ�һ��Ԫ�ء�
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Command used: `git add memory/ .learnings/ && $ts = Get-Date -Format 'yyyy-MM-dd HH:mm'; git commit -m "🧠 auto-sync: $ts"; if ($LASTEXITCODE -eq 0) { git push origin master }`
- Environment: OpenClaw exec on Windows PowerShell

### Suggested Fix
在 PowerShell 中改用分号和 `$LASTEXITCODE` 控制流程，不要使用 `&&`。

### Metadata
- Reproducible: yes
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260314-011

---
## [ERR-20260326-001] python_utf8_subprocess_kw_encoding_gbk

**Logged**: 2026-03-26T11:21:58.9636030+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Windows PowerShell 下通过 here-string 管道喂给 `python -` 时，中文关键词/城市参数在本次分片扫描首轮被编码成 `????`，导致真实浏览器请求命中错误 URL（404）并产出空结果文件。

### Error
```text
智联请求日志出现：kw=%3F%3F%3F%3F；
输出文件 `dual_platform_brand_scan_pages_3_4_20260326_111829.json` 中 city/keywords 被写成 `??` / `????`；
首轮统计 total_jobs=0。
```

### Context
- Operation attempted: 子会话执行双平台品牌扫描分片（pages 3-4）
- Command style: PowerShell here-string `@' ... '@ | python -`
- Environment: OpenClaw exec on Windows PowerShell
- Follow-up: 改为 `python -X utf8 -` + Unicode escape 字面量后重跑成功，得到 live 数据文件 `qing-agent\\data\\dual_platform_brand_scan_pages_3_4_rerun_20260326_112023.json`

### Suggested Fix
Windows 下涉及中文参数的临时 Python 管道脚本，避免直接依赖 PowerShell 默认编码；优先使用 `python -X utf8 -`、`$env:PYTHONIOENCODING='utf-8'`，或在脚本中使用 Unicode escape/UTF-8 文件落盘再执行。

### Metadata
- Reproducible: yes
- Related Files: qing-agent\\data\\dual_platform_brand_scan_pages_3_4_20260326_111829.json, qing-agent\\data\\dual_platform_brand_scan_pages_3_4_rerun_20260326_112023.json, .learnings\\ERRORS.md
- See Also: ERR-20260317-001

---
## [ERR-20260324-001] memory_business_progress_not_recorded_same_day

**Logged**: 2026-03-24T18:56:00+08:00
**Priority**: critical
**Status**: pending
**Area**: infra

### Summary
2026-03-24 下午的求职 Agent 业务推进没有及时落入统一记忆，导致主会话无法直接回答“下午做到哪一步了”。

### Error
```
memory/memory_search.py 无法检索到 2026-03-24 下午业务推进记录；
memory/episodic/2026-03-24.jsonl 仅有凌晨 03:06 与 03:08 的 memory 定时任务记录。
```

### Context
- Operation attempted: 回答用户“今天下午做到哪一步、还有哪些 bug 没修好”
- Expected: 统一记忆中应存在今天下午的业务推进、筛选结果、bug 状态或任务完成记录
- Actual: 只能从工作区文件与 git 状态反推，无法从主记忆直接检索到下午业务流水
- Evidence: `memory/episodic/2026-03-24.jsonl` 仅包含 `run-memory-distillation` 与 `run-memory-reflection` 两条凌晨记录

### Suggested Fix
把“业务阶段完成 / 关键筛选结果 / bug 状态变化”接入统一记忆主链，至少在每次下午求职主流程结束后立即调用正式记录入口，确保主库、working 视图、episodic 备份同步更新。

### Metadata
- Reproducible: yes
- Related Files: memory/episodic/2026-03-24.jsonl, memory/working/session_current.json, .learnings/ERRORS.md
- See Also: ERR-20260317-001, ERR-20260318-002

---
## [ERR-20260319-003] git_push_github_connection_reset

**Logged**: 2026-03-19T18:03:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
记忆同步 cron 在本地提交成功后，推送到 GitHub 时因连接被重置而失败。

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Recv failure: Connection was reset
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Local result: commit 成功，提交哈希 `a5a31fb`
- Remote step failed: `git push origin master`
- Environment: OpenClaw exec on Windows PowerShell

### Suggested Fix
优先重试 `git push origin master`；若仍失败，检查本机网络连通性、GitHub 可达性、代理/VPN 配置，或确认是否为 GitHub 短时网络抖动。

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260317-001, ERR-20260318-002

### Recurrence
- **Last-Seen**: 2026-03-25T19:03:00+08:00
- **Notes**: 再次出现相同的 GitHub 推送连接重置问题；本地提交成功，提交哈希 `9b0b450`，远端推送失败。

---
## [ERR-20260318-002] git_auto_sync_powershell_if_expression

**Logged**: 2026-03-18T05:03:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
记忆同步 cron 再次执行失败，因为在 PowerShell 的 `if` 条件里把命令和 `$LASTEXITCODE` 检查写进同一对括号，触发了解析错误。

### Error
```
����λ�� ��:4 �ַ�: 57
+ if (-not (git diff --cached --quiet -- memory .learnings; $LASTEXITCO ...
+                                                         ~
����ʽ��ȱ���ҡ�)����
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Command used: `if (-not (git diff --cached --quiet -- memory .learnings; $LASTEXITCODE -eq 0)) { ... }`
- Environment: OpenClaw exec on Windows PowerShell

### Suggested Fix
先单独执行 `git diff --cached --quiet -- memory .learnings`，再用 `$LASTEXITCODE` 保存到变量或单独判断，不要把语句与比较表达式混写在同一个 `if (...)` 子表达式里。

### Metadata
- Reproducible: yes
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260317-001

---
## [ERR-20260317-001] powershell-test-path

**Logged**: 2026-03-17T18:04:45Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
PowerShell cron sync command used Test-Path 'memory' -or Test-Path '.learnings', which PowerShell parsed incorrectly and caused the sync job to fail before git status checks.

### Error
`
Test-Path : ???????????????or???????????
????��?? ??:3 ???: 24
+ if (Test-Path 'memory' -or Test-Path '.learnings') {
+                        ~~~
    + CategoryInfo          : InvalidArgument: (:) [Test-Path]??ParentContainsErrorRecordException
    + FullyQualifiedErrorId : NamedParameterNotFound,Microsoft.PowerShell.Commands.TestPathCommand
`

### Context
- Command/operation attempted: scheduled git sync for memory/ and .learnings/
- Input or parameters used: if (Test-Path 'memory' -or Test-Path '.learnings')
- Environment details if relevant: PowerShell on Windows

### Suggested Fix
Wrap each Test-Path call in parentheses before using -or, or skip the conditional and check paths independently.

### Metadata
- Reproducible: yes
- Related Files: .learnings/ERRORS.md

---
## [ERR-20260318-001] memory_reflection_worker

**Logged**: 2026-03-18T04:17:17
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Reflection worker reads episodic data from the backup directory instead of the active memory directory.

### Error
`
[Reflection] EPISODIC_DIR: C:\Users\TR\.openclaw\workspace\memory-cleanup-backup-20260317-095759\episodic
[Reflection] Loaded episodes: 0
[Reflection] No episodes to reflect on
`

### Context
- Operation attempted: scheduled 
un-memory-reflection
- Script used: memory-cleanup-backup-20260317-095759/reflection-worker.js
- The script sets MEMORY_ROOT = __dirname, which resolves to the backup folder, not workspace/memory

### Suggested Fix
Move/restore the reflection worker under the active memory/ directory or change path resolution to target workspace/memory explicitly / query the SQLite main DB directly.

### Metadata
- Reproducible: yes
- Related Files: memory-cleanup-backup-20260317-095759/reflection-worker.js, memory/episodic/2026-03-17.jsonl
- See Also: LRN-20260318-001

---
## [ERR-20260319-001] memory_reflection_worker_missing

**Logged**: 2026-03-19T04:15:53+08:00
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Scheduled memory reflection could not run because the active workspace has no `memory/reflection-worker.js`.

### Error
```
NO_REFLECTION_WORKER
```

### Context
- Operation attempted: scheduled `run-memory-reflection`
- Command used: `if (Test-Path "C:/Users/TR/.openclaw/workspace/memory/reflection-worker.js") { node ... } else { Write-Output "NO_REFLECTION_WORKER" }`
- Environment: OpenClaw exec on Windows PowerShell
- Result: no active reflection worker exists under the workspace `memory/` directory, so scheduled reflection currently depends on ad-hoc/manual fallback.

### Suggested Fix
Restore a supported reflection worker under `workspace/memory/`, or replace scheduled reflection with a stable DB-backed script that reads the active SQLite memory store directly instead of relying on a missing JS worker.

### Metadata
- Reproducible: yes
- Related Files: memory/, memory/distillation.log, .learnings/ERRORS.md
- See Also: ERR-20260318-001

---
## [ERR-20260318-003] git_push_network_reset

**Logged**: 2026-03-18T15:04:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
����ͬ�� cron �� commit �ɹ���git push �� GitHub ʧ�ܣ�ԭ����Զ�� HTTPS ���ӱ����á�

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Recv failure: Connection was reset
```

### Context
- Operation attempted: ÿ�ռ���ͬ���� GitHub
- Command used: `$ts = Get-Date -Format 'yyyy-MM-dd HH:mm'; git add memory/ .learnings/; git commit -m "?? auto-sync: $ts"; if ($LASTEXITCODE -eq 0) { git push origin master }`
- Result: local commit succeeded (`8e3ec2b`), push failed on network transport
- Environment: OpenClaw exec on Windows PowerShell

### Suggested Fix
�´� cron ����ʱ����ֱ��ִ�� `git push origin master`���������ʧ�ܣ��ټ�� GitHub ��ͨ�ԡ�����/VPN����Զ����֤״̬��

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260317-001, ERR-20260318-002

---
## [ERR-20260319-002] git_push_network_reset

**Logged**: 2026-03-19T16:03:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
记忆同步 cron 本次提交成功，但 `git push origin master` 再次因到 GitHub 的 HTTPS 连接被重置而失败。

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Recv failure: Connection was reset
```

### Context
- Operation attempted: 每日记忆同步到 GitHub
- Result: local commit succeeded (`edb5757`), but push failed during HTTPS transport
- Environment: OpenClaw exec on Windows PowerShell
- Prior behavior: same transport failure was already seen on 2026-03-18

### Suggested Fix
下次优先直接重试 `git push origin master`；如果仍失败，检查当前网络、代理/VPN、GitHub 连通性，必要时考虑切换为更稳定的认证/传输方式。

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260318-003, ERR-20260317-001, ERR-20260318-002

---
## [ERR-20260326-001] distillation_log_utf8_read

**Logged**: 2026-03-26T01:07:29Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
Appending to memory/distillation.log via Python Path.read_text(..., encoding='utf-8') failed because the existing log file contains non-UTF-8 bytes.

### Error
`
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb5 in position 1316: invalid start byte
`

### Context
- Operation attempted: append a new scheduled distillation line by reading then rewriting memory/distillation.log
- Environment: Windows PowerShell, workspace memory maintenance run at 2026-03-26 09:07 Asia/Shanghai
- Recovery: switched to PowerShell Add-Content append path, which avoids decoding the legacy mixed-encoding file.

### Suggested Fix
Normalize memory/distillation.log to UTF-8 if we want Python text rewrite operations to be reliable; until then, prefer append-only writes that do not decode the whole file.

### Metadata
- Reproducible: yes
- Related Files: memory/distillation.log
- See Also: ERR-20260319-001

---
## [ERR-20260327-001] git_push

**Logged**: 2026-03-27T10:05:28+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Daily memory sync commit succeeded, but git push to GitHub failed due to connection reset.

### Error
`
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Recv failure: Connection was reset
`

### Context
- Command/operation attempted: git push origin master
- Previous step succeeded: commit fd4539 created by cron sync job
- Environment: Windows host, OpenClaw workspace cron execution

### Suggested Fix
Retry push later; if recurrent, inspect network stability, proxy/VPN, GitHub reachability, or credential helper state.

### Metadata
- Reproducible: unknown
- Related Files: memory/, .learnings/
- See Also: none

---
## [ERR-20260327-001] browser_gemini_submit_path

**Logged**: 2026-03-27T11:34:30+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
�ڰ���ȷ��·�� Gemini �»Ự������������ʱ��browser ������ act(type) �׶�ֱ�ӳ�ʱʧЧ��������ʾҪ������ OpenClaw gateway����ǰ���ܼ������� browser ���ߡ�

### Error
```text
status: error
error: timed out. Restart the OpenClaw gateway (OpenClaw.app menubar, or `openclaw gateway`). Do NOT retry the browser tool �� it will keep failing. Use an alternative approach or inform the user that the browser is currently unavailable.
```

### Context
- ������ memory_search �� preflight_guard
- �ѳɹ��ҵ� Gemini �ѵ�¼��ǩҳ
- ��ͨ�� evaluate ����������족�����»Ự `https://gemini.google.com/app`
- ������ snapshot��������ʵ textbox `����˫��������ʾ`
- �ڶ���ʵ textbox ִ�� browser.act(kind=type) ������������ʱʧ��
- ������ȷҪ��Ҫ�������� browser tool

### Suggested Fix
���ȼ�鲢���� OpenClaw gateway / browser control server���ָ����ټ��� Gemini �ύ��·�����������ô���Ҫ�������� snapshot/act/ref����Ӧֱ���л��������湤��ʧЧ + ���޸�·������

### Metadata
- Reproducible: unknown
- Related Files: memory/2026-03-27.md
- See Also: LRN-20260327-001

---
## [ERR-20260327-001] ripgrep_missing

**Logged**: 2026-03-27T14:28:11.7109030+08:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
�� qing-agent �г����� rg ��λ��ʽ�������ʧ�ܣ���ǰ Windows ����δ��װ ripgrep��

### Error
`
rg : �޷��� rg ʶ��Ϊ cmdlet���������ű��ļ�������г�������ơ�
`

### Context
- Command/operation attempted: rg -n "run_auto_apply_round|run_vectorbrain_stage|run_dual_platform_apply_strict|Ʒ������|���Բ߻�|Ʒ�Ʋ߻�" -S .
- Environment: Windows PowerShell, workspace=qing-agent

### Suggested Fix
�� Windows ����Ĭ������ʹ�� PowerShell Select-String / Get-ChildItem����Ҫ���� rg һ�����á�

### Metadata
- Reproducible: yes
- Related Files: C:/Users/TR/.openclaw/workspace/.learnings/ERRORS.md

---
## [ERR-20260327-002] powershell_heredoc_misuse

**Logged**: 2026-03-27T14:38:42.7836173+08:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
�� PowerShell �������� Bash ��� python - <<'PY' heredoc������ͳ�ƽű�δִ�С�

### Error
`
MissingFileSpecification / '<' is reserved for future use
`

### Context
- Command/operation attempted: python - <<'PY' ...
- Environment: Windows PowerShell

### Suggested Fix
�� Windows PowerShell ��Ĭ��ʹ�� python -c����ʱ .py �ļ����� PowerShell here-string ���Σ���Ҫֱ������ Bash heredoc��

### Metadata
- Reproducible: yes
- Related Files: C:/Users/TR/.openclaw/workspace/.learnings/ERRORS.md

---
## [ERR-20260327-001] git_memory_sync_github_https_connect_timeout

**Logged**: 2026-03-27T15:03:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
����ͬ�� cron ���α����ύ�ɹ����� `git push origin master` ���޷����� GitHub 443 �˿ڶ�ʧ�ܡ�

### Error
```
fatal: unable to access 'https://github.com/Ching-W0121/Qing-OpenClaw-memory.git/': Failed to connect to github.com port 443 after 21108 ms: Could not connect to server
```

### Context
- Operation attempted: ÿ�ռ���ͬ���� GitHub
- Result: local commit succeeded (`15060c5`), but push failed during HTTPS connection establishment
- Environment: OpenClaw exec on Windows PowerShell
- Recent related pattern: 2026-03-19 ������ GitHub HTTPS ���ӱ����ã�����Ϊ���ӳ�ʱ/���ɴ�

### Suggested Fix
�´�����ֱ������ `git push origin master`������ʧ�ܣ���鵱ǰ���硢����/VPN������ǽ�� GitHub ��ͨ�ԣ���Ҫʱ���ø��ȶ��Ĵ���/����·����

### Metadata
- Reproducible: unknown
- Related Files: .learnings/ERRORS.md
- See Also: ERR-20260319-001, ERR-20260317-001

---
