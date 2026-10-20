# word-master — 模板驱动的 Word 工程文档生产线

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-blue)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](https://www.python.org/downloads/)

[English](./README.md) | 中文

> **可编辑只是及格线，格式不漂移才是硬道理。** word-master 交给你的是一份真正的 Word 文档：样式来自单位模板的样式表、编号来自域、题注图表自动编号——AI 只负责写内容，一个字号都不许它自己定。形态上与 [ppt-master](https://github.com/hugohe3/ppt-master) 同源：一套在有 Agent 能力的 AI 工具里运行的工作流（一个 "skill"），在你本机生成，数据不出本地，不锁定任何平台和模型。

<p align="center">
  <img src="docs/assets/before-after.png" alt="同一份内容，两种产出：通用 AI 直出 vs word-master 契约锁定 + 门禁把关" width="100%">
</p>

<p align="center">
  <a href="#快速开始"><strong>快速开始</strong></a> ·
  <a href="#为什么做它"><strong>为什么做它</strong></a> ·
  <a href="#核心理念"><strong>核心理念</strong></a> ·
  <a href="#文档导航"><strong>文档导航</strong></a> ·
  <a href="#项目状态"><strong>项目状态</strong></a>
</p>

---

## 为什么做它

AI 已经能写正文了。问题出在正文之外：**每次跑出来的文档都不一样。** 标题忽大忽小，编号手打、插一章就全错位，表格样式两章之间不统一，图名跑到图上面，评审一句"格式重排"退回来重做。

市面方案都差最后一块：

| 现有做法 | 差在哪 |
|---|---|
| 通用 "docx skill" 提示词 | 没有样式源，模型每次都靠猜 |
| Jinja2 / docxtpl 邮件合并 | 填空很强，但没有"文档结构"概念——编号、题注、交叉引用全靠手 |
| Markdown → Pandoc → DOCX | 产出一套全新的通用样式表，单位模板被扔掉 |
| "用 Word 样式不就行了" | 理论上对，实际上没人强制，粘一段文字就断链 |

word-master 补的就是这一块：**固定模板 + 样式库 + 生产线 + 质量门禁**，面向工程报告/技术文件场景。

## 核心理念

**内容与样式彻底分离。** AI 产出带语义标记的内容（`#` 标题、`:::figure` 图、`{{ref:fig:x}}` 交叉引用），格式全部由模板契约决定，由确定性脚本注入、由质量门禁把关：

```
主题/材料 ──▶ 事实研究(facts.json 溯源) ──▶ init+导入 ──▶ ⛔确认(模板+大纲)
         ──▶ AI 写 content.md（纯语义，不碰格式）──▶ docx_builder 注入模板
         ──▶ doc_checker 质量门禁(fail-closed) ──▶ 交付（WPS 里 Ctrl+A → F9 刷域）
```

四件事撑起它：

- **模板包可组合、可扩展**：每套模板 = 单位原件字节副本 + 清理壳 + 机器契约 `contract.json` + 人类契约文档 + 解包分析。单位在用模板走 *Create Template* 路线入库
- **门禁 fail-closed**：样式白名单（越权即拦）、标题/题注编号必须是自动编号域、7 级以下序号必须手打（单位约定，跨文档合并不串号）、题注方位固定（图下表上）、字体越权检测——blocking 不清零不能交付
- **事实溯源**：每条关键数据带 `fact_id`，来源优先级 国家政策 ＞ 政府发文 ＞ 法规 ＞ 新闻 ＞ 博客，文尾自动生成来源附录
- **三条路线，一个契约**：生成报告（Generate DOCX）/ 模板入库（Create Template）/ 改已有文档（Edit Native DOCX，未改部分字节保留）

## 快速开始

### 1. 前置条件

**只需要装 [Python](https://www.python.org/downloads/) 3.10+。** 其余依赖一行装齐：

```bash
pip install -r requirements.txt
```

**无需 Microsoft Office**——WPS 即可。目录与交叉引用是域，打开后 `Ctrl+A` → `F9` 刷新。

<details>
<summary><strong>Windows</strong> — 干净环境的三条注意事项</summary>

- 装 Python 时**勾选 "Add python.exe to PATH"**。
- `python` 不在 PATH 时，用完整路径也能跑：
  `"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -X utf8 ...`
- 中文 Windows 上跑脚本务必带 `-X utf8`，否则控制台输出可能抛 `UnicodeEncodeError`。
</details>

### 2. 选一个 Agent

word-master 跑在**任何具备 agent 能力的工具**里——能读写文件、执行命令、多轮对话即可。

| 类型 | 例子 |
|---|---|
| **IDE 内置 agent** | [Cursor](https://cursor.sh/)、[Windsurf](https://codeium.com/windsurf)、带 agent 的 VS Code、[Zed](https://zed.dev/) |
| **IDE 插件** | [Claude Code](https://claude.ai/code)（VS Code / JetBrains）、[GitHub Copilot](https://github.com/features/copilot)、[Cline](https://cline.bot/) |
| **CLI agent** | [Claude Code](https://claude.ai/code) CLI、[Codex CLI](https://github.com/openai/codex)、Gemini CLI、[pi](https://github.com/earendil-works/pi-mono) |

没用过也没关系——它在这个项目里只扮演一个角色：一个能读写文件的 AI 聊天窗口，不需要你写代码。

### 3. 安装

```bash
git clone https://github.com/NewRudy/word-master.git
cd word-master
pip install -r requirements.txt
```


#### 国内镜像

同步镜像到 [Gitee](https://gitee.com/hhhsbgitee/word-master) 和
[AtomGit](https://atomgit.com/RudyYa/word-master)，国内访问通常比 GitHub 快。
镜像是单向推送的，可能滞后几分钟；Issue 和 PR 请提到 GitHub。

#### 以后更新#### 以后更新

```bash
git pull
pip install -r requirements.txt   # 仅当 requirements.txt 有变化
```

### 4. 生成

**先用 Agent 打开项目目录**（IDE：文件 → 打开文件夹；CLI：`cd word-master` 再启动 agent）。之后全在聊天里进行。

**方式 A —— 手里有材料。** 把 DOCX / PDF / 文本放进 `projects/<项目>/sources/`（也可以让 agent 帮你跑 `project_manager.py init` 建目录），然后说：

```
你：用 projects/xxx/sources/材料.docx 写一份可行性研究报告
```

**方式 B —— 只有一个主题。** 直接说主题即可；agent 会先做事实研究、把来源记进 `facts.json`，再拿大纲跟你确认。

默认情况下，agent 会先跟你确认规格（这是 `⛔ BLOCKING` 门禁，它不会自作主张往下走）：

```
AI：  开始前先确认：
     [模板]   qiji_heading（七级标题工程报告）
     [大纲]   1 概述 / 2 建设必要性 / 3 建设内容 / 4 结论与建议
     [篇幅]   约 6000 字，3 图 2 表
     [事实]   需研究（国家政策优先）
```

**快速生成（跳过确认回合）**——明确说出来即可：

```
你：快速生成，不用跟我确认
```

你明确说的会被照做；你没说的由 agent 自行决定。它仍然做研究、套契约、跑门禁——省掉的是交互，不是质量关。

> **产物**：文档落在 `projects/<项目>/exports/<名称>_<时间戳>.docx`，原生可编辑 DOCX；每次构建新时间戳，旧版本保留。
>
> **出问题了？** 让 agent 读 `skills/word-master/SKILL.md`；其余情况见 **[FAQ](./docs/faq.md)**。

### 5. 命令速览（了解原理用）

```bash
PY="python"   # Windows: "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -X utf8

"$PY" skills/word-master/scripts/template_manager.py list                    # 看模板库
"$PY" skills/word-master/scripts/project_manager.py init <项目名>             # 建项目
"$PY" skills/word-master/scripts/project_manager.py import-sources <项目> <材料...>
"$PY" skills/word-master/scripts/project_manager.py validate <项目>           # 校验项目完整性
"$PY" skills/word-master/scripts/docx_builder.py build <项目>                 # 构建
"$PY" skills/word-master/scripts/doc_checker.py check <项目> --json           # 门禁
```

日常使用不需要手敲这些命令——agent 会跑。

### 6. 选模板（或者带自己的）

仓库自带四个模板包——一份参考实现，三个派生变体：

| 包名 | 适用场景 | 正文字体 | 最深标题 |
|---|---|---|---|
| `qiji_heading` | 工程技术报告（参考实现，单位真实模板） | 宋体 小四 | 7 级 |
| `gov_report` | 政府机关公文 / 技术报告 | 仿宋 小四 | 5 级 |
| `acceptance_report` | 验收 / 评审报告 | 宋体 小四 | 5 级 |
| `meeting_minutes` | 会议纪要 / 工作简报 | 宋体 小四 | 3 级 |

```bash
"$PY" skills/word-master/scripts/project_manager.py init 我的报告 --template gov_report
```

只差角色样式或标题深度？几秒钟派生一个新包：

```bash
"$PY" skills/word-master/scripts/template_derive.py qiji_heading my_template     --desc "我的单位报告模板：四级标题、楷体正文"     --max-heading-level 4     --set-role "body:font=楷体,Times New Roman;size=14"
```

派生工具会校验产出的 OOXML（每个 part 可解析、`python-docx` 能打开、每个契约角色指向真实样式），校验不过就报错，绝不写一个坏包。完整说明见 [`templates/README.md`](skills/word-master/templates/README.md)。

### 7. 导入单位自己的模板（可选，但这才是重点）

如果单位有强制模板，一次性入库：

```bash
"$PY" skills/word-master/scripts/template_manager.py analyze 你的模板.docx --out /tmp/tpl
"$PY" skills/word-master/scripts/template_manager.py install 你的模板.docx my_unit_template
```

然后让 agent 走完 *Create Template* 路线：跟你评审推导出的契约（`⛔ BLOCKING`）、生成清理壳、写 `template_contract.md`。之后每份报告都用单位的样式表。

---

## 文档导航

| | 文档 | 说明 |
|---|---|---|
| 📘 | [SKILL.md](./skills/word-master/SKILL.md) | 全局纪律、硬规则与路由入口 |
| 🧭 | [路由](./skills/word-master/workflows/routing.md) | 三条路线怎么选 |
| 🛠️ | [生成报告](./skills/word-master/workflows/generate-docx.md) | Step 1–7 主流程 |
| 📦 | [模板入库](./skills/word-master/workflows/create-template.md) | 单位 `.docx` → 模板包 |
| ✏️ | [改已有文档](./skills/word-master/workflows/edit-native-docx.md) | 定点修改，其余字节保留 |
| 📐 | [内容语法](./skills/word-master/references/content-grammar.md) | `content.md` 的全部语法 |
| 📚 | [模板库](./skills/word-master/templates/README.md) | 现有模板包、派生方法、如何新增 |
| 🏗️ | [脚本工具链](./skills/word-master/scripts/) | project / template / builder / checker / derive |
| 💼 | [演示项目](./projects/_demo/) | 端到端示例，门禁通过 |
| ❓ | [FAQ](./docs/faq.md) | 模型选择、成本、排错 |
| 🆚 | [为什么选它](./docs/why-word-master.md) | 适用边界，什么时候不该用 |

---

## 项目状态

**v0.2.0**：三路线骨架 + 四个模板包（一份参考实现 + 三个派生变体）+ 构建器 + fail-closed 门禁，端到端演示已通过。

路线图：确认页 UI（阶段式交互）→ PDF 来源转文本 → WPS COM 自动刷新域 → 模板库扩充（标书、年报、测试报告）→ 图表数据驱动。

## 贡献

欢迎提 Issue 与 PR。新增模板包请走 *Create Template* 流程：`template_src.docx` 字节完整、契约双文件（`contract.json` + `template_contract.md`）同步。详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 开源协议

[MIT](./LICENSE)

## 致谢

- [ppt-master](https://github.com/hugohe3/ppt-master) —— 本项目的架构蓝本与灵感来源（路由式 skill 包、门禁纪律、工程化管理均参照其设计）
- [python-docx](https://github.com/python-openxml/python-docx)

## 赞助与支持

word-master 免费开源，始终保持 Provider 中立。如果它替你省下了一次重排，欢迎支持项目维护——见 [SPONSORING.md](./SPONSORING.md)。
