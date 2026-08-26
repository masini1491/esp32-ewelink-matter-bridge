# Reference routing

本目錄保存 S1 所需的可追溯研究 synthesis，不保存 upstream source copy。實作前先讀 [upstream-sources.md](sources/upstream-sources.md)，再依 task 讀 architecture、contract 或 validation authority。

- Matter bridge／framework／target：`docs/build.md`、`docs/architecture.md` 與 sources dossier 的 esp-matter、ConnectedHomeIP、Arduino-ESP32 entries。
- eWeLink LAN 行為與第一個 device contract：sources dossier 的 SonoffLAN entry 與 `docs/architecture.md`。
- eWeLink CUBE 與 Tasmota：僅作 product／architecture evidence；不得 port source。

S1 pinned revisions 是 research baseline，不代表這些 repositories 被 vendored、被 runtime dependency 選用，或允許不受限制的 reuse。任何後續 upstream revisit 必須記錄 revision 與證據變化。
