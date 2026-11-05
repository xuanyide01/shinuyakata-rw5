# UI 0.3.7 接手说明

版本：0.3.7 / code95；包名：`com.codex.yakata.rw5`；目标：REDMI Watch 5，432×514。

## 合并范围

本仓库是 UI 覆盖补丁。`src/pages/index/index.ux`、`src/common/ui2/`、`src/manifest.json` 为主要交付。`src/common/engine.js` 与已验收基础工程相同，随仓库提供用于独立 UI 测试。其余原作内容不在仓库中。

在已有本地工程副本中覆盖相同路径；不要清空工程，不要替换存档。原有 `src/common/ui/`、背景和 logo、字体与授权文件、catalog、story、既有测试等需由原本工程保留。源码 UI 页面与引擎不作重写。

## 三项修复

1. `exitApplication()` 先判断 loading/storageBusy，再清理逐字、自动和刷新计时器，递增读取令牌，调用 `$app.exit()`。直接沿用系统生命周期，未通过重启设备实现退出。
2. 菜单由固定 key 列表改成独立 text 按钮。自动状态直接绑定 `autoEnabled`，速度绑定 `autoSpeedLabel`；动作继续调用原 `menuAction()`。
3. 场景组件仅在 play 时显示，保留组件以复用缓存；非 play 模式覆盖 432×514 不透明底层，panel/choices 设置实色背景。

## 构建

Node.js 和 Python 3；完整工程兼容编译器为 `aiot-toolkit@1.1.0`。此处的 `npm test` 只运行三个自编 UI 测试。完整工程还包含其他 12 项测试。

在完成合并的工程中执行：

```sh
python tools/build-ui-only.py
```

编译器默认查找 `tools/compat-toolkit/node_modules/aiot-toolkit`，也可用环境变量 `WATCH_COMPAT_TOOLKIT` 指定路径。此脚本不生成剧情、译文、立绘或字体。完整审计需要原有 0.3.5 源码归档及相应报告；报告内路径是验收时的本机路径，新环境须配置相应路径，不能把缺少基准的情况当作审计通过。

`build-ui-classic.cjs` 用于从已有非剧情 UI 图集再生成按键和面板，需要本地 UI 源图片和 sharp；仓库已经提供生成结果，不必为普通界面修改运行资源转换。`fix-ui-037.py` 是 0.3.6 到 0.3.7 的一次性修复脚本，当前源码无需重跑。

## 验证和限制

- 验收工程：15 项测试通过；公开 UI 子集：3 项测试，可独立运行。
- 1,005 个受保护文件对比，883 个包内文件不变；剧情、CG、立绘、译文、引擎、字体保持原始字节。
- 模拟器验证菜单开关文字即时刷新、速度三态循环、退出销毁生命周期。隔离测试还验证自动推进至选项和界面遮挡。
- 2026-11-05 用户确认修改通过并授权发布；没有另行声称本次验收使用了哪款实体设备。
- 模拟器不含 HOME 桌面，退出后黑屏属于该测试镜像缺少启动器；真实桌面显示仍依赖设备环境。
- 不据此声称全部剧情或长期内存稳定性通过。

## 发布边界

GitHub 只发布 UI 源码补丁、非剧情界面素材、检查报告和文档。不发布原作剧情、CG、立绘、字库、基础游戏资源或完整 BIN/RPK。原本地安装包与历史交付保持原样。

原作界面图片及第三方组件不在自编代码的 MIT 授权范围内。作者 xuanyide；基础工程 DeepSeek；UI 实现与修复 Codex。联系：shining237841@gmail.com。
