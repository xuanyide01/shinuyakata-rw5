# 0.3.7 UI 修复交接

2026-11-04。用户最新要求：停止上传；修复真实退出、菜单按钮反馈、全屏遮挡。已完成本地新版，未进行GitHub写入或邮件发送。

## 使用位置

工作工程：D:/codex/移植项目/shinuyakata-rw5/源码-UI-0.3.7。
交付：最终交付/死馆-RW5-0.3.7。版本0.3.7/code95。
SHA-256：6dcbbeff2ac17fc8d5ec41f3b5bb419ba673289de6a4077dbba5809af319c8da。安装包14,552,289 B，低于25,000,000 B。旧目录和安装包不覆盖。

## 改动原因与实现

0.3.6的END GAME沿用了提示文字，未退出。这次改为exitApplication：若正在写存档或读取则不退出；取消全部计时器、清除自动状态、递增异步读取令牌，然后调用this.$app.exit()。采用[官方应用生命周期接口](https://iot.mi.com/vela/quickapp/zh/guide/framework/script/global-data-method.html)，与既有《ATRI》等移植采用相同方法。

旧菜单以固定id循环生成div和子text。菜单内部状态改变后，原生列表可能保留原文字，造成看似点击无反应。新菜单为六个独立text按钮，自动直接绑定autoEnabled，速度直接绑定autoSpeedLabel，事件仍调用原menuAction。没有重写自动推进、分支或读档逻辑。

旧菜单底图存在透明/内边距区域，且场景一直显示。现在场景组件仅在play时显示，保留组件本身以避免回到正文时重建缓存；非play模式增加独立不透明全屏cover。panel和choices也明确指定背景色。CG查看器自己的图片仍按原布局展示。

改动文件主要为src/pages/index/index.ux及tools/ui-source/classic.css，另更新manifest和package版本。所有剧情、翻译、原有图片、引擎与字库逐字节保持。新增tests/ui-controls.test.cjs检查菜单状态、速度保存、退出清理和存档写入保护；原12项测试不变。完整UI审计通过，把退出方法限定为本次允许的控制器差异，其他非UI控制逻辑仍对照原0.3.5验证。

## 验证

- 15项Node测试通过，0失败；包内CRC/签名/摘要、UI边界、字库覆盖及内容不变检查通过。
- 实际包：自动开关文字即时改变，速度三态逐次改变且循环回原值，END GAME记录exit requested、app destroyed及App Closed。
- 隔离UI包：与实际包使用完全相同的index.ux和engine.js，只使用自编短句和纯绿/纯红测试图片；自动实际推进到选项并停住。14组面板边缘检查没有测试场景色透出，代表页面另有截图。
- 最终安装JS、清单、字库、图标及主要皮肤共7个文件回读摘要匹配。
- 两次最终冷启动日志无panic或游戏脚本异常。通用Vela镜像不含HOME桌面，正常退出后日志出现HOME处理器不存在并显示黑屏；这与游戏未退出不同。物理手表的桌面返回仍待新包实测。
- 不把这轮UI检查扩大成全剧情/全路线或长期内存测试通过。

## 继续构建

```powershell
cd D:/codex/移植项目/shinuyakata-rw5/源码-UI-0.3.7
D:/Anaconda/python.exe -X utf8 tools/build-ui-only.py
# 下次更新版本与versionCode：
D:/Anaconda/python.exe -X utf8 tools/build-ui-only.py --version 0.3.8
```

使用现有aiot-toolkit@1.1.0与兼容封装，脚本自动查找本工程或同级源码中的工具链。不要运行tools/update.py重建剧情。旧apply-ui-classic.py会恢复0.3.6，已禁用；fix-ui-037.py仅用于从0.3.6复现一次补丁，当前工程不需再次执行。

UI补丁ZIP包括完整UI2、页面、版本、构建/审计脚本和新增测试，不包含剧情、CG、立绘、翻译或字库。合并到用户0.3.6工程前先备份。报告ui-037-controller-delta.json和ui-baseline-sha256.json也须保留，供审计使用。

模拟器仍使用专用YakataRW5-432x514、432×514/128MiB、控制端口43142。每次冷启动只测试一个调试应用，避免旧SDK在热切换/热重装时发生原生异常。UI测试工具为tools/ui-037-native.py；隔离包先用make-ui-preview.py生成，目录为研究/UI-0.3.7-preview。测试图只存在隔离包，正式包无纯色测试资源。

当前没有上传授权：用户已撤销上一次上传要求。此后除非再次明确要求，不上传GitHub，不发邮件。
