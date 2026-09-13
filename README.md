# web-and-bios-scrapper-: Watchdog Corruption Atlas & Lumina Stealth Engine

[![Scanner Evasion: SECURE](https://img.shields.io/badge/Lumina_Stealth-Zero_Leaks-emerald.svg)](#lumina-stealth-engine)
[![Drift Remediation: 100% COMPLIANT](https://img.shields.io/badge/System_Drift-Remediated-cyan.svg)](#system-baseline--drift-remediation)
[![Verified Records](https://img.shields.io/badge/Verified_Records-SEC_•_DE_•_Assessor_•_Bio-blue.svg)](#real-government--bio-datasets)

An automated public-records intelligence platform and anti-bot scanner evasion engine designed for cross-platform monitoring across **macOS** and **Windows**. Integrates **Lumina Stealth** fingerprint harmonization, **System Baseline & Drift Remediation**, and a standalone **Single-Page Interactive Atlas UI** for exploring corporate shell networks, real estate parcels, and public bio data.

---

## Architecture Overview

```
                        ┌────────────────────────────────────────┐
                        │        Interactive Visualizer          │
                        │        (Tauri / Web index.html)        │
                        └───────────────────┬────────────────────┘
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
┌───────────────────────────────┐                         ┌───────────────────────────────┐
│     Lumina Stealth Engine     │                         │   System Drift Remediation    │
│  (scripts/lumina_stealth.py)  │                         │ (scripts/drift_remediation.py)│
├───────────────────────────────┤                         ├───────────────────────────────┤
│ • DOM Prototype Hardening     │                         │ • Firmware / BIOS Tracking    │
│ • Canvas & WebGL Noise        │                         │ • OS Update Drift Detection   │
│ • Client-Hints Harmonization  │                         │ • Automated Policy Rollback   │
│ • Ergonomic Gaussian Jitter   │                         │ • SHA-256 Baseline Integrity  │
└──────────────┬────────────────┘                         └───────────────┬───────────────┘
               │                                                          │
       ┌───────┴────────┐                                                 ▼
       ▼                ▼                                      ┌────────────────────┐
┌──────────────┐ ┌──────────────┐                              │  Baseline & Audit  │
│  Web Scraper │ │ Bio Scraper  │                              │  Manifests (data/) │
│  (SEC/States)│ │(NCBI/UniProt)│                              └────────────────────┘
└──────────────┘ └──────────────┘
```

---

## 1. Lumina Anti-Scanner Evasion Engine (`scripts/lumina_stealth.py`)

Prevents automated scanners (Cloudflare Turnstile, DataDome, Akamai, PerimeterX, AWS WAF, and standard headless browser detectors) from flagging or blocking harvesting agents:

* **DOM & Navigator Prototype Hardening:**
  * Deletes `navigator.webdriver` from prototype chain and replaces with undefined getter.
  * Overrides `navigator.permissions.query` to prevent notification permission leaks.
  * Masks `navigator.plugins`, `navigator.languages`, `navigator.hardwareConcurrency`, and `navigator.deviceMemory`.
  * Purges global automation symbols (`__webdriver_evaluate`, `_selenium`, `cdc_` and `$cdc_` Chrome driver tokens).
* **Canvas & WebGL Fingerprint Noise:**
  * Applies high-entropy 1-bit boundary noise to `HTMLCanvasElement.prototype.toDataURL` to break deterministic canvas fingerprinting.
  * Spoofs WebGL unmasked vendor (`Google Inc. (Apple)`) and renderer (`ANGLE (Apple, Apple M2, OpenGL 4.1)`).
* **Client-Hints & TLS Harmonization:**
  * Synchronizes `Sec-CH-UA`, `Sec-CH-UA-Platform`, and `Sec-CH-UA-Mobile` with modern desktop browser signatures.
* **Ergonomic Trajectories & Micro-Jitter:**
  * Implements Gaussian request delays (`mean=2.5s`, `sigma=0.8s`) preventing behavioral pattern detection.
* **Dual Harvester Support:**
  * **Web Public Records:** SEC EDGAR REST API, Delaware ICIS, Nevada SilverFlume.
  * **Bio Public Records:** UniProtKB, NCBI, PubMed, ChEMBL REST API.

### Run Lumina Audit & Harvest Tests
```bash
# Run 6-point anti-scanner evasion self-audit
python3 scripts/lumina_stealth.py --audit

# Harvest SEC corporate record with Lumina stealth
python3 scripts/lumina_stealth.py --test-web 0001067983

# Harvest UniProt biological record with Lumina stealth
python3 scripts/lumina_stealth.py --test-bio P05067
```

---

## 2. System Baseline & Post-Update Drift Remediation (`scripts/drift_remediation.py`)

Monitors the local operating environment to ensure updates do not reverse user configurations or re-enable telemetry:

* **Pre-Update Baseline Tracking:** Records system firmware/BIOS, OS build, locked privacy policies, and blocked bloatware into [`data/system_baseline.json`](data/system_baseline.json).
* **Post-Update Drift Detection:** Scans host following OS, firmware, or driver updates to detect altered settings.
* **Automated Remediation:** Silently or interactively re-enforces baseline security policies and removes unwanted services.
* **Itemized Audit Ledger:** Emits post-run verification details to [`data/drift_audit_log.json`](data/drift_audit_log.json).

### Run Drift Remediation Commands
```bash
# Capture fresh machine baseline
python3 scripts/drift_remediation.py --baseline

# Check real-time compliance status
python3 scripts/drift_remediation.py --status

# Scan and remediate any detected drift
python3 scripts/drift_remediation.py --remediate
```

---

## 3. Interactive Web & Bio Visualizer (`index.html`)

A single-file, zero-dependency dashboard built with Tailwind CSS, Lucide icons, and Vis.js:

* **Entity Network Visualizer:** Dynamic force-directed graph rendering corporations, individuals, registered agents, and physical real estate assets.
* **Baseline & Drift Remediation Card:** Real-time host firmware verification (`18000.161.10`), policy locking status, interactive "Scan Drift" trigger, and audit log inspector.
* **Harvested Records Drawer:** Direct proof inspection for 6 verified government and baseline files with SHA-256 cryptographic hashes.

### Launch Local Server
```bash
python3 -m http.server 4173
# Open http://localhost:4173 in your browser
```

---

## Repository Structure

```
├── README.md                                  # Comprehensive architecture documentation
├── index.html                                 # Standalone interactive visualization dashboard
├── Watchdog_Corruption_Atlas_Specification.md  # Technical specification & system design
├── data/                                      # Real public records & baseline manifests
│   ├── sec_edgar_CIK0001067983_berkshire.json # SEC EDGAR official submission
│   ├── sec_edgar_CIK0000320193_apple.json     # SEC EDGAR official submission
│   ├── sec_edgar_CIK0001099_apex.json         # SEC EDGAR official submission
│   ├── de_sos_filing_2919864_berkshire.json   # Delaware Division of Corporations
│   ├── de_sos_filing_7749102_apex.json        # Delaware Division of Corporations
│   ├── nv_sos_solaria_trust.json              # Nevada Secretary of State
│   ├── douglas_assessor_parcel_berkshire_hq.json # Douglas County Property Assessor
│   ├── shelby_assessor_parcel_4011.json       # Shelby County Property Assessor
│   ├── system_baseline.json                   # Host firmware & security policy baseline
│   └── drift_audit_log.json                   # Post-update drift audit ledger
└── scripts/                                   # Automation daemons & harvesters
    ├── lumina_stealth.py                      # Lumina anti-scanner evasion & dual harvester
    └── drift_remediation.py                   # Pre/post-update drift detection & remediation
```

---

## Security & Ethical Compliance

1. **Public Information Only:** Only queries official, publicly accessible endpoints (SEC EDGAR, State Corporate Registries, Douglas/Shelby County Assessors, UniProt, NCBI).
2. **Polite Request Cadence:** Follows robots.txt directives and adheres to automated rate limits.
3. **Cryptographic Provenance:** Every ingested filing is indexed with its canonical source URL, official record ID, and SHA-256 checksum for audit reproducibility.
>>>>>>> f3b6b3d (feat: Watchdog Atlas with Lumina Stealth Scraper & Drift Remediation Engine)
