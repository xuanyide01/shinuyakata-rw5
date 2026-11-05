# UI 皮肤说明（0.2.6）

按 PC 原版的冷色调重做手表 UI：深蓝黑底 + 钢青描边 + 银白文字，按钮沿用原版选项条（`select_normal.png` / `select_over.png`，505×62 紫灰渐变 + 浅色描边 + 4px 圆角）的观感。

## 素材清单（`src/common/ui2/`，全部 RGBA PNG）

| 文件 | 尺寸 | 用途 |
| --- | --- | --- |
| box.png | 432×228 | 对话框底板：A→B 竖向渐变、顶部 2px #779bbc、内 1px #2c4257 |
| namebar.png | 432×42 | 说话人名条下划线（22px 起 120×2） |
| panel.png | 396×470 | 菜单面板：1px 描边 + 内描边 + 四角 12px 直角括号 |
| btn.png / btn_press.png | 380×52 | 主按钮常态 / 按下（紫灰渐变、2px #e8e6f0 描边、顶部高光） |
| btn_small.png / btn_small_press.png | 118×46 | 底栏与翻页小按钮 |
| divider.png | 260×16 | 分隔线（金色菱形） |
| cursor.png | 14×14 | 选项指示菱形 |
| slot_plate.png | 400×64 | 存档栏位底板（左 3px 钢青竖条） |
| chapter_plate.png | 400×64 | 章节卡片底板（左 3px 金色竖条 + 右上 L 角） |

## 生成方式

`tools/build-ui-skin.py`：纯 Pillow 绘制，4 倍超采样后 LANCZOS 缩回，保证边缘抗锯齿；所有半透明元素保留 alpha。可重复执行，输出稳定。

> 说明：本轮原本计划由本机 Codex 生成素材，但 Codex 子任务在启动阶段即失败（product-error，未产生任何输出）。为保证交付，改用上述脚本生成同一套规格的素材；脚本已入库，后续可随时替换为 Codex 产出的同尺寸文件。

## 套用位置（`src/pages/index/index.ux`）

- `.dialogue-panel` → `box.png` 背景（432×228，与对话区完全重合）
- `.panel` → `panel.png`（396×470，居中 18×22 起）
- `.button` / `.primary` / `.muted` → `btn.png` / `btn_press.png`（352×52）
- `.tool` → `btn_small.png`（118×46，底栏"上一句/菜单/下一句"）
- `.menu-cell` → `btn_small.png` 拉伸至 180×66（阅读菜单六宫格）
- `.slot` → `slot_plate.png`；`.chapter-card` → `chapter_plate.png`
- 标题页：删除「普通剧情调试版 · 版本号」文字与 `.edition` 样式，其余保持原样

## 已知取舍

- Vela 的 `text` 无禁则处理，CJK 标点偶尔出现在行首（与 UI 无关，属文字排版层）。
- 面板底部留 22px 露底，与原版对话框悬浮感一致；如需满屏可把 `.panel` 的 top/height 调成 0/514。
