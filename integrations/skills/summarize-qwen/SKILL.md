# 网页总结技能（使用 Qwen 3.5 Plus）

## 无需额外 API 密钥

使用 OpenClaw 内置的 `web_fetch` 工具 + 当前 Qwen 模型完成网页总结。

## 使用方法

### 方法 1：直接让我总结

```
庆：总结一下这个网页 https://example.com/article
```

我会自动使用 `web_fetch` 获取内容，然后用 Qwen 3.5 Plus 总结。

### 方法 2：手动获取内容后让我总结

```powershell
# OpenClaw 内置命令
web_fetch "https://example.com" --extractMode markdown
```

然后把内容发给我，我来总结。

## 总结选项

我可以按以下要求总结：
- **长度**: 简短/中等/详细
- **格式**: 要点/段落/表格
- **重点**: 技术细节/商业信息/关键结论

## 示例

```
庆：总结这个文章，要简短的要点
https://example.com/news/ai-trends-2026

青：好的，我来获取并总结...
[使用 web_fetch 获取内容]
[用 Qwen 3.5 Plus 分析并总结]
✅ 完成！文章要点如下：
- ...
```

## 优势

| 方案 | API 密钥 | 速度 | 灵活性 |
|------|----------|------|--------|
| summarize CLI | 需要 | 快 | 固定格式 |
| web_fetch + Qwen | ❌ 不需要 | 快 | ✅ 可定制 |

---

**庆，直接用这个方案就好！要我总结网页时，直接把链接发给我。**
