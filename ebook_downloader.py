"""
Ebook Downloader untuk Pendidikan Anak Berkebutuhan Khusus
============================================================
Script ini membantu mengunduh ebook dari berbagai sumber yang tersedia.

Catatan Penting:
- Link asli (book.onread.com) adalah link affiliate yang mengarah ke halaman pembelian
- Script ini menyediakan alternatif untuk mengunduh ebook dari sumber-sumber legal
"""

import requests
import os
from urllib.parse import urlparse, unquote
from pathlib import Path
import re


class EbookDownloader:
    def __init__(self, download_folder="downloads"):
        """Inisialisasi downloader dengan folder tujuan download."""
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    
    def sanitize_filename(self, filename):
        """Bersihkan nama file dari karakter yang tidak valid."""
        # Hapus karakter yang tidak valid untuk nama file Windows
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Batasi panjang nama file
    
    def download_file(self, url, filename=None):
        """
        Download file dari URL.
        
        Args:
            url: URL file yang akan didownload
            filename: Nama file (opsional, akan diambil dari URL jika tidak disediakan)
        
        Returns:
            Path file yang telah didownload, atau None jika gagal
        """
        try:
            print(f"\n📥 Mencoba mengunduh dari: {url}")
            
            # Kirim request
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Tentukan nama file
            if not filename:
                # Coba dapatkan dari Content-Disposition header
                content_disp = response.headers.get('Content-Disposition')
                if content_disp and 'filename=' in content_disp:
                    filename = re.findall('filename="?([^"]+)"?', content_disp)
                    filename = filename[0] if filename else None
                
                # Jika tidak ada, ambil dari URL
                if not filename:
                    parsed_url = urlparse(url)
                    filename = unquote(os.path.basename(parsed_url.path))
                
                # Jika masih kosong, beri nama default
                if not filename or filename == '':
                    filename = 'ebook_downloaded.pdf'
            
            filename = self.sanitize_filename(filename)
            filepath = self.download_folder / filename
            
            # Download dengan progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ Berhasil mengunduh: {filepath}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Gagal mengunduh: {e}")
            return None
    
    def download_from_direct_url(self, url):
        """Download dari URL langsung (jika tersedia)."""
        return self.download_file(url)


def main():
    """Fungsi utama untuk menjalankan downloader."""
    print("=" * 60)
    print("📚 EBOOK DOWNLOADER - Pendidikan Anak Berkebutuhan Khusus")
    print("=" * 60)
    
    downloader = EbookDownloader(download_folder="downloads")
    
    print("\n⚠️  CATATAN PENTING:")
    print("-" * 40)
    print("""
Link yang Anda berikan (book.onread.com) adalah link affiliate/iklan
yang mengarah ke halaman pembelian, bukan link download langsung.

Sumber-sumber alternatif untuk ebook topik serupa:
1. ResearchGate - https://www.researchgate.net (banyak jurnal & ebook gratis)
2. Scribd - https://www.scribd.com (perlu akun, ada versi gratis)
3. Repository Universitas - cari di Google dengan: 
   "Pendidikan Anak Berkebutuhan Khusus filetype:pdf site:ac.id"
4. Google Scholar - https://scholar.google.com
5. Perpustakaan Digital Nasional - https://e-resources.perpusnas.go.id
    """)
    
    print("\n" + "=" * 60)
    print("PILIH OPSI:")
    print("=" * 60)
    print("1. Download dari URL langsung (jika Anda punya link PDF)")
    print("2. Cari di repository universitas Indonesia")
    print("3. Keluar")
    
    while True:
        try:
            choice = input("\nMasukkan pilihan (1-3): ").strip()
            
            if choice == "1":
                url = input("Masukkan URL file PDF/ebook: ").strip()
                if url:
                    downloader.download_from_direct_url(url)
                else:
                    print("❌ URL tidak valid!")
            
            elif choice == "2":
                print("\n🔍 Repository Universitas Indonesia yang menyediakan ebook gratis:")
                repositories = [
                    ("UMJ Repository", "https://repository.umj.ac.id"),
                    ("USD Repository", "https://repository.usd.ac.id"),
                    ("Perpustakaan UPI", "http://perpustakaan.upi.edu"),
                    ("Repository UNY", "https://eprints.uny.ac.id"),
                    ("Perpusnas Digital", "https://e-resources.perpusnas.go.id"),
                ]
                
                for name, url in repositories:
                    print(f"   • {name}: {url}")
                
                print("\n💡 Tips: Cari di Google dengan query:")
                print('   "Pendidikan Anak Berkebutuhan Khusus Tunagrahita filetype:pdf site:ac.id"')
            
            elif choice == "3":
                print("\n👋 Terima kasih telah menggunakan Ebook Downloader!")
                break
            
            else:
                print("❌ Pilihan tidak valid. Silakan pilih 1-3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Program dihentikan oleh pengguna.")
            break


if __name__ == "__main__":
    main()
