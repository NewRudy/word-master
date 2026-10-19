# word-master — 模板驱动的 Word 工程文档生产线

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](#项目状态)

> 可编辑只是及格线，**格式不漂移才是硬道理。** word-master 交给你的是一份真正的 Word 文档：样式来自单位模板的样式表、编号来自域、题注图表自动编号——AI 只负责写内容，一个字号都不许它自己定。形态上与 [ppt-master](https://github.com/hugohe3/ppt-master) 同源：一套在有 Agent 能力的 AI 工具里运行的工作流（一个 "skill"），在你本机生成，数据不出本地，不锁定任何平台和模型。

<p align="center">
  <a href="#快速开始"><strong>快速开始</strong></a> ·
  <a href="#核心理念"><strong>核心理念</strong></a> ·
  <a href="#文档导航"><strong>文档导航</strong></a> ·
  <a href="#项目状态"><strong>项目状态</strong></a>
</p>

---

## 为什么做它

AI 生成 Word 最大的问题不是写不出来，而是**每次格式都不一样**：标题忽大忽小、编号手打错位、表格样式随机。市面方案（通用 docx skill、Jinja2 填空模板）都没有"固定模板 + 样式库 + 生产线 + 质量门禁"的完整组合——word-master 补的就是这一块，面向**工程报告/技术文件**场景。

## 核心理念

**内容与样式彻底分离。** AI 产出带语义标记的内容（`#` 标题、`:::figure` 图、`{{ref:fig:x}}` 交叉引用），格式全部由模板契约（`contract.json`）决定，由确定性脚本注入、由质量门禁把关：

```
主题/材料 ──▶ 事实研究(facts.json 溯源) ──▶ init+导入 ──▶ ⛔确认(模板+大纲)
         ──▶ AI 写 content.md（纯语义，不碰格式） ──▶ docx_builder 注入模板
         ──▶ doc_checker 质量门禁(fail-closed) ──▶ 交付（F9 刷目录）
```

- **模板库可组合、可扩展**：每套模板 = 单位原件字节副本 + 清理壳 + 机器契约 + 人类契约文档 + 解包分析。单位在用模板走 Create Template 路线入库
- **门禁 fail-closed**：样式白名单（越权即拦）、标题/题注编号必须是域、7 级以下手打序号（单位约定）、题注方位（图下表上）、字体越权检测——blocking 不清零不能交付
- **事实溯源**：每条关键数据带 `fact_id`，来源优先级 国家政策 ＞ 政府发文 ＞ 法规 ＞ 新闻 ＞ 博客，文尾自动生成来源附录
- **三条路线**：生成报告（Generate DOCX）/ 模板入库（Create Template）/ 改已有文档（Edit Native DOCX，未改部分字节保留）

## 快速开始

### 1. 前置条件

只需 [Python](https://www.python.org/downloads/) 3.10+，依赖一行装齐：

```bash
pip install -r requirements.txt
```

**无需 Microsoft Office**——WPS 即可（目录/交叉引用域打开后 Ctrl+A → F9 刷新）。

### 2. 选择一个 Agent

任何具备 agent 能力（可读写文件、执行命令、多轮对话）的 AI 工具均可驱动：Claude Code、Cursor、Codex CLI 等。打开本项目目录，在聊天里说"用这份材料写一份报告"即可，日常使用不需要手敲命令。

### 3. 命令速览（了解原理用）

```bash
PY="python"   # Windows: "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -X utf8

"$PY" skills/word-master/scripts/template_manager.py list        # 看模板库
"$PY" skills/word-master/scripts/project_manager.py init 项目名    # 建项目
"$PY" skills/word-master/scripts/project_manager.py import-sources projects/xxx 材料.docx
"$PY" skills/word-master/scripts/docx_builder.py build projects/xxx        # 构建
"$PY" skills/word-master/scripts/doc_checker.py check projects/xxx --json  # 门禁
```

> **输出说明**：成品在 `projects/<项目>/exports/<名称>_<时间戳>.docx`，原生可编辑 DOCX；每次构建新时间戳，旧版本保留。

## 文档导航

| | 文档 | 说明 |
|---|---|---|
| 📘 | [SKILL.md](skills/word-master/SKILL.md) | 全局纪律、硬规则与路由入口 |
| 🧭 | [路由](skills/word-master/workflows/routing.md) | 三条路线怎么选 |
| 🛠️ | [生成报告](skills/word-master/workflows/generate-docx.md) | Step 1–7 主流程 |
| 📦 | [模板入库](skills/word-master/workflows/create-template.md) | 单位 .docx → 模板包 |
| ✏️ | [改已有文档](skills/word-master/workflows/edit-native-docx.md) | 定点修改，其余字节保留 |
| 📐 | [内容语法](skills/word-master/references/content-grammar.md) | content.md 的全部语法 |
| 🏗️ | [脚本工具链](skills/word-master/scripts/) | project/template/builder/checker |
| 💼 | [冒烟示例](projects/) | 端到端示例项目 |

## 项目状态

**v0.1.0 MVP**：三路线骨架 + qiji_heading 模板（七级标题工程报告）+ 构建器 + 质量门禁，已通过端到端冒烟测试。

路线图：确认页 UI（阶段式交互）→ PDF 来源转文本 → WPS COM 自动刷新域 → 多模板库扩充 → 图表数据驱动。

## 贡献

欢迎提 Issue 与 PR。新增模板包请走 Create Template 流程，保证 `template_src.docx` 字节完整、契约双文件（JSON+MD）同步。

## 开源协议

[MIT](LICENSE)

## 致谢

- [ppt-master](https://github.com/hugohe3/ppt-master) —— 本项目的架构蓝本与灵感来源（路由式 skill 包、门禁纪律、工程化管理均参照其设计）
- [python-docx](https://github.com/python-openxml/python-docx)
