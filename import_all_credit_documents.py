# file: import_all_credit_documents.py
import os
from scrapers.local_folder_scraper import LocalFolderScraper
from quick_import import quick_import_folder   # вече съдържа прогрес‑бар и DB запис

# 1. Създайте временна папка, където ще „монтираме“ всичките източници
temp_root = r"C:\credit-guardian\import_all"
os.makedirs(temp_root, exist_ok=True)

# 2. Създайте junction‑ове (Windows) – ако вече съществуват, ги прескочете
def make_junction(src, dst):
    if not os.path.isdir(dst):
        os.system(f'mklink /J "{dst}" "{src}"')

make_junction(r"C:\credit-guardian\legal data", os.path.join(temp_root, "legal_data"))
make_junction(r"F:\credit", os.path.join(temp_root, "credit_misc"))

# 3. Стартирайте импорт с филтър за ключовата дума "кредит"
class CreditKeywordScraper(LocalFolderScraper):
    def _process_file(self, file_path):
        # използваме съществуващия екстракт, след което филтрираме
        content = super()._extract_content(file_path)
        if not content:
            return None
        if "кредит" not in content.lower():
            self.logger.info(f"Skipping {file_path} – missing keyword")
            return None
        return content

scraper = CreditKeywordScraper(temp_root)
data = scraper.run("data/credit_documents.json")   # JSON е опционален, основно за дебъг

# 4. Заредете резултатите в DB чрез вече готовата функция
quick_import_folder(temp_root)   # (функцията се имплементира в quick_import.py)

print("✅ Импортът завърши! Пуснете `python status_check.py` за преглед.")
