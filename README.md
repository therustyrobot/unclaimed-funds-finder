<img width="1376" height="768" alt="Unclaimed_Funds_Finder_title_202605092114" src="https://github.com/user-attachments/assets/dc890090-2ba2-4c49-b227-944d0e3bbe9b" />

# 💰 Unclaimed Funds Finder

> **Billions of dollars in unclaimed property are sitting in state government vaults right now — and some of it may have your name on it.**

Unclaimed property is money or assets that have been turned over to the state after a period of inactivity. This includes forgotten bank accounts, uncashed paychecks, security deposits, insurance payouts, stock dividends, safe deposit box contents, and more. States are legally required to hold this money indefinitely until the rightful owner (or their heirs) comes forward to claim it — for free.

This tool automatically searches official state unclaimed property databases on the **1st of every month** and emails results directly to you — nothing is stored publicly anywhere.

## ⚙️ How it works

1. GitHub Actions fires on the 1st of every month at 9am CT
2. Playwright (headless Chrome) searches each configured state's official unclaimed property site for every person in your `SEARCH_PEOPLE` secret
3. Results are sent by email via SendGrid — full details inline, with direct links to claim
4. Nothing is committed back to the repo. Results exist only in the email.

## 🔒 Privacy model

| What | Where | Public? |
|------|-------|---------|
| Names to search | GitHub secret (`SEARCH_PEOPLE`) | ✗ Never |
| Notification email | GitHub secret (`NOTIFICATION_EMAIL`) | ✗ Never |
| Search results | Emailed, then discarded | ✗ Never |
| Repo contents | `config.json` (states only), source code | ✓ Yes, but contains no personal data |

## 🚀 Setup

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

## 🛠️ Customizing

### Add / remove states
Edit the `states` array in `config.json`:
```json
{ "states": ["TN", "IA", "TX"] }
```

> **Which states should I include?** Add every state where you (or anyone you're searching for) has ever **lived, worked, owned a business, or attended school** — property can be reported to any of those states. Don't forget states from decades ago; unclaimed funds have no expiration date.

Available states:

| Code | State | Official site |
|------|-------|---------------|
| `AL` | Alabama | treasury.alabama.gov/unclaimed-property |
| `AK` | Alaska | treasury.dor.alaska.gov/Unclaimed-Property.aspx |
| `AZ` | Arizona | azdor.gov/unclaimed-property |
| `AR` | Arkansas | claimit.ar.gov |
| `CA` | California | claimit.ca.gov |
| `CO` | Colorado | colorado.findyourunclaimedproperty.com |
| `CT` | Connecticut | ctbiglist.com |
| `DE` | Delaware | unclaimedproperty.delaware.gov |
| `FL` | Florida | fltreasurehunt.gov |
| `GA` | Georgia | dor.georgia.gov/unclaimed-property-program |
| `HI` | Hawaii | unclaimedproperty.ehawaii.gov |
| `ID` | Idaho | yourmoney.idaho.gov |
| `IL` | Illinois | icash.illinoistreasurer.gov |
| `IN` | Indiana | indianaunclaimed.gov |
| `IA` | Iowa | unclaimedproperty.iowa.gov |
| `KS` | Kansas | kansascash.ks.gov |
| `KY` | Kentucky | treasury.ky.gov/unclaimedproperty |
| `LA` | Louisiana | treasury.la.gov/unclaimed-property |
| `ME` | Maine | maineunclaimedproperty.gov |
| `MD` | Maryland | marylandtaxes.gov/unclaimed-property |
| `MA` | Massachusetts | findmassmoney.com |
| `MI` | Michigan | unclaimedproperty.michigan.gov |
| `MN` | Minnesota | mn.gov/commerce/consumers/your-money/find-missing-money |
| `MS` | Mississippi | treasury.ms.gov/unclaimed-money |
| `MO` | Missouri | treasurer.mo.gov/unclaimedproperty |
| `MT` | Montana | mtreasure.mt.gov |
| `NE` | Nebraska | treasurer.nebraska.gov/up |
| `NV` | Nevada | claimitnv.gov |
| `NH` | New Hampshire | nh.gov/treasury/unclaimed-property |
| `NJ` | New Jersey | unclaimedfunds.nj.gov |
| `NM` | New Mexico | tax.newmexico.gov/businesses/unclaimed-property |
| `NY` | New York | osc.ny.gov/unclaimed-funds |
| `NC` | North Carolina | nccash.com |
| `ND` | North Dakota | land.nd.gov/unclaimed-property |
| `OH` | Ohio | com.ohio.gov/unfd |
| `OK` | Oklahoma | oktreasure.com/unclaimed-property |
| `OR` | Oregon | unclaimed.oregon.gov |
| `PA` | Pennsylvania | patreasury.gov/unclaimed-property |
| `RI` | Rhode Island | findrimoney.com |
| `SC` | South Carolina | treasurer.sc.gov/our-office/programs/unclaimed-property-program |
| `SD` | South Dakota | southdakota.findyourunclaimedproperty.com |
| `TN` | Tennessee | unclaimedproperty.tn.gov |
| `TX` | Texas | claimittexas.gov |
| `UT` | Utah | mycash.utah.gov |
| `VT` | Vermont | vermontunclaimedproperty.gov |
| `VA` | Virginia | vamoneysearch.gov |
| `WA` | Washington | ucp.dor.wa.gov |
| `WV` | West Virginia | wvtreasury.com/Unclaimed-Property |
| `WI` | Wisconsin | statetreasury.wi.gov/ucp |
| `WY` | Wyoming | wyuincash.wyo.gov |

To add a state not listed, add an entry to the `STATES` dict in `src/scraper.py`. Most states use the same SWS platform — just swap in the correct base URL.

### Change the schedule
Edit the `cron` line in `.github/workflows/check.yml`:
```
0 15 1 * *    ← 1st of every month at 9am CT (default)
0 15 * * 1    ← every Monday
0 15 1 */3 *  ← every 3 months
```

## 📋 Notes

- Searching is 100% free — these are official government databases
- Never pay a third-party "finder fee" to claim funds you locate here
- The scraper uses a real headless Chromium browser to handle Cloudflare protections naturally

## ⚠️ Please be responsible

Use a sensible search interval. The default (1st of every month) is intentionally conservative. If many people run this tool aggressively — hourly, daily, or across dozens of states simultaneously — state databases may rate-limit or block automated traffic, breaking access for everyone. Once a month is more than enough for unclaimed property that often sits for years. Be a good citizen of these public resources.
