---
name: verified-release-and-ui-craft
description: >-
  Unified release-hardening, security-audit, cryptographic-hygiene, and tactile anti-slop UI engineering skill.
  Combines TruffleHog (v3+ verified secret scanning), cloudflare/security-audit-skill (6-phase adversarial validation),
  qybaihe/bla artifact entanglement with strict server-side boundary caveats, authenticated encryption vs. hashing
  separation, and Oil UI multi-direction tactile/spring-physics UI craft stripped of generic AI chrome.
version: 1.0.0
---

# Verified Release & Tactile UI Craft

## Overview

`verified-release-and-ui-craft` is the unified pre-release security, cryptographic hygiene, artifact integrity, and tactile frontend engineering skill for **LUMINA OS**, **Allora App**, **Market Haven**, and all Antigravity workspaces.

It synthesizes four verified pillars into one deterministic workflow:
1. **Security & Secret Hygiene** (`trufflesecurity/trufflehog` v3+ & `cloudflare/security-audit-skill`)
2. **Artifact Hardening with Boundary Realism** (`qybaihe/bla` & SHA-256 entanglement)
3. **Cryptographic Separation** (Authenticated Encryption vs. Integrity Hashing vs. Salted Credential KDFs)
4. **Tactile & Anti-Slop UI Craft** (`oil-oil/oil-ui` multi-direction exploration, spring physics, micro-textures, zero AI chrome)

---

## Pillar 1: Security & Secret Hygiene

### 1.1 TruffleHog v3+ Secret Scanning
`trufflesecurity/trufflehog` (v3+) provides 700–800+ credential detectors with **active API verification** (`--results=verified`) across Git history, filesystems, and object stores.

```bash
# Scan Git history for verified live credentials (fail on any hit)
trufflehog git file://. --results=verified --fail

# Scan local filesystem / build output before release
trufflehog filesystem . --results=verified --fail
```

### 1.2 Cloudflare 6-Phase Security Audit Workflow (`cloudflare/security-audit-skill`)
When performing a full security audit on a repository, execute all 6 phases in order:

1. **Reconnaissance**: Map entry points, trust boundaries, auth flows, and data sinks into `architecture.md` and initialize `coverage-ledger.json`.
2. **Coverage-Led Hunting**: Systematically audit every module in `coverage-ledger.json` (never cherry-pick); mark files/routes covered only after inspection.
3. **Adversarial Candidate Validation**: Spawn a **fresh verifier agent** (no shared confirmation bias) to attempt to disprove every candidate vulnerability with concrete exploit paths or counter-evidence.
4. **Schema-Validated JSON Output**: Emit findings in strict machine-validated JSON (`id`, `severity`, `file`, `line`, `cwe`, `evidence`, `verified_by`).
5. **Independent Record Verification**: Re-run reproduction commands/tests and verify file/line citations directly against the current working tree.
6. **Target-Neutral Reporting**: Report verified findings objectively with exact remediation diffs and no hype.

---

## Pillar 2: Artifact Hardening & Boundary Caveat (`qybaihe/bla`)

`qybaihe/bla` (`bla-agents`) applies deception (VLQ v3 honey SourceMaps, shadow state machines), analyzer budget exhaustion, and cross-artifact SHA-256 entanglement (`--self-seal`, `--sidecar-entangle`).

> [!IMPORTANT]
> **Critical Security Boundary Rule**: Automated de-obfuscation tools (`anti-bla`) can strip client-side decoys if a single seed constant is recovered.
> - **NEVER** place proprietary algorithms, API keys, or secrets in client-side bundles.
> - Keep sensitive logic and credentials strictly on **server-side** or **air-gapped** infrastructure.
> - Treat client-side BLA hardening strictly as a **cost-amplifying layer**, never as a security boundary.

For release bundles, always generate and verify an independent SHA-256 integrity manifest:

```bash
python3 ~/.gemini/config/skills/verified-release-and-ui-craft/scripts/verified_release_craft.py \
  sha256-manifest --dir ./dist --out ./dist/SHA256SUMS.json

python3 ~/.gemini/config/skills/verified-release-and-ui-craft/scripts/verified_release_craft.py \
  verify-manifest --manifest ./dist/SHA256SUMS.json
```

---

## Pillar 3: Cryptographic Separation

Enforce strict separation between **confidentiality**, **integrity**, and **credential storage**:

| Use Case | Required Primitive | Prohibited / Anti-Pattern |
| :--- | :--- | :--- |
| **Confidentiality** (two-way encryption) | `AES-256-GCM` or `ChaCha20-Poly1305` (unique nonce/IV per message) | ECB mode, unauthenticated CBC without HMAC, custom XOR |
| **Artifact / Payload Integrity** (one-way) | `SHA-256` (or `SHA-512` / `BLAKE2b`) | `MD5`, `SHA-1` |
| **Password / Credential Storage** | Salted `Argon2id` or `bcrypt` | Raw `SHA-256(password)`, unsalted hashes |

Scan a codebase for cryptographic anti-patterns:

```bash
python3 ~/.gemini/config/skills/verified-release-and-ui-craft/scripts/verified_release_craft.py \
  check-crypto-patterns --dir ./src
```

---

## Pillar 4: Tactile & Anti-Slop UI Craft (`Oil UI` + Motion + Surface Depth)

### 4.1 Multi-Direction Visual Exploration (`github.com/oil-oil/oil-ui`)
Before committing to a single UI layout:
1. Generate **3 distinct visual directions** varying **layout architecture, typography pairing, and color palette**.
2. Render and compare them **side-by-side** across **desktop and mobile** viewports.
3. Capture rendered screenshots (e.g., via Chrome DevTools MCP `take_screenshot`) and refine spacing, contrast, and hierarchy against the actual rendered pixels.

### 4.2 Tactile Surface Depth & Spring Physics (`@motion_ui_interface`)
- **Micro-textures**: Subtle felt/grain SVG noise overlays (`opacity: 0.02–0.05`), ambient radial lighting, and layered glassmorphism (`backdrop-filter: blur(...)` with hairline `1px` specular borders).
- **Motion**: Use spring-physics transitions (mass/stiffness/damping) for interactive state changes rather than flat linear easing.

### 4.3 Zero AI Slop Chrome
Strip generic AI UI boilerplate from all production interfaces:
- Gratuitous emojis in headings, nav items, and action buttons.
- Generic chatbot greetings (*"How can I help you today?"*, *"I'm your AI assistant..."*).
- Redundant status badges (*"AI-Powered"*, *"Smart"*, *"Online"*).
- *"Powered by AI"* / *"Generated by AI"* footers.

Audit frontend source files for AI slop chrome:

```bash
python3 ~/.gemini/config/skills/verified-release-and-ui-craft/scripts/verified_release_craft.py \
  audit-ui-slop --dir ./src
```

---

## Bundled Helper CLI

Location: `~/.gemini/config/skills/verified-release-and-ui-craft/scripts/verified_release_craft.py` (zero external dependencies; Python 3 standard library only).

Subcommands:
- `check-tools`: Check availability of `trufflehog`, `bla`, `git`, and `python3`.
- `sha256-manifest`: Generate a deterministic SHA-256 manifest JSON for release artifacts.
- `verify-manifest`: Verify release artifacts against a SHA-256 manifest JSON (exits non-zero on mismatch or missing file).
- `check-crypto-patterns`: Static scan for weak hashes (`md5`, `sha1`), raw `sha256` password hashing, and `AES.MODE_ECB`.
- `audit-ui-slop`: Scan UI files (`.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.css`) for generic AI chrome and boilerplate phrases.
