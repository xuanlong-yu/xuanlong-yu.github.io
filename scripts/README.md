# 脚本说明

## scholar_to_publications.py

从 [Google Scholar](https://scholar.google.com/citations?user=o3Q56qsAAAAJ) 抓取出版物列表，生成 `_includes/generated_publications.html`，供 Publications 页面使用。

### 安装依赖

```bash
pip install scholarly
```

### 运行

在**项目根目录**下执行：

```bash
python scripts/scholar_to_publications.py
```

或指定其他 Scholar 用户 ID：

```bash
python scripts/scholar_to_publications.py --user YOUR_SCHOLAR_ID
```

### 说明

- **成功时**：会覆盖 `_includes/generated_publications.html`，Publications 页面将展示 Scholar 上的列表（按年倒序）。Scholar 提供的数据可能缺少 PDF/github 等链接，可在生成后手动编辑该文件补全。
- **失败时**：不会修改原有 `generated_publications.html`，可继续使用当前内容。
- **限流**：若被 Google 限流，可参考 [scholarly 文档](https://scholarly.readthedocs.io/) 配置代理（如 ScraperAPI、FreeProxies 等）。
