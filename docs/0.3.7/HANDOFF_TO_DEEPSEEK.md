# 当前交接状态 · 0.1.1

请先读 DEEPSEEK_QUICK_UPDATE.md、README.md 和 VALIDATION.md；这些文档取代 0.1.0 的旧状态。

已接入 5,335 条普通原文，未收录 12,059 条；已建立 69 脚本、99 场景、11 组选项、8 个结局出口的转换和测试，703 组素材需求索引。当前仍非全剧情／全画面版本。所有未收录段落可按原索引继续审核补文。

代码：src/common/engine.js；界面：src/pages/index/index.ux；转换：tools/build-story.py；白名单：converted/story-review.json；更新：python tools/update.py。旧 schema=1 存档、包名 com.codex.yakata.rw5、yakata_rw5_slot_v1_ 键保持。新剧情使用原文索引和稳定页 ID，补文时不整体移动后续场景。

模拟器 SDK：D:/codex/2026-11-02/vela-sdk；NODE_PATH：D:/codex/2026-11-02/native-toolkit/node_modules；本项目设备数据：../研究/vela-environment；设备名 YakataRW5-432x514。仅操作本项目专用实例，不能清其他会话的设备或存档。

全部资源仍位于同级「原始资源解码」和「可调用资源」。后者有 resource_catalog、scene_index、resource_store.py 与详细说明。原 I 盘资源只读，不执行原游戏 EXE，不发邮件，不自动上传 GitHub。

普通剧情白名单才会打包。本次更新只处理普通剧情；完整素材库独立留在本机。
