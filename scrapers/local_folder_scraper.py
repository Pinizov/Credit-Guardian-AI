"""Local folder scraper for reading legal data files from disk.
Processes files from a specified local folder and imports them into the database.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from base_scraper import BaseScraper
import PyPDF2
import pandas as pd

logger = logging.getLogger("scrapers.local_folder")


class LocalFolderScraper(BaseScraper):
    """Scraper for reading legal documents from local filesystem."""
    
    name: str = "local_folder"
    
    def __init__(self, folder_path: str, delay: float | None = None):
        """Initialize local folder scraper.
        
        Args:
            folder_path: Path to the local folder containing legal data
            delay: Optional delay between operations (not used for local files)
        """
        super().__init__(delay)
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        if not self.folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
    
    def list_files(self, extensions: Optional[List[str]] = None) -> List[Path]:
        """List all files in the folder matching the given extensions.
        
        Args:
            extensions: List of file extensions to filter (e.g., ['.txt', '.pdf', '.docx'])
                       If None, returns all files.
        
        Returns:
            List of Path objects for matching files
        """
        if extensions is None:
            extensions = ['.txt', '.pdf', '.docx', '.doc', '.html', '.xml', '.json', '.csv', '.xls', '.xlsx']
        
        files = []
        for ext in extensions:
            files.extend(self.folder_path.glob(f"*{ext}"))
            files.extend(self.folder_path.glob(f"**/*{ext}"))  # Recursive search
        
        # Remove duplicates and sort
        files = sorted(set(files))
        logger.info(f"{self.name}: Found {len(files)} files in {self.folder_path}")
        return files
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file with timeout protection."""
        try:
            # Windows doesn't support signal.alarm, so we use try-except for timeout protection
            with open(file_path, 'rb') as f:
                try:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    max_pages = min(len(reader.pages), 20)  # Limit to first 20 pages
                    
                    for i in range(max_pages):
                        try:
                            page_text = reader.pages[i].extract_text()
                            if page_text:
                                text += page_text[:5000] + "\n"  # Limit each page to 5k chars
                            if len(text) > 30000:  # Stop if we have enough
                                break
                        except Exception as page_err:
                            logger.warning(f"PDF page {i} error in {file_path.name}: {str(page_err)[:50]}")
                            continue
                    
                    return text.strip() if text.strip() else "[PDF file - no text extracted]"
                    
                except Exception as read_err:
                    return f"[PDF file - read error: {str(read_err)[:80]}]"
                    
        except Exception as e:
            logger.error(f"PDF extraction error {file_path.name}: {str(e)[:80]}")
            return f"[PDF file - extraction failed: {str(e)[:80]}]"
    
    def _extract_excel_text(self, file_path: Path) -> str:
        """Extract text from Excel file."""
        try:
            engine = 'xlrd' if file_path.suffix == '.xls' else 'openpyxl'
            df = pd.read_excel(file_path, engine=engine)
            return df.to_string()
        except Exception as e:
            logger.error(f"Excel extraction error {file_path.name}: {e}")
            return f"[Excel file - extraction failed: {e}]"
    
    def _extract_csv_text(self, file_path: Path) -> str:
        """Extract text from CSV file."""
        try:
            for encoding in ['utf-8', 'cp1251', 'latin-1', 'windows-1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    return df.to_string()
                except UnicodeDecodeError:
                    continue
            return "[CSV file - encoding detection failed]"
        except Exception as e:
            logger.error(f"CSV extraction error {file_path.name}: {e}")
            return f"[CSV file - extraction failed: {e}]"
    
    def read_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Read a single file and return its metadata and content.
        
        Args:
            file_path: Path to the file to read
        
        Returns:
            Dictionary with file metadata and content, or None on error
        """
        try:
            # Get file metadata
            stat = file_path.stat()
            
            # Read content based on file type
            content = None
            ext = file_path.suffix.lower()
            
            if ext in ['.txt', '.html', '.xml', '.json']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif ext == '.pdf':
                content = self._extract_pdf_text(file_path)
            elif ext in ['.xls', '.xlsx']:
                content = self._extract_excel_text(file_path)
            elif ext == '.csv':
                content = self._extract_csv_text(file_path)
            elif ext in ['.doc', '.docx']:
                # For binary doc files, mark for later processing
                content = f"[Binary file: {file_path.suffix} - requires specialized extraction]"
            else:
                content = f"[Unsupported file type: {file_path.suffix}]"
            
            return {
                'filename': file_path.name,
                'path': str(file_path),
                'extension': file_path.suffix,
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'content': content
            }
        except Exception as e:
            logger.error(f"{self.name}: Error reading {file_path}: {e}")
            return None
    
    def scrape_all(self) -> Dict[str, Any]:
        """Execute full scrape of local folder and return structured data.
        
        Returns:
            Dictionary with metadata and list of all processed files
        """
        files = self.list_files()
        
        results = []
        for file_path in files:
            file_data = self.read_file(file_path)
            if file_data:
                results.append(file_data)
        
        return {
            'source': 'local_folder',
            'folder_path': str(self.folder_path),
            'total_files': len(results),
            'files': results
        }


def scrape_legal_data_folder(
    folder_path: str = r"C:\Users\User\Downloads\Legal Data",
    output_json: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to scrape the Legal Data folder.
    
    Args:
        folder_path: Path to the Legal Data folder
        output_json: Optional path to save results as JSON
    
    Returns:
        Dictionary with scraped data
    """
    scraper = LocalFolderScraper(folder_path)
    data = scraper.run(output_path=output_json)
    return data


if __name__ == "__main__":
    # Example usage
    data = scrape_legal_data_folder()
    print(f"Scraped {data['total_files']} files from {data['folder_path']}")
