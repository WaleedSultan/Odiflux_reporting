# Security

This module extends existing models only (`res.company`, `res.partner`,
`account.account`, `res.config.settings`). No new `ir.model` records are
introduced in v1, so **no** `ir.model.access.csv` is required.

Access follows native accounting groups (`account.group_account_*`).
Add CSV rows here only if future wizards / transient FS helpers need them.
