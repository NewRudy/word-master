# 模板库

`skills/word-master/templates/docs/` 下的每个目录是一个**模板包**。它是 word-master 的核心资产：格式保证来自这里，而不是来自提示词。

## 当前模板包

| 包名 | 适用场景 | 正文 | 最深标题 | 目录深度 |
|---|---|---|---|---|
| `qiji_heading` | 工程技术报告（参考实现，单位原件） | 宋体 小四 | 7 级 | 3 级 |
| `gov_report` | 政府机关公文 / 技术报告 | 仿宋 小四 | 5 级 | 3 级 |
| `acceptance_report` | 验收 / 评审报告 | 宋体 小四 | 5 级 | 3 级 |
| `meeting_minutes` | 会议纪要 / 工作简报 | 宋体 小四 | 3 级 | 2 级 |

后三个都是**派生包**：它们与 `qiji_heading` 共用同一份单位原件（`template_src.docx` 字节副本）、同一套样式表和编号体系，只在契约层面覆盖了正文字体/字号和标题深度限制。

> 为什么派生而不是各写一份：手写的 `styles.xml` 几乎总是有微妙错误，而 Word 打不开的模板比没有模板更糟。派生保证 OOXML 合法。

## 模板包结构

```
templates/docs/<name>/
├── template_src.docx      # 单位原件字节副本，永不修改（审计线索）
├── template.docx          # 清理后的构建壳（builder 注入的目标）
├── contract.json          # 机器真相：角色→styleId、白名单、编号、门禁规则
├── template_contract.md   # contract.json 的人类可读孪生
└── analysis.md            # 入库分析：样式清单、瑕疵登记、缺口清单
```

五个文件缺一不可，`tests/test_template_derive.py` 会检查。

## 三种获取模板包的方式

### 1. 用现成的

```bash
python skills/word-master/scripts/project_manager.py init 我的报告 --template gov_report
```

### 2. 派生一个新变体（推荐，几分钟）

只改角色样式或标题深度时用这个：

```bash
python skills/word-master/scripts/template_derive.py qiji_heading my_template \
    --desc "我的单位报告模板：四级标题、楷体正文" \
    --max-heading-level 4 \
    --set-role "body:font=楷体,Times New Roman;size=14"
```

参数：

| 参数 | 说明 |
|---|---|
| `--desc` | 写进 `templates_index.json` 和契约的描述 |
| `--title` | 壳里"目 录"那行文字 |
| `--set-role ROLE:...` | 覆盖角色样式，可重复。支持 `font=中文,西文`、`size=磅`、`bold=true/false`、`align=center/left/right/both` |
| `--toc-depth N` | 目录深度 |
| `--max-heading-level N` | 允许的最深标题级别（1–7），更深的标题会被 builder 拒绝 |

可用的角色名见任一 `contract.json` 的 `styles` 键：`doc_title`、`h1`–`h7`、`body`、`bullet`、`figure`、`fig_caption`、`table_caption`、`table_cell`、`table`、`toc_heading` 等。

派生工具会做四件事，任一失败就报错而不是产出一个坏包：

1. 每个 XML part 必须仍是合法 XML
2. `python-docx` 必须能打开 `template.docx`
3. 契约里每个角色必须指向真实存在的样式
4. 角色样式必须在白名单内；覆盖过的字体必须同步进 `fonts.cjk_allowed` / `latin_allowed`

### 3. 入库单位自己的模板（完整能力）

单位的模板是强制的那一份时，必须走这条：

```bash
python skills/word-master/scripts/template_manager.py analyze 单位模板.docx --out /tmp/tpl
python skills/word-master/scripts/template_manager.py install 单位模板.docx my_unit
```

然后按 [`workflows/create-template.md`](../workflows/create-template.md) 完成：审阅推导出的契约（`⛔ BLOCKING`）、手工补 `analysis.md` 的瑕疵登记与缺口清单、生成清理壳、写 `template_contract.md`、注册。

验收清单见 [`CONTRIBUTING_CN.md`](../../../CONTRIBUTING_CN.md#新增模板包)。

## 模板包之间不能混用

一份 `content.md` 绑定一个模板。切换模板需要重新构建，且**可能要改内容**：

- 目标模板的标题深度更浅 → 删掉超深的章节层级
- 目标模板的 `max_heading_level` 更低 → builder 会直接报错，不会静默降级

这是有意的：静默降级会让章节编号错位，而错位正是这个项目要消灭的问题。

## 贡献模板包

高价值贡献。但注意授权：单位内部模板往往不能公开。这种情况请用一份合成的替代文档贡献**契约结构**，并在 `analysis.md` 里说明。

模板包的验收标准在 [`CONTRIBUTING_CN.md`](../../../CONTRIBUTING_CN.md#新增模板包)，简版：

1. `template_src.docx` 字节完整、永不修改
2. `contract.json` 与 `template_contract.md` 同步（先改 JSON）
3. 每个角色映射到模板里真实存在的 `styleId`
4. `analysis.md` 的瑕疵登记和缺口清单是人工填的，不是机器草稿
5. 建一个项目跑通 `build` + `check`，`blocking = 0`
