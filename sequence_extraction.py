from Bio import Entrez, SeqIO
import os
import time

# Set your email for NCBI Entrez
Entrez.email = "anummunirmughal@gmail.com"  # <-- Replace with your email

# Search parameters
organism = "Streptococcus pyogenes"
resistant_keywords = ["resistant", "antibiotic resistance", "macrolide-resistant", "erm", "mef"]
susceptible_keywords = ["susceptible", "sensitive"]

def search_genomes(keyword, max_records=5):
    query = f'"{organism}"[Organism] AND ("complete genome"[Title] OR "whole genome"[Title]) AND {keyword}'
    handle = Entrez.esearch(db="nucleotide", term=query, retmax=max_records)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]

def fetch_and_save_genome(genome_id, label):
    # Fetch summary for metadata
    summary_handle = Entrez.esummary(db="nucleotide", id=genome_id)
    summary = Entrez.read(summary_handle)[0]
    summary_handle.close()
    title = summary.get("Title", "")

    # Fetch the genome sequence in FASTA format
    with Entrez.efetch(db="nucleotide", id=genome_id, rettype="fasta", retmode="text") as handle:
        records = list(SeqIO.parse(handle, "fasta"))  # Use parse, not read
        if not records:
            print(f"Warning: No sequence found for {genome_id} ({title}). Skipping.")
            return
        filename = f"{label}_{genome_id}.txt"
        with open(filename, "w") as out_handle:
            SeqIO.write(records, out_handle, "fasta")
    print(f"Saved {label} genome: {title} to {filename}")

def main():
    os.makedirs("genomes", exist_ok=True)
    os.chdir("genomes")

    # Search and download resistant genomes
    print("Searching for resistant genomes...")
    resistant_ids = set()
    for kw in resistant_keywords:
        ids = search_genomes(kw)
        resistant_ids.update(ids)
        time.sleep(0.5)  # Be gentle to NCBI servers

    for genome_id in resistant_ids:
        fetch_and_save_genome(genome_id, "resistant")
        time.sleep(0.5)

    # Search and download susceptible genomes
    print("Searching for susceptible genomes...")
    susceptible_ids = set()
    for kw in susceptible_keywords:
        ids = search_genomes(kw)
        susceptible_ids.update(ids)
        time.sleep(0.5)

    for genome_id in susceptible_ids:
        # Avoid downloading the same genome twice
        if genome_id in resistant_ids:
            continue
        fetch_and_save_genome(genome_id, "susceptible")
        time.sleep(0.5)

if __name__ == "__main__":
    main()