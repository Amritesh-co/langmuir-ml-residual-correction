#!/usr/bin/env python3
"""
Download free/open-access research papers for fluoride adsorption project
"""

import os
import requests
from pathlib import Path
from typing import Dict, List, Tuple

# Set proper headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

# Papers with direct PDF/download links
PAPERS: Dict[str, Dict[str, str]] = {
    # ArXiv papers (direct PDF links)
    "R28": {
        "title": "XGBoost: A Scalable Tree Boosting System",
        "url": "https://arxiv.org/pdf/1603.02754.pdf",
        "type": "arxiv"
    },
    
    # WHO documents (direct PDF or redirects)
    "R30": {
        "title": "WHO Drinking Water Guidelines (2017)",
        "url": "https://apps.who.int/iris/bitstream/handle/10665/254637/9789241549950-eng.pdf",
        "type": "who"
    },
    "R31": {
        "title": "WHO Fluoride in Drinking Water",
        "url": "https://apps.who.int/iris/bitstream/handle/10665/42034/924156173X.pdf",
        "type": "who"
    },
    
    # MDPI papers (open access - try /pdf endpoint)
    "R16_R33": {
        "title": "Key Parameters in Adsorption for Effective Fluoride Removal",
        "url": "https://www.mdpi.com/2076-3417/14/5/2161/pdf",
        "type": "mdpi"
    },
    
    # Public domain / Open access journals
    "R25": {
        "title": "Latin Hypercube Sampling (McKay 1979)",
        "url": "https://www.jstor.org/stable/1268722",
        "type": "jstor"  # May need institution login
    },
    
    # ResearchGate (might not work without login)
    "R7": {
        "title": "Coconut Husk Fixed Bed Adsorption",
        "url": "https://www.researchgate.net/publication/323670439",
        "type": "researchgate"
    },
    
    # IOP Science Open Access
    "R29": {
        "title": "ML for Groundwater Fluoride Prediction",
        "url": "https://iopscience.iop.org/article/10.1088/1748-9326/aad487/pdf",
        "type": "iop"
    },
    
    # Statistical Learning textbook (free from authors)
    "R36": {
        "title": "An Introduction to Statistical Learning (ISLR)",
        "url": "https://www.statlearning.com/s/ISLR2.pdf",
        "type": "textbook"
    },
    
    # Springer Open Access (direct HTML may work)
    "R15": {
        "title": "Al-OH Activated Carbon for Fluoride Removal",
        "url": "https://link.springer.com/content/pdf/10.1007/s13201-016-0479-z.pdf",
        "type": "springer"
    },
    
    # Wiley Open Access
    "R18": {
        "title": "Hazardous Anion Removal - Comparative Study",
        "url": "https://onlinelibrary.wiley.com/doi/pdf/10.1155/2018/3975948",
        "type": "wiley"
    },
    
    # JMLR (Journal of Machine Learning Research)
    "R35": {
        "title": "Scikit-learn: Machine Learning in Python",
        "url": "https://jmlr.org/papers/volume12/pedregosa11a/pedregosa11a.pdf",
        "type": "jmlr"
    },
    
    # Innoriginal (open-access journal)
    "R10": {
        "title": "Coconut Shell Isotherm and Kinetics",
        "url": "https://innoriginal.com/index.php/iijs/article/view/221/pdf",
        "type": "journal"
    },
}

def download_paper(ref: str, paper_info: Dict[str, str], output_dir: Path) -> Tuple[bool, str]:
    """
    Download a single paper. Returns (success, message)
    """
    url = paper_info["url"]
    title = paper_info["title"]
    paper_type = paper_info["type"]
    
    filename = output_dir / f"{ref}_{title.replace(' ', '_')[:40]}.pdf"
    
    try:
        print(f"\n📥 Downloading {ref}: {title}...", end=" ")
        
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True, stream=True)
        response.raise_for_status()
        
        # Check if we got a PDF
        content_type = response.headers.get('content-type', '').lower()
        
        if 'pdf' in content_type or response.content[:4] == b'%PDF':
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_kb = filename.stat().st_size / 1024
            print(f"✅ {size_kb:.1f} KB")
            return True, f"{ref}: Downloaded {size_kb:.1f} KB"
        else:
            print(f"⚠️ Not a PDF (got {content_type})")
            return False, f"{ref}: Wrong content type ({content_type})"
    
    except requests.RequestException as e:
        print(f"❌ Error: {str(e)[:50]}")
        return False, f"{ref}: {str(e)[:50]}"
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return False, f"{ref}: {str(e)[:50]}"

def main():
    output_dir = Path(__file__).parent
    
    print("=" * 70)
    print("RESEARCH PAPERS DOWNLOADER")
    print("Fluoride Adsorption Project - Free/Open-Access Papers")
    print("=" * 70)
    
    print(f"\nTarget folder: {output_dir}")
    print(f"Papers to download: {len(PAPERS)}")
    
    successful = []
    failed = []
    
    for ref, paper_info in PAPERS.items():
        success, message = download_paper(ref, paper_info, output_dir)
        if success:
            successful.append(message)
        else:
            failed.append(message)
    
    # Print summary
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"\n✅ Successful: {len(successful)}")
    for msg in successful:
        print(f"   {msg}")
    
    if failed:
        print(f"\n⚠️ Failed/Skipped: {len(failed)}")
        for msg in failed:
            print(f"   {msg}")
    
    print(f"\n📊 Success rate: {len(successful)}/{len(PAPERS)} ({100*len(successful)//len(PAPERS)}%)")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        os.system("pip install requests -q")
    
    main()
