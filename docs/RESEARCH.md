# Research basis and product decision

Research date: 2026-09-24. This is desk research, not customer validation.
Links describe advertised capabilities or reported behavior at inspection time.

## Direction changes

The repository began as an archive handover/classification specification. Later
discussion considered linking correction requests to resubmitted documents. Inspection
showed significant overlap with existing products and trace-it, including its
stale-decision alerts. Both directions are superseded for this implementation.

The selected hypothesis is source-to-destination invoice preservation checking for
small ERP integrators. It changes the initial user and task: diagnose a connector or
importer, with evidence and repeatable cases.

## Reported pain

### Unused invoice references

[Odoo community report](https://www.reddit.com/r/Odoo/comments/1wdpgag/incoming_einvoices_in_odoo_xml_contains_po_and/)
describes order/delivery references present in incoming XML but not usefully exposed
by the import flow, requiring an external viewer. This is an individual account.
Reproduce the stated configuration before claiming a product defect or prevalence.

### Recalculated or selectively extracted values

[Mustang discussion 1173](https://github.com/ZUGFeRD/mustangproject/discussions/1173)
describes difficulties preserving raw source values and distinguishing them from
calculated/imported representations. The maintainer disputes parts of the interpretation
and explains existing behavior. The reporter identifies at least one issue as apparently
fixed in the development version. Do not characterize all versions as silently corrupting
invoices. The useful research question is whether our checks can expose supported
representation differences with accurate attribution.

### Limited import contracts

[ERPNext EU eInvoice](https://github.com/alyf-de/eu_einvoice) documents imported/exported
fields, mappings and limitations. An integration's published scope matters: unsupported
fields should not automatically be labeled bugs. SourceCheck needs explicit required
facts and destination coverage.

## Competing capabilities

| Source | Observed claim/capability | Design consequence |
|---|---|---|
| [trace-it](https://github.com/Martinhdeez/trace-it) | Ingestion, evidence, versioned decisions and backtesting | Reuse engineering; do not claim those features as new |
| [trace-it alerts](https://github.com/Martinhdeez/trace-it/blob/84c4c0463862640940efb1232344287a2d03bcf5/backend/app/features/alerts/service.py) | Flags prior decisions affected by source/rule changes | Stale-decision warnings were not a defensible unique distinction |
| [QuerySurge](https://www.querysurge.com/solutions/etl-testing) | Source/target data testing | Generic preservation testing already exists |
| [ZUGFeRD Validator](https://zugferd-validator.de/en/docs) | PDF/XML consistency for invoice number/date/total; requires readable PDF text for that documented function | Focus beyond those fields and on destination output, without generalizing limitations to all competitors |
| [Xenett](https://help.xenett.com/en/articles/13192960-client-portal-workflow) | Transaction questions, attachments and follow-up | Client clarification is an established workflow |
| [Keeper](https://help.keeper.app/en/collections/3532690-client-portal-communications) | Client communication and transaction questions | Do not position another question portal as novel |
| [Numerint](https://numerint.com/faq) | Xero data/attachment archives with underlying identifiers | Archive export alone is not differentiated |
| [Suralink](https://www.suralink.com/technology/agent-library-suralink) | Request prescreening and version comparison | Resubmission review has direct adjacent competitors |

Vendor pages establish advertised functions, not measured quality. This search does
not establish that no product offers our proposed combination. No market-size,
price-superiority or adoption claim follows from these links.

## Proposed opportunity

An invoice-focused app linking page/XML evidence to actual destination fields, handling
coverage and text meaning, and saving reusable importer regression cases may reduce
diagnosis effort for small integrators. That is an inference to test.

Potential accumulated value comes from reviewed integration profiles, known failure
cases and useful workflow, not merely choosing Jev. Avoid expanding into a general
ERP or automation platform before testing this task.

## Jev rationale and limits

[Official TypeSafe introduction](https://docs.typesafe.ai/introduction) describes typed
questions, structured outputs and independent evaluation of questions. This fits
bounded semantic relation suggestions. It does not establish superiority on invoice
preservation, calibrated correctness on our data or the ability to inspect images.

Exact values and schema validation use code. Our pipeline supplies observations and
candidate alignments; Jev cannot repair omitted input. Evaluate it against the same
pipeline without Jev and preserve unfavorable findings.

## Evidence required next

- Reproduced importer cases with exact version/configuration and independent references.
- Real reviewable UI behavior and measurable diagnosis effort.
- Representative integrator feedback, repeat use and willingness to pay.
- An assessment of whether existing tools already solve those users' cases adequately.

Until then, use "planned", "proposed" and "reported" appropriately. Do not present a
software prototype or synthetic benchmark as proof of business value.
