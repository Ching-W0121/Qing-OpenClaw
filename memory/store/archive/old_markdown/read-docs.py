# -*- coding: utf-8 -*-
from docx import Document
import os

# 获取桌面路径
desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')

# 查找包含"产品"和"agent"的 docx 文件
for f in os.listdir(desktop):
    if f.endswith('.docx') and 'agent' in f.lower():
        full_path = os.path.join(desktop, f)
        print(f"\n{'='*60}")
        print(f"文件：{f}")
        print(f"路径：{full_path}")
        print('='*60)
        try:
            doc = Document(full_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    print(para.text)
        except Exception as e:
            print(f"读取失败：{e}")
