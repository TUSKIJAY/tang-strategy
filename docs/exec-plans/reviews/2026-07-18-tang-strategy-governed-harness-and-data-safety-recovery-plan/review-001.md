# 交付物评审意见

**审核对象**: 2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

方案方向正确, 且大部分关键边界已经落到可执行层面. 当前 DB 的 43 天基线, 三个历史来源日, `market_days` 逻辑键, `bars_1m` / `bars_5m` 外键关系及历史整数 ID 不可复用等事实均得到正确处理. 从当前 DB 副本开始, 只插入缺失逻辑日, 再用原 43 天规范化摘要和历史来源摘要双向核对, 能避免把本地 6 天 seed 当成恢复主来源.

方案也正确区分了 Vite SPA 静态构建与旧 per-day HTML: 当前发布链是 tracked DB -> `frontend/public/reviews` JSON -> `frontend/dist` -> `gh-pages`, 而不是从 `docs/` 发布. 删除范围具有恢复完成和 consumer 复核前置, 远端动作被明确排除, provider/frontend 等无关清理只进入 optimization intake. Governed skeleton 的 15 项完整 surface 中, 既有 `docs/README.md` 保留并手工合并, 其余 14 项缺口已被纳入 bootstrap, 方向与 profile 契约一致.

当前不足集中在数据库晋升协议. 方案未处理候选构建到原子替换之间原 DB 发生变化的竞态, 也未把非空但语义残缺的 candidate 定义为拒绝条件. 这两项均可绕过现有日期集合检查并造成静默数据丢失, 因而不能裁决为 `approve`.

## 问题清单

### 严重问题

- **候选快照与晋升之间缺少原 DB 漂移保护**
  - 位置: `3. Constraints And Invariants`, `4. Data Recovery Method`, `5. Rebuild Fail-Closed Design`, `10. Rollback And Recovery Strategy`.
  - 问题描述: 方案从当前 DB 制作副本, 完成长时间验证后用 `os.replace` 晋升, 但没有规定如何阻止或检测这段时间内原 DB 被其他进程写入. 原 DB 可能被本地 API import, 另一个维护进程或仍在运行的服务更新. 此时恢复 candidate 仍基于旧快照, rebuild 的 superset 比较也可能基于旧集合. `os.replace` 本身只能保证单次路径替换的原子性, 不能证明被替换对象仍是最初验证的版本. 直接复制一个正在写入的 SQLite 文件也不是稳定快照协议.
  - 影响范围: 可能覆盖候选构建后新增的交易日, bars, strategy, teaching 或 metadata, 与“原 43 天不变”和默认 fail-closed 的核心目标冲突. 该风险也使 rollback backup 可能对应错误版本.
  - 改进建议: 在方案中增加统一的 snapshot/promotion protocol. 使用 SQLite 一致性备份能力或明确的写入静默窗口创建基线快照; 保存原 DB 的字节摘要和逻辑摘要; 晋升前在写排他条件下重新核对当前 DB 与基线完全一致; 任一漂移立即非零退出并重新构建 candidate, 不得继续替换. 同一协议应同时用于三日恢复和 rebuild. 还需规定连接关闭, journal/WAL sidecar 处理及目录同文件系统条件, 并新增“验证期间原 DB 被并发写入时拒绝晋升且新写入保留”的隔离测试.

- **日期集合 superset 不能单独证明 rebuild candidate 未丢失有效数据**
  - 位置: `5. Rebuild Fail-Closed Design` 第 100-107 行附近, `7. Phases And Acceptance Gates` Phase 2, `8. Validation Matrix` Backend and data safety.
  - 问题描述: 方案要求 `candidate_keys >= current_keys`, 但未定义每个已发现 seed 是否成功形成完整 market-day 数据. 当前 importer 可以为包含空 `bars_1m` / `bars_5m` 数组的 JSON 建立 `market_days` 行; SQLite `integrity_check` 和日期 superset 都会通过. Fresh candidate 还会重建 `strategies` 和 `teaching_assets`, 现有设计没有防止这些非 market-day 表因输入缺失而被清空或缩减.
  - 影响范围: candidate 可保留全部日期键, 却把某些日期的 bar 数据变为空或把运行时策略/教学资产缩减, 随后原子替换正常发生. 这仍属于 silent data loss, 与“真正 fail closed”不一致.
  - 改进建议: 明确 candidate 的语义完整性门. 至少要求 discovered file count 与 imported logical-key count 一致, 每日实际 1m/5m 行数与 `market_days.bar_count_*` 及 seed metadata 一致, 必需 bar 集非空, 所有 bar 外键有效, active strategies 和 required teaching assets 满足当前运行时契约. 若 rebuild 允许有意更新既有 bars, 应明确哪些差异属于 canonical reimport, 哪些计数/表缩减必须拒绝. 增加“日期键齐全但 bars 为空/计数不符”和“非市场表缺失”的失败测试, 并证明原 DB 字节不变.

### 中等问题

- **规范化 hash 契约尚不足以稳定复核**
  - 位置: `4. Data Recovery Method` 的 Read-only evidence 与 Candidate acceptance.
  - 问题描述: 方案写明“excluding only database-local foreign-key identity where needed”, 但未给出精确投影, 排序, 数值编码和 `NULL` 处理. `market_days.id` 是本地主键, `bars.market_day_id` 是本地外键; 两者应分别明确排除. `imported_at`, `meta_json` 原文和浮点序列化是否纳入也需要固定, 否则不同实现可能得到不可比较摘要.
  - 改进建议: 在 plan 或 evidence contract 中列出每张表的确切 hash 列, `ORDER BY` 规则和 canonical serialization. 对 market day 建议排除 `id` 但保留 source/title/count/imported_at/meta; 对 bars 排除 `market_day_id`, 保留 `idx` 及全部数据列, 并按 `idx` 排序. 原 43 天, 三个来源日和晋升后 DB 必须复用同一实现.

- **Governed checker 的完整 artifact 清单应在方案内显式化**
  - 位置: `7. Phases And Acceptance Gates` Phase 0 与 Phase 5.
  - 问题描述: 方案写了“14 missing artifacts”和“all generated indexes/templates/SOPs”, 但未列出 checker 最终必须断言的完整路径. 当前 checker 的 governed 列表仍只覆盖部分 surface, 尤其容易漏掉 decision template, plan/review templates, optimization index/record template 等文件.
  - 改进建议: 把完整 governed 路径清单写入 Phase 5 验收, 并要求 checker 对 15 项 governed surface 全部断言. `docs/README.md` 作为既有手工合并文件计入总 surface, 其余 14 项作为本次补齐范围. 同时保留 workflow 路径, job/display name 和 lifecycle links 校验.

### 轻微问题

- **激活术语存在一处不一致**
  - 位置: `3. Constraints And Invariants` 第 62 行附近.
  - 改进建议: 将“after independent acceptance”统一为 plan 审核裁决词 `after independent approve`, 避免与 implementation acceptance 的 `accept` 裁决混淆.

## 未验证项

- 三个恢复日的规范化行级 hash: 本次只读审核确认了历史来源存在, 目标日期和声明的 960/192 counts, 但方案尚未执行恢复. 应在临时 DB 中按修订后的统一 hash 契约验证.
- 原 43 天在 candidate 和晋升后完全不变: 需要 Phase 1 实际候选构建与晋升前漂移门通过后验证.
- Rebuild 的失败路径和并发写入保护: 当前实现尚未修复, 需要隔离测试证明 no-seed, subset, malformed nonempty seed, import/integrity failure 和 concurrent drift 均保留原 DB.
- Review/Backtest 手工回归: 需要实现完成后的浏览器运行环境和 2026-07-17 一日回归证据.
- 最终 governed validator 与 workflow contract: 当前 skeleton 存在, 但 checker/workflow 尚处于计划内待实现状态.

## 裁决理由

方案的架构方向, 数据来源选择, ID 重映射, Pages 输出模型, docs 删除前置, 权限边界和 scope control 均可保留, 不需要推翻重做, 因此不适用 `reject`. 但当前 promotion protocol 存在 TOCTOU 漂移窗口, rebuild 又可能接受日期键齐全但 bars 或非市场表残缺的 candidate. 两项问题直接影响原 DB 是否能被安全保留, 不能留到执行阶段临场处理. 将漂移门, SQLite 一致性快照, candidate 语义完整性和对应失败测试折回方案后, 才具备 `approve` 条件.
