# 《死馆》RW5 0.3.6 UI 交接

日期：2026-11-04。作者：xuanyide。执行：Codex。本次只做界面，不处理剧情或 CG。

## 当前入口

- 工作工程：D:/codex/移植项目/shinuyakata-rw5/源码-UI-0.3.6。
- 原 DeepSeek 工程和最终交付/死馆-RW5-0.3.5 未覆盖。新工程直接从用户指定的 0.3.5 源码 ZIP 独立解出。
- 新交付：最终交付/死馆-RW5-0.3.6。版本 0.3.6 / code 94，包名 com.codex.yakata.rw5。
- 最终包 14,552,193 B；SHA-256：e559aa5c493a98b3798d4c57a35669eb9882c5913804557a436253c9d2ff32ef。原证书一致，保留兼容封装。

## 视觉与文件

标题字标来自原作 title@allbtns%cref;off.png 和 over.png，不再用字体重绘替代。原交接认为缺失的独立按钮，实际可从 cref 精灵图拆分。按 title.csv：正常图先放回 (23,16)，恢复至217×293透明画布；各项以50像素步距截217×46。保留前五项，HOME PAGE仍无入口。原 logo 和标题图未改。

END GAME沿用0.3.5的侧键返回桌面提示，没有新增RW5强制退出接口。新增菜单右上角「章节选择」只是把已有 openChapters 接到可见控件，函数未改。

风格采用原作冷紫/黑底、细框、红色笔触和烛台纹饰。装饰只使用非剧情 message@base%base.png 的边缘区域。UI图片和矢量模板都可重复生成；没有新增动画或循环计时器。

主要改动：

- src/pages/index/index.ux：模板、完整CSS、标题按压状态activeTitle及两个简单触摸方法；原有游戏控制方法保持一致。
- src/common/ui2/：原版字标、五个over状态、title-shade，以及面板/按钮/卡片贴图。
- src/manifest.json、package.json：版本信息。
- tools/build-ui-classic.cjs、tools/ui-source/：精灵拆分及SVG生成源。
- tools/build-ui-only.py、audit-ui-only.py、check-ui-installed.cjs：UI专用构建、边界审计与模拟器字节检查。

正文继续使用 yakata 和原 watch.otf；舞台432×286、立绘坐标和图片比例不变。主要面板标题从x32附近开始，避开屏幕R角。长标题用Vela的 lines 和 text-overflow 样式，参考[官方文本组件文档](https://iot.mi.com/vela/quickapp/zh/components/basic/text.html)。本SDK不识别普通控件的 :active 样式，已移除；标题按压通过图片状态实现。

## 内容不变的证据

reports/ui-only-audit.json 对照0.3.5源码ZIP与RPK：比较1005个受保护的src/converted/tests文件；剧情、翻译、引擎、目录、字库和原有场景图片字节均相同。最终包有883个文件与旧包完全一致；只允许UI、编译页面、版本清单、构建时间与签名变化。app.js除版本和编译器模块编号外一致，页面脚本除标题触摸状态外一致。

本轮不调用原作脚本、图片或翻译转换器。历史模拟器有一个旧存档不被0.3.5目录接受，仍原样保留；本轮没有覆盖它。不要把新UI解释成修复旧剧情数据或证明所有历史版本存档兼容。

## 快速继续构建

优先在本次工作工程继续。只改index.ux或ui2时：

```powershell
cd D:/codex/移植项目/shinuyakata-rw5/源码-UI-0.3.6
D:/Anaconda/python.exe -X utf8 tools/build-ui-only.py
# 发布下一版本时同时递增versionCode：
D:/Anaconda/python.exe -X utf8 tools/build-ui-only.py --version 0.3.7
```

命令运行现有测试、固定 aiot-toolkit@1.1.0 编译器、兼容封装和UI范围审计；失败即停，不自动安装或发布。不会重建剧情、翻译、立绘或字库。若只重画UI贴图，可加 --assets；它会读取上述三张原作UI图片，不读剧情CG。

不要用 tools/update.py 做本轮UI构建，它会调用剧情转换。tools/apply-ui-classic.py 是从0.3.5首次换肤的复现脚本，不应在手动改好index.ux后反复运行，它会恢复模板及0.3.6/code94。

编译器自动查找本工程或同级「源码」里的 tools/compat-toolkit/node_modules/aiot-toolkit。也可通过 WATCH_COMPAT_TOOLKIT 指定。若移动到其他电脑，先按原项目package-lock安装兼容工具链；UI审计还需要 reports/ui-baseline-sha256.json 指向正确的0.3.5源码ZIP，且同目录保留0.3.5.rpk。

如要合并回另一份0.3.5源码，先备份并确认版本，再覆盖本次「UI源码与工具补丁.zip」内列出的文件。补丁不包含story、images、portraits、converted内容或字库；这些继续使用用户自己的0.3.5工程。不要覆盖其他开发者正在修改的工作区。

## 原生模拟器与验证范围

SDK D:/codex/2026-11-02/vela-sdk；NODE_PATH D:/codex/2026-11-02/native-toolkit/node_modules；设备数据 ../研究/vela-environment；设备 YakataRW5-432x514，432×514，128MiB。控制页 http://127.0.0.1:43142/。

实际包：标题/设置/序章首屏/阅读菜单/章节前后页/存档及覆盖取消/读档页等14张检查截图，未继续浏览原作相关场景。隔离UI测试：相同index.ux和engine.js，包名com.codex.yakata.uipreview，只用自编测试文字及标题图作占位；18张截图覆盖按压态、字号切换、鉴赏翻页及返回页、差分计数、正文滑动、选项、第30栏保存读取、确认和结束页。screenshots/ui-preview不是实际游戏CG预览。

现有12项Node测试通过。最终UI JS、manifest、字库、图标及关键皮肤图片已从设备拉回，与交付RPK逐项比较。最终实际包和隔离包各自的冷启动日志无panic/游戏脚本异常。本版实机与长时间内存测试未做。

开发中SDK曾在停止/重启调试应用、以及在同一启动周期打开第二个调试应用时发生vappxms原生data abort，导致截图冻结；保留研究日志，不计为通过。最终改为每次正常关机后冷启动，只启动一个调试应用。不要热切换测试包。长时间无输入可能黑屏，先唤醒再截图；不能把旧截图或冻结截图当检查通过。若SDK原生崩溃且关机无响应，先核对设备名和进程路径，仅处理本项目专用虚拟机，不能清用户磁盘或其他模拟器。

UI字节比对与最终检查报告随补丁提供；原作全剧情和路线正确性不在本轮验证范围。没有GitHub上传或邮件发送。
