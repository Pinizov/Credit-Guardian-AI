"""Quick test of local data import - just count files and show structure."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))

from local_folder_scraper import LocalFolderScraper

def test_import():
    print("Testing local legal data folder...")
    
    folder_path = r"C:\Users\User\Downloads\Legal Data"
    scraper = LocalFolderScraper(folder_path)
    
    print(f"\nScanning {folder_path}...")
    data = scraper.scrape_all()
    
    print(f"\n✅ Found {data['total_files']} files")
    print("\nFile breakdown:")
    
    extensions = {}
    for file in data['files']:
        ext = file['extension']
        extensions[ext] = extensions.get(ext, 0) + 1
        print(f"  - {file['filename'][:60]} ({file['size_bytes']:,} bytes)")
    
    print("\n📊 Summary by extension:")
    for ext, count in sorted(extensions.items()):
        print(f"  {ext}: {count} files")

if __name__ == "__main__":
    test_import()
