# FastAPITemplate

![FastAPITemplate Banner](./assets/fastapitemplate_banner_01.png)

**FastAPITemplate** is a full-stack application that allows you to have a template to start your FastAPI application based on GenericSuite.

You can view the [Source Code here](https://github.com/tomkat-cr/genericsuite-basecamp/tree/main/docs/code/fastapitemplate).


![FastAPITemplate Logo](./ui/src/_images/app_logo_horizontal.svg)
![FastAPITemplate Bots Logo](./ui/src/_images/hack_team_logo_horizontal.svg)

## Directory Structure

```
fastapitemplate/
├── config_dbdef/                 # Configuration database definitions
├── server/                       # Server application
├── ui/                           # User interface
└── mcp-server/                   # MCP server
```

## Installation

```bash
git clone https://github.com/tomkat-cr/genericsuite-basecamp.git
cd genericsuite-basecamp/docs/code/fastapitemplate
```

## Configuration

Run the following command to copy the example environment files to the appropriate locations:

```bash
make init-app-environment
```

Or manually copy:

```bash
cp server/.env.example server/.env
cp ui/.env.example ui/.env
```

## Running the application without Docker

```bash
# With a remote MongoDB database
make dev
```

## Running the application with Docker

Start the application and its docker containers:

```bash
# With a local database database
make run

# With a remote MongoDB database
APP_STAGE=qa make run
```

Terminate the application and its docker containers:

```bash
make down
```

Soft restart (only docker compose restart):

```bash
make restart
```

Hard restart (down and up):

```bash
make hard-restart
```

Run the local database only:

```bash
make run-db-only
```

## Starting a New Project from This Template

### Prerequisites

- Git
- Node.js 18+, npm 8+
- Python 3.12+, `uv`
- Docker (or Podman)

### Step 1 — Copy the template directory

**Option A — automated (recommended):**

Run the helper script from the basecamp repo and follow the instructions:

```bash
curl -fsSL https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/main/scripts/new-project-from-template.sh | bash
```

Then skip to Step 4.

If you have the basecamp repo cloned locally, you can use the helper script from the basecamp repo root. It clones the repo, copies the template, initialises a git repo, and optionally renames the app — all in one step:

```bash
# Clone the basecamp repo
git clone https://github.com/tomkat-cr/genericsuite-basecamp.git
cd genericsuite-basecamp

# Copy + rename in one step (skips Step 2 and 3 below)
bash scripts/new-project-from-template.sh ~/projects/myapp myapp
bash scripts/new-project-from-template.sh ~/projects/myapp myapp myapp.com

# Copy only
bash scripts/new-project-from-template.sh ~/projects/myapp
```

Then:

```bash
cd ~/projects/myapp
```

**Option B — manual:**

```bash
git clone --depth 1 https://github.com/tomkat-cr/genericsuite-basecamp.git _tmp
cp -r _tmp/docs/code/fastapitemplate ~/projects/myapp
cp -r _tmp/scripts/rename-app.sh ~/projects/myapp/scripts/rename-app.sh
rm -rf _tmp
cd ~/projects/myapp
```

### Step 2 — Initialize a new Git repository

> Skip if you used **Option A** above — the script already did this.

```bash
rm -rf .git
git init
git add .
git commit -m "Initial commit from fastapitemplate"
```

### Step 3 — Rename the app

> Skip if you used **Step 1 Option A** with a `<new-app-name>` argument.

**Option A — automated (recommended):**

```bash
bash scripts/rename-app.sh <new-app-name> [<new-domain>]

# Examples:
bash scripts/rename-app.sh myapp
bash scripts/rename-app.sh myapp myapp.com
```

The script processes all `*.json`, `*.toml`, `*.yml`, `*.yaml`, `*.md`, `*.sh`, `*.conf`, `*.example`, `*.txt` and `*.cfg` files, skipping `.git/`, `node_modules/`, `dist/`, `build/`, and Python cache directories. It handles macOS and Linux `sed` differences automatically.

**Option B — manual:**

Replace every occurrence of `fastapitemplate` (and `fastapitemplate.com`) with your app name across these key files:

| File | Fields to update |
|---|---|
| `package.json` | `"name"` |
| `server/pyproject.toml` | `description` |
| `server/.env.example` | `APP_NAME`, `APP_DOMAIN_NAME`, CORS origins, AWS resource names |
| `ui/.env.example` | `REACT_APP_APP_NAME`, `APP_LOCAL_DOMAIN_NAME`, API URLs, `REACT_APP_URI_PREFIX` |
| `deploy/docker-compose.yml.example` | Container names, image names |

### Step 4 — Configure environment files

```bash
make init-app-environment
```

Then open each generated `.env` file and fill in your secrets:

```bash
# Required in server/.env
APP_SECRET_KEY=<random strong string>
APP_SUPERADMIN_EMAIL=<your email>
APP_DB_ENGINE_QA=<your db engine: MONGODB, DYNAMODB, POSTGRES, SUPABASE, MYSQL>
APP_DB_NAME_QA=<your db name>
APP_DB_URI_QA=<your MongoDB / Postgres / etc. URI>
OPENAI_API_KEY=<your key>      # only if using AI features with OpenAI
```

### Step 5 — Install dependencies

```bash
make install-all
```

### Step 6 — Run the application

```bash
# Without Docker (remote database, QA stage)
make dev

# With Docker (local containerized database, DEV stage)
make run
```

### Step 7 — Push to your new repository

```bash
git remote add origin https://github.com/<your-org>/<your-repo>.git
git push -u origin main
```
