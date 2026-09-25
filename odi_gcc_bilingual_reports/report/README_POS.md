# POS templates

`pos_receipt_templates.xml` in this folder is a **non-loaded reference**
(empty shell). Real POS data is shipped by the sibling companion:

```
/workspace/odi_gcc_bilingual_reports_pos/
```

Main module manifest intentionally omits POS XML and does **not** depend on
`point_of_sale`, so Accounting-only databases install cleanly.
