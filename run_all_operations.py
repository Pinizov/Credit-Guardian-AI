#!/usr/bin/env python
# run_all_operations.py
"""
Unified pipeline script for Credit Guardian.

Automates the entire data update and analysis workflow:
1. Scrape legal documents from lex.bg, BNB rates, KZP complaints, NSI data
2. Import local documents (PDFs, etc.)
3. Generate embeddings using sentence-transformers (FREE, local)
4. Regenerate the legal system prompt
5. Run status check
6. (Optional) Analyze a specific contract using the selected LLM provider

Usage:
    python run_all_operations.py                           # Full pipeline
    python run_all_operations.py --skip-scrape             # Skip web scraping
    python run_all_operations.py --contract path/to/contract.pdf
    python run_all_operations.py --provider perplexity --contract file.pdf

Environment Variables:
    AI_PROVIDER: "ollama" or "perplexity" (default: ollama)
    OLLAMA_URL: Ollama server URL (default: http://localhost:11434)
    PERPLEXITY_API_KEY: Required if using Perplexity provider
"""

import argparse
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent


def print_header(title: str):
    """Print section header."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_cmd(description: str, cmd: list, cwd: str = None, optional: bool = False) -> bool:
    """
    Run a command with output capture.
    
    Args:
        description: Human-readable description
        cmd: Command as list of strings
        cwd: Working directory (default: PROJECT_ROOT)
        optional: If True, don't exit on failure
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n>>> {description}")
    print(f"    Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Print output (truncated if too long)
        output = result.stdout
        if len(output) > 2000:
            print(output[:1000])
            print(f"\n... ({len(output) - 2000} chars truncated) ...\n")
            print(output[-1000:])
        else:
            print(output)
        
        if result.returncode != 0:
            print(f"    ⚠️  Exit code: {result.returncode}")
            if not optional:
                print(f"    ❌ FAILED: {description}")
                return False
        else:
            print(f"    ✓ Done")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"    ⏱️  Timeout after 5 minutes")
        if not optional:
            return False
        return False
    except FileNotFoundError:
        print(f"    ⚠️  Command not found: {cmd[0]}")
        if not optional:
            return False
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        if not optional:
            return False
        return False


def run_scrapers(skip: bool = False):
    """Run web scrapers to update legal data."""
    print_header("1. WEB SCRAPING")
    
    if skip:
        print("    (Skipped by --skip-scrape flag)")
        return
    
    # Lex.bg - Bulgarian laws
    run_cmd(
        "Scraping lex.bg (законодателство)",
        [sys.executable, "-c", 
         "from scrapers.lex_bg_scraper import LexBgScraper; LexBgScraper().scrape_priority_laws()"],
        optional=True
    )
    
    # BNB - Interest rates
    run_cmd(
        "Scraping BNB (базова лихва)",
        [sys.executable, "-c",
         "from scrapers.bnb_rates_scraper import BNBRatesScraper; BNBRatesScraper().run('data/bnb_rates.json')"],
        optional=True
    )
    
    # KZP - Consumer complaints
    run_cmd(
        "Scraping KZP (жалби и решения)",
        [sys.executable, "-c",
         "from scrapers.kzp_complaints_scraper import KZPComplaintsScraper; KZPComplaintsScraper().run('data/kzp_data.json')"],
        optional=True
    )
    
    # NSI - Macro indicators
    run_cmd(
        "Scraping NSI (макро индикатори)",
        [sys.executable, "-c",
         "from scrapers.nsi_macro_scraper import NSIMacroScraper; NSIMacroScraper().run('data/nsi_macro.json')"],
        optional=True
    )


def run_imports():
    """Import local documents into database."""
    print_header("2. LOCAL IMPORTS")
    
    # Quick import from local folder
    if (PROJECT_ROOT / "quick_import.py").exists():
        run_cmd(
            "Importing local documents",
            [sys.executable, "quick_import.py"],
            optional=True
        )
    else:
        print("    (quick_import.py not found, skipping)")


def run_embeddings():
    """Generate embeddings for articles."""
    print_header("3. EMBEDDINGS GENERATION")
    
    if (PROJECT_ROOT / "generate_embeddings.py").exists():
        run_cmd(
            "Generating embeddings (sentence-transformers)",
            [sys.executable, "generate_embeddings.py"]
        )
    else:
        print("    (generate_embeddings.py not found, skipping)")


def run_prompt_update():
    """Regenerate the legal prompt."""
    print_header("4. PROMPT REGENERATION")
    
    script_path = PROJECT_ROOT / "scripts" / "update_legal_prompt.py"
    if script_path.exists():
        run_cmd(
            "Regenerating legal_prompt.txt",
            [sys.executable, str(script_path)]
        )
    else:
        print("    (scripts/update_legal_prompt.py not found, skipping)")


def run_status_check():
    """Run database status check."""
    print_header("5. STATUS CHECK")
    
    if (PROJECT_ROOT / "status_check.py").exists():
        run_cmd(
            "Checking database status",
            [sys.executable, "status_check.py"]
        )
    else:
        print("    (status_check.py not found, skipping)")


def analyze_contract(contract_path: str, provider: str, model: str = None):
    """Analyze a specific contract using LLM."""
    print_header("6. CONTRACT ANALYSIS")
    
    # Check if file exists
    contract_file = Path(contract_path)
    if not contract_file.exists():
        print(f"    ❌ File not found: {contract_path}")
        return
    
    print(f"    Provider: {provider}")
    print(f"    Contract: {contract_path}")
    
    try:
        # Import required modules
        sys.path.insert(0, str(PROJECT_ROOT))
        
        from ai_agent.llm_client import LLMClient
        from ai_agent.pdf_processor import PDFProcessor
        
        # Extract text from PDF
        print("\n    Extracting text from PDF...")
        if contract_path.lower().endswith('.pdf'):
            contract_text = PDFProcessor.extract_text(contract_path)
        else:
            # Assume it's a text file
            with open(contract_path, 'r', encoding='utf-8') as f:
                contract_text = f.read()
        
        print(f"    Extracted {len(contract_text)} characters")
        
        if len(contract_text) < 50:
            print("    ⚠️  Very short text extracted. Check if PDF has selectable text.")
            return
        
        # Initialize LLM client
        print(f"\n    Initializing LLM client ({provider})...")
        client = LLMClient(provider=provider, model=model)
        
        # Analyze contract
        print("\n    Analyzing contract (this may take 1-2 minutes)...")
        analysis = client.analyze_contract(contract_text)
        
        # Print results
        print("\n" + "-" * 40)
        print("ANALYSIS RESULTS")
        print("-" * 40)
        
        # Key fields
        for key in ['contract_number', 'creditor', 'principal', 'stated_apr', 'calculated_real_apr']:
            if key in analysis:
                print(f"  {key}: {analysis[key]}")
        
        # Violations
        violations = analysis.get('violations', [])
        if violations:
            print(f"\n  VIOLATIONS ({len(violations)}):")
            for i, v in enumerate(violations[:5], 1):  # Show first 5
                print(f"    {i}. [{v.get('severity', 'unknown')}] {v.get('type', 'unknown')}")
                if 'description' in v:
                    print(f"       {v['description'][:100]}...")
        
        # Summary
        if 'summary' in analysis:
            print(f"\n  SUMMARY: {analysis['summary']}")
        
        # Generate complaint
        print("\n" + "-" * 40)
        print("COMPLAINT GENERATION")
        print("-" * 40)
        
        complaint = client.generate_complaint(
            analysis,
            user_name="Тестов Потребител",
            user_address="ул. „Тестова" № 1, София"
        )
        
        # Print first 1000 chars of complaint
        print(complaint[:1000])
        if len(complaint) > 1000:
            print(f"\n... ({len(complaint) - 1000} chars more) ...")
        
    except ImportError as e:
        print(f"    ❌ Import error: {e}")
        print("    Make sure all dependencies are installed.")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="Credit Guardian - Unified Operations Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_operations.py                    # Full pipeline
  python run_all_operations.py --skip-scrape      # Skip web scraping
  python run_all_operations.py --contract doc.pdf # Analyze specific contract
  python run_all_operations.py --provider perplexity --contract doc.pdf
        """
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["ollama", "perplexity"],
        default=os.getenv("AI_PROVIDER", "ollama"),
        help="LLM provider for contract analysis (default: from AI_PROVIDER env or 'ollama')"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Model name (default: provider-specific from env)"
    )
    
    parser.add_argument(
        "--contract", "-c",
        type=str,
        help="Path to contract PDF/TXT for analysis"
    )
    
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip web scraping step"
    )
    
    parser.add_argument(
        "--only-analyze",
        action="store_true",
        help="Only analyze contract (skip all other steps)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        CREDIT GUARDIAN - UNIFIED OPERATIONS PIPELINE       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Provider: {args.provider}")
    if args.contract:
        print(f"  Contract: {args.contract}")
    
    # If only analyzing, skip other steps
    if args.only_analyze:
        if not args.contract:
            print("\n❌ --only-analyze requires --contract")
            sys.exit(1)
        analyze_contract(args.contract, args.provider, args.model)
        print("\n✓ Analysis complete!")
        return
    
    # Run full pipeline
    run_scrapers(skip=args.skip_scrape)
    run_imports()
    run_embeddings()
    run_prompt_update()
    run_status_check()
    
    # Optional contract analysis
    if args.contract:
        analyze_contract(args.contract, args.provider, args.model)
    
    # Final summary
    print_header("PIPELINE COMPLETE")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("  Next steps:")
    print("    1. Review status_check.py output above")
    print("    2. Test with: python run_all_operations.py --contract your_contract.pdf")
    print("    3. Start the server: python app.py")
    print()


if __name__ == "__main__":
    main()

