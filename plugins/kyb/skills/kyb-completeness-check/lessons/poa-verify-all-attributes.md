# Proof of Address — verify ALL three attributes from the document itself

A Proof of Address is only valid if the document ITSELF shows all three:
1. **Subject name** — correct subject (company name for company PoA; UBO name for UBO PoA)
2. **Address shown** — a physical address printed on the document (business address for company; residential for UBO)
3. **Recency** — point-in-time ≤90 days, or duration-based not expired

Confirming 2 of 3 does NOT carry the third. Each must be checked independently against the actual
document content.

**Address must be printed ON the PoA document.** Do NOT infer the address from the certificate of
incorporation, tax card (e.g. NPWP), system data, or another file. If the submitted PoA does not
display an address → NOT_SUPPORTED (state "address not shown on document" as the gap).

Failure case: a bank "Account Activities" export was passed as company PoA because it had the
company name and was recent — but it showed no business address. It should have been NOT_SUPPORTED
(soft failure). This is the "no rationalizing" rule applied to PoA: two green checks must not create
false confidence in the third.
