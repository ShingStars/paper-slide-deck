# 组件库与组合语法

页框架、布局、组件是三个层级：页框架承载导航目标；布局决定内容关系；组件呈现信息。不要把示例中的搭配理解为固定页模板。

## 页框架与布局

每页是片段根级 `<section class="slide" id="slide-topic" data-title="简短页名">`。ID 唯一；data-title 供导航使用。壳层自动生成序号，无须写死总页数。

```html
<section class="slide" id="slide-intro" data-title="观点与证据">
  <header class="slide-heading">
    <div class="part">/ PART 02</div>
    <h2>标题应表达本页的核心意思</h2>
    <p class="subtitle">可选的上下文，不必每页都有副标题</p>
  </header>
  <div class="slide-body"><!-- 按内容选择组件，也可以直接用短段落和列表 --></div>
  <footer class="slide-footer">可选的来源、限定条件或页脚</footer>
</section>
```

布局类：`.stack` 上下堆叠，`.two-column` 等宽双栏，`.two-column.wide-left` 左宽右窄，`.two-column.wide-right` 左窄右宽，`.grid.cols-2` / `.cols-3` / `.cols-4` 多列，`.center` 居中，`.align-center` 垂直居中。支持在构建时加入少量额外 CSS 定义内容需要的布局。保持每个组件可以混用。

## Hero — 主题、立场、章节开场

适合引入一个主题或一句关键结论，不是每页固定开头。

```html
<div class="hero">
  <div class="part">/ 一份可离线打开的演示文稿</div>
  <h1>从零散文本<br>到清晰的讲述</h1>
  <p class="hero-lead">这一页只需要说明主题、价值和即将展开的问题。</p>
  <div class="tag-row"><span class="badge cyan">主题关键词</span></div>
</div>
```

## Window — 代码、配置、命令、结构化原文

显示真实文本，不运行用户代码。`&`、`<`、`>` 必须 HTML 转义，尤其是 `</script>` 一类字符串。代码正文中的换行就是复制时的换行。

```html
<div class="window-group">
  <div class="file-label">example.json</div>
  <div class="window">
    <div class="window-bar"><span class="traffic" aria-hidden="true"><i></i><i></i><i></i></span><span class="window-title">example.json</span><button class="copy-code" type="button">复制</button></div>
    <div class="window-body" tabindex="0" role="region" aria-label="代码示例"><pre><code>{
  "theme": "paper"
}</code></pre></div>
  </div>
</div>
```

## Table — 逐项对比、映射、参数

列名必须是同一层级的可比维度；内容过多拆页。表格外围包 `.table-wrap`，手机可横向滚动，不把全页撑宽。

```html
<div class="table-wrap" tabindex="0" role="region" aria-label="组件选型表">
  <table><thead><tr><th scope="col">内容特征</th><th scope="col">组件</th><th scope="col">作用</th></tr></thead>
    <tbody><tr><td><span class="mono">代码 / 配置</span></td><td>Window</td><td>保留可复制的原始内容</td></tr></tbody>
  </table>
</div>
```

## Grid — 分类、阶段、平级要点

每张卡有清晰分类和简短说明。用 2/3/4 列适配真实数量，不为凑满格子编造信息。

```html
<div class="grid cols-3">
  <article class="info-card"><span class="badge blue">01 / 分类</span><h3>明确的小标题</h3><p>说明这一类内容的含义与用途。</p></article>
  <article class="info-card"><span class="badge cyan">02 / 分类</span><h3>另一个平级要点</h3><p>文字长度允许自然变化。</p></article>
</div>
```

## TwoColumn — 双方比较、因果、代码解析

它是可嵌套布局，不限制内部组件。可以把 Window 放左、标签解释放右，也可左右各一张信息卡。比较时维度对齐；避免一侧三行、另一侧大段正文造成信息失衡。

```html
<div class="two-column">
  <article class="compare-panel"><span class="badge rose">之前</span><h3>零散信息</h3><ul><li>缺少讲述顺序</li><li>信息层级混杂</li></ul></article>
  <article class="compare-panel"><span class="badge green">之后</span><h3>连续讲述</h3><ul><li>按观点和证据编排</li><li>用组件区分关系</li></ul></article>
</div>
```

## QuoteCard — 结论、引用、提示、警示

普通结论不要伪造成他人的名言。引用只有来源确实提供时才写 `<cite>`。多个短说明可用 `.note`，不需要全都做成大引号。

```html
<blockquote class="quote-card"><p>统一的是视觉语言，自由的是内容组织。</p><cite>仅在有真实来源时填写</cite></blockquote>
<aside class="note"><span class="badge yellow">提示</span><p>用于对主内容作补充或说明适用条件。</p></aside>
```

## Stats — 有依据的数据与规模

每个数字必须来自原文、实际生成结果或可验证计算。没有数字就选择其他组件，不编造增长率、评分、用户规模。单位和口径与数字一起呈现。

```html
<div class="stats">
  <article class="stat"><div class="stat-value">1<span>个文件</span></div><h3>独立交付</h3><p>样式和交互均在 HTML 内。</p></article>
  <article class="stat"><div class="stat-value">8<span>类组件</span></div><h3>自由组合</h3><p>这里的 8 仅指本组件库，其他任务不能直接套用。</p></article>
</div>
```

## SlideNav — 真实分页

由 runtime.js 自动读取 `.slide`，渲染外侧圆点导航和当前页码。不手工复制 `.dot`，不写死 7/9，不添加 B 站的灰色白箭头缩放按钮。

- 桌面：右侧纵向圆点，上一页 / 下一页、页码和全屏按钮。
- 手机：底部紧凑导航，圆点可横向滚动。
- hash 对应实际页 ID，重开带 hash 的文件直接进入该页；无效 hash 回到第一页。
- 只显示当前页；其他页使用 hidden 和 inert，防止键盘进入不可见内容。
- `.copy-code`、表格横向滚动、代码选择等操作不会触发翻页。

## 组合选择示例（非固定模板）

| 内容关系 | 可选组合 |
| --- | --- |
| 主题和一句关键结论 | Hero + QuoteCard |
| 程序及逐段解释 | TwoColumn（Window + `.stack` 下的 `.note`） |
| 可比的方案属性 | 通栏 Table，或 TwoColumn + 简短 Table |
| 无先后关系的几类概念 | Grid + 页脚小结 |
| 原文有明确数据 | Stats + QuoteCard / Table |
| 过程和建议 | 自由安排的 Grid、列表、TwoColumn，不需要凭空加入数字 |

使用必要组件即可。不要每页都采用同样的左代码右解释，也不要把示例 Hero、卡片数量、标题和作者复制到用户成品。
