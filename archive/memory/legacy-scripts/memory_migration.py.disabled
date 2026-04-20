#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆大迁移脚本 (Memory Migration)

功能:
1. 扫描记忆文件夹所有文件
2. 清洗数据（空白符、无意义日志）
3. 语义切片（>500 字按段落切分）
4. 元数据标记（创建时间、项目标签、文件名）
5. 非文本文件处理（图片/PDF 二进制存储+OCR 提取）
6. 自动钩子（任务完成后自动写入数据库）

作者：青 (Qing)
创建日期：2026-03-14
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import base64

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_vault import add_memory, search_memory, init_database, DB_PATH

# ==================== 配置 ====================

MEMORY_DIR = Path(__file__).parent.parent  # workspace 根目录
MEMORY_FILES_PATTERNS = [
    "**/*.md",           # Markdown 文件
    "**/*.txt",          # 文本文件
    "**/*.json",         # JSON 文件
    "**/*.jsonl",        # JSONL 文件
    "**/*.log",          # 日志文件
    "**/*.png",          # 图片
    "**/*.jpg",
    "**/*.jpeg",
    "**/*.pdf",          # PDF
]

# 专门扫描 memory 目录
MEMORY_DIR_EXPLICIT = Path(__file__).parent  # memory 文件夹本身

# 项目标签映射
PROJECT_TAGS = {
    "qing-agent": ["qing-agent", "services", "pipeline", "tests"],
    "memory": ["memory", "memory_vault", "semantic", "episodic"],
    "learnings": [".learnings", "LEARNINGS", "ERRORS"],
    "docs": ["docs", "GPT 咨询", "Gemini 咨询"],
    "config": [".openclaw", "openclaw.json", "HEARTBEAT"],
}

# 无意义日志模式
NOISE_PATTERNS = [
    r"^\[.*\]\s*Exec completed.*",  # 执行完成日志
    r"^\[.*\]\s*System:.*",         # 系统日志
    r"^Command exited with code.*", # 退出码
    r"^\s*Process.*running.*",      # 进程状态
    r"^\s*\(no output.*\)",         # 无输出
    r"^\s*```\s*$",                 # 代码块标记
    r"^\s*---\s*$",                 # 分隔线
]

# ==================== 数据清洗 ====================

def clean_text(text: str) -> str:
    """清洗文本（移除空白符和无意义日志）"""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 移除无意义日志
        is_noise = False
        for pattern in NOISE_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                is_noise = True
                break
        
        if not is_noise:
            # 移除首尾空白符
            cleaned = line.strip()
            if cleaned:  # 保留非空行
                cleaned_lines.append(cleaned)
    
    return '\n'.join(cleaned_lines)

# ==================== 语义切片 ====================

def semantic_slice(text: str, max_length: int = 500) -> List[str]:
    """
    语义切片（按段落切分，确保每条记忆有明确中心思想）
    
    Args:
        text: 原始文本
        max_length: 单条记忆最大长度
    
    Returns:
        切片后的文本列表
    """
    if len(text) <= max_length:
        return [text]
    
    slices = []
    
    # 按段落分割
    paragraphs = re.split(r'\n\s*\n', text)
    
    current_slice = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # 如果当前段落 + 已有内容超过限制
        if len(current_slice) + len(para) > max_length:
            # 保存当前切片
            if current_slice:
                slices.append(current_slice)
            
            # 如果单个段落超长，按句子切分
            if len(para) > max_length:
                sentences = re.split(r'[。！？.!?\n]', para)
                current_slice = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    
                    if len(current_slice) + len(sent) > max_length:
                        slices.append(current_slice)
                        current_slice = sent
                    else:
                        current_slice += " " + sent if current_slice else sent
            else:
                current_slice = para
        else:
            current_slice += "\n\n" + para if current_slice else para
    
    # 保存最后一个切片
    if current_slice:
        slices.append(current_slice)
    
    return slices if slices else [text]

# ==================== 元数据标记 ====================

def extract_metadata(file_path: Path) -> Dict:
    """提取文件元数据"""
    stat = file_path.stat()
    
    # 项目标签
    project_tag = "unknown"
    rel_path = str(file_path.relative_to(MEMORY_DIR))
    for tag, patterns in PROJECT_TAGS.items():
        if any(pattern in rel_path for pattern in patterns):
            project_tag = tag
            break
    
    return {
        "source_file": rel_path,
        "original_filename": file_path.name,
        "file_size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "project_tag": project_tag,
        "file_type": file_path.suffix.lower(),
        "migration_date": datetime.now().isoformat(),
    }

# ==================== 非文本文件处理 ====================

def extract_text_from_image(file_path: Path) -> str:
    """从图片提取文字（简化版：返回文件信息）"""
    # TODO: 集成 OCR（如 pytesseract）
    # 当前返回文件摘要
    stat = file_path.stat()
    return f"[图片文件] {file_path.name} - 大小：{stat.st_size} 字节 - 创建：{datetime.fromtimestamp(stat.st_ctime).date()}"

def extract_text_from_pdf(file_path: Path) -> str:
    """从 PDF 提取文字（简化版：返回文件信息）"""
    # TODO: 集成 PyPDF2 或 pdfplumber
    stat = file_path.stat()
    return f"[PDF 文件] {file_path.name} - 大小：{stat.st_size} 字节 - 创建：{datetime.fromtimestamp(stat.st_ctime).date()}"

def file_to_binary(file_path: Path) -> bytes:
    """读取文件二进制"""
    with open(file_path, 'rb') as f:
        return f.read()

# ==================== 记忆迁移 ====================

def migrate_file(file_path: Path, dry_run: bool = False) -> int:
    """
    迁移单个文件到数据库
    
    Args:
        file_path: 文件路径
        dry_run: 预览模式（不实际写入）
    
    Returns:
        迁移的记忆条数
    """
    print(f"\n📄 处理：{file_path.relative_to(MEMORY_DIR)}")
    
    # 提取元数据
    metadata = extract_metadata(file_path)
    
    # 非文本文件处理
    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        text_content = extract_text_from_image(file_path)
        memory_type = 'media'
        metadata['binary_data'] = "base64:" + base64.b64encode(file_to_binary(file_path)).decode('utf-8')[:100] + "..."  # 只存摘要
    
    elif file_path.suffix.lower() == '.pdf':
        text_content = extract_text_from_pdf(file_path)
        memory_type = 'media'
        metadata['binary_data'] = "base64:" + base64.b64encode(file_to_binary(file_path)).decode('utf-8')[:100] + "..."
    
    else:
        # 文本文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except:
            print(f"  ⚠️  读取失败，跳过")
            return 0
        
        # 清洗数据
        cleaned_text = clean_text(raw_text)
        
        # 确定记忆类型
        if 'ERROR' in file_path.name or 'error' in file_path.name.lower():
            memory_type = 'error'
        elif 'LEARN' in file_path.name or 'learning' in file_path.name.lower():
            memory_type = 'learning'
        elif 'semantic' in str(file_path):
            memory_type = 'semantic'
        elif 'episodic' in str(file_path):
            memory_type = 'episodic'
        else:
            memory_type = 'archived'
        
        text_content = cleaned_text
    
    # 语义切片
    slices = semantic_slice(text_content, max_length=500)
    
    print(f"  📊 切片数：{len(slices)} | 类型：{memory_type}")
    
    # 添加到数据库
    if not dry_run:
        count = 0
        for i, slice_text in enumerate(slices, 1):
            if len(slice_text.strip()) < 20:  # 跳过太短的切片
                continue
            
            # 添加元数据
            slice_metadata = metadata.copy()
            slice_metadata['slice_index'] = i
            slice_metadata['slice_total'] = len(slices)
            
            mem_id = add_memory(
                memory_text=slice_text[:2000],  # 限制长度
                memory_type=memory_type,
                metadata=slice_metadata
            )
            
            if mem_id > 0:
                count += 1
        
        print(f"  ✅ 已迁移 {count} 条记忆")
        return count
    else:
        # 预览模式
        print(f"  👁️  预览：将迁移 {len(slices)} 条记忆")
        for i, slice_text in enumerate(slices[:2], 1):  # 只显示前 2 条
            print(f"\n    [{i}/{len(slices)}]")
            print(f"    {slice_text[:150]}...")
        return len(slices)

def scan_and_migrate(dry_run: bool = False):
    """扫描并迁移所有记忆文件（包括 memory 目录本身）"""
    print("=" * 60)
    print("记忆大迁移 (Memory Migration)")
    print("=" * 60)
    print(f"扫描目录：{MEMORY_DIR}")
    print(f"额外扫描：{MEMORY_DIR_EXPLICIT}")
    print(f"预览模式：{'是' if dry_run else '否'}")
    
    # 初始化数据库
    init_database()
    
    total_migrated = 0
    file_count = 0
    
    # 扫描 workspace 根目录
    for pattern in MEMORY_FILES_PATTERNS:
        files = list(MEMORY_DIR.glob(pattern))
        
        # 排除某些目录
        files = [f for f in files if not any(exclude in str(f) for exclude in [
            'node_modules', '.git', '__pycache__', 'memory_vault.db'
        ])]
        
        for file_path in files:
            if file_path.is_file():
                count = migrate_file(file_path, dry_run)
                total_migrated += count
                file_count += 1
    
    # 额外扫描 memory 目录本身
    print(f"\n🔍 额外扫描 memory 目录：{MEMORY_DIR_EXPLICIT}")
    for pattern in MEMORY_FILES_PATTERNS:
        files = list(MEMORY_DIR_EXPLICIT.glob(pattern))
        
        # 排除数据库文件和脚本本身
        files = [f for f in files if f.name not in ['memory_vault.db', 'memory_migration.py', 'test_memory_vault.py']]
        
        for file_path in files:
            if file_path.is_file():
                count = migrate_file(file_path, dry_run)
                total_migrated += count
                file_count += 1
    
    print("\n" + "=" * 60)
    print(f"迁移完成!")
    print(f"  扫描文件：{file_count} 个")
    print(f"  迁移记忆：{total_migrated} 条")
    print("=" * 60)
    
    return total_migrated

# ==================== 自动钩子 ====================

class MemoryHook:
    """记忆自动钩子 - 任务完成后自动写入数据库"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        init_database(self.db_path)
        print(f"✅ 记忆钩子已激活")
    
    def on_task_complete(self, task_name: str, outcome: str, details: Dict):
        """
        任务完成钩子
        
        Args:
            task_name: 任务名称
            outcome: 结果 (success/failed/partial)
            details: 详细信息
        """
        # 构建记忆文本
        memory_text = f"任务：{task_name} - 结果：{outcome}"
        if details.get('error'):
            memory_text += f" - 错误：{details['error']}"
        if details.get('method'):
            memory_text += f" - 方法：{details['method']}"
        
        # 确定记忆类型
        if outcome == 'failed':
            memory_type = 'error'
        elif outcome == 'success':
            memory_type = 'learning'
        else:
            memory_type = 'episodic'
        
        # 添加到数据库
        mem_id = add_memory(
            memory_text=memory_text,
            memory_type=memory_type,
            metadata={
                'task_name': task_name,
                'outcome': outcome,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'auto_generated': True,
                'hook': 'on_task_complete'
            },
            db_path=self.db_path
        )
        
        if mem_id > 0:
            print(f"📝 记忆已自动记录：{task_name} ({outcome})")
        else:
            print(f"⚠️  记忆已存在：{task_name}")
    
    def on_reflection(self, reflection_data: Dict):
        """
        反思记录钩子
        
        Args:
            reflection_data: 反思数据
        """
        # 提取关键信息
        lessons = reflection_data.get('lessons', [])
        trigger_type = reflection_data.get('trigger_type', 'manual')
        
        # 添加每条教训到数据库
        for lesson in lessons:
            mem_id = add_memory(
                memory_text=lesson,
                memory_type='learning',
                metadata={
                    'trigger_type': trigger_type,
                    'timestamp': datetime.now().isoformat(),
                    'auto_generated': True,
                    'hook': 'on_reflection'
                },
                db_path=self.db_path
            )
            
            if mem_id > 0:
                print(f"📝 反思已记录：{lesson[:50]}...")

# ==================== 命令行工具 ====================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python memory_migration.py migrate     # 执行迁移")
        print("  python memory_migration.py preview     # 预览（不实际写入）")
        print("  python memory_migration.py hook        # 测试钩子")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'migrate':
        scan_and_migrate(dry_run=False)
    
    elif command == 'preview':
        scan_and_migrate(dry_run=True)
    
    elif command == 'hook':
        # 测试钩子
        hook = MemoryHook()
        hook.on_task_complete("browser_act", "success", {"method": "标准流程"})
        hook.on_task_complete("git_push", "failed", {"error": "连接被重置"})
        hook.on_reflection({
            "trigger_type": "error",
            "lessons": ["必须等待 10 秒让 React 完全加载", "操作前必须检索记忆"]
        })
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
