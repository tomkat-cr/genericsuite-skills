---
name: privacy-policy-checker
description: Use when an app's privacy policy needs to be checked against what the app actually does before an App Store, Google Play or production release — undisclosed third-party AI providers (OpenAI, Anthropic, ElevenLabs), analytics/ad SDKs, location, contacts, microphone or camera data, a policy that has not been updated in several releases, a rejected Data Safety form or Privacy Nutrition Label, or a "we never share your data" claim that the code contradicts. Also use when preparing a store submission privacy review or a GDPR/CCPA/COPPA disclosure gap check.
argument-hint: "[app-root] [privacy-policy-url-or-path]"
---

Compare what an app's code **actually does** against what its privacy policy
**says it does**, and produce a report the developer can act on.

Bundled references — READ the ones you need before reporting:

- `references/data-inventory-checklist.md` — the fixed sweep that turns a
  codebase into a data inventory (manifests, SDK deps, env keys, network calls),
  per stack: Flutter, Kotlin/Android, Swift/iOS, React Native, web, backend,
  GenericSuite.
- `references/compliance-requirements.md` — Google Play Data Safety categories,
  Apple Privacy Nutrition Label types + ATT, GDPR, CCPA/CPRA, COPPA, and the
  AI/third-party-provider disclosure rules, with the verbatim category names.
- `references/report-template.md` — the report's required section order.

## Hard constraints

1. **Every verdict cites both sides.** A row in the alignment matrix needs code
   evidence (`path:line`) AND policy evidence (a quoted phrase, or the explicit
   token `NOT FOUND IN POLICY` after searching the full text). A verdict with
   only one side is not a finding — go get the other side.
2. **Never assess a policy you have not fully materialized.** You must have the
   complete policy text saved locally (Step 1) before writing any verdict.
   Summarized or partial text cannot support a "the policy does not mention X"
   claim, because the omission may be the summarizer's, not the policy's.
3. **This is not legal advice.** The report is a developer-facing engineering
   artifact for counsel to review. Say so in the report. Never tell the user the
   app "is compliant" — report alignment between code and policy, and which
   store/regulatory requirements appear unmet.
4. **Never edit the live policy** (`PRIVACY.md`, the hosted page, store form)
   unless the user explicitly asks. Proposed wording goes in the report, where
   the user chooses to adopt it.
5. **Never write secrets and never transmit the code or policy anywhere.** Read
   `.env*` files for provider *names and keys present*, never copy key values
   into the report — `OPENAI_API_KEY (set)` is the correct notation.
6. **Absent evidence is not absence.** If a data flow cannot be confirmed from
   this repo (server-side behavior, a vendor's own retention), mark it
   `UNVERIFIED` and list it under Limitations. Never silently drop it, and never
   promote a guess to a finding.

## Step 1 — Materialize the policy text

Ask for the privacy policy URL if not given. Then, in order:

1. **URL** — fetch the raw document and save it to
   `<report-dir>/privacy-policy-fetched.txt`, recording the URL and the
   retrieval timestamp:
   ```bash
   curl -sSL --max-time 30 -A 'Mozilla/5.0' "$POLICY_URL" \
     | sed -e 's/<script[^>]*>.*<\/script>//g' -e 's/<[^>]*>//g' \
     | sed -e 's/&nbsp;/ /g' -e 's/&amp;/\&/g' -e '/^[[:space:]]*$/d'
   ```
   If that yields little text (a JS-rendered page), retry with WebFetch asking
   for the **complete verbatim text, reproduced in full, no summarizing** — and
   note in the report that the text came through a converter.
2. **Local fallback** — if the URL fails or none was given, look for
   `PRIVACY*.md`, `docs/privacy*`, `ui/public/privacy*`, `**/privacy-policy.*`,
   `legal/*`, or a path the user names.
3. **No policy anywhere** — do not stop. Run Steps 2–3 anyway and report the
   inventory, then OFFER to draft a first-version policy skeleton from it
   (clearly labeled as a draft requiring legal review). Do not write the draft
   unless the user accepts.

Report the policy's own "last updated" date next to the app's current version.
A policy older than the features it must cover is a finding in itself.

## Step 2 — Build the data inventory

Run the full sweep in `references/data-inventory-checklist.md` for every stack
present. Do not skip a section because the app "obviously" does not do that —
the checklist exists because coverage that relies on what you notice varies
between runs; coverage that walks a fixed list does not.

Record each item as: **what data**, **captured where** (`path:line`), **sent to
whom** (first-party backend, or a named third party), **why** (the feature).

Third-party recipients are found in dependency manifests, `.env*` keys, SDK
initialization, and hardcoded hostnames. Every AI provider, analytics SDK, ad
network, crash reporter, payment processor and email sender is a recipient.

## Step 3 — Determine which requirement sets apply

| Signal in the repo | Requirement set |
|---|---|
| `pubspec.yaml`, `AndroidManifest.xml`, `build.gradle`, `Info.plist`, `.xcodeproj`, React Native | Google Play Data Safety, Apple Nutrition Labels + ATT |
| Any EU/EEA/UK users (assume yes unless the user says otherwise) | GDPR/UK GDPR |
| Any California users (assume yes unless told otherwise) | CCPA/CPRA |
| Age gate, DOB field, kids category, or ad SDK + under-13 audience | COPPA / Play Families |
| Any AI provider or third-party API in the inventory | AI subprocessor disclosure |

## Step 4 — Compare, then write the report

Follow `references/report-template.md` exactly. The report is:

1. **Verdict line** — `ALIGNED`, `GAPS FOUND`, or `BLOCKING GAPS`, with counts
   per verdict type. `BLOCKING GAPS` whenever any row is `CONTRADICTED`, or any
   store-required disclosure is missing.
2. **Scope** — app root, policy source + retrieval timestamp, policy "last
   updated" date, app version, platforms, requirement sets applied.
3. **Alignment matrix** — **one row for every inventory item from Step 2**,
   including the aligned ones. Columns: Data / Feature | Code evidence
   (`path:line`) | Policy evidence (quote or `NOT FOUND IN POLICY`) | Verdict.
   Verdicts: `COVERED`, `PARTIAL`, `CONTRADICTED`, `MISSING`, `UNVERIFIED`,
   `N/A`. A reader must be able to tell "checked, and it is fine" apart from
   "not checked" — which is what the aligned rows are for.

   **One row per data item, not per recipient.** A row is keyed to the *what
   data* field of a Step 2 inventory item; the recipients for that item are
   named inside the row and its finding. Ten vendors receiving analytics data
   is one analytics row naming ten vendors, not ten rows.

   **Verdict decision rule** — apply in this order, so the same facts produce
   the same verdicts across runs:

   | Test, in order | Verdict |
   |---|---|
   | The policy states something the code disproves — quote the statement | `CONTRADICTED` |
   | The policy describes the item but omits a material aspect (a recipient, the precision, the scope) | `PARTIAL` |
   | The policy is silent on the item | `MISSING` |
   | The policy describes the item accurately | `COVERED` |
   | The repo cannot settle it | `UNVERIFIED` |
   | The item does not exist in this app | `N/A` |

   A **blanket claim** the code disproves ("we never share", "we do not collect
   your location") is ONE `CONTRADICTED` row for that claim, naming every
   instance that breaks it. The individual undisclosed items it covers stay
   `MISSING` — they are not each a separate contradiction. Otherwise one
   sentence in the policy inflates the contradiction count by a dozen and buries
   the rows where the policy makes a specific false statement.
4. **Structural sections** — the required-clause checklist from
   `references/compliance-requirements.md` (rights, legal basis, transfers,
   retention, opt-out, contact), each `PRESENT` or `ABSENT`.
5. **Findings** — ordered `CONTRADICTED` → `MISSING` → `PARTIAL`. Each names the
   specific store rule or regulation it implicates and why it matters.
6. **Patch-ready clauses** — for every non-`COVERED` row, the actual replacement
   or addition text, in a fenced block, written in the policy's own voice and
   reading level, ready to paste. Not a description of what to write.
7. **Store form mapping** — the Play Data Safety and Apple Nutrition Label
   tables, filled from the inventory: category, collected?, shared?, linked to
   identity?, used for tracking?.
8. **Non-policy action items** — the fixes that belong in code or config rather
   than the document (a missing `NSUserTrackingUsageDescription`, a retention
   setting that contradicts the stated promise, a consent step that does not
   exist).
9. **Limitations and disclaimer** — `UNVERIFIED` rows, what this repo cannot
   show, and the not-legal-advice statement.

Write it to `<app-root>/privacy-policy-alignment-report.md` unless the user
names another path, then print the verdict line and the findings count.

## Common mistakes

| Mistake | Fix |
|---|---|
| Listing only the gaps | Aligned rows are evidence of coverage. Every inventory item gets a row. |
| "Add a section covering AI providers" | That is a TODO, not a deliverable. Write the paragraph. |
| Treating the policy document as the whole job | Store forms and Info.plist strings are separate artifacts reviewers check first. |
| "The policy doesn't mention X" from a summarized fetch | Constraint 2. Search the full saved text. |
| Declaring the app compliant | Out of scope. Report alignment and unmet requirements. |
| Naming an SDK as a recipient without checking it is wired up | A dependency in a manifest that is never initialized is `UNVERIFIED`, not a finding. |
