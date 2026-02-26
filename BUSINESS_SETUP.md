# Business Setup Checklist — Bellissimo AI Labs LLC
# Agent-Runnable Format
#
# HOW AN AGENT USES THIS FILE:
#   Each task has: status, required_permissions, tools_needed, steps, output
#   An agent with the right permissions reads this file, executes each task,
#   updates the status field, and saves outputs to /setup-outputs/
#
# PERMISSIONS MODEL:
#   "browser" — can open URLs and fill forms
#   "email"   — can send/receive email
#   "files"   — can read/write local files
#   "payment" — can process payments (human confirmation required)
#   "human"   — requires human in the loop

---

## TRACK 1 — Legal Entity

### Task: Register Wyoming LLC
- status: [ ] pending
- required_permissions: [browser, payment, human]
- tools_needed: web_browser, form_fill
- estimated_cost: ~$100 state fee + registered agent (~$50/yr)
- steps:
  1. Navigate to wyomingllc.com or dos.wyo.gov
  2. Select "Domestic LLC"
  3. Entity name: "Bellissimo AI Labs LLC"
  4. Registered agent: Northwest Registered Agent (recommended, ~$125/yr)
  5. Submit Articles of Organization + pay state fee
  6. Download and save certificate
- output: LLC_certificate.pdf → /setup-outputs/legal/
- notes: Wyoming has no state income tax, strong privacy, low fees. Best state for single-member LLCs.

### Task: Obtain EIN from IRS
- status: [ ] pending
- required_permissions: [browser, human]
- dependency: Wyoming LLC must be registered first
- tools_needed: web_browser, form_fill
- estimated_cost: $0 (free)
- steps:
  1. Navigate to irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online
  2. Select "LLC" as entity type
  3. Select "sole member" (single-member LLC)
  4. Complete SS-4 form online
  5. EIN issued instantly — save confirmation
- output: EIN_confirmation.pdf → /setup-outputs/legal/
- notes: Need LLC certificate before applying. EIN is required for bank account and invoicing.

### Task: Draft Operating Agreement
- status: [ ] pending
- required_permissions: [files]
- tools_needed: text_generation (Claude)
- estimated_cost: $0 (generate with AI, review yourself)
- steps:
  1. Generate single-member LLC operating agreement using Claude
  2. Review for: member name, entity name, Wyoming jurisdiction, profit distribution
  3. Sign and date
  4. Store in /setup-outputs/legal/
- output: operating_agreement.pdf → /setup-outputs/legal/
- notes: Not legally required in Wyoming but highly recommended for banking.

---

## TRACK 2 — Banking & Payments

### Task: Open Mercury Bank Business Checking
- status: [ ] pending
- required_permissions: [browser, email, human]
- dependency: Wyoming LLC certificate + EIN required
- tools_needed: web_browser, document_upload
- estimated_cost: $0 (no fees)
- steps:
  1. Navigate to mercury.com
  2. Click "Open an account"
  3. Select "LLC"
  4. Upload: LLC certificate, EIN confirmation, government ID
  5. Complete identity verification
  6. Wait for approval (typically 1-3 business days)
- output: Mercury account number + routing number → /setup-outputs/banking/
- notes: Mercury is startup-friendly, no minimums, excellent API for future automation.

### Task: Set Up Stripe for Payments
- status: [ ] pending
- required_permissions: [browser, human]
- dependency: Mercury bank account recommended first
- tools_needed: web_browser
- estimated_cost: 2.9% + 30¢ per transaction (no monthly fee)
- steps:
  1. Navigate to stripe.com
  2. Create account with business email
  3. Enter business details (Bellissimo AI Labs LLC)
  4. Connect Mercury bank account for payouts
  5. Enable invoicing feature
  6. Create first invoice template
- output: Stripe account ID + API keys → /setup-outputs/banking/
- notes: Stripe API keys will be used by future billing automation agents.

---

## TRACK 3 — Digital Presence

### Task: Secure Domain
- status: [ ] pending
- required_permissions: [browser, payment]
- tools_needed: web_browser, domain_search
- estimated_cost: $15–$50/yr depending on TLD
- steps:
  1. Check availability (in order of preference):
     - bellissimo.ai (premium, worth it if available)
     - bellissimoailabs.com
     - bellissimo-ai.com
     - getbellissimo.com
  2. Register via Cloudflare Registrar (cheapest, no markup)
  3. Enable privacy protection (hide personal info from WHOIS)
  4. Point nameservers to Vercel or Netlify when site is ready
- output: Domain confirmation + registrar login → /setup-outputs/digital/
- notes: .ai domains are ~$50–$70/yr. Worth it for brand positioning.

### Task: Set Up Google Workspace (Business Email)
- status: [ ] pending
- required_permissions: [browser, payment]
- dependency: Domain secured first
- tools_needed: web_browser, DNS_configuration
- estimated_cost: $6–$12/mo (Google Workspace Starter)
- steps:
  1. Navigate to workspace.google.com
  2. Set up with domain
  3. Create: jb@bellissimo.ai (or primary domain)
  4. Configure MX records in Cloudflare DNS
  5. Verify domain ownership
- output: Business email active → /setup-outputs/digital/

### Task: Reserve Social Handles
- status: [ ] pending
- required_permissions: [browser]
- tools_needed: web_browser
- estimated_cost: $0
- steps:
  1. Check and reserve on: LinkedIn, Twitter/X, Instagram
  2. Handle target: @bellissimoailabs or @bellissimo_ai
  3. Use same profile photo and 1-line bio across all
  4. Don't post yet — just reserve
- output: Handle list → /setup-outputs/digital/

---

## TRACK 4 — Compliance & Admin

### Task: Open Basic Bookkeeping
- status: [ ] pending
- required_permissions: [browser, human]
- dependency: Mercury + EIN
- tools_needed: web_browser
- estimated_cost: $0 (Wave) or $15/mo (QuickBooks Simple Start)
- steps:
  1. Create Wave account (wave.com) — free
  2. Connect Mercury bank account for auto-import
  3. Create chart of accounts (Services Revenue, Software, Contractors, Travel)
  4. Set up invoice template with Bellissimo AI Labs branding
- output: Bookkeeping system active

### Task: Create Service Agreement Template
- status: [ ] pending
- required_permissions: [files]
- tools_needed: text_generation (Claude)
- estimated_cost: $0
- steps:
  1. Generate 1-page service agreement covering:
     - Scope of services (AI consulting, agent development, strategy)
     - Payment terms (net 15, monthly retainer)
     - IP ownership (client owns outputs, Bellissimo owns methodology)
     - Confidentiality
     - Termination (30-day notice)
  2. Review and sign template
  3. Store as reusable template
- output: service_agreement_template.docx → /setup-outputs/legal/

---

## TRACK 5 — AI Infrastructure

### Task: Set Up Anthropic API for Production
- status: [ ] pending
- required_permissions: [browser, payment]
- tools_needed: web_browser
- estimated_cost: Pay-per-use (budget $50/mo to start)
- steps:
  1. Navigate to console.anthropic.com
  2. Create production API key (separate from dev key)
  3. Set spending limit: $50/mo to start
  4. Store API key in .env file (ANTHROPIC_API_KEY_PROD)
  5. Set up billing alerts
- output: Production API key active

### Task: Deploy First Agent (The Reveal)
- status: [ ] pending
- required_permissions: [files, browser]
- dependency: Domain + Anthropic API key
- tools_needed: Python, Claude API, web_server
- steps:
  1. Build ceo_interview_agent.py (CEO intake → structured data → report)
  2. Deploy to Railway.app or Render (free tier)
  3. Connect to website intake form
  4. Test end-to-end with one internal run
- output: Live agent endpoint URL

---

## COMPLETION TRACKER

| Track | Tasks | Done | Status |
|---|---|---|---|
| Legal Entity | 3 | 0 | Not started |
| Banking & Payments | 2 | 0 | Not started |
| Digital Presence | 3 | 0 | Not started |
| Compliance & Admin | 2 | 0 | Not started |
| AI Infrastructure | 2 | 0 | Not started |
| **TOTAL** | **12** | **0** | **0%** |

---

## AGENT EXECUTION NOTES

To run this checklist as an agent:
1. Agent reads this file and identifies all `status: [ ] pending` tasks
2. Agent checks dependencies — skips tasks with unmet dependencies
3. For tasks requiring `human` permission — agent pauses and sends notification
4. For tasks requiring `payment` — agent presents cost summary and waits for approval
5. Agent updates status to `[x] complete` and logs output file path after completion
6. Agent re-runs the completion tracker table at the end

Future: This file becomes the input to a `business_setup_agent.py` that automates
the browser-based steps via Playwright or similar tool.

---

*Last updated: 2026-02-25*
