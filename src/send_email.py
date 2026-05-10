"""
send_email.py — sends the full search results as an email via SendGrid.
Reads results from /tmp/ufm_results.json (written by scraper.py, never committed).
No report page — email is the only output.

Required GitHub secrets:
  SENDGRID_API_KEY   — from sendgrid.com (free, 100 emails/day)
  NOTIFICATION_EMAIL — recipient address
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

RESULTS_PATH = Path("/tmp/ufm_results.json")


def fmt_currency(val):
    try:    return f"${float(val):,.2f}"
    except: return str(val) if val else ""


def extract_fields(prop):
    name   = (prop.get("ownerName") or
               f"{prop.get('firstName','')} {prop.get('lastName','')}".strip() or
               prop.get("name", "—"))
    amount = (prop.get("reportedAmount") or prop.get("amount") or
               prop.get("cashReportedValue") or prop.get("value"))
    holder = prop.get("holderName") or prop.get("holder") or prop.get("reportingOrganizationName") or "—"
    ptype  = prop.get("propertyTypeName") or prop.get("propertyType") or prop.get("type") or "—"
    city   = prop.get("ownerCity") or prop.get("city") or ""
    state  = prop.get("ownerState") or prop.get("state") or ""
    loc    = ", ".join(filter(None, [city, state])) or ""
    return {"name": name, "amount": fmt_currency(amount) if amount else "",
            "holder": holder, "type": ptype, "location": loc}


def build_html(results, total_hits, hits):
    generated = results.get("generated_at", "")
    try:
        dt       = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        date_str = dt.strftime("%B %d, %Y")
    except Exception:
        date_str = generated

    hdr_color = "#f59e0b" if total_hits else "#10b981"
    hero      = f"{total_hits} match{'es' if total_hits!=1 else ''} found" if total_hits else "No matches this month"
    hero_sub  = ("Review the results below and click through to file your claim — it's free."
                 if total_hits else "All searches came back clean. We'll check again next month.")

    rows = ""
    for h in hits:
        p     = h["person"]
        pname = f"{p.get('first_name','')} {p['last_name']}".strip()
        rows += f"""
        <tr><td colspan="5" style="padding:16px 24px 8px;font-weight:600;font-size:15px;
          border-top:1px solid #e5e7eb;color:#111827;">
          {pname} — {h['state_name']}
          <span style="font-weight:400;font-size:12px;color:#6b7280;margin-left:8px;">
            {h['count']} match{'es' if h['count']!=1 else ''}
          </span></td></tr>
        <tr style="background:#f9fafb;">
          <th style="padding:6px 24px;text-align:left;font-size:11px;color:#6b7280;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Name on Record</th>
          <th style="padding:6px 16px;text-align:left;font-size:11px;color:#6b7280;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Holder</th>
          <th style="padding:6px 16px;text-align:left;font-size:11px;color:#6b7280;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Type</th>
          <th style="padding:6px 16px;text-align:left;font-size:11px;color:#6b7280;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Location</th>
          <th style="padding:6px 24px;text-align:right;font-size:11px;color:#6b7280;font-weight:500;text-transform:uppercase;letter-spacing:.05em;">Amount</th>
        </tr>"""
        for prop in h["results"]:
            f = extract_fields(prop)
            rows += f"""<tr>
          <td style="padding:10px 24px;font-size:13px;color:#111827;border-bottom:1px solid #f3f4f6;">{f['name']}</td>
          <td style="padding:10px 16px;font-size:13px;color:#374151;border-bottom:1px solid #f3f4f6;">{f['holder']}</td>
          <td style="padding:10px 16px;font-size:13px;color:#374151;border-bottom:1px solid #f3f4f6;">{f['type']}</td>
          <td style="padding:10px 16px;font-size:13px;color:#374151;border-bottom:1px solid #f3f4f6;">{f['location']}</td>
          <td style="padding:10px 24px;font-size:13px;color:#059669;font-weight:600;text-align:right;
            border-bottom:1px solid #f3f4f6;font-family:monospace;">{f['amount'] or '—'}</td>
        </tr>
        <tr><td colspan="5" style="padding:0 24px 12px;font-size:12px;">
          <a href="{h['claim_url']}" style="color:#2563eb;text-decoration:none;">
            → File a claim at the official {h['state_name']} site (free)
          </a></td></tr>"""

    searches  = results.get("searches", [])
    err_count = len([s for s in searches if "error" in s])

    # Clean searches summary (no hits)
    clean = [s for s in searches if s["count"] == 0 and "error" not in s]
    clean_rows = ""
    if clean:
        clean_rows = "<tr><td colspan='5' style='padding:16px 24px 8px;font-size:13px;color:#6b7280;border-top:1px solid #e5e7eb;'><strong>Clean searches (no matches):</strong> "
        clean_rows += ", ".join(
            f"{s['person'].get('first_name','')} {s['person']['last_name']} ({s['state_name']})"
            for s in clean
        ) + "</td></tr>"

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
  style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);">

  <tr><td style="background:{hdr_color};padding:32px 40px;">
    <p style="margin:0;font-size:11px;color:rgba(255,255,255,.8);letter-spacing:.1em;text-transform:uppercase;">
      Unclaimed Funds Monitor</p>
    <h1 style="margin:8px 0 4px;font-size:26px;font-weight:700;color:#fff;">
      {hero}</h1>
    <p style="margin:0;font-size:14px;color:rgba(255,255,255,.85);">{hero_sub}</p>
  </td></tr>

  <tr><td style="padding:14px 40px;background:#f9fafb;border-bottom:1px solid #e5e7eb;">
    <table width="100%" cellpadding="0" cellspacing="0"><tr>
      <td style="font-size:12px;color:#6b7280;">
        Run date: <strong style="color:#374151;">{date_str}</strong></td>
      <td style="font-size:12px;color:#6b7280;text-align:right;">
        {len(searches)} searches · {total_hits} total matches</td>
    </tr></table>
  </td></tr>

  <tr><td><table width="100%" cellpadding="0" cellspacing="0">
    {rows}
    {clean_rows}
  </table></td></tr>

  <tr><td style="padding:24px 40px;text-align:center;border-top:1px solid #e5e7eb;">
    <p style="margin:0;font-size:12px;color:#9ca3af;">
      Results are emailed only — nothing is stored publicly.<br>
      Searching is always free. Never pay a third-party finder fee.
      {"<br>WARNING: " + str(err_count) + " search(es) failed this run." if err_count else ""}
    </p>
  </td></tr>

</table></td></tr></table>
</body></html>"""


def build_text(results, total_hits, hits):
    generated = results.get("generated_at", "")
    try:
        dt       = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        date_str = dt.strftime("%B %d, %Y")
    except Exception:
        date_str = generated

    lines = [f"Unclaimed Funds Monitor — {date_str}", "="*45, ""]
    if total_hits:
        lines.append(f"{total_hits} match{'es' if total_hits!=1 else ''} found\n")
        for h in hits:
            p = h["person"]
            lines.append(f"{p.get('first_name','')} {p['last_name']} — {h['state_name']} ({h['count']} match{'es' if h['count']!=1 else ''})")
            for prop in h["results"]:
                f = extract_fields(prop)
                lines.append(f"  • {f['name']} | {f['holder']} | {f['type']} | {f['amount'] or 'amount unknown'}")
            lines.append(f"  → Claim: {h['claim_url']}\n")
    else:
        lines.append("No matches found this month.\n")

    searches = results.get("searches", [])
    clean    = [s for s in searches if s["count"] == 0 and "error" not in s]
    if clean:
        lines.append("Clean (no matches): " + ", ".join(
            f"{s['person'].get('first_name','')} {s['person']['last_name']} ({s['state_name']})"
            for s in clean
        ))

    lines += ["", "Results emailed only — nothing stored publicly.",
              "Never pay a third-party finder fee."]
    return "\n".join(lines)


def send_sendgrid(api_key, to_email, from_email, subject, html, text):
    payload = json.dumps({
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": "Unclaimed Funds Monitor"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": text},
                    {"type": "text/html",  "value": html}],
    }).encode()

    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(f"Email sent! Status: {r.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"SendGrid error {e.code}: {e.read().decode()}", file=sys.stderr)
        return False


def main():
    if not RESULTS_PATH.exists():
        print("No results found at /tmp/ufm_results.json — skipping email")
        return

    with open(RESULTS_PATH) as f:
        results = json.load(f)

    to_email = os.environ.get("NOTIFICATION_EMAIL", "").strip()
    if not to_email:
        print("NOTIFICATION_EMAIL secret not set — skipping email")
        return

    searches   = results.get("searches", [])
    hits       = [s for s in searches if s["count"] > 0]
    total_hits = sum(s["count"] for s in hits)

    generated = results.get("generated_at", "")
    try:
        dt       = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        date_str = dt.strftime("%B %d, %Y")
    except Exception:
        date_str = generated

    subject = (f"[Unclaimed Funds] {total_hits} match{'es' if total_hits!=1 else ''} found — {date_str}"
               if total_hits else f"[Unclaimed Funds] No matches — {date_str}")

    html = build_html(results, total_hits, hits)
    text = build_text(results, total_hits, hits)

    api_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    if not api_key:
        print("⚠️  SENDGRID_API_KEY not set — printing to stdout")
        print(f"\nTO: {to_email}\nSUBJECT: {subject}\n\n{text}")
        return

    # SendGrid requires the from address to be a verified Sender Identity.
    # Default to NOTIFICATION_EMAIL (the address you already control and verified).
    # Override with SENDGRID_FROM_EMAIL if you want a different verified sender.
    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "").strip() or to_email

    print(f"Sending email to {to_email}...")
    ok = send_sendgrid(api_key, to_email, from_email, subject, html, text)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
