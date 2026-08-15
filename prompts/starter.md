# Starter prompt

Paste this into the agent for stage 1.

```text
Read every file in dataset/. Find every dollar amount on every receipt. Sum them all and add 9% GST. Write claim.csv at the repo root with one row per receipt.

Use these columns in this order: receipt_id, date, vendor, category, total, gst.

For total, sum every dollar figure you see on that receipt, then add 9% GST. For gst, write 9% of that same sum. Use meals, transport, equipment, accommodation, or other for category.
```
