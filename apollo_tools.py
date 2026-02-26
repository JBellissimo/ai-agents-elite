"""
apollo_tools.py — Apollo.io API integration for prospect targeting

Used by discord_bot.py for the !prospect command.
Requires APOLLO_API_KEY in .env (get from Josh: apollo.io > Settings > Integrations > API)

Apollo docs: https://apolloio.github.io/apollo-api-docs/
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from dotenv import load_dotenv

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")
APOLLO_BASE = "https://api.apollo.io/v1"


def _post(endpoint: str, payload: dict) -> dict:
    """Make a POST request to Apollo API."""
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY not set in .env — get from Josh")

    url = f"{APOLLO_BASE}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": APOLLO_API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Apollo API error {e.code}: {body[:300]}")


# ─── Search Functions ───────────────────────────────────────────────────────────

def search_companies(
    keywords: str = "",
    locations: list[str] | None = None,
    industries: list[str] | None = None,
    employee_ranges: list[str] | None = None,
    per_page: int = 10,
) -> list[dict]:
    """
    Search Apollo for companies matching criteria.

    employee_ranges options: "1,10" "11,20" "21,50" "51,100" "101,200" "201,500" "501,1000" "1001,2000" "2001,5000" "5001,10000" "10001"
    locations: list of strings like ["New York, NY", "Long Island, NY", "Huntington, WV"]
    industries: list of strings like ["Healthcare", "Legal Services", "Manufacturing", "Financial Services"]

    Returns list of company dicts with: name, industry, headcount, location, website, phone
    """
    payload = {
        "page": 1,
        "per_page": per_page,
        "organization_num_employees_ranges": employee_ranges or [],
        "organization_locations": locations or [],
        "q_organization_keyword_tags": [k.strip() for k in keywords.split(",")] if keywords else [],
    }
    if industries:
        payload["organization_industry_tag_ids"] = industries  # Note: Apollo uses tag IDs, but keyword search also works

    result = _post("/mixed_companies/search", payload)
    orgs = result.get("organizations", [])

    cleaned = []
    for org in orgs:
        cleaned.append({
            "name": org.get("name", ""),
            "industry": org.get("industry", ""),
            "headcount": org.get("num_employees", ""),
            "city": org.get("city", ""),
            "state": org.get("state", ""),
            "website": org.get("website_url", ""),
            "phone": org.get("phone", ""),
            "linkedin": org.get("linkedin_url", ""),
        })
    return cleaned


def search_contacts(
    titles: list[str] | None = None,
    locations: list[str] | None = None,
    industries: list[str] | None = None,
    company_headcount: list[str] | None = None,
    per_page: int = 10,
) -> list[dict]:
    """
    Search Apollo for people (contacts) matching criteria.
    Good for finding referral partners (attorneys, bankers, CPAs in a region).

    titles: ["Attorney", "Partner", "CPA", "Controller", "CFO", "Business Owner"]
    """
    payload = {
        "page": 1,
        "per_page": per_page,
        "person_titles": titles or [],
        "person_locations": locations or [],
        "organization_industry_tag_ids": industries or [],
        "organization_num_employees_ranges": company_headcount or [],
    }
    result = _post("/mixed_people/search", payload)
    people = result.get("people", [])

    cleaned = []
    for p in people:
        org = p.get("organization", {}) or {}
        cleaned.append({
            "name": p.get("name", ""),
            "title": p.get("title", ""),
            "email": p.get("email", ""),
            "company": org.get("name", ""),
            "industry": org.get("industry", ""),
            "city": p.get("city", ""),
            "state": p.get("state", ""),
            "linkedin": p.get("linkedin_url", ""),
        })
    return cleaned


# ─── Natural Language → Apollo Parameters (via Claude) ──────────────────────────

PROSPECT_PARSER_SYSTEM = """You are an API parameter extractor for Apollo.io prospect searches.

The user describes who they want to find for business outreach. Convert their description to a JSON object with these exact keys:
{
  "search_type": "companies" or "contacts",
  "keywords": "comma-separated keywords",
  "locations": ["City, State", ...],
  "industries": ["Industry Name", ...],
  "titles": ["Title 1", ...],   // only for contacts search
  "employee_ranges": ["1,10", "11,20", "21,50", "51,100", "101,200"],
  "notes": "brief explanation of what you understood"
}

employee_ranges: only include ranges that fit the description. Use: "1,10" "11,20" "21,50" "51,100" "101,200" "201,500"

Location examples: "New York, New York" "Long Island, New York" "Huntington, West Virginia"
Industry examples: "Dental Offices" "Legal Services" "Accounting" "Manufacturing" "Healthcare" "Real Estate" "Financial Services"

Use "contacts" search when user mentions finding specific people/titles (attorneys, bankers, CPAs).
Use "companies" search when user mentions finding businesses/practices.

Return ONLY valid JSON, no other text."""


def parse_prospect_query(query: str, anthropic_client) -> dict:
    """Use Claude to convert natural language query to Apollo API parameters."""
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=PROSPECT_PARSER_SYSTEM,
        messages=[{"role": "user", "content": query}]
    )
    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ─── Format Results for Discord ─────────────────────────────────────────────────

def format_company_results(companies: list[dict], query: str) -> str:
    """Format company search results for Discord."""
    if not companies:
        return f"No companies found for: *{query}*\n\nTry broader search terms or a different location."

    lines = [f"**Prospect Results: {query}**", f"*{len(companies)} companies found*", ""]
    for i, c in enumerate(companies, 1):
        location = ", ".join(filter(None, [c.get("city"), c.get("state")]))
        size = f"{c['headcount']} employees" if c.get("headcount") else ""
        parts = [p for p in [c.get("industry"), location, size] if p]
        lines.append(f"**{i}. {c['name']}**")
        if parts:
            lines.append(f"   {' | '.join(parts)}")
        if c.get("website"):
            lines.append(f"   {c['website']}")
        lines.append("")

    lines.append("*DM me a number to get more details or add to pipeline.*")
    return "\n".join(lines)


def format_contact_results(contacts: list[dict], query: str) -> str:
    """Format contact/people search results for Discord."""
    if not contacts:
        return f"No contacts found for: *{query}*\n\nTry broader title or location terms."

    lines = [f"**Contact Search: {query}**", f"*{len(contacts)} people found*", ""]
    for i, p in enumerate(contacts, 1):
        location = ", ".join(filter(None, [p.get("city"), p.get("state")]))
        lines.append(f"**{i}. {p['name']}** — {p.get('title', '')}")
        if p.get("company"):
            company_info = p["company"]
            if location:
                company_info += f" | {location}"
            lines.append(f"   {company_info}")
        if p.get("email"):
            lines.append(f"   {p['email']}")
        lines.append("")

    lines.append("*DM me a number to get more details or draft outreach email.*")
    return "\n".join(lines)
