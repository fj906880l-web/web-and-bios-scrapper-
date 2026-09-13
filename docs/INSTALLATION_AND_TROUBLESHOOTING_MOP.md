# Method of Procedure (MOP): Installation, Operation & Troubleshooting Runbook

**Document ID:** `MOP-OPS-WBS-2026-V2`  
**Classification:** Standard Operating Procedure (SOP / MOP)  
**System:** Web & Bio's Scrapper (Watchdog Corruption Atlas & Lumina Stealth Subsystems)  
**Supported Platforms:** macOS (Apple Silicon / Intel), Windows 11/10 (PowerShell 5.1+), Linux (Ubuntu/Debian/RHEL)  

---

## 1. Scope & Purpose

This Method of Procedure (MOP) establishes standard engineering guidelines for deploying, verifying, operating, and troubleshooting the **Web & Bio's Scrapper** platform. The system provides automated public-records intelligence across corporate entities (SEC EDGAR, State Corporate Registries, County Property Assessors) and biomedical research repositories (UniProt, ChEMBL, NCBI), backed by the **Lumina Stealth Anti-Scanner Shield** and cross-platform **System Baseline & Drift Remediation**.

---

## 2. System Architecture & Prerequisites

### 2.1 Technical Specifications
* **Core Language:** Python 3.10 or higher (compatible with Python 3.11, 3.12, 3.13, 3.14).
* **Zero External Dependencies:** Built entirely with Python standard libraries (`urllib.request`, `json`, `hashlib`, `gzip`, `platform`, `subprocess`, `random`, `math`, `time`). No mandatory third-party pip packages required.
* **Frontend Runtime:** Zero-build single-file HTML5 interface (`index.html`) using CDN-served Tailwind CSS, Lucide icons, and Vis.js network visualizer.

### 2.2 System Requirements
| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | macOS 12+, Windows 10, Ubuntu 20.04+ | macOS 15+ (Apple Silicon), Windows 11 |
| **CPU Architecture** | x86_64 or arm64 (Apple Silicon M-series supported) | Apple M1/M2/M3/M4 or Intel Core i7 12th+ Gen |
| **Memory (RAM)** | 2.0 GB free memory | 8.0 GB free memory |
| **Disk Space** | 200 MB free space (datasets + documentation) | 1.0 GB (for extensive public record archives) |
| **Network** | Outbound HTTPS (TCP port 443) | Stable broadband connection |

---

## 3. Step-by-Step Installation Procedure

### Step 3.1: Repository Clone & Workspace Setup
Clone the official repository from GitHub into your local workspace:

```bash
# Clone the repository
git clone https://github.com/fj906880l-web/web-and-bios-scrapper-.git

# Navigate into project directory
cd web-and-bios-scrapper-
```

### Step 3.2: Python Virtual Environment (Optional but Recommended)
Initialize an isolated virtual environment:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3.3: Configure Script Execution Permissions
Ensure all automation scripts have execution permissions:

```bash
# macOS / Linux
chmod +x scripts/*.py

# Windows (PowerShell)
# Execution policies are governed by PowerShell execution scopes (see Troubleshooting TR-05)
```

---

## 4. Operational Verification Checklist (MOP Checklist)

Execute the following 5 standard operational checks to confirm operational integrity.

### MOP-01: Lumina Anti-Scanner Evasion Self-Audit
Verify that the Lumina anti-detection engine passes all 6 anti-automation heuristic checks with zero detection leaks:

```bash
python3 scripts/lumina_stealth.py --audit
```
* **Expected Output:**
  ```
  [*] Running Lumina Anti-Scanner Evasion Audit...
  [✔] ALL 6 SCANNER SIGNATURE CHECKS PASSED — ZERO AUTOMATION LEAKS DETECTED.
  ```

---

### MOP-02: Web Corporate Public Records Harvester
Harvest live corporate public records from the U.S. Securities and Exchange Commission (SEC EDGAR REST API):

```bash
# Run automated sample harvest (Berkshire Hathaway & Apple Inc)
python3 scripts/web_scraper.py --harvest-samples

# Or query a custom corporate CIK
python3 scripts/web_scraper.py --sec 0001067983
```
* **Expected Output:**
  ```
  [*] [1/2] Harvesting SEC EDGAR CIK 0001067983 (Berkshire Hathaway)...
      ✔ Entity: BERKSHIRE HATHAWAY INC | EIN: 470813844 | State: DE
      ✔ Recent Filings: 5 forms indexed | SHA-256: cecd20c8ae22...
  [✔] All public web corporate datasets successfully retrieved and indexed in data/.
  ```

---

### MOP-03: Bio's Biomedical Public Records Harvester
Harvest live biological and chemical records from UniProt, ChEMBL, and NCBI:

```bash
# Run automated sample harvest (APP Protein, Aspirin, APP Gene)
python3 scripts/bio_scraper.py --harvest-samples

# Or query a specific UniProt accession or ChEMBL ID
python3 scripts/bio_scraper.py --uniprot P05067
python3 scripts/bio_scraper.py --chembl CHEMBL25
```
* **Expected Output:**
  ```
  [*] [1/3] Harvesting UniProt P05067 (Human APP)...
      ✔ Entry: Amyloid-beta precursor protein | Gene: APP | Length: 770 aa
  [*] [2/3] Harvesting ChEMBL CHEMBL25 (Aspirin)...
      ✔ Compound: ASPIRIN | Max Phase: 4.0 | SMILES: CC(=O)Oc1ccccc1C(=O)O
  [*] [3/3] Harvesting NCBI Gene ID 351 (APP)...
      ✔ Gene: APP (amyloid beta precursor protein) | Chromosome: 21
  [✔] All public bio datasets successfully retrieved and indexed in data/.
  ```

---

### MOP-04: System Baseline & Drift Remediation Check
Inspect host machine hardware, firmware/BIOS version, and locked security configurations:

```bash
# Check current machine baseline status
python3 scripts/drift_remediation.py --status

# Capture fresh pre-update baseline manifest
python3 scripts/drift_remediation.py --baseline
```
* **Expected Output:**
  ```json
  {
    "scanned_at": "2026-09-13T00:09:05Z",
    "drift_detected": false,
    "drift_count": 0,
    "system_health": "COMPLIANT"
  }
  ```

---

### MOP-05: Single-Page Interactive Visualizer Launch
Launch the local web dashboard to explore entity network graphs and baseline files:

```bash
python3 -m http.server 4173
```
* Open your web browser to: **`http://localhost:4173`**
* Verify that the force graph renders, presets load, and clicking "View Proof" on any file opens the formatted JSON inspector modal.

---

## 5. Troubleshooting Runbook & Symptom Matrix

| Code | Symptom | Root Cause | Remediation Procedure |
| :--- | :--- | :--- | :--- |
| **TR-01** | `HTTP 403 Forbidden` or CAPTCHA challenge from Cloudflare / Akamai | Scraper detected as automated bot due to default `urllib` headers, missing Client-Hints, or `navigator.webdriver` flag. | Ensure all requests route through `LuminaStealthSession`. Verify `navigator.webdriver` prototype removal and client-hints synchronization. Run `python3 scripts/lumina_stealth.py --audit`. |
| **TR-02** | `'utf-8' codec can't decode byte 0x8b in position 1` | Server returned a compressed `gzip` byte stream while the script expected raw text. | The `decode_payload()` helper in `lumina_stealth.py` automatically decompresses payloads starting with magic bytes `0x1f 0x8b`. Ensure you use `decode_payload(resp.read())` instead of `.decode("utf-8")`. |
| **TR-03** | Git push error: `fatal: unable to access ... The requested URL returned error: 403` | Active GitHub Personal Access Token (PAT) lacks `Contents: Read and write` scope on this repository. | 1. Open `https://github.com/settings/tokens`.<br>2. Select your token.<br>3. Under **Repository permissions** &rarr; **Contents**, select **Read and write**.<br>4. Save changes and re-run `git push origin main`. |
| **TR-04** | `git push rejected: Updates were rejected because the remote contains work that you do not have locally` | Remote repository has new commits (e.g. `SECURITY.md`) created via GitHub UI. | Rebase your local changes over remote HEAD:<br>`git fetch origin main`<br>`git rebase origin/main`<br>`git push origin main` |
| **TR-05** | Windows PowerShell: `Execution of scripts is disabled on this system` | Default Windows PowerShell execution policy blocks `.ps1` execution. | Open PowerShell and set the session execution policy:<br>`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`<br>Or run scripts directly via Python: `python scripts\drift_remediation.py`. |
| **TR-06** | `OSError: [Errno 48] Address already in use: 4173` | A background HTTP server process is already bound to port 4173. | Locate and terminate the lingering process:<br>`lsof -i :4173`<br>`kill -9 <PID>`<br>Or start the HTTP server on another port: `python3 -m http.server 8080`. |
| **TR-07** | `HTTP 429 Too Many Requests` from public API | Request rate exceeded target endpoint rate limit (e.g. SEC EDGAR allows max 10 requests/sec). | `LuminaStealthSession` automatically introduces Gaussian micro-jitter delays (`mean=2.5s`, `sigma=0.8s`). Increase `min_s` delay parameter in `ergonomic_delay()` if querying aggressively. |
| **TR-08** | Apple Silicon macOS: `SPFirmwareDataType returns empty output` | On macOS Apple Silicon (M1-M4), firmware data is located under `SPHardwareDataType` rather than legacy Intel `SPFirmwareDataType`. | The `drift_remediation.py` script automatically falls back to `system_profiler SPHardwareDataType` and extracts `System Firmware Version: 18000.161.10`. No manual intervention required. |

---

## 6. Maintenance & Operational Best Practices

1. **SHA-256 Cryptographic Verification:** All files in `data/` must carry their computed SHA-256 hash. If raw data changes, update the hash manifest using `hashlib.sha256(content.encode()).hexdigest()`.
2. **Periodic Drift Scans:** In enterprise environments, configure a daily cron job or launchd daemon on macOS / Scheduled Task on Windows to run `python3 scripts/drift_remediation.py --scan` to detect unauthorized telemetry or registry changes immediately following OS updates.
3. **Ethical Harvester Conduct:** Always respect robots.txt rate-limits, provide contact headers in User-Agents when harvesting federal endpoints, and never execute denial-of-service query spikes against public services.
