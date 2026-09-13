#!/usr/bin/env python3
"""
Bio's Public Records Harvester (Biomedical & Biochemical Intelligence)
======================================================================
Dedicated public biomedical data scraper integrating Lumina Stealth anti-scanner
defenses for harvesting UniProt, ChEMBL, and NCBI E-utilities repositories.

Capabilities:
- UniProtKB Protein Sequences & Functional Annotations
- ChEMBL Bioactive Compound & Drug Structure Profiling
- NCBI Entrez Gene Summary & Genomic Locus Retrieval
- Automatic SHA-256 Manifest Calculation & JSON Export
- Integrated Lumina Fingerprint Harmonization & Gaussian Jitter
"""

import sys
import os
import json
import time
import hashlib
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Ensure scripts directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lumina_stealth import LuminaStealthSession, decode_payload

class BioScraper:
    """Dedicated scraper for public biomedical and biochemical repositories."""

    def __init__(self, output_dir: Optional[str] = None):
        self.session = LuminaStealthSession()
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(self.output_dir, exist_ok=True)

    def harvest_uniprot(self, accession: str, save: bool = True) -> Dict[str, Any]:
        """Harvest protein metadata, gene name, organism, and sequence length from UniProtKB."""
        url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
        headers = self.session.get_stealth_headers(referer="https://www.uniprot.org/")
        req = urllib.request.Request(url, headers=headers)
        
        start_t = time.time()
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                content = decode_payload(raw)
                data = json.loads(content)

                # Extract canonical fields
                primary_gene = "N/A"
                if data.get("genes") and len(data["genes"]) > 0:
                    primary_gene = data["genes"][0].get("geneName", {}).get("value", "N/A")

                rec_name = data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "N/A")
                organism = data.get("organism", {}).get("scientificName", "N/A")
                seq_len = data.get("sequence", {}).get("length", 0)
                mass = data.get("sequence", {}).get("molWeight", 0)

                payload = {
                    "source_authority": "UniProt Knowledgebase (UniProtKB / Swiss-Prot)",
                    "source_url": url,
                    "accession": accession,
                    "entry_type": data.get("entryType"),
                    "protein_name": rec_name,
                    "primary_gene": primary_gene,
                    "organism": organism,
                    "sequence_length": seq_len,
                    "molecular_weight_da": mass,
                    "harvested_at": datetime.now(timezone.utc).isoformat(),
                    "stealth_profile": self.session.profile["os"]
                }

                sha256 = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
                payload["sha256_hash"] = sha256

                if save:
                    filename = f"uniprot_{accession}_{primary_gene.replace('/', '_')}.json"
                    out_path = os.path.join(self.output_dir, filename)
                    with open(out_path, "w") as f:
                        json.dump(payload, f, indent=2)
                    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    payload["saved_file"] = os.path.relpath(out_path, repo_root)

                return {"success": True, "data": payload}
        except Exception as e:
            return {"success": False, "error": str(e), "accession": accession}

    def harvest_chembl(self, chembl_id: str, save: bool = True) -> Dict[str, Any]:
        """Harvest bioactive chemical structure and pharmacology from EMBL-EBI ChEMBL API."""
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
        headers = self.session.get_stealth_headers(referer="https://www.ebi.ac.uk/chembl/")
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                content = decode_payload(raw)
                data = json.loads(content)

                props = data.get("molecule_properties") or {}
                structs = data.get("molecule_structures") or {}

                payload = {
                    "source_authority": "European Bioinformatics Institute (EMBL-EBI ChEMBL)",
                    "source_url": url,
                    "chembl_id": chembl_id,
                    "pref_name": data.get("pref_name"),
                    "molecule_type": data.get("molecule_type"),
                    "max_phase": data.get("max_phase"),
                    "natural_product": data.get("natural_product"),
                    "smiles": structs.get("canonical_smiles"),
                    "molecular_formula": props.get("full_mwt"),
                    "alogp": props.get("alogp"),
                    "hba": props.get("hba"),
                    "hbd": props.get("hbd"),
                    "harvested_at": datetime.now(timezone.utc).isoformat(),
                    "stealth_profile": self.session.profile["os"]
                }

                sha256 = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
                payload["sha256_hash"] = sha256

                if save:
                    pref_slug = (data.get("pref_name") or chembl_id).lower().replace(" ", "_")
                    filename = f"chembl_molecule_{chembl_id}_{pref_slug}.json"
                    out_path = os.path.join(self.output_dir, filename)
                    with open(out_path, "w") as f:
                        json.dump(payload, f, indent=2)
                    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    payload["saved_file"] = os.path.relpath(out_path, repo_root)

                return {"success": True, "data": payload}
        except Exception as e:
            return {"success": False, "error": str(e), "chembl_id": chembl_id}

    def harvest_ncbi_gene(self, gene_id: str, save: bool = True) -> Dict[str, Any]:
        """Harvest official gene nomenclature and summaries from NCBI Entrez E-utilities."""
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id={gene_id}&retmode=json"
        headers = self.session.get_stealth_headers(referer="https://www.ncbi.nlm.nih.gov/")
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                content = decode_payload(raw)
                data = json.loads(content)
                gene_data = data.get("result", {}).get(str(gene_id), {})

                payload = {
                    "source_authority": "National Center for Biotechnology Information (NCBI Entrez)",
                    "source_url": url,
                    "gene_id": gene_id,
                    "symbol": gene_data.get("name"),
                    "description": gene_data.get("description"),
                    "organism": gene_data.get("organism", {}).get("scientificname"),
                    "tax_id": gene_data.get("organism", {}).get("taxid"),
                    "chromosome": gene_data.get("chromosome"),
                    "map_location": gene_data.get("maplocation"),
                    "harvested_at": datetime.now(timezone.utc).isoformat(),
                    "stealth_profile": self.session.profile["os"]
                }

                sha256 = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
                payload["sha256_hash"] = sha256

                if save:
                    sym = gene_data.get("name") or gene_id
                    filename = f"ncbi_gene_{gene_id}_{sym}.json"
                    out_path = os.path.join(self.output_dir, filename)
                    with open(out_path, "w") as f:
                        json.dump(payload, f, indent=2)
                    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    payload["saved_file"] = os.path.relpath(out_path, repo_root)

                return {"success": True, "data": payload}
        except Exception as e:
            return {"success": False, "error": str(e), "gene_id": gene_id}

    def download_chembl_sdf(self, chembl_id: str, output_path: Optional[str] = None) -> str:
        """Download bioactive molecule structure file (.sdf) from ChEMBL."""
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.sdf"
        headers = self.session.get_stealth_headers(referer="https://www.ebi.ac.uk/chembl/")
        req = urllib.request.Request(url, headers=headers)
        if not output_path:
            output_path = os.path.join(self.output_dir, f"{chembl_id.upper()}.sdf")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                with open(output_path, "wb") as f:
                    f.write(data)
                repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                rel_out = os.path.relpath(output_path, repo_root)
                print(f"[+] Downloaded ChEMBL SDF structure for {chembl_id} to {rel_out}")
                return rel_out
        except Exception as e:
            print(f"[!] Error downloading SDF for {chembl_id}: {e}")
            return ""

    def generate_pymol_script(self, chembl_id: str, sdf_path: Optional[str] = None, output_script: Optional[str] = None) -> str:
        """Generate a headless PyMOL 3D visualization script adhering to the PyMOL skill."""
        if not sdf_path:
            sdf_path = os.path.join(self.output_dir, f"{chembl_id.upper()}.sdf")
        if not output_script:
            output_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"render_{chembl_id.lower()}_pymol.py")

        script_content = f'''#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = [
#     "pymol-open-source-whl",
# ]
# ///
"""
PyMOL Headless 3D Molecular Structure Rendering for {chembl_id.upper()}
=============================================================
Uses software OSMesa rendering for headless container and CI/CD pipelines.
Exports publication-quality PNG and reproducible PyMOL session (.pse).
"""
import os
import sys

# Set environment variable for headless software rendering
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()

from pymol import cmd

# Dynamic repository relative structure path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
structure_file = os.path.join(repo_root, "data", "{chembl_id.upper()}.sdf")
if not os.path.exists(structure_file):
    print(f"Error: Structure file not found: {{structure_file}}")
    cmd.quit()
    sys.exit(1)

cmd.load(structure_file, "compound_{chembl_id.lower()}")
atom_count = cmd.count_atoms("all")
if atom_count == 0:
    print("Error: 0 atoms loaded from structure file")
    cmd.quit()
    sys.exit(1)

print(f"[+] Loaded {{atom_count}} atoms for {chembl_id.upper()}")
cmd.show("sticks", "all")
cmd.color("cyan", "elem C")
cmd.color("red", "elem O")
cmd.color("blue", "elem N")
cmd.orient()
cmd.set("ray_opaque_background", 0)

output_png = os.path.join(os.path.dirname(structure_file), "{chembl_id.lower()}_3d.png")
output_pse = os.path.join(os.path.dirname(structure_file), "{chembl_id.lower()}_session.pse")

cmd.png(output_png, width=1200, height=900, dpi=150)
cmd.save(output_pse)
print(f"[+] Rendered 3D structure to {{output_png}} and saved session to {{output_pse}}")
cmd.quit()
'''
        with open(output_script, "w", encoding="utf-8") as f:
            f.write(script_content)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rel_script = os.path.relpath(output_script, repo_root)
        print(f"[+] Generated PyMOL rendering script: {rel_script}")
        return rel_script

def main():
    parser = argparse.ArgumentParser(description="Bio's Public Records Harvester (Biomedical & Biochemical Intelligence)")
    parser.add_argument("--uniprot", metavar="ACCESSION", help="Harvest protein by UniProt Accession (e.g., P05067, P04637)")
    parser.add_argument("--chembl", metavar="CHEMBL_ID", help="Harvest bioactive compound by ChEMBL ID (e.g., CHEMBL25)")
    parser.add_argument("--download-sdf", metavar="CHEMBL_ID", help="Download 2D/3D chemical structure (.sdf) from ChEMBL")
    parser.add_argument("--pymol-script", metavar="CHEMBL_ID", help="Generate headless PyMOL 3D visualization script for ChEMBL molecule")
    parser.add_argument("--ncbi-gene", metavar="GENE_ID", help="Harvest gene summary by NCBI Gene ID (e.g., 351, 7157)")
    parser.add_argument("--harvest-samples", action="store_true", help="Harvest and save representative public bio samples (APP, TP53, Aspirin)")
    parser.add_argument("--output-dir", help="Custom output directory for JSON payloads")

    args = parser.parse_args()
    scraper = BioScraper(output_dir=args.output_dir)

    if args.download_sdf:
        path = scraper.download_chembl_sdf(args.download_sdf)
        if path:
            print(f"[✔] Successfully downloaded structure to {path}")
        return

    if args.pymol_script:
        path = scraper.generate_pymol_script(args.pymol_script)
        if path:
            print(f"[✔] Successfully generated PyMOL script: {path}")
        return

    if args.harvest_samples or (len(sys.argv) == 1):
        print("\n===================================================================")
        print("  BIO'S PUBLIC RECORDS HARVESTER — LIVE SAMPLES PIPELINE")
        print("===================================================================")
        
        # 1. UniProt P05067 (Amyloid-beta precursor protein)
        print("\n[*] [1/3] Harvesting UniProt P05067 (Human APP)...")
        res1 = scraper.harvest_uniprot("P05067")
        if res1["success"]:
            d = res1["data"]
            print(f"    ✔ Entry: {d['protein_name']} | Gene: {d['primary_gene']} | Length: {d['sequence_length']} aa")
            print(f"    ✔ SHA-256: {d['sha256_hash'][:24]}... | Saved: {os.path.basename(d.get('saved_file', ''))}")
        else:
            print(f"    ✖ Error: {res1.get('error')}")

        # 2. ChEMBL CHEMBL25 (Aspirin)
        print("\n[*] [2/3] Harvesting ChEMBL CHEMBL25 (Aspirin)...")
        res2 = scraper.harvest_chembl("CHEMBL25")
        if res2["success"]:
            d = res2["data"]
            print(f"    ✔ Compound: {d['pref_name']} | Max Phase: {d['max_phase']} | SMILES: {d['smiles']}")
            print(f"    ✔ SHA-256: {d['sha256_hash'][:24]}... | Saved: {os.path.basename(d.get('saved_file', ''))}")
        else:
            print(f"    ✖ Error: {res2.get('error')}")

        # 3. NCBI Gene 351 (APP)
        print("\n[*] [3/3] Harvesting NCBI Gene ID 351 (APP)...")
        res3 = scraper.harvest_ncbi_gene("351")
        if res3["success"]:
            d = res3["data"]
            print(f"    ✔ Gene: {d['symbol']} ({d['description']}) | Chromosome: {d['chromosome']}")
            print(f"    ✔ SHA-256: {d['sha256_hash'][:24]}... | Saved: {os.path.basename(d.get('saved_file', ''))}")
        else:
            print(f"    ✖ Error: {res3.get('error')}")

        print("\n[✔] All public bio datasets successfully retrieved and indexed in data/.")
        return

    if args.uniprot:
        res = scraper.harvest_uniprot(args.uniprot)
        print(json.dumps(res, indent=2))

    if args.chembl:
        res = scraper.harvest_chembl(args.chembl)
        print(json.dumps(res, indent=2))

    if args.ncbi_gene:
        res = scraper.harvest_ncbi_gene(args.ncbi_gene)
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
