# 💰 Unclaimed Funds Monitor

Automatically searches state unclaimed property databases on the 1st of every month and emails results directly to you — nothing is stored publicly anywhere.

## How it works

1. GitHub Actions fires on the 1st of every month at 9am CT
2. Playwright (headless Chrome) searches each configured state's official unclaimed property site for every person in your `SEARCH_PEOPLE` secret
3. Results are sent by email via SendGrid — full details inline, with direct links to claim
4. Nothing is committed back to the repo. Results exist only in the email.

## Privacy model

| What | Where | Public? |
|------|-------|---------|
| Names to search | GitHub secret (`SEARCH_PEOPLE`) | ✗ Never |
| Notification email | GitHub secret (`NOTIFICATION_EMAIL`) | ✗ Never |
| Search results | Emailed, then discarded | ✗ Never |
| Repo contents | `config.json` (states only), source code | ✓ Yes, but contains no personal data |

## Setup

### 1. Fork this repo

### 2. Add GitHub secrets
Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

**`SEARCH_PEOPLE`** — JSON array of people to search:
```json
[
  {"first_name": "Jane", "last_name": "Smith"},
  {"first_name": "John", "last_name": "Smith"}
]
```

**`NOTIFICATION_EMAIL`** — where to send results:
```
you@example.com
```

**`SENDGRID_API_KEY`** — free at [sendgrid.com](https://sendgrid.com) (100 emails/day free forever):
1. Sign up → Settings → API Keys → Create API Key
2. Permission: "Mail Send" only
3. Copy the key and save it as this secret

### 3. Run it
Actions → Check Unclaimed Funds → Run workflow

## Customizing

### Add / remove states
Edit the `states` array in `config.json`:
```json
{ "states": ["TN", "IA", "TX"] }
```

Available states:

| Code | State | Official site |
|------|-------|---------------|
| `TN` | Tennessee | unclaimedproperty.tn.gov |
| `IA` | Iowa | unclaimedproperty.iowa.gov |
| `TX` | Texas | claimittexas.gov |
| `FL` | Florida | fltreasurehunt.gov |
| `CA` | California | claimit.ca.gov |

To add a state not listed, add an entry to the `STATES` dict in `src/scraper.py`. Most states use the same SWS platform — just swap in the correct base URL.

### Change the schedule
Edit the `cron` line in `.github/workflows/check.yml`:
```
0 15 1 * *    ← 1st of every month at 9am CT (default)
0 15 * * 1    ← every Monday
0 15 1 */3 *  ← every 3 months
```

## Notes

- Searching is 100% free — these are official government databases
- Never pay a third-party "finder fee" to claim funds you locate here
- The scraper uses a real headless Chromium browser to handle Cloudflare protections naturally
