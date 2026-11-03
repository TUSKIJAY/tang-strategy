# IBKR MCP 人工备用源

本入口接收助手已取得的 SPY/QQQ 市场数据包，不登录 IBKR，不要求本机 Gateway，也不读账户、持仓或订单。默认定时任务仍用 TradingView。只有明确指定 MCP 包和摘要的人工生产调用可以新增 MCP 市场日。

## 数据包

包在仓库之外。manifest.json 记录 schema_version=1、provider=ibkr_mcp、trade_date、精确美国 STK 合约选择证据，以及 SPY/QQQ 各 ONE_MIN、FIVE_MINS 的四份完整工具响应。responses 每项记录 symbol、tool=interactive_brokers_ibkr_get_price_history、实际 request、file 和 SHA-256。request 使用 outside_rth=true，period 与 step_count 二选一。不要补造不存在的 whatToShow 参数。

工具文本 JSON 和 structuredContent 同时存在时必须一致。校验严格检查数值、时区、顺序、真实 NYSE 日历及常规时段逐根覆盖。盘前盘后稀疏记录保留，缺口不补。1m 和源生 5m 都保留；零量沿用价导致的聚合差异单列，无法解释的差异拒绝。摘要证明包未变化，不证明全市场成交完整性。

运行使用源生 5m OHLCV。VWAP 是每分钟 (H+L+C)/3 按源成交量累计的近似值；5m 取桶末分钟的累计值。无累计成交量时为 null，常规时段必须可用。历史均线预热只读取得，元数据列出预热日期和 provider。成交量单位未声明时保留未知，不自乘系数。两个复盘页面仅在 MCP 日显示“IBKR MCP · 近似 VWAP”。

## 验证与接纳

先用项目现有 Python 环境运行 backend/scripts/accept_ibkr_mcp_package.py，传 date、--package、--manifest-sha256、--repo-dir，加 --validate-only。此模式不打开数据库、不晋升数据。

不加 --validate-only 时，脚本只接纳尚不存在的双标的市场日。运行指标构建后，复用 accept_staged_pair 的候选库、历史保留、规范交易投影、integrity/FK、原子晋升和种子回滚。--db-path 与 --accepted-seed-dir 可显式指定临时测试位置；真实原始包和临时数据库不提交。

## 发布与恢复

生产 runner 的人工调用同时指定 --mode production、--trade-date YYYY-MM-DD、--mcp-package 和 --mcp-manifest-sha256。必须是已经收盘的交易日，并且只补当前最早且唯一的缺失工作日。该入口仍受生产授权、固定 cron 声明和 publisher lease 约束。

runner 在同一 lease 下将包固化到外部 state/tang-publisher/market-packages/<manifest-sha256>/；事务只引用此只读持久包。新 MCP 事务为 v2，绑定 provider、日期、路径及摘要。历史 v1 继续按 TradingView 读取和写回，不升级旧记录。

普通 cron 不恢复未完成 MCP 事务。人工恢复需带同一持久包和摘要，拒绝换日、换包或换源。若事务已经 pages_verified，沿用原有 --expected-renderer-sha 恢复要求。已完成日不能通过 MCP 入口重新抓取；未来规范内容更新只读既有行情和包绑定，不改市场数据。

Pages 和页面验收通过后才投递；投递沿用消息收据、内容回读和幂等恢复。原失败记录保留，新的成功记录单独产生。后台无人值守 MCP 客户端不在本实现范围。
