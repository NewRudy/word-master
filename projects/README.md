# projects/

用户项目工作区。每个项目一个目录：`<slug>_<YYYYMMDD>/`，由 `project_manager.py init` 创建。

```
<project>/
├── project.json      # 项目元数据（名称/模板/状态/时间线）
├── sources/          # 原始材料（含 converted/ 文本转换）
├── facts.json        # 事实溯源（word-master.fact-provenance.v1）
├── content.md        # AI 产出的内容中间格式（content-grammar）
└── exports/          # 构建与导出产物（带时间戳，不覆盖）
```
