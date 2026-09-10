# Data inventory checklist

Walk every section. A section that does not apply is recorded as `N/A` — it is
not skipped silently. Coverage that depends on what you happen to notice varies
between runs; coverage that walks a fixed list does not.

For each hit record: **what data** · **captured where** (`path:line`) · **sent
to whom** · **why (feature)**.

---

## 1. Declared permissions and purpose strings

| Where | Look for |
|---|---|
| `android/app/src/main/AndroidManifest.xml` | every `<uses-permission>`; `<queries>`; `com.google.android.gms.permission.AD_ID` |
| `ios/**/Info.plist` | every `NS*UsageDescription`; `UIBackgroundModes`; `GADApplicationIdentifier` |
| `ios/**/*.entitlements` | HealthKit, HomeKit, iCloud, push |
| Flutter | permissions are declared in the platform files above, not `pubspec.yaml` |
| Web | `navigator.geolocation`, `getUserMedia`, `Notification.requestPermission`, `navigator.contacts` |

**Cross-check both directions.** A permission with no code using it is dead
weight to remove (and still triggers store review questions). Code that needs a
permission absent from the manifest is a crash. A purpose string that describes
a *different* purpose than the policy states is a contradiction to report.

## 2. Third-party SDKs and services

Read the dependency manifest for the stack — `pubspec.yaml`, `package.json`,
`build.gradle(.kts)`, `Podfile`/`Package.swift`, `pyproject.toml`,
`requirements.txt` — and classify every entry that leaves the device:

| Class | Examples of what to look for |
|---|---|
| Analytics | firebase_analytics, amplitude, mixpanel, segment, posthog, matomo |
| Crash / APM | crashlytics, sentry, bugsnag, datadog, new_relic |
| Advertising | google_mobile_ads, admob, applovin, unity_ads, facebook_audience_network, IDFA/AAID use |
| Attribution | appsflyer, adjust, branch, singular |
| Push | firebase_messaging, onesignal, apns tokens |
| Payments | stripe, revenuecat, purchases_flutter, in_app_purchase, braintree, paddle |
| Auth / social | firebase_auth, auth0, google_sign_in, sign_in_with_apple, facebook_login |
| Storage / backend | supabase, firebase, aws-sdk, appwrite |
| Email / SMS | sendgrid, mailgun, twilio, postmark, ses |
| Support / session replay | intercom, zendesk, fullstory, hotjar, logrocket, smartlook |
| AI / ML | see section 3 |

Each of these is a **recipient of user data** and belongs in the policy's
processor/sharing disclosure. A dependency present but never initialized is
`UNVERIFIED`, not a finding — check for the init call before naming it.

## 3. AI and model providers

The disclosure most often missing. Search dependency manifests, `.env*`
(names only, never values), config files, and hardcoded hostnames for:

- **Model APIs** — `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`/
  Gemini, `GROQ_`, `MISTRAL_`, `COHERE_`, `TOGETHER_`, `HUGGINGFACE_`,
  `AWS_BEDROCK`, `AZURE_OPENAI_`, `OPENROUTER_`, `api.openai.com`,
  `api.anthropic.com`
- **Speech** — Whisper, Deepgram, AssemblyAI, ElevenLabs, `ELEVENLABS_API_KEY`,
  Google STT/TTS, Azure Speech
- **Vision / image** — Replicate, Stability, Clarifai, Vision API
- **Vector stores / RAG** — Pinecone, Weaviate, Qdrant, Chroma, pgvector,
  Milvus. A vector index is a **persistent copy of user content** living outside
  the primary database, and account-deletion paths usually miss it.
- **Frameworks** — langchain, llama_index, semantic-kernel, vercel `ai`

For each provider record:

1. **What user content reaches it** — trace the payload. Follow the object, not
   the endpoint name: a `profile` or `context` field frequently carries email,
   date of birth, location or history the caller did not think about.
2. **How much history** — a `history_window_days`, a conversation buffer or a
   RAG retrieval means far more than the current input is transmitted.
3. **Inference performed** — health, mood, biometric, financial or demographic
   inference is often *special-category* data (GDPR Art. 9) even when the raw
   input was not, and needs an explicit legal basis.
4. **Retention and training** — whether the provider's terms allow training on
   the data, and the configured retention. Note the plan/endpoint if visible;
   otherwise `UNVERIFIED`.

**GenericSuite apps:** `ai_langchain_models.py` / `ai_embeddings.py` enumerate
configured providers; `ai_gpt_fn_index.py` lists the tools an assistant may
call, and each tool's data reach counts. Check `.env.example` for which
providers are actually wired.

## 4. First-party collection

- **Account fields** — signup/profile forms, user model/schema, ORM models.
  GenericSuite: `config_dbdef` frontend/backend JSON define collected fields.
- **User-generated content** — text, photos, video, audio, documents, location
  tags attached to records.
- **Device and network** — device model, OS, app version, IP, locale, timezone,
  advertising ID, install ID, fingerprinting.
- **Behavioral** — screen views, feature usage, session length, search terms.
- **Inferred** — scores, segments, recommendations, risk/mood/health signals.
- **Sensitive by category** — health, biometrics, precise location, financial,
  government ID, race/ethnicity, religion, sexual orientation, union
  membership, immigration status, children's data.

## 5. Identity linkage

Decide, per item, whether it is tied to a person — this drives Apple's "Linked
to You" and Play's identifiability answers, and it is routinely understated.

Look for: a stable user ID set on an analytics SDK (`setUserId`), an email or
phone set as a user property, an ID in request headers, a device ID persisted
across installs, or a first-party ID joined to an ad ID.

A policy describing analytics as anonymous or aggregate while the code calls
`setUserId` / `setUserProperties({email})` is `CONTRADICTED`.

## 6. Data leaving the device — network surfaces

Grep for `http://`, `https://`, `fetch(`, `axios`, `dio`, `URLSession`,
`OkHttp`, `requests.`, websockets. For each destination that is not the app's
own backend, identify the company. For the app's own backend, identify what it
then forwards (the backend's own `.env` and SDKs are part of this inventory).

## 7. Retention, deletion and consent

- Retention settings in config/env (`*_RETENTION_*`, TTL indexes, lifecycle
  rules) — compare against the policy's stated retention promise.
- Account deletion path: does it reach analytics, the vector store, backups,
  and the AI providers' logs? Stores require an in-app deletion route and a
  web-accessible deletion request.
- Consent mechanics: is there any consent gate before collection begins, a
  cookie/tracking banner, an ATT prompt, per-SDK opt-out, or a "do not sell or
  share" control? Collection that starts at first launch with no gate is a
  finding even when disclosed.
- Children: age gate, DOB, kids category, ad SDKs in an app plausibly used by
  under-13s.
