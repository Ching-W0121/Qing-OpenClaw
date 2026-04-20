# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
import os

desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')

# 查找求职 agent 补充
for f in os.listdir(desktop):
    if f.endswith('.docx') and '补充' in f:
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
        break
