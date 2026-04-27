# GitHub Upload Checklist

检查日期：2026-04-27

## 已完成检查

- [x] Git 仓库存在，当前分支为 `main`。
- [x] 工作区上传前已检查，原始 CSV、`.claude/`、日志和续跑状态文件处于 ignored 状态。
- [x] 大文件检查：本地最大文件是 `data/raw/bulk/*.csv`，已被忽略；已跟踪文件中最大的是构建 HTML 和 processed JSON，仓库体积可控。
- [x] 敏感信息扫描：未发现真实 API key；`POLYGON_API_KEY` 只作为环境变量名出现在文档和脚本中。
- [x] 本机绝对路径清理：历史 handoff 文档中的 `C:/Users/LENOVO/...` 链接已改为仓库相对链接。
- [x] `.gitignore` 已补充 `.env`、密钥文件和 Python 缓存目录。
- [x] 已添加 GitHub Actions CI：校验核心 JSON，执行 `python scripts/build_standalone.py`，并确认 standalone 构建产物已提交。
- [x] 已补充双许可证：代码 MIT，文档、教学材料、策略笔记和 `reference/` 资料 CC BY-NC 4.0。

## 上传前人工确认

- [x] 仓库是否公开：`reference/` 与教学内容包含策略资料，已确认可以公开。
- [x] License：已补充 `LICENSE`，代码 MIT，内容资料 CC BY-NC 4.0。
- [ ] GitHub Pages：如果希望直接在线访问，需要在 GitHub 仓库 Settings 中启用 Pages，并选择合适的发布路径。
- [ ] Remote：当前本地仓库还没有配置 GitHub remote，创建远端仓库后再执行 `git remote add origin <url>`。

## 推荐上传命令

```bash
git status
git add .
git commit -m "chore: prepare repository for GitHub upload"
git remote add origin <your-github-repo-url>
git push -u origin main
```
