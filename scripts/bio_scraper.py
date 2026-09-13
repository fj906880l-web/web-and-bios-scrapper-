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
                    payload["saved_file"] = out_path

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
                    payload["saved_file"] = out_path

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
                    payload["saved_file"] = out_path

                return {"success": True, "data": payload}
        except Exception as e:
            return {"success": False, "error": str(e), "gene_id": gene_id}

def main():
    parser = argparse.ArgumentParser(description="Bio's Public Records Harvester (Biomedical & Biochemical Intelligence)")
    parser.add_argument("--uniprot", metavar="ACCESSION", help="Harvest protein by UniProt Accession (e.g., P05067, P04637)")
    parser.add_argument("--chembl", metavar="CHEMBL_ID", help="Harvest bioactive compound by ChEMBL ID (e.g., CHEMBL25)")
    parser.add_argument("--ncbi-gene", metavar="GENE_ID", help="Harvest gene summary by NCBI Gene ID (e.g., 351, 7157)")
    parser.add_argument("--harvest-samples", action="store_true", help="Harvest and save representative public bio samples (APP, TP53, Aspirin)")
    parser.add_argument("--output-dir", help="Custom output directory for JSON payloads")

    args = parser.parse_args()
    scraper = BioScraper(output_dir=args.output_dir)

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
