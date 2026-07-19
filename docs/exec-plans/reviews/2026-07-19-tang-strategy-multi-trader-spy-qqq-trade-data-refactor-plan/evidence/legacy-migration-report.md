# Legacy Trade Migration Report

## Phase 0 Source Inventory

- Source directory: `content/trader-trades/`
- Files: `20`
- Legacy trades: `27`
- Day-level note entries: `2`
- Notes-with-trades date: `2026-05-26`
- Trades-empty note date: `2026-05-29`
- Migration state: not run in Phase 0
- Legacy file mutation/removal: not run and not authorized before Phase 6

| Source path | Trades | Day note | SHA-256 |
| --- | ---: | --- | --- |
| `content/trader-trades/2026-05-26.json` | 2 | yes | `2b1308cf62038cbb9f58beb38eb8655fdf7d90e3ff688719332331410ad0cd51` |
| `content/trader-trades/2026-05-27.json` | 1 | no | `656795d5daf370f8c51f5a966dcfe1161625346a8ec6f0141b8c467319111e4f` |
| `content/trader-trades/2026-05-29.json` | 0 | yes | `dd40d46aedf4a109c7e7a715d68f1b1b36417202c1260631f7d729413a6b3314` |
| `content/trader-trades/2026-06-02.json` | 1 | no | `d44bb62a29bb5e750a844b5ecc41e40426e0e332862d68654d167f41e24b6243` |
| `content/trader-trades/2026-06-08.json` | 3 | no | `122f34c96d1c2500f65d0d245e768ad2839159a6cde3fd6102ed80a5f3120f37` |
| `content/trader-trades/2026-06-15.json` | 3 | no | `17756fb45d3af15de411268155c432a08c0e847855cbdd7b073de5bd5f42e7df` |
| `content/trader-trades/2026-06-22.json` | 1 | no | `145a112f60bf6297a626d047dd7e6d339ba89158542c3afbd9a4749cab2af0b9` |
| `content/trader-trades/2026-06-23.json` | 2 | no | `6d424faee8fb6b4ea580a2223853f5004db6d43d4b3acea2837b46cac9d6287a` |
| `content/trader-trades/2026-06-24.json` | 1 | no | `ac2cd8c855cd1fbdad6ad8971a1fd12921a9aa9585547a2d91dfd2c95eacc74e` |
| `content/trader-trades/2026-06-25.json` | 1 | no | `97d0f7c03926ed30d93ed99c592fc96d4f936f086e2ab72723fae32d226c102a` |
| `content/trader-trades/2026-06-29.json` | 1 | no | `8aacad518bee677e7932c4d6c1e94cf836532150f9993164c0f897f0d1671451` |
| `content/trader-trades/2026-06-30.json` | 1 | no | `2c615bb1e280b1e9e5db23cd0f5b50d8680adc784ba55e1a3b8dae9d0ee11c15` |
| `content/trader-trades/2026-07-01.json` | 1 | no | `c869ccac80167f16ee69752b09c006a57e3ee622706cf3f4404401e4eef0d155` |
| `content/trader-trades/2026-07-02.json` | 1 | no | `66ca3bffc1f71e7c6612e12a80668669daa33e361630addfbed101490600a69a` |
| `content/trader-trades/2026-07-07.json` | 3 | no | `941ede867d75ca1bb3b35d5490628292488827157000fd855c3dbc58880b7741` |
| `content/trader-trades/2026-07-08.json` | 1 | no | `d4f476393ec10ede3ff539e967a160b4cabf9b2e46f9f0ad3c03ee4a9d0ec7e4` |
| `content/trader-trades/2026-07-09.json` | 1 | no | `e3cb3ddc317610d1724d99f980573bb31ffa43e3689a3e93f01fbfb8c6156861` |
| `content/trader-trades/2026-07-15.json` | 1 | no | `c8d2b05449af3c187c8d9417ad69b983f3ad804c453a1347ef115fafbeccfe3b` |
| `content/trader-trades/2026-07-16.json` | 1 | no | `4198a62702b253cce7ac94face2b3705642441ec9a648c1c3c913ad482737928` |
| `content/trader-trades/2026-07-17.json` | 1 | no | `f664044a519ceab8c237a38c7ada1e9d0a1d643e2aabb61ed70e1b25ee65f504` |

All files report ticker `SPY` and expose the current keys `date`, `notes`, `ticker`, and `trades`. Phase 1 must classify all 27 trades and both day notes without writing canonical data; Phase 3 will append the field-level source-to-target reconciliation and idempotency result here.

## Phase 1 Pure Classification

- Result: pass
- Canonical files written: none
- Tracked DB touched: no
- Source files: `20`
- Classified trade rows: `27`
- Classified day-context rows: `2`
- Allowlisted reported returns: `4`
- Approximate exit times extracted: `3`
- Review-required rows: `1`
- Position-size percentages converted to returns: `0`
- Repeat-run result: byte-for-byte equal deterministic JSON in the focused fixture

| Kind | Source | Index | Target ID | Return | Exit | Rule/reason | Review |
| --- | --- | ---: | --- | ---: | --- | --- | --- |
| trade | `content/trader-trades/2026-05-26.json` | 0 | `tg_20260526_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-05-26.json` | 1 | `tg_20260526_tang_spy_002` | — | — | `no_allowlisted_reported_result` | no |
| day context | `content/trader-trades/2026-05-26.json` | 0 | `ctx_20260526_tang_spy_001` | — | — | `preserve_day_context` | no |
| trade | `content/trader-trades/2026-05-27.json` | 0 | `tg_20260527_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| day context | `content/trader-trades/2026-05-29.json` | 0 | `ctx_20260529_tang_spy_001` | — | — | `preserve_day_context` | no |
| trade | `content/trader-trades/2026-06-02.json` | 0 | `tg_20260602_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-06-08.json` | 0 | `tg_20260608_tang_spy_001` | `50.0` | `11:41` approximate | `allow_explicit_signed_result_with_result_verb` | no |
| trade | `content/trader-trades/2026-06-08.json` | 1 | `tg_20260608_tang_spy_002` | `40.0` | `14:07` approximate | `allow_explicit_signed_result_with_result_verb` | no |
| trade | `content/trader-trades/2026-06-08.json` | 2 | `tg_20260608_tang_spy_003` | `40.0` | `14:31` approximate | `allow_explicit_signed_result_with_result_verb` | no |
| trade | `content/trader-trades/2026-06-15.json` | 0 | `tg_20260615_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-06-15.json` | 1 | `tg_20260615_tang_spy_002` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-06-15.json` | 2 | `tg_20260615_tang_spy_003` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-06-22.json` | 0 | `tg_20260622_tang_spy_001` | — | — | `review_ambiguous_unsigned_percentage_with_end_word` | yes |
| trade | `content/trader-trades/2026-06-23.json` | 0 | `tg_20260623_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-06-23.json` | 1 | `tg_20260623_tang_spy_002` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-06-24.json` | 0 | `tg_20260624_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-06-25.json` | 0 | `tg_20260625_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-06-29.json` | 0 | `tg_20260629_tang_spy_001` | `30.0` | — | `allow_explicit_signed_result_with_result_verb` | no |
| trade | `content/trader-trades/2026-06-30.json` | 0 | `tg_20260630_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-01.json` | 0 | `tg_20260701_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-07-02.json` | 0 | `tg_20260702_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-07.json` | 0 | `tg_20260707_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-07.json` | 1 | `tg_20260707_tang_spy_002` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-07.json` | 2 | `tg_20260707_tang_spy_003` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-08.json` | 0 | `tg_20260708_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-07-09.json` | 0 | `tg_20260709_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |
| trade | `content/trader-trades/2026-07-15.json` | 0 | `tg_20260715_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-16.json` | 0 | `tg_20260716_tang_spy_001` | — | — | `deny_position_size_percentage` | no |
| trade | `content/trader-trades/2026-07-17.json` | 0 | `tg_20260717_tang_spy_001` | — | — | `no_allowlisted_reported_result` | no |

The single review-required row preserves the full 2026-06-22 note and leaves reported outcome null. The 11 position-size rows are explicit deny classifications, not review ambiguities. Phase 3 will add source/target field-parity results after canonical files exist.

## Phase 3 Canonical Migration

- Result: pass
- Registry: `content/traders/index.json`, one active Tang identity, SHA-256 `366af03ec69e4c9466190204be443a80169dd4c4d0a861bc4e0220bf0aff8c13`
- Canonical daily files: `20`
- Canonical trade groups / contexts: `27` / `2`
- Pure-render to tracked canonical comparison: exact for all 21 documents
- Sorted aggregate canonical SHA-256: `f22c5866cea04f39ec772b7542f75f06b1537bcae860668773dd7dd2da589a7e`
- Source records unaccounted: `0`
- Source notes altered or dropped: `0`
- Position-size percentages promoted to outcomes: `0`
- Reported outcomes / extracted approximate exits / review-required rows: `4` / `3` / `1`
- Repeat render: byte-for-byte idempotent
- Legacy source removal: not run; deferred to Phase 6

| Canonical file | Groups | Contexts | SHA-256 |
| --- | ---: | ---: | --- |
| `2026-05-26.json` | 2 | 1 | `fa7df409dda956738c708d850f06d44f359ac6ba56d1803caf224df3ed471ab8` |
| `2026-05-27.json` | 1 | 0 | `6224327dc5f5aee551cb3d197fbb262eaeb5e644950c19eb94d702baa2f811d4` |
| `2026-05-29.json` | 0 | 1 | `1bda05ce03cb8531685e6629fda5d475911d0343a189308693688619374d1a31` |
| `2026-06-02.json` | 1 | 0 | `46d6d32b5921eaae2b3fba263da62b8c4e35e523874633a8879c57abf5dc48d2` |
| `2026-06-08.json` | 3 | 0 | `f5ff9532550486e53f02fb43edb3e03613e60f0ed3542262af31f989fcd882af` |
| `2026-06-15.json` | 3 | 0 | `660e04f4e9f2f1a3c11a909c9ab34d0b5dc12a63f4dba859beb232b9f07e3376` |
| `2026-06-22.json` | 1 | 0 | `16a7d544d89e1533fde1e8f516da9ca82e009605335d4d1a093527a5a4c6f574` |
| `2026-06-23.json` | 2 | 0 | `c3ae5cfccea058872458f4ff9b1abe3264318ce93154b20616778859e8e263da` |
| `2026-06-24.json` | 1 | 0 | `1b6cf5551846f15ef5956329fda4e1f1339d9e6992118cacd1611a7bbe421104` |
| `2026-06-25.json` | 1 | 0 | `42f6c4afd98ec73887d765e4c8bb1278e0c149025ad5ceee1a5ce711b980f546` |
| `2026-06-29.json` | 1 | 0 | `ac7be3d628af6654cbbf3ff97f86614a20896e99dc85b8654bec5c13eefe973a` |
| `2026-06-30.json` | 1 | 0 | `4ceb9a0a0e42e1705b46103cd1174de99508e9fa94e203bf88b862484c088163` |
| `2026-07-01.json` | 1 | 0 | `0d457086c0ef817c956a98225735beda69a8fd4dace1d15a1bc946426e39130a` |
| `2026-07-02.json` | 1 | 0 | `293afee033a7106a5cd690e0ca7b5f0d6321faad9554fb76e7ce1fd1cafd32ab` |
| `2026-07-07.json` | 3 | 0 | `7283c0396abc2cf687b46a9b6590c9b50da862180e6a9d0a61fd01e85d4922d1` |
| `2026-07-08.json` | 1 | 0 | `47bf6afa96508f56e97a1bcbe7530130e68939cfd62bc74f55488b774d370506` |
| `2026-07-09.json` | 1 | 0 | `258e036b35e4b6e05e9cf444f0cd39c1d9df3ba751b106084eb2060ed3431f83` |
| `2026-07-15.json` | 1 | 0 | `351b40a94bce2f608a648ebeacafb0fd024d246d9b36e2951d2d2617fa161bc3` |
| `2026-07-16.json` | 1 | 0 | `f1cebe5afece1bf5f0d91759175263c222d2f40c481a450cbea60012a154f5be` |
| `2026-07-17.json` | 1 | 0 | `73091d1024bb47f64193215d70105c918e4cba05973066f0ba0df58dcb3eef46` |

Service-level acceptance covers readonly/admin access, trader/ticker/exact-date/date-range/status/review/eligibility filters, the 2026-06-08 reported-return set, the 2026-05-29 context-only day, full-repository validation before admin writes, candidate-file fsync, atomic replacement, forced replacement failure cleanup, and explicit target-schema SQLite projection. These handlers remain unregistered; existing assemble/static code does not read the new canonical directory in Phase 3.
