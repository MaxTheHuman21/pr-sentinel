"""
Script de debug para entender el merge de findings
"""
import sys
sys.path.insert(0, '/home/yamato/pr-sentinel')

from dotenv import load_dotenv
import os
import github_client
import repo_analyzer
import llm_reasoner
import sentinel

load_dotenv()

# Obtener datos de PR #15
repo = "MaxTheHuman21/pr-sentinel"
pr_number = 15
token = os.getenv("GITHUB_TOKEN")

print("=== OBTENIENDO DIFF ===")
diff, changed_files = github_client.get_pr_diff(repo, pr_number, token)
print(f"Archivos cambiados: {changed_files}\n")

print("=== ANÁLISIS LOCAL ===")
local_blockers, local_warnings = sentinel._local_adr_analysis(diff, {}, changed_files)
print(f"\nBlockers locales ({len(local_blockers)}):")
for i, b in enumerate(local_blockers, 1):
    print(f"  {i}. ADR={b.get('adr_reference')}, File={b.get('file')}")
    print(f"     Desc: {b.get('description')[:80]}...")

print(f"\nWarnings locales ({len(local_warnings)}):")
for i, w in enumerate(local_warnings, 1):
    print(f"  {i}. ADR={w.get('adr_reference')}, File={w.get('file')}")

print("\n=== LLAMADA AL LLM ===")
adrs, rules = sentinel._read_adrs_and_rules("demo_repo")
api_key = os.getenv("WATSONX_API_KEY")
llm_findings = sentinel._reason_with_llm(diff, adrs, rules, {}, changed_files, api_key, {})

print(f"\nBlockers del LLM ({len(llm_findings.get('blockers', []))}):")
for i, b in enumerate(llm_findings.get('blockers', []), 1):
    print(f"  {i}. ADR={b.get('adr_reference')}, File={b.get('file')}")
    print(f"     Desc: {b.get('description')[:80]}...")

print("\n=== MERGE ===")
merged = sentinel._merge_findings(llm_findings, local_blockers, local_warnings)
print(f"\nBlockers finales ({len(merged.get('blockers', []))}):")
for i, b in enumerate(merged.get('blockers', []), 1):
    print(f"  {i}. ADR={b.get('adr_reference')}, File={b.get('file')}")
    print(f"     Desc: {b.get('description')[:80]}...")

# Made with Bob
