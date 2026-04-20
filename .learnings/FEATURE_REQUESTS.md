## [FEAT-20260326-001] acp_gemini_runtime_for_external_diagnosis

**Logged**: 2026-03-26T11:40:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Requested Capability
通过 ACP runtime 直接拉起 Gemini 会话，承接对求职 Agent 分片扫描问题的外部诊断与修复。

### User Context
用户明确要求“把这些问题都丢给 Gemini，让它来给你解读和解决”，但当前 sessions_spawn(runtime=\"acp\", agentId=\"gemini\") 返回 ACP backend 未配置，无法直接执行。

### Suggested Action
配置并启用 acpx runtime plugin / ACP backend，使 Gemini ACP 会话可用；之后主会话可把诊断任务直接交给 Gemini 处理。

### Metadata
- Source: user_feedback
- Related Files: openclaw ACP runtime config
- Tags: acp, gemini, infra, capability-gap

---
