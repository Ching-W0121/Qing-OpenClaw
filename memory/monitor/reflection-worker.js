#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const MONITOR_ROOT = __dirname;
const MEMORY_ROOT = path.resolve(MONITOR_ROOT, '..');
const WORKSPACE_ROOT = path.resolve(MEMORY_ROOT, '..');
const LEARNINGS_DIR = path.join(WORKSPACE_ROOT, '.learnings');
const LEARNINGS_FILE = path.join(LEARNINGS_DIR, 'LEARNINGS.md');
const DISTILL_LOG = path.join(MEMORY_ROOT, 'distillation.log');
const LESSONS_FILE = path.join(MEMORY_ROOT, 'store', 'semantic', 'lessons.json');

function nowIso() {
  return new Date().toISOString();
}

function nowCnTag() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}+08:00`;
}

function appendLog(line) {
  fs.appendFileSync(DISTILL_LOG, line + '\n', 'utf8');
}

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function queryEpisodes(limit = 50) {
  const script = [
    'import sqlite3, json',
    `conn=sqlite3.connect(r"${path.join(MEMORY_ROOT, 'store', 'database', 'optimized_memory.db').replace(/\\/g, '\\\\')}")`,
    'conn.row_factory=sqlite3.Row',
    'cur=conn.cursor()',
    `rows=cur.execute("SELECT id, timestamp, event_type, content, metadata FROM episodes ORDER BY id DESC LIMIT ${limit}").fetchall()`,
    'print(json.dumps([dict(r) for r in rows], ensure_ascii=False))'
  ].join('; ');
  const out = execFileSync('python', ['-c', script], { encoding: 'utf8', cwd: WORKSPACE_ROOT });
  return JSON.parse(out || '[]');
}

function loadJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return fallback;
  }
}

function saveJson(file, data) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

function appendLearning(entry) {
  ensureDir(LEARNINGS_DIR);
  let prefix = '';
  if (fs.existsSync(LEARNINGS_FILE) && fs.statSync(LEARNINGS_FILE).size > 0) prefix = '\n';
  fs.appendFileSync(LEARNINGS_FILE, prefix + entry.trim() + '\n', 'utf8');
}

function hasPatternKey(patternKey) {
  try {
    const txt = fs.readFileSync(LEARNINGS_FILE, 'utf8');
    return txt.includes(`Pattern-Key: ${patternKey}`);
  } catch {
    return false;
  }
}

function buildLearning(id, summary, details, action, patternKey, seeAlso = '') {
  return `## [${id}] best_practice

**Logged**: ${nowIso()}
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
${summary}

### Details
${details}

### Suggested Action
${action}

### Metadata
- Source: reflection
- Related Files: memory/reflection-worker.js, memory/semantic/lessons.json, memory/database/optimized_memory.db
- Tags: memory, reflection, worker, db-first
${seeAlso ? `- See Also: ${seeAlso}\n` : ''}- Pattern-Key: ${patternKey}

---`;
}

function main() {
  ensureDir(path.dirname(LESSONS_FILE));
  ensureDir(LEARNINGS_DIR);

  const episodes = queryEpisodes(50);
  const lessons = loadJson(LESSONS_FILE, {
    lessons: [],
    strategies: [],
    mistakes: [],
    patterns: [],
    updated_at: null,
    source: 'reflection-worker',
    episodes_reflected: 0,
    date_range: null,
  });

  const recentTaskCompletions = episodes.filter(e => e.event_type === 'task_completion');
  const recentContents = episodes.map(e => String(e.content || ''));

  const derivedPatterns = [];
  if (recentContents.some(t => t.includes('run-memory-distillation'))) {
    derivedPatterns.push('最近一次 distillation 已写回主库，并能刷新长期摘要视图。');
  }
  if (recentContents.some(t => t.includes('run-memory-reflection'))) {
    derivedPatterns.push('最近一次 reflection 已写回主库；反思结果应继续通过正式 worker 自动产出。');
  }
  if (recentContents.some(t => t.includes('主记忆') || t.includes('主库'))) {
    derivedPatterns.push('围绕记忆系统的对话正在收口到“主库优先、兼容视图降级”的统一口径。');
  }
  if (recentContents.some(t => t.includes('执行闸门') || t.includes('READY') || t.includes('BLOCKED'))) {
    derivedPatterns.push('记忆与反思系统必须从提示层下沉到执行闸门层：未通过 preflight / probe / slow-task-dispatch 检查时应直接阻断。');
  }
  if (recentContents.some(t => t.includes('sentinel') || t.includes('监控系统'))) {
    derivedPatterns.push('应保留实时监控层来检测“查了但没遵守”“反思了但没改变执行”的执行偏移。');
  }

  for (const p of derivedPatterns) {
    if (!lessons.patterns.includes(p)) lessons.patterns.push(p);
  }

  const mdFirstPattern = 'switch.memory_reads_to_active_store';
  if (!hasPatternKey(mdFirstPattern)) {
    appendLearning(buildLearning(
      'LRN-20260319-003',
      'Reflection worker itself should follow the same db-first memory rule it is meant to enforce.',
      'The reflection worker has now been restored under workspace/memory and reads the active SQLite memory DB directly. This closes the earlier missing-worker gap and aligns maintenance jobs with the same source-of-truth rule expected from normal assistant turns: structured memory first, compatibility/summaries second.',
      'Keep scheduled reflection db-first; if summaries are updated, treat them as downstream views rather than upstream truth sources.',
      'harden.reflection_worker_db_first',
      'LRN-20260319-002, LRN-20260319-001'
    ));
  }

  lessons.updated_at = nowIso();
  lessons.source = 'reflection-worker';
  lessons.episodes_reflected = episodes.length;
  if (episodes.length) {
    const oldest = episodes[episodes.length - 1]?.timestamp || null;
    const newest = episodes[0]?.timestamp || null;
    lessons.date_range = `${oldest || ''} -> ${newest || ''}`;
  }
  saveJson(LESSONS_FILE, lessons);

  appendLog(`[REFLECT-COMPLETE-${nowCnTag()}] Reflection worker completed: DB-first reflection restored under workspace/memory; reflected ${episodes.length} episodes; updated lessons.json and ensured reflection guidance is logged.`);

  const summary = {
    ok: true,
    worker: path.join('memory', 'reflection-worker.js'),
    episodes_reflected: episodes.length,
    recent_task_completions: recentTaskCompletions.length,
    lessons_file: LESSONS_FILE,
    updated_at: lessons.updated_at,
  };
  process.stdout.write(JSON.stringify(summary, null, 2));
}

main();
