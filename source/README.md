# 星轨疾跑 / Star Rail Runner

XBuilder 原生项目源码。详细操作与导入步骤见交付包根目录的《使用说明.md》。直接将交付包根目录的 StarRailRunner.xbp 导入 https://x.qiniu.com 即可。

入口：main.spx。资源入口：assets/index.json。

- tools/build.py：原创美术、音效、角色脚本和项目文件生成。
- tools/package.py：只打包现有项目，不覆盖修改。
- tools/test_core.py、tools/core_test.go：19 项测试，直接使用 main.spx 的实际逻辑。
- tools/native-check/：使用官方 spx 3.3.0 解释器及资源加载器验证 .xbp。

代码和原创素材使用 MIT 许可，见 LICENSE。XBuilder、spx 与相关工具属于各自项目；本交付不包含其引擎二进制。
