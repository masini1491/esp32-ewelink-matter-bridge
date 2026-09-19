# Evidence staging inbox

本目錄是 sanitized Evidence Staging Surface，不具 execution authority，也不是 canonical validation 或 architecture truth。正式結論須 reconciliation 至 `VALIDATION.md` 等 canonical owner；本目錄不定義第二套 validation taxonomy。

Evidence record 應在適用時保留：

- evidence identity
- safe target／board／device identity
- source／firmware／build／revision identity
- measurement／test conditions
- authorized action／scenario
- observed result
- timestamp meaning／precision
- evidence classification／pending status
- sanitization／provenance
- completeness state
- reconciliation target／status

Evidence 第一次寫入 Git 前必須 sanitized。不得提交 raw `deviceKey`、Wi-Fi credentials、Matter secrets、MAC/private-network identifiers、private endpoints 或 personal data；大型敏感/raw logs 應留在 Git 外，Git 僅保存安全 digest、metadata、hash 或 pointer。
