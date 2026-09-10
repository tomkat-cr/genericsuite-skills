# Report template

Emit these sections, in this order. Keep the headings. Drop a section only when
its requirement set does not apply (Step 3), and say so in one line rather than
omitting the heading silently.

---

# Privacy policy alignment report — <app name>

**Verdict: BLOCKING GAPS** — 3 contradicted · 5 missing · 2 partial · 6 covered · 1 unverified

> `ALIGNED` only when no row is `CONTRADICTED` or `MISSING` and every structural
> clause required by an applicable requirement set is `PRESENT`.
> `BLOCKING GAPS` whenever any row is `CONTRADICTED`, or a store-required
> disclosure is absent. Otherwise `GAPS FOUND`.

## Scope

| | |
|---|---|
| App root | `/path/to/app` |
| App version | 2.3.1+41 (`pubspec.yaml:5`) |
| Policy source | `https://…/privacy` — retrieved 2026-09-07 14:22 UTC → `privacy-policy-fetched.txt` |
| Policy last updated | March 2, 2021 — **4 major versions behind** |
| Platforms | iOS, Android (Flutter) |
| Requirement sets applied | Play Data Safety · Apple Nutrition Labels + ATT · GDPR · CCPA/CPRA · AI disclosure |

## Alignment matrix

One row per inventory item — including covered ones, so "checked and fine" is
distinguishable from "not checked".

| # | Data / Feature | Code evidence | Policy evidence | Verdict |
|---|---|---|---|---|
| 1 | Precise location on every entry | `lib/services/telemetry.dart:17-27` | "We do not collect your location." (§Information we collect) | `CONTRADICTED` |
| 2 | Journal text → OpenAI, Anthropic | `server/.env.example:6-7`, `lib/services/ai_service.dart:21-34` | `NOT FOUND IN POLICY` | `MISSING` |
| 3 | Email address at signup | `lib/models/user.dart:12` | "we collect your email address" (§Information we collect) | `COVERED` |
| 4 | Provider-side retention | — | "removed … within 30 days" (§Data retention) | `UNVERIFIED` |

## Structural clauses

| Requirement set | Clause | Status |
|---|---|---|
| GDPR | Legal basis per purpose (Art. 6) | `ABSENT` |
| GDPR | Named processors | `ABSENT` |
| CCPA | "Do Not Sell or Share" control | `ABSENT` |
| Both | Contact for privacy requests | `PRESENT` — §Contact |

## Findings

Ordered `CONTRADICTED` → `MISSING` → `PARTIAL`. Each finding states the rule it
implicates and the consequence — not just the mismatch.

### F1 · Policy denies location collection that the code performs — `CONTRADICTED`

**Code:** `lib/services/telemetry.dart:17-27` attaches `LocationAccuracy.best`
lat/lng to every `entry_created` event, sent to Firebase Analytics and
Amplitude. `ACCESS_FINE_LOCATION` at `AndroidManifest.xml:3`.

**Policy:** "We do not collect your location."

**Why it matters:** Play Data Safety requires *Precise location* declared as
collected and shared; Apple requires *Precise Location*, Linked to You. An
affirmative denial of a practice the binary performs is materially misleading,
not merely an omission — it is the highest-risk class of gap here. The iOS
purpose string ("tags entries with where you wrote them") already contradicts
the policy, so the two user-facing texts disagree with each other.

## Patch-ready clauses

Actual text, in the policy's voice, ready to paste. One block per non-`COVERED`
row, keyed to the finding.

### F1 — replace the sentence "We do not collect your location."

```markdown
**Location.** When you create an entry, MindJournal records your precise
location (GPS coordinates) and attaches it to that entry so you can see where
you were when you wrote it. These coordinates are also included in the usage
analytics we send to Firebase Analytics and Amplitude. You can turn location
off for MindJournal in your device settings at any time; entries you create
afterwards will have no location attached, and entries already saved keep the
location recorded at the time.
```

### F2 — add after "Sharing"

```markdown
**AI processing.** To transcribe voice entries, analyse mood and generate your
weekly reflections, we send the content of your entries — and, for weekly
summaries, up to 90 days of your entry history together with your email
address, date of birth and city — to the following providers, who process it on
our behalf:

| Provider | What it receives | Purpose | Location |
|---|---|---|---|
| OpenAI | Voice recordings, entry text | Transcription, mood analysis | United States |
| Anthropic | Entry text and history | Weekly summaries | United States |
| ElevenLabs | Reflection text | Voice playback | United States |
| Pinecone | Entry text and embeddings | Search over past entries | United States |

These providers process your data under contract and are not permitted to use
it to train their models. Because they operate in the United States, this
involves transferring your data outside the UK and EEA; we rely on Standard
Contractual Clauses for these transfers.
```

> Bracket anything you could not verify — `[CONFIRM: retention window]` — rather
> than asserting it. Wording the developer must check is safe; wording that
> quietly invents a commitment is not.

## Store form mapping

### Google Play — Data safety

| Category → Type | Collected | Shared | Purpose | Evidence |
|---|---|---|---|---|
| Location → Precise location | Yes | Yes (Firebase, Amplitude) | Analytics, App functionality | `telemetry.dart:17-27` |
| Audio files → Voice or sound recordings | Yes | Yes (OpenAI) | App functionality | `ai_service.dart:11-18` |
| Contacts → Contacts | Yes | Yes (backend, Amplitude event) | App functionality | `telemetry.dart:31-43` |

### Apple — Privacy Nutrition Label

| Type | Linked to You | Used to Track You | Purpose | Evidence |
|---|---|---|---|---|
| Precise Location | Yes | No | Analytics, App Functionality | `telemetry.dart:17-27` |
| Audio Data | Yes | No | App Functionality | `ai_service.dart:11-18` |
| Advertising Data | Yes | **Yes** | Third-Party Advertising | `pubspec.yaml:21`, `AndroidManifest.xml:9` |

## Non-policy action items

Fixes that belong in code or configuration, not in the document.

| # | Action | Where | Why |
|---|---|---|---|
| A1 | Add `NSUserTrackingUsageDescription` and call the ATT prompt | `ios/Runner/Info.plist` | AdMob + AD_ID meets Apple's tracking definition; missing ATT is a rejection risk on its own |
| A2 | Reconcile `ENTRY_RETENTION_DAYS=0` with the 30-day deletion promise | `server/.env.example:21` | Either the config or the policy is wrong; today the code contradicts the commitment |
| A3 | Propagate account deletion to the Pinecone index | backend deletion path | Vector copies survive primary-database deletion |

## Limitations and disclaimer

- `UNVERIFIED` rows and why: server-side behavior, vendor retention, and the
  encryption claim cannot be confirmed from this repository.
- Static analysis only — runtime behavior, remote config and feature flags may
  differ from what the code suggests.
- Policy text as retrieved at the timestamp above; a later edit changes the
  result.

**This report is an engineering artifact, not legal advice.** It compares
observable code behavior against policy text and against publicly documented
store and regulatory requirements. Have qualified counsel review both the
findings and any adopted wording before publishing.
