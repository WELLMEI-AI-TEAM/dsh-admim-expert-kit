# v0.2.0 当前分发入口

| 文件 | 用途 |
| --- | --- |
| upload/dsh-admin-*-v0.2.0.zip（5个） | 每包单独上传/导入一个技能，根有SKILL.md，含资料、脚本、样例和Apache-2.0许可证 |
| upload/packages-v0.2.0.json | 5个单包版本、文件数与SHA256 |
| admin-expert-kit-skillhub-ready-v0.2.0.zip | 5个单包与manifest的组合下载包；先解开再逐个导入，不是单个技能 |
| admin-expert-kit-v0.2.0-MANUAL-ONLY.zip | 全套手工安装与源码包，含测试、构建工具和5个单包；按skills子目录安装 |
| SHA256SUMS-v0.2.0.txt | 本版7个ZIP的SHA256 |
| skillhub-ready/dsh-admin-*/ | 与源码同步的发布目录，技能名/metadata.slug使用dsh-前缀 |

新包尚未上传市场或进行真实宿主导入验证。旧v0.1.x ZIP保留作历史参考，当前维护版本为0.2.0，不要根据旧包名选择最新版。独立包无需其他技能、连接器、账号或pip依赖即可运行检查；制作Word/Excel仍取决于实际文档工具。

安装见 [INSTALL.md](INSTALL.md)，版本与范围见 [MANIFEST.md](MANIFEST.md)。从仓库根运行 `python -B tools/build_release.py` 可重建，再运行 `python -B tools/verify_release.py` 检查独立包和解压后的回归。
