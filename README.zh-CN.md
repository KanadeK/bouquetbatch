# BouquetBatch 中文说明

[English README](README.md)

BouquetBatch 是一个离线命令行优化器：输入花材批次、花束配方、替代优先级和带日期的订单，输出可追溯的拣货方案。它实现了真实的最小费用最大流分配，不是花店 POS、库存增删改查界面，也不是空壳。

## 能解决什么

当多个订单争用同一批易腐花材时，简单按顺序贪心分配可能把通用花材先给了可替代的需求，导致只能使用该花材的需求缺货。BouquetBatch 会在全局范围内：

1. 先最大化已分配的花材枝数；
2. 再保护数字更小的高优先级订单；
3. 优先使用替代等级更低的花材；
4. 优先消耗更早到期的合格批次；
5. 最后按稳定标识消除随机性。

同一份输入在相同版本下会得到字节一致的输出。

## 安装与运行

需要 Python 3.11 或更新版本。

```console
uv tool install .
bouquetbatch plan examples/complete.json --output market-plan
```

输出目录包含 plan.json、pick-list.csv 和 report.html。CSV 已防止表格公式注入，HTML 完全离线且无脚本。

## 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 已生成完整方案 |
| 1 | 输入有效，已生成带缺货项的方案 |
| 2 | 命令、输入、读写或输出目录有误 |

短缺不是程序崩溃。退出 1 时查看 diagnostics，它会区分可用库存、已分配给其他需求的库存、尚未到货和已经过期的库存。

## 输入与验收

最完整的可运行样例见 [examples/complete.json](examples/complete.json)，字段说明见 [docs/input-format.md](docs/input-format.md)，严格契约见 [docs/spec.md](docs/spec.md)。

```console
uv sync --locked --dev
uv run python scripts/check.py
```

质量门执行格式、静态检查、严格类型、分支覆盖率、三类示例、打包，以及在全新虚拟环境中安装 wheel 后的冒烟测试。失败修复见 [docs/troubleshooting.md](docs/troubleshooting.md)。

## 明确不做

v0.1 不做 POS、CRM、报价、采购、账号、云同步、图片识别，也不扩展为通用生产排程系统。项目只把一件事做实：把易腐批次可靠地分配给花束配方需求。

许可证：MIT。
