# Stage 2: review the claim

Open this conversation after stage 1, or after you copy `dataset/claim.reference.csv` if you skipped extraction.

You may point the agent at `claim.csv` or at `dataset/claim.reference.csv`. Also point it at the files in `policy/`.

Paste the prompt below. Then walk the talking points in order.

```text
Read claim.csv if it exists. If it does not, read dataset/claim.reference.csv. Read every file in policy/.

We will review this claim together against the policy. Walk the questions below in order. For each one, name the relevant clause and give a verdict using the words in policy/general.md. Do not invent a clause that is not in the files.

1. The claim period includes dates before and after 1 July 2026. The meal cap changed on that date. Which document wins, and for which rows?

2. Find two meal receipts on the same day before 1 July 2026. Together they go over $35. Neither one goes over $35 alone. How does the cap apply?

3. Find a restaurant receipt that has a wine line. What is covered? What is not?

4. Some receipts have no GST registration number. Can we still claim the gross amount? What happens to GST reclaim?

5. Compare the equipment rows. One sits in the $200 to $1000 band. One sits above $1000. What does each need?

6. Is the same expense claimed more than once? Check across sources, not only by id.

7. There is a co-working day pass. What does the policy say about it?
```
