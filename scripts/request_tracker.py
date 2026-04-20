#!/usr/bin/env python3
"""
请求追踪工具 - 记录用户请求和执行结果
升级：除 requests.jsonl 外，强制同步到统一记忆系统（SQLite + FAISS）。
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field

WORKSPACE = os.path.expanduser(r'~\.openclaw\workspace')
MEMORY_DIR_DEFAULT = os.path.join(WORKSPACE, 'memory')
sys.path.insert(0, MEMORY_DIR_DEFAULT)

for _stream_name in ('stdout', 'stderr'):
    _stream = getattr(sys, _stream_name, None)
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8', errors='replace')

from unified_memory import append_episode  # type: ignore


@dataclass
class UserRequest:
    id: str
    timestamp: str
    user_name: str
    request_type: str
    content: str
    context: Dict = field(default_factory=dict)
    priority: str = 'normal'


@dataclass
class Execution:
    request_id: str
    start_time: str
    end_time: str
    actions: List[str]
    results: List[str]
    files_created: List[str]
    files_modified: List[str]
    success: bool
    metrics: Dict = field(default_factory=dict)


@dataclass
class Reflection:
    request_id: str
    timestamp: str
    what_went_well: List[str]
    what_went_wrong: List[str]
    improvements: List[str]
    unnecessary: List[str]
    lessons: List[str]


@dataclass
class RequestRecord:
    request: UserRequest
    execution: Optional[Execution]
    reflection: Optional[Reflection]


class RequestTracker:
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or MEMORY_DIR_DEFAULT
        self.requests_file = os.path.join(self.memory_dir, 'requests.jsonl')
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(self.memory_dir, exist_ok=True)
        if not os.path.exists(self.requests_file):
            with open(self.requests_file, 'w', encoding='utf-8'):
                pass

    def _generate_id(self) -> str:
        now = datetime.now()
        return f"REQ-{now.strftime('%Y%m%d-%H%M%S')}"

    def _write_record(self, record: RequestRecord):
        with open(self.requests_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + '\n')

    def _write_all(self, records: List[RequestRecord]):
        with open(self.requests_file, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(asdict(record), ensure_ascii=False) + '\n')

    def _read_all(self) -> List[RequestRecord]:
        records = []
        with open(self.requests_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    records.append(RequestRecord(
                        request=UserRequest(**data['request']),
                        execution=Execution(**data['execution']) if data.get('execution') else None,
                        reflection=Reflection(**data['reflection']) if data.get('reflection') else None,
                    ))
        return records

    def _sync_to_memory(self, event_type: str, title: str, content: str, metadata: Dict[str, Any]):
        try:
            append_episode(
                content=content,
                timestamp=metadata.get('timestamp') or datetime.now().isoformat(),
                session_id=metadata.get('session_id', 'request-tracker'),
                channel=metadata.get('channel', 'local'),
                event_type=event_type,
                metadata={'title': title, **metadata}
            )
        except Exception:
            pass

    def log_request(self, content: str, request_type: str = 'other', context: Dict = None, priority: str = 'normal') -> str:
        request = UserRequest(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            user_name='庆',
            request_type=request_type,
            content=content,
            context=context or {},
            priority=priority,
        )
        record = RequestRecord(request=request, execution=None, reflection=None)
        self._write_record(record)
        self._sync_to_memory(
            'user_request',
            f'请求追踪: {request_type}',
            f'[request] {request_type}\n\n{content}',
            {
                'request_id': request.id,
                'request_type': request_type,
                'priority': priority,
                'context': context or {},
                'source': 'request_tracker',
                'tags': ['request', request_type],
                'timestamp': request.timestamp,
            }
        )
        print(f"[REQUEST] {request.id}: {content[:50]}...")
        return request.id

    def log_execution(self, request_id: str, actions: List[str], results: List[str], files_created: List[str] = None,
                      files_modified: List[str] = None, metrics: Dict = None, success: bool = True):
        execution = Execution(
            request_id=request_id,
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            actions=actions,
            results=results,
            files_created=files_created or [],
            files_modified=files_modified or [],
            metrics=metrics or {},
            success=success,
        )
        records = self._read_all()
        for record in records:
            if record.request.id == request_id:
                record.execution = execution
                break
        self._write_all(records)
        self._sync_to_memory(
            'execution_record',
            f'执行记录: {request_id}',
            '[execution]\n\n动作：' + '\n- '.join([''] + actions) + '\n\n结果：' + '\n- '.join([''] + results),
            {
                'request_id': request_id,
                'success': success,
                'actions': actions,
                'results': results,
                'files_created': files_created or [],
                'files_modified': files_modified or [],
                'metrics': metrics or {},
                'source': 'request_tracker',
                'tags': ['execution', 'success' if success else 'failed'],
                'timestamp': execution.end_time,
            }
        )
        print(f"[EXECUTION] {request_id}: {len(actions)} actions, success={success}")

    def log_reflection(self, request_id: str, what_went_well: List[str] = None, what_went_wrong: List[str] = None,
                       improvements: List[str] = None, unnecessary: List[str] = None, lessons: List[str] = None):
        reflection = Reflection(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            what_went_well=what_went_well or [],
            what_went_wrong=what_went_wrong or [],
            improvements=improvements or [],
            unnecessary=unnecessary or [],
            lessons=lessons or [],
        )
        records = self._read_all()
        for record in records:
            if record.request.id == request_id:
                record.reflection = reflection
                break
        self._write_all(records)
        content = '[reflection]\n\n做得好：' + '\n- '.join([''] + (what_went_well or []))
        if what_went_wrong:
            content += '\n\n问题：' + '\n- '.join([''] + what_went_wrong)
        if improvements:
            content += '\n\n改进：' + '\n- '.join([''] + improvements)
        if lessons:
            content += '\n\n经验：' + '\n- '.join([''] + lessons)
        self._sync_to_memory(
            'reflection_record',
            f'反思记录: {request_id}',
            content,
            {
                'request_id': request_id,
                'what_went_well': what_went_well or [],
                'what_went_wrong': what_went_wrong or [],
                'improvements': improvements or [],
                'unnecessary': unnecessary or [],
                'lessons': lessons or [],
                'source': 'request_tracker',
                'tags': ['reflection'],
                'timestamp': reflection.timestamp,
            }
        )
        print(f"[REFLECTION] {request_id}: {len(lessons or [])} lessons learned")

    def search(self, query: str) -> List[RequestRecord]:
        records = self._read_all()
        results = []
        query_lower = query.lower()
        for record in records:
            searchable = f"{record.request.content} {' '.join(record.execution.results if record.execution else [])}".lower()
            if query_lower in searchable:
                results.append(record)
        return results

    def get_by_date(self, date: str) -> List[RequestRecord]:
        return [r for r in self._read_all() if r.request.timestamp.startswith(date)]

    def get_by_type(self, request_type: str) -> List[RequestRecord]:
        return [r for r in self._read_all() if r.request.request_type == request_type]

    def summary(self) -> str:
        records = self._read_all()
        lines = ['[REQUEST TRACKER] Summary', f'   Total requests: {len(records)}', '', 'Recent requests:']
        recent = sorted(records, key=lambda r: r.request.timestamp, reverse=True)[:10]
        for record in recent:
            req = record.request
            status = '[OK]' if record.execution and record.execution.success else '[PENDING]'
            lines.append(f'   {status} [{req.timestamp[:10]}] {req.content[:50]}')
        return '\n'.join(lines)


if __name__ == '__main__':
    tracker = RequestTracker()
    if len(sys.argv) < 2:
        print('Usage: request_tracker.py <command> [args]')
        print('Commands: summary | search <query> | date <YYYY-MM-DD> | type <type>')
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'summary':
        print(tracker.summary())
    elif cmd == 'search':
        query = ' '.join(sys.argv[2:])
        results = tracker.search(query)
        print(f'\n[SEARCH: {query}]')
        print(f'  Found: {len(results)} results')
        for r in results:
            print(f'  [{r.request.timestamp[:10]}] {r.request.content}')
    elif cmd == 'date':
        date = sys.argv[2]
        results = tracker.get_by_date(date)
        print(f'\n[DATE: {date}]')
        print(f'  Found: {len(results)} results')
        for r in results:
            print(f'  [{r.request.timestamp}] {r.request.content}')
    elif cmd == 'type':
        req_type = sys.argv[2]
        results = tracker.get_by_type(req_type)
        print(f'\n[TYPE: {req_type}]')
        print(f'  Found: {len(results)} results')
        for r in results:
            print(f'  [{r.request.timestamp[:10]}] {r.request.content}')
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)
