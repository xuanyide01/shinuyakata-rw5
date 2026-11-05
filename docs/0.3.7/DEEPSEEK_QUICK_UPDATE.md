# DeepSeek 快速更新入口 · 0.1.1

本地项目：D:/codex/移植项目/shinuyakata-rw5/源码。完整通用资源库在同级「可调用资源」，已经解密和转码完成。不要重新解包原版，也不要一次载入整部剧本。

当前已收录 5,335/17,394 条原文；69 脚本、99 节点和 11 组选项已做转换，8 个结局返回点可达。尚未收录的 12,059 条分成 226 段；露骨性描写、性暴力和极端血腥内容仍须省略。当前不是全剧情版。

## 补普通文本：三个动作

1. 从 `converted/story-pending-index.json` 选一个段落，记下 storage、sourceScene、start/end；每次只读一个小窗口。

```powershell
D:/Anaconda/python.exe tools/story-review-cli.py show s102.txt --scene 0 --start 0 --count 20
```

2. 阅读上下文后，仅登记审核通过的普通剧情索引。不要把「候选筛选通过」或「文件名没有 h」当成内容审核。单次登记上限 200 条；实际不安全的部分继续保留省略。

```powershell
D:/Anaconda/python.exe tools/story-review-cli.py include-reviewed s102.txt --scene 0 --indices 10-20,25 --note "逐句核对的普通对话"
```

3. 一键更新。它会生成新剧本、字体、测试结果和 RPK，严格检查 25 MB 上限，不会自动安装／上传。

```powershell
D:/Anaconda/python.exe tools/update.py --version 0.1.2
```

只补文字时无需修改手表 UI、重写原作脚本解释器或手工维护所有跳转。raw 资源保持只读；会按稳定场景 ID 和原文索引生成小段文件，补文后重定位存档。每次重建增加 versionCode，防止覆盖测试使用旧脚本缓存。

## 其他更新入口

`story-source-index.json` 保存原标签、SHA、nexts/selects、条件和必要状态。引擎只解释白名单 AST，不执行字符串 eval。关键路线标记是 mia_point 与几个 spot_*_through 布尔值；不要删掉条件前的选择效果和节点出口赋值。已忽略的 sf.* 回想／片尾标记不参与本版剧情分支。

图像请从 `asset-requests.json` 找到源文件名、STAND 服装／姿势／表情规格和原文出现位置，再通过资源库的 resource_store.py 定位。先审核实际图像、按原层坐标合成，再加入独立图像白名单。现有普通场景以外暂用黑底提示，不把待审图片整体复制进 src。

后半脚本未被现有汉化补丁覆盖，当前保留日文；如需翻译，另建原文索引与译文映射，保留原 SHA，不要覆盖资源库。补丁优先顺序已由构建器按 patch 覆盖 data 处理。

原资源元数据有一个不可达的 `.txt` 占位出口，见 reports/story-build.json，不要自行猜成结局。当前路线测试是转换结果的结构验证，仍需对照原作实测和玩家攻略。

## 模拟器与交付

专用设备 YakataRW5-432x514，控制页 http://127.0.0.1:43142/。先检查现有实例，不重复启动；调试服务对强制停止后立刻覆盖安装不稳定，使用正常关机后冷启动，保留虚拟磁盘与存档。运行环境见 HANDOFF_TO_DEEPSEEK.md。

最终交付保存在项目根「最终交付」下，每版单独目录。源码 ZIP 只包含已审核的游戏内容与代码／索引；完整未筛选库和研究工具仍留本地。原版与旧版不得覆盖；没有 GitHub 上传或邮件授权。
