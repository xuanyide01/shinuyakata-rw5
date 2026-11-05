# 死馆 RW5 移植版 —— 标题界面 / UI 设计交接

版本：**0.3.5**（2026-11-04）
目标设备：REDMI Watch 5 / Vela 快应用，画布 **432 × 514**，包名 `com.codex.yakata.rw5`，安装包上限 **25,000,000 B**（当前 14,489,745 B）。

---

## 1. 这一版现在是什么状态

| 项 | 状态 |
| --- | --- |
| 剧情 | 全量：69 个脚本、198 个场景、17,394 条正文（原文照译，未删减） |
| 画面 | 682 张舞台/CG、277 张立绘（按原作 env 快照逐帧判定，CG 帧不叠立绘） |
| 系统 | 30 存档位、自动播放、章节跳转、CG 鉴赏 56 组 / 14 页、阅读设置 |
| 标题 | 5 项：NEW GAME / LOAD GAME / GALLERY / CONFIG / END GAME（原版还有 HOME PAGE，本移植无此功能） |
| 验证 | 12 项 Node 测试通过；包审计通过（911 条目、692 图、字体 0 缺字）；模拟器逐屏截图通过 |

**当前 UI 是"占位级"的**：颜色、底板、按钮都是脚本生成的纯色渐变 PNG，不是原作美术。这一轮请 Codex 重做标题与全局 UI 的视觉设计。

---

## 2. 目录结构与你要动的文件

工程根：`D:\codex\移植项目\shinuyakata-rw5\源码`

```
src/
  pages/index/index.ux        ← 唯一页面：模板 + 全部脚本 + 全部 CSS（108 行，CSS 在 101 行之后，压缩成单行）
  common/
    ui2/*.png                 ← 本移植自制的 UI 贴图（可整包替换）
    watch.otf                 ← 正文字体（YakataWatchText 子集，496 KB）
    title-font.ttf            ← 标题字体（原作 MTLc3m 子集，8 KB）
    ui/title.jpg              ← 标题背景（原作 title_bg）
    ui/logo.png               ← 标题 LOGO（原作 title@logo%layer）
    ui/transparent.png
    catalog.js engine.js      ← 数据/引擎，**不要改**
    story/*.txt portraits/*.png images/*.jpg  ← 资源，**不要改**
converted/                    ← 构建中间产物，**不要手改**
tools/                        ← 构建工具（见第 4 节）
dist/                         ← 构建输出 .rpk
```

### 2.1 UI 相关入口（全部在 `index.ux`）

| 区域 | 选择器 | 说明 |
| --- | --- | --- |
| 标题容器 | `.title` `.title-art` `.title-logo` `.title-list` `.title-row` `.title-action` | 5 个入口是**图片字标**，不是文字 |
| 对话区 | `.scene` `.art` `.background` `.portrait` | 舞台 432×286，立绘按 op 的 pw/ph/left/top 定位 |
| 对话框 | `.dialogue-panel` `.name-row` `.speaker` `.chapter-name` `.reading` `.prose` `.toolbar` `.tool` | 对话板 432×228，贴在 y=286 |
| 菜单 | `.panel` `.heading` `.subheading` `.menu-grid` `.menu-cell` `.button` `.primary` `.muted` | 全屏 432×514 底板 |
| 章节 | `.chapter-list` `.chapter-card` `.card-name` `.pager` `.pager-item` | 每页 3 条 |
| 存档 | `.slots` `.slot` `.slot-name` `.slot-meta` `.slot-preview` | 30 位 / 每页 4 条 |
| 鉴赏 | `.gallery-list` `.gallery-card` `.gallery-thumb` `.card-name` `.card-meta` | 2×2 网格、每页 4 组 |
| CG 查看 | `.cg-panel` `.cg-image` `.cg-label` `.cg-back` | 图 432×243 在 y=92 |
| 确认/结局/关于 | `.information` `.compact` `.loading` `.scene-hint` | |

模板与脚本是同一文件：`<template>`（1–38 行）、`<script>`（40–100 行）、`<style>`（101–108 行，规则压成单行，用 `}` 分隔）。

### 2.2 现有 ui2 贴图（可整体替换，文件名保持）

| 文件 | 尺寸 | 用途 |
| --- | --- | --- |
| `box.png` | 432×228 | 对话框底板 |
| `namebar.png` | 432×42 | 说话人名条下划线 |
| `panel.png` | 396×470 | 弹出面板（当前仅保留备用） |
| `panel_full.png` | 432×514 | **全屏菜单底板** |
| `btn.png` / `btn_press.png` | 380×52 | 主按钮常态/按下（按 340×52 拉伸） |
| `btn_small.png` / `btn_small_press.png` | 118×46 | 底栏「上一句/菜单/下一句」、翻页 |
| `card_plate.png` | 176×150 | 鉴赏卡片底板 |
| `chapter_plate.png` | 400×64 | 章节卡片底板（按 368×92 拉伸） |
| `slot_plate.png` | 400×64 | 存档栏位底板（按 372×79 拉伸） |
| `divider.png` / `cursor.png` | 260×16 / 14×14 | 分隔线、指示菱形 |
| `title-start/load/gallery/settings/end.png` | 260×52 | 标题 5 个入口字标 |

标题背景与 LOGO 用的是原作素材：`src/common/ui/title.jpg`（432×243）与 `src/common/ui/logo.png`（228×159 显示）。

---

## 3. 原作素材情况（重要）

原作标题按钮在原包里是**逐张图片**：`uipsd/title@new%button;nosave`、`title@load%button`、`title@gallery%button`、`title@config%button`、`title@end%button`、`title@hp%button`，均 222×46，坐标见 `可调用资源/text/patch/title.csv`：

```
type,new,button,80,379,222,46
type,load,button,80,429,222,46
type,gallery,button,80,479,222,46
type,config,button,80,529,222,46
type,end,button,80,579,222,46
type,hp,button,80,628,222,46
type,logo,layer,6,23,455,317
file,allbtns,title@allbtns%cref;over,0,0,217,293,over
```

**但本作发行版并没有这些按钮贴图**。整包索引（`reports/xp3/data.xp3.index.json`、`patch.xp3.index.json`）里 `title@` 只有 3 个文件：

```
uipsd/title@allbtns%cref;off.png   217×293
uipsd/title@allbtns%cref;over.png  217×293
uipsd/title@logo%layer.png         455×317
```

原作内嵌字体在 `可调用资源/files/data/sysscn/`：

```
MTLc3m.ttf  モトヤLシーダ3        （标题字标当前用这款）
MTLmr3m.ttf モトヤLマルベリ3等幅
SourceHanSansJP-{Light,Normal,Medium,Bold,Heavy}.otf
```

所以标题只能在「原作字体栅格化」与「重新设计贴图」之间二选一。**如果 Codex 有别的渠道拿到 `title@new%button` 等原图，直接替换 `title-start.png` 等 5 张即可，尺寸 260×52（或 222×46，改 CSS 宽度）。**

---

## 4. 构建 / 验证命令

```powershell
cd D:\codex\移植项目\shinuyakata-rw5\源码
$env:PYTHONIOENCODING='utf-8'

# 只改 UI（index.ux 或 src/common/ui2/*）时：一条命令重建 + 审计
D:\Anaconda\python.exe -X utf8 tools\update.py --version 0.3.6

# 单独重生成 UI 贴图（脚本化设计，可重复执行）
D:\Anaconda\python.exe -X utf8 tools\build-ui-skin.py
D:\Anaconda\python.exe -X utf8 tools\build-title-art.py

# 审计（update.py 内部已调用；失败会打印断言内容）
D:\Anaconda\python.exe -X utf8 tools\audit-delivery.py

# 单测
node --test tests\*.test.cjs
```

产物：`dist\com.codex.yakata.rw5.debug.<版本>.rpk`（必须 < 25,000,000 B；签名由 `tools\repack-rpk.cjs` 完成，不要手改 dist 内的 zip）。

### 模拟器

```powershell
$env:NODE_PATH='D:\codex\2026-11-02\native-toolkit\node_modules'
$env:WATCH_SDK_HOME='D:\codex\2026-11-02\vela-sdk'
$env:STARRY_EMULATOR_HOME='D:\codex\移植项目\shinuyakata-rw5\研究\vela-environment'
$env:WATCH_VVD_NAME='YakataRW5-432x514'
node tools\emulator-server.cjs            # 后台常驻，控制口 127.0.0.1:43142
```

控制口：`/screen`（截图 PNG）、`/click?x=&y=`、`/install?rpk=<绝对路径,URL 编码>`、`/start`、`/shutdown`。

**换包必须冷启动**：`/shutdown` → 结束 `emulator`/`qemu-system-armel-headless` 进程 → 重开 server → `/install` → `/start`。热装会卡住显示。

---

## 5. 硬性约束

1. **画布固定 432×514**，不要出现横向滚动；右侧/底部留 8px 安全边（实机 R 角会裁）。
2. **包体 < 25 MB**。当前 14.49 MB，美术预算约 **+8 MB**；一张全屏 432×514 PNG 建议 ≤ 250 KB（用 PNG-8 / 调色板量化）。
3. **正文文字必须仍用 `font-family:yakata`**（`/common/watch.otf`），它覆盖全部 17,394 条正文的汉字；不要替换正文字体，否则会缺字。
4. **不要修改** `src/common/story/`、`portraits/`、`images/`、`catalog.js`、`engine.js`、`converted/`、`tests/`。
5. **本交接只涉及 UI 贴图**：不要读取 `可调用资源/images/` 下的 CG 图，也不要把原作画面贴图放进包内新增文件。
6. 颜色/字体可以自由设计，但**入口数量与 id 不能变**：`start / load / gallery / settings / end`（`titleRows` 里的 id 是点击分发依据）。
7. 所有新增图片放 `src/common/ui2/`，在 CSS 里用 `url('/common/ui2/xxx.png')` 引用；打包白名单会自动包含该目录（`tools/audit-delivery.py` 已放宽到该目录下所有 png/jpg）。

---

## 6. 建议的改法（设计方向）

1. **标题**：以原作《死に逝く君、館に芽吹く憎悪》的冷色调 + 黑色蕾丝/烛台意象为骨架。可只保留 `title.jpg` 背景 + `logo.png`，入口做成：
   - 方案 A（贴近原作）：文字条目 + 命中时 `title@allbtns%cref;over.png` 作为光标框，位置按 `title.csv` 的比例缩放到 432 宽；
   - 方案 B（贴图化）：自己画 5 张 222×46 风格按钮（暗紫玻璃 + 细白描边 + 血渍噪点），替换 `title-*.png`。
2. **对话框**：原作是半透明暗紫黑 + 上沿细亮线 + 底部彩色光泽，目前 `box.png` 太素，可重做（保持 432×228）。
3. **菜单**：`panel_full.png` 可加暗角、噪点、边缘装饰（保持 432×514 不透明）。
4. **按钮**：`btn/btn_small` 走"暗紫玻璃 + 1px 提亮 + 按下内凹"，按下态比常态暗 15%。
5. **鉴赏格**：`card_plate.png` 可加内阴影与选中态；如需第二态，新增 `card_plate_press.png` 并在 `.gallery-card` 上用 `:active`（Vela 支持 `:active` 有限，稳妥做法是新增点击态类）。

---

## 7. 验收

- `tools\update.py --version <新版本>` 全流程通过（含 12 项测试 + 审计）。
- 模拟器冷启动后逐屏截图：标题 / 阅读 / 菜单 / 章节 / 存档 / 鉴赏 / CG 查看 / 设置 / 结局 —— 无溢出、无遮挡、无 R 角裁切。
- 正文在任何界面都不缺字（审计里 `completeFontCoverage: true`）。
- 包体 < 25 MB。
