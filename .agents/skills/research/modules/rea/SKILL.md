---
name: rea
description: Reverse engineer anything with agents, from app behavior down to native binaries using REA (morluto/rea). Inspect native executables, Electron/ASAR, JavaScript trees, .NET assemblies, firmware, network captures, and runtime behavior.
trigger: /rea
metadata:
  version: "6.4.0"
  provider: "morluto/rea"
  tool_count: 170
---

# REA: Reverse Engineer Anything

Reverse engineer anything with agents, from application behavior down to native binaries.
Based on [morluto/rea](https://github.com/morluto/rea) (REA Agents v6.4.0).

## When to Activate

Use REA when a question or task depends on:
1. **Shipped Artifacts**: Binaries, Mach-O, ELF, PE, DMG, APK, IPA, AppX/MSIX, or firmware images.
2. **Decompilation / Disassembly**: Hopper, Ghidra, or IDA Pro decompilation and pseudocode analysis.
3. **JavaScript & Electron**: Extracted ASARs, webpack/vite bundles, IPC bridges, preload scripts, and module graphs.
4. **.NET / Managed Assemblies**: C# metadata, assemblies, or NativeAOT PE/ELF analysis.
5. **Network & Protocol Captures**: PCAP/PCAPNG, HAR, Fiddler SAZ, mitmproxy, or aioquic qlog analysis.
6. **Runtime Observation**: Passive browser, Electron debugging, and runtime state reconciliation.

> [!NOTE]
> Skip REA for ordinary source-code architecture reviews of projects where full source code is already present. Use REA when inspecting compiled, packed, obfuscated, or third-party targets.

---

## MCP Server Registration

REA is globally registered in Antigravity's MCP configuration (`/Users/malcolm/.gemini/config/mcp_config.json`) as:

```json
"rea": {
  "command": "npx",
  "args": [
    "-y",
    "rea-agents@6.4.0",
    "mcp"
  ]
}
```

This server exposes 170+ specialized reverse-engineering tools across binary analysis, JavaScript parsing, and runtime capture.

---

## CLI Quick Commands

When working in the terminal or inspecting artifacts outside of active MCP calls:

```bash
# Verify REA and agent readiness
npx -y rea-agents@latest doctor --client antigravity --json

# Analyze extracted JavaScript or Electron ASAR directly (zero disassembler required)
npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json

# Inspect an Evidence Bundle
npx -y rea-agents@latest inspect-evidence-bundle '{"path":"/path/to/bundle.json","detail":"summary"}'

# Update REA to latest release
rea update || npx -y rea-agents@latest setup --client antigravity --yes
```

---

## Target Routing Guide

1. **JavaScript / Electron App or ASAR**:
   - Primary: `analyze_javascript_application` (use `detail: "summary"` for large graphs).
   - Module inspection: `inspect_analysis_view` using the returned `parent_evidence_id`.
   - Feature tracing: `trace_application_feature` once a seed function or IPC message is known.

2. **Native Executable / Library (Mach-O, ELF, PE)**:
   - Open target: `open_binary` with target path and preferred provider (`hopper`, `ghidra`, or `ida`).
   - Overview: `binary_overview` for metadata and section inventories.
   - Decompile: `analyze_function` for pseudocode and assembly.
   - Cross-references: `xrefs`.
   - Cleanup: Always call `close_binary` when the investigation completes.

3. **Archive / Package Member Inventory (ZIP, APK, IPA, MSIX, DMG)**:
   - Call `open_binary` on archive path, then `inspect_artifact` for file hierarchies and cryptographic digests.

4. **Android APKs**:
   - Call `inspect_android_package` to inspect manifests, permissions, entry points, and decompiled classes.

5. **Firmware Images**:
   - Call `inspect_firmware_regions` and `extract_firmware` to discover header offsets, partitions, and filesystems.

6. **Network & Protocol Captures**:
   - Inspect HAR/SAZ/mitmproxy: `inspect_web_network_capture`.
   - Inspect PCAP/PCAPNG: `inspect_pcap_capture`.

7. **Runtime & Browser**:
   - List open targets: `list_browser_targets` / `list_electron_targets`.
   - Run scenario: `capture_browser_scenario`.

---

## Reference Guides

Detailed specialized documentation is available in the paired skill reference folder:
- [Native & Artifacts Guide](file:///Users/malcolm/.gemini/config/skills/reverse-engineer-anything/references/native-and-artifacts.md)
- [JavaScript & Electron Guide](file:///Users/malcolm/.gemini/config/skills/reverse-engineer-anything/references/javascript-applications.md)
- [Android Applications Guide](file:///Users/malcolm/.gemini/config/skills/reverse-engineer-anything/references/android-applications.md)
- [Runtime Observation Guide](file:///Users/malcolm/.gemini/config/skills/reverse-engineer-anything/references/runtime-observation.md)
- [Evidence Workflows Guide](file:///Users/malcolm/.gemini/config/skills/reverse-engineer-anything/references/evidence-workflows.md)
- [Connection & Recovery Guide](file:///Users/malcolm/.gemini/config/skills/reverse-engineer-anything/references/connection-and-recovery.md)

---

## Method & Evidence Invariants

1. **Distinguish Observations vs Inferences**:
   - Clearly separate direct observations (raw bytes, exported symbols, string tables, HTTP frames) from inferred conclusions (decompiled pseudocode logic, candidate API names).
2. **Cite Evidence IDs**:
   - Trace findings to specific `parent_evidence_id` and artifact hashes.
3. **Preserve Boundaries**:
   - Static analysis does not prove runtime execution; runtime captures reflect specific executed paths, not exhaustive behavior.
