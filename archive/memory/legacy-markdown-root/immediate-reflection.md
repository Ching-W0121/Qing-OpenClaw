# 实时反思触发脚本

**用途**: 当同一错误发生 3 次时，立即触发反思（不等 6 小时）

---

## 🔧 使用方法

```powershell
# 手动触发
node memory/immediate-reflection.js "错误描述"

# 自动触发（失败计数器达到 3 次时）
node memory/immediate-reflection.js --auto "browser_act"
```

---

## 📋 反思流程

```javascript
// memory/immediate-reflection.js

async function triggerImmediateReflection(errorType) {
    console.log(`🔴 触发即时反思：${errorType}`);
    
    // 1. 读取最近 50 条 episodic 记录
    const episodes = readLastNEpisodes(50);
    
    // 2. 筛选相关错误
    const relatedErrors = episodes.filter(e => 
        e.tools?.includes('browser') || 
        e.outcome === 'failed'
    );
    
    // 3. 调用 LLM 分析
    const analysis = await llm.analyze(relatedErrors, `
        分析这些失败记录，提取：
        1. 根本原因
        2. 解决方案
        3. 预防措施
    `);
    
    // 4. 更新 lessons.json
    updateLessons(analysis);
    
    // 5. 追加 LEARNINGS.md
    appendLearnings(analysis);
    
    // 6. 追加 ERRORS.md
    appendErrors({
        type: errorType,
        timestamp: new Date().toISOString(),
        analysis: analysis
    });
    
    console.log(`✅ 反思完成，已记录到：`);
    console.log(`   - memory/semantic/lessons.json`);
    console.log(`   - .learnings/LEARNINGS.md`);
    console.log(`   - .learnings/ERRORS.md`);
}
```

---

## 📊 触发历史

| 日期 | 错误类型 | 触发原因 | 结果 |
|------|----------|----------|------|
| 2026-03-14 | browser_act | 动态页面元素失效×3 | ✅ 已记录 |
| 2026-03-14 | browser_snapshot | 死循环等待×3 | ✅ 已记录 |

---

## ✅ 输出文件

反思完成后更新：
1. `memory/semantic/lessons.json` - 添加新教训
2. `.learnings/LEARNINGS.md` - 追加学习记录
3. `.learnings/ERRORS.md` - 追加错误记录
4. `memory/failure_tracker.md` - 重置计数器

---

**创建时间**: 2026-03-14 18:10  
**状态**: 待实现（需要编写 JS 脚本）
