# Compliance requirements reference

Category names below are reproduced from the primary sources so the report's
store-form mapping uses the vocabulary the forms actually present.

Sources: Google Play Data safety form (support.google.com/googleplay/
android-developer/answer/10787469), Apple App Privacy Details
(developer.apple.com/app-store/app-privacy-details/). Verify against the live
pages when a submission is imminent — both change.

---

## 1. Google Play — Data safety form

Declared per data type: **collected?**, **shared?**, **required or optional?**,
**purposes**, **ephemeral or persisted?**

> "Collect" = transmitted off the device, **including via third-party libraries
> and SDKs**. "Share" = transferred to a third party, server-to-server or
> on-device to another app.

The SDK clause is what catches most apps: an analytics or ad SDK sending data
from the device is *your* collection, and onward transfer to that vendor is
*sharing* — regardless of whether your own servers ever see it.

| Category | Types |
|---|---|
| Location | Approximate location · Precise location |
| Personal info | Name · Email address · User IDs · Address · Phone number · Race and ethnicity · Political or religious beliefs · Sexual orientation · Other info |
| Financial info | User payment info · Purchase history · Credit score · Other financial info |
| Health and fitness | Health info · Fitness info |
| Messages | Emails · SMS or MMS · Other in-app messages |
| Photos and videos | Photos · Videos |
| Audio files | Voice or sound recordings · Music files · Other audio files |
| Files and docs | Files and docs |
| Calendar | Calendar events |
| Contacts | Contacts |
| App activity | App interactions · In-app search history · Installed apps · Other user-generated content · Other actions |
| Web browsing | Web browsing history |
| App info and performance | Crash logs · Diagnostics · Other app performance data |
| Device or other IDs | Device or other IDs |

Also declared: encryption in transit, and whether users can request data
deletion.

**Play policy requirements beyond the form**
- A privacy policy link in the store listing **and** in the app, at a URL that
  is publicly reachable, non-expiring, and not gated by a login.
- The form must match both the policy and actual app behavior — mismatch is its
  own violation, independent of the underlying data practice.
- Contacts/SMS/call-log/location have their own restricted-permission rules;
  uploading an address book requires prominent disclosure and consent.
- Families policy: apps targeting children have SDK restrictions and cannot use
  ad IDs for personalized advertising.

## 2. Apple — Privacy Nutrition Labels + ATT

| Category | Types |
|---|---|
| Contact Info | Name · Email Address · Phone Number · Physical Address · Other User Contact Info |
| Health & Fitness | Health · Fitness |
| Financial Info | Payment Info · Credit Info · Other Financial Info |
| Location | Precise Location · Coarse Location |
| Sensitive Info | racial/ethnic data, sexual orientation, pregnancy, disability, religious beliefs, etc. |
| Contacts | Contacts |
| User Content | Emails or Text Messages · Photos or Videos · Audio Data · Gameplay Content · Customer Support · Other User Content |
| Browsing History | Browsing History · Search History |
| Identifiers | User ID · Device ID |
| Purchases | Purchase History |
| Usage Data | Product Interaction · Advertising Data · Other Usage Data |
| Diagnostics | Crash Data · Performance Data · Other Diagnostic Data |
| Surroundings | Environment Scanning |
| Body | Hands · Head |
| Other Data | Other Data Types |

Each type is classified as **Used to Track You**, **Linked to You**, or **Not
Linked to You**, plus purposes: Third-Party Advertising · Developer's
Advertising or Marketing · Analytics · Product Personalization · App
Functionality · Other Purposes.

**Tracking**, per Apple:

> linking data collected from your app about a particular end-user or device,
> such as a user ID, device ID, or profile, with Third-Party Data for targeted
> advertising or advertising measurement purposes, or sharing data collected
> from your app about a particular end-user or device with a data broker.

Not tracking: linkage that stays on-device; a data broker using the data solely
for fraud/security detection or consumer-reporting creditworthiness.

**ATT.** If the app tracks by that definition, it must call
`ATTrackingManager.requestTrackingAuthorization` and ship
`NSUserTrackingUsageDescription` in `Info.plist`. An ad/attribution SDK present
with no ATT prompt and no usage-description string is a rejection risk on its
own, separate from the policy document. Also required: an in-app account
deletion path for any app offering account creation.

## 3. GDPR / UK GDPR

Required in the policy (Arts. 13–14):

| Clause | Present? |
|---|---|
| Controller identity and contact details | |
| DPO / EU representative where applicable | |
| Purposes **and legal basis per purpose** (Art. 6) — consent, contract, legitimate interests (with the balancing test named) | |
| Categories of data | |
| Recipients / categories of recipients — **naming processors** (each AI provider, analytics, ad and hosting vendor) | |
| International transfers + safeguard used (SCCs, adequacy) — most US AI providers are a transfer | |
| Retention period per category, or the criteria used | |
| Rights: access, rectification, erasure, restriction, portability, objection, withdraw consent | |
| Right to lodge a complaint with a supervisory authority | |
| Automated decision-making / profiling, with meaningful logic (Art. 22) | |
| Whether provision is required and consequences of refusal | |

**Art. 9 special categories** — health, biometric, sexual orientation, religion,
political opinion, ethnicity, union membership — need an Art. 9 condition in
addition to an Art. 6 basis, usually explicit consent. An AI feature *inferring*
mood, mental state or health from ordinary text produces Art. 9 data even though
the input was ordinary text.

## 4. CCPA / CPRA (California)

| Clause | Present? |
|---|---|
| Categories of personal information collected, sources, business purposes | |
| Categories disclosed for a business purpose, and to whom | |
| Whether PI is **sold or shared** — "shared" covers cross-context behavioral advertising, which most ad-SDK setups are, with no money changing hands | |
| "Do Not Sell or Share My Personal Information" link/control, and Global Privacy Control honoring | |
| Sensitive PI: categories collected and a limit-use control | |
| Rights: know, delete, correct, opt out, non-discrimination; how to exercise them and the verification method | |
| Retention period per category | |
| Notice at collection, at or before the point of collection | |

## 5. COPPA / children

Triggered by an app directed to children under 13, or actual knowledge of
under-13 users. A DOB field or age gate in the code is evidence the age is
known. Requires verifiable parental consent before collection, no behavioral
advertising, and data minimization. Google Play Families and Apple Kids Category
add their own SDK restrictions. A policy disclaiming under-13 users while the
app ships ad SDKs, precise location and contact upload is a gap worth flagging
even when the disclaimer is technically accurate.

## 6. AI and third-party provider disclosure

No single statute names this section, but store review, GDPR processor
disclosure and CCPA sharing rules together require it. A policy that predates
the app's AI features is the single most common gap. Cover:

1. **That AI processing happens at all**, and on which user content.
2. **Named providers**, not "trusted third parties" — GDPR expects processors
   identifiable, and generic phrasing fails a Data Safety review that lists
   specific recipients.
3. **What is transmitted** — including history windows and profile fields the
   payload carries beyond the obvious input.
4. **Training** — whether the provider may train on the data. If the answer is
   no because of the plan or endpoint used, say so; users read silence as yes.
5. **Retention at the provider**, including vector-store copies, and how account
   deletion propagates to them.
6. **Inference disclosure** — what the model concludes about the user, and Art.
   22 information if any decision is automated.
7. **Human review**, if provider staff or contractors may see content.
8. **Region of processing**, for the transfer clause.
