# Content Grammar (markdown-superset)

The only format the AI authors. One `content.md` per project. The builder parses
it line-based; anything outside this grammar is a builder error — do not improvise.

## Front Matter (optional, first lines)

```
@title: 文档主标题        → Title 样式段落（doc.title）
@template: qiji_heading  → 校验用（须与 project.json 一致）
```

## Headings

```
# 一级标题        → h1（自动编号 1.）
## 二级标题       → h2（1.1.）
### 三级标题      → h3 … ###### → h6，####### → h7（最深）
```

Heading text never contains manual numbers. `########` 及更深 → 语法错误。

## Paragraphs

Plain lines → body style（首行缩进、1.5 倍行距等由模板决定）。
空行分段。行内强调：`**加粗**`、`*斜体*`（映射为 run 级 b/i，其余直接格式禁止）。

## Manual Numbering Zone（7 级标题以下）

直接把序号打进正文文本，模板不自动编号：

```
（1）一级序号正文……
1) 二级序号正文……
① 三级序号正文……
a) 四级序号正文……
```

层级约定：（1）→ 1) → ① → a) → ●（项目符号列表用 `- ` 引出，见下）。

## Lists

```
- 项目符号项      → Normal + 圆点编号（numId=7）
```

有序列表不用语法——按 Manual Numbering Zone 手打。

## Figures

```
:::figure <slug>
<img: D:/path/to/image.png>
:::

:::caption fig <slug> 图题文字（不带"图x.x-x"前缀）
```

- `figure` 块插入嵌入型图片（样式自动居中）；`caption fig` 必须紧跟其后
- 图题编号由模板自动生成；**前缀手打 = blocking**
- 正文交叉引用：`如{{ref:fig:<slug>}}所示` → 渲染为指向"图x.x-x"的域

## Tables

```
:::caption tbl <slug> 表题文字（不带"表x.x-x"前缀）

| 列1 | 列2 | 列3 |
| --- | --- | --- |
| 单元格 | 单元格 | 单元格 |

:::
```

- `caption tbl` 在表**上方**；表体用标准管道表
- 表题编号自动；表样式与单元格样式由模板 contract 决定
- 交叉引用：`见表{{ref:tbl:<slug>}}`

## Fact Citations

```
……结论句。<!-- F001 -->
```

句子（或句组）后紧跟 HTML 注释式 fact 引用；`F0xx` 必须存在于 `facts.json`。
builder 把被引用事实汇总为文尾"来源"附录（Title 样式标题，不占章节号）。

## Escape / Reserved

- 行首 `@`、`:::`、`{{` 为保留前缀，正文不得以它们开头
- 需要原样输出这些字符时，联系人工调整（此为 MVP 已知限制）
