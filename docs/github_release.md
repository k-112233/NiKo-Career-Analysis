# 提交 GitHub：v1.0.0

建议仓库名：`niko-career-analysis`，可见性：Public。

建议描述：`Source-audited NiKo career analysis with Python, SQLite, reproducible reports and an offline interactive dashboard.`

## 手动上传

1. 解压 `dist/niko-career-analysis-v1.0.0.zip`。上传解压后的项目文件，而不是 ZIP 本身，也不要上传工作目录里的旧工程文件。
2. 在 GitHub 新建空的公开仓库，上传根目录里的 README、代码、data、reports、docs、dashboard、.github 等内容。注意包含 `.github/workflows/ci.yml`。
3. 提交说明可直接使用：`Release v1.0.0: reproducible NiKo career analysis`。
4. 查看 Actions 中的 `Portfolio checks`。本地验证不代表远程 Actions 已经运行；首次上传后检查实际状态。
5. 可新建 GitHub Release，标签 `v1.0.0`，说明使用根目录的 `CHANGELOG.md`。附件可上传 ZIP 及 SHA-256 文件。

## 使用 Git 提交

在解压后的根目录执行，替换 YOUR_ACCOUNT 为你的用户名。仓库名可按实际修改。

```bash
git init -b main
git add .
git commit -m "Release v1.0.0: reproducible NiKo career analysis"
git remote add origin https://github.com/YOUR_ACCOUNT/niko-career-analysis.git
git push -u origin main
```

你需要在本机已有自己的 Git 作者信息及 GitHub 登录方式。项目不携带凭据，也没有替你创建仓库或上传。

## 可选展示与项目介绍

GitHub Pages 可选择从 main 分支根目录发布，根目录 `index.html` 将进入离线看板。此项目没有服务端 API 或额外配置要求。

Topics：`counter-strike`, `data-analysis`, `python`, `pandas`, `sqlite`, `esports`, `data-visualization`。

可用于项目介绍的表述：

> 围绕 NiKo 构建 2,030 条地图观察数据的可复现分析项目，完成多来源身份核验、系列赛/地图粒度区分、冲突隔离和缺失指标处理，并交付统计报告、离线交互看板及自动化检查。

保留“部分覆盖”“观察性分析”的说明，不将其表述为完整生涯数据库或因果预测模型。代码与第三方数据许可分别见 LICENSE 与 DATA_LICENSES.md。原始旧工程及其 Git 历史未被覆盖。
