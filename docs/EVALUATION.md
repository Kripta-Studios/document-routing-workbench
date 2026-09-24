# Evaluation protocol

Status: protocol plus a small development-only functional run. The held-out and
live Jev benchmarks remain incomplete. See [RESULTS.md](RESULTS.md).

## Questions

1. Does the comparator detect verified preservation problems without false alarms?
2. Does it abstain when source facts, target coverage or line correspondence are unknown?
3. Does Jev add useful semantic comparison beyond the same deterministic pipeline?
4. Can an integrator diagnose actual import behavior faster with the app?

These need different evidence. Keep functional fixtures, public-corpus observations,
synthetic stress cases and customer-pilot results separate.

## Reference unit and annotations

A case links original bytes, representations, importer output, mapping/coverage
profile, source facts and expected checks. Record source family, hashes, tool versions,
capture method and annotation origin.

Expected checks must be independent of the importer under test. Raw XML extraction
can establish declared exact values; reviewed page evidence can establish visual facts.
XML validity does not guarantee agreement with the PDF or business correctness.

Annotation origins: upstream, deterministic_constructed, assistant_reviewed,
human_reviewed. Never describe assistant labels as human ground truth. Record reviewer
identity/category, time, criteria version and disagreements. An unresolved reference
is excluded from a correctness denominator but retained in coverage/uncertainty counts.

The evaluator can access expected labels; the comparator and Jev cannot. Exclude
error-revealing filenames, mutation IDs and upstream valid/invalid directory names.

## Corpus preparation

Before model development, inventory and deduplicate exact hashes and related families:
PDF/XML versions, alternate renderings, importer versions, mutations and repeated
source examples stay together.

Target 150 independent source families if the reviewed inventory supports it. This is
a target, not a claim about available unique invoices. If fewer qualify, use all eligible
families, report the smaller denominator and do not pad it with duplicates.

Freeze 60% development, 20% validation and 20% test by deterministic family hash ordering
with seed 20260924. Commit the sanitized ID/revision/split manifest before tuning.
Publish actual counts and rounding rules. Every derived variant inherits its family's
partition. Record any provenance-based exclusion before predictions are inspected.

Use development for profiles/prompts and validation for selection. Freeze code,
profiles, criteria and thresholds before the initial test run. Later iterations retain
the original results and are labeled exploratory; they do not reset the untouched test.

## Three technical suites

### Functional and synthetic faults

Owned fixtures specify exact expected behavior, including absent paths under known
versus unknown coverage. Mutations include changed amounts, lost order references,
legitimate normalization, contradictory instructions, repeated lines and malformed XML.
Track mutations and expected differences explicitly. Do not pool their error rate
with naturally occurring importer behavior.

### Real importer observations

Execute pinned Mustang versions and capture their genuine outputs. Audit selected
facts against independent source observations and bridge coverage. A field unavailable
through our bridge is unobserved, not a confirmed importer loss.

A second version does not automatically provide a better reference. Attribute observed
differences to the recorded code/configuration and report unresolved causes.

Later, capture Odoo output from actual stored fields using a pinned export/query
definition. Uploaded user JSON has unverified execution provenance unless established.

### Semantic comparison

Build reviewed source/destination pairs for equivalent, contradictory,
partially_preserved and insufficient_evidence. Partial means supported content is
retained but a required part is omitted, without an explicit contradiction; contradiction
takes precedence when the same fact is asserted incompatibly. Incomplete observations
yield insufficient evidence.

Test actual extracted text and a separately reviewed transcription where available.
This isolates OCR effects. Do not treat corrected transcripts as the live OCR pipeline.

## Baselines

Use identical observations, profiles and candidate line pairs:

1. Deterministic comparator: exact matching plus explicit normalization; abstain on
   unsupported semantic judgments.
2. Same comparator with a documented lexical/text-matching baseline for semantic pairs.
3. Same comparator plus Jev semantic suggestions.

Report rules-only abstention rather than forcing it to answer every pair. A simple
lexical baseline is not the best possible learned classifier. Another model or trained
baseline requires enough training data and an explicit remaining comparison question.

Jev must not select an expected answer or infer the result from metadata. Test whether
its extra coverage comes with more false alarms. Keep the app usable if it adds no value.

## Metrics

Report all counts before ratios:

- Files attempted, parsed, unsupported and failed; unique families and representations.
- Required checks, observable checks, source-uncertain checks, unobserved destinations
  and unresolved line mappings.
- Precision/recall/F1 for verified issues on checkable annotated facts, plus false-alarm
  rate on legitimate transformations and missed-important-issue counts.
- Document-level issues and false alarms, alongside field-level metrics so a long
  invoice does not silently dominate the result.
- Semantic macro-F1, confusion matrix and abstention. Show coverage/error trade-offs
  only for explored validation thresholds; no automatic acceptance in the MVP.
- Calibration analysis only when enough independent labels exist. Provider confidence
  is not a probability of whole-document correctness.
- Median/p95 parse, OCR, importer, comparison, Jev and end-to-end latency.
- Separate cold initialization, warm fresh execution and cached replay.
- Actual usage tokens, pricing source/date, estimated cost and unknown-billing attempts.
  Zero returned usage after a timeout is not evidence of zero cost.
- Download, cache, environment, rendered-page and report storage separately.

Failures stay in pipeline denominators, while semantic-only metrics explicitly describe
the observable annotated subset. Use family-level resampling if reporting confidence
intervals. Small samples cannot establish rare-failure safety.

## Review and reporting

Review false positives/negatives for source uncertainty, coverage errors, alignment,
normalization, semantic interpretation and reference mistakes. Record corrections as
new annotation versions with reasons; do not relabel because Jev disagrees.

Save private run artifacts sufficient for offline aggregate reproduction. Publish only
permitted sanitized artifacts, manifest hashes, configuration versions and commands.
If private data prevents public reproduction, state exactly what can be reproduced
from the public release and provide an owned-fixture run separately.

Publish a candid conclusion: measured benefit, no measured benefit, or insufficient
evidence for Jev. Keep old receipt country agreement and reviewed receipt scores out
of all SourceCheck results.

## User pilot

After technical validation, compare actual diagnosis/acceptance tasks with integrators'
current process. Include mapping/setup and correction time, counterbalance task order,
record important missed issues and repeat use. Product targets in PRODUCT.md are
hypotheses. Software completion and business validation are separate milestones.

## Implementation note, 2026-09-24

`configs/evaluation-manifest.json` freezes two inspected families, both assigned to
development by the specified seed/hash rule. It was written after implementation
work began, so it does **not** create an untouched validation or test cohort.
`sourcecheck evaluate` reports six authored functional variants, four actual Mustang
executions across the two families, and four authored semantic pairs. The variants
inherit their owned source family and cannot increase the independent-family count.
Rules abstain on the semantic pairs; the lexical SequenceMatcher baseline has an
explicit 0.86 equivalent threshold. Jev predictions are absent because no
authorized key was available. This is a functionality and attribution check, not
the precision/recall or macro-F1 study specified above. All detailed numbers and
reproduction commands are in [RESULTS.md](RESULTS.md).
