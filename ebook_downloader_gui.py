"""
Ebook Downloader GUI - Modern & Premium Design dengan Fitur Pencarian
======================================================================
Aplikasi GUI untuk mencari dan mengunduh ebook dari berbagai sumber.
PERBAIKAN: Validasi file PDF dan peringatan link pencarian
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
from urllib.parse import urlparse, unquote, quote_plus
from pathlib import Path
import re
import threading
import webbrowser


class ModernStyle:
    """Konfigurasi warna dan style modern."""
    BG_PRIMARY = "#0f0f23"
    BG_SECONDARY = "#1a1a2e"
    BG_CARD = "#16213e"
    BG_INPUT = "#1f2937"
    BG_HOVER = "#2d3748"
    
    ACCENT_PRIMARY = "#6366f1"
    ACCENT_SECONDARY = "#8b5cf6"
    ACCENT_SUCCESS = "#10b981"
    ACCENT_WARNING = "#f59e0b"
    ACCENT_ERROR = "#ef4444"
    ACCENT_INFO = "#3b82f6"
    
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = (FONT_FAMILY, 22, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 11)
    FONT_HEADING = (FONT_FAMILY, 13, "bold")
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_SMALL = (FONT_FAMILY, 9)
    FONT_BUTTON = (FONT_FAMILY, 10, "bold")


class AnimatedButton(tk.Canvas):
    """Custom animated button dengan hover effects."""
    
    def __init__(self, parent, text, command, width=150, height=40, 
                 color=ModernStyle.ACCENT_PRIMARY, hover_color=ModernStyle.ACCENT_SECONDARY,
                 bg=ModernStyle.BG_SECONDARY):
        super().__init__(parent, width=width, height=height, 
                        bg=bg, highlightthickness=0)
        
        self.command = command
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.width = width
        self.height = height
        self.current_color = color
        self.bg = bg
        
        self._draw_button()
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _draw_button(self):
        self.delete("all")
        self._create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                  radius=8, fill=self.current_color, outline="")
        self.create_text(self.width//2, self.height//2, text=self.text,
                        fill=ModernStyle.TEXT_PRIMARY, font=ModernStyle.FONT_BUTTON)
    
    def _create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self.current_color = self.hover_color
        self._draw_button()
        self.config(cursor="hand2")
    
    def _on_leave(self, event):
        self.current_color = self.color
        self._draw_button()
    
    def _on_click(self, event):
        if self.command:
            self.command()


class SearchResultItem(tk.Frame):
    """Widget untuk menampilkan hasil pencarian."""
    
    def __init__(self, parent, title, url, source, description="", 
                 is_direct_download=False, on_download=None, on_open=None):
        super().__init__(parent, bg=ModernStyle.BG_SECONDARY)
        
        self.url = url
        self.on_download = on_download
        self.is_direct = is_direct_download
        
        self.pack(fill=tk.X, pady=3, padx=5)
        
        content = tk.Frame(self, bg=ModernStyle.BG_SECONDARY)
        content.pack(fill=tk.X, padx=12, pady=10)
        
        # Title and source
        title_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY)
        title_frame.pack(fill=tk.X)
        
        # Source badge with color based on type
        badge_color = ModernStyle.ACCENT_SUCCESS if is_direct_download else ModernStyle.ACCENT_INFO
        source_label = tk.Label(
            title_frame,
            text=source,
            font=(ModernStyle.FONT_FAMILY, 8, "bold"),
            fg=ModernStyle.BG_PRIMARY,
            bg=badge_color,
            padx=6,
            pady=2
        )
        source_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Direct download indicator
        if is_direct_download:
            direct_label = tk.Label(
                title_frame,
                text="📥 DIRECT",
                font=(ModernStyle.FONT_FAMILY, 7, "bold"),
                fg=ModernStyle.ACCENT_SUCCESS,
                bg=ModernStyle.BG_SECONDARY,
                padx=4
            )
            direct_label.pack(side=tk.LEFT, padx=(0, 8))
        else:
            search_label = tk.Label(
                title_frame,
                text="🔍 SEARCH",
                font=(ModernStyle.FONT_FAMILY, 7),
                fg=ModernStyle.ACCENT_WARNING,
                bg=ModernStyle.BG_SECONDARY,
                padx=4
            )
            search_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Title
        title_label = tk.Label(
            title_frame,
            text=title[:70] + "..." if len(title) > 70 else title,
            font=ModernStyle.FONT_BODY,
            fg=ModernStyle.ACCENT_PRIMARY,
            bg=ModernStyle.BG_SECONDARY,
            cursor="hand2"
        )
        title_label.pack(side=tk.LEFT, fill=tk.X)
        title_label.bind("<Button-1>", lambda e: webbrowser.open(url))
        
        # URL preview
        url_label = tk.Label(
            content,
            text=url[:60] + "..." if len(url) > 60 else url,
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_SECONDARY,
            anchor=tk.W
        )
        url_label.pack(fill=tk.X, pady=(3, 0))
        
        # Description
        if description:
            desc_label = tk.Label(
                content,
                text=description[:100] + "..." if len(description) > 100 else description,
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_SECONDARY,
                bg=ModernStyle.BG_SECONDARY,
                anchor=tk.W,
                wraplength=500
            )
            desc_label.pack(fill=tk.X, pady=(3, 0))
        
        # Action buttons
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        
        if is_direct_download:
            # Download button for direct links
            download_btn = tk.Label(
                btn_frame,
                text="⬇️ Download Langsung",
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_PRIMARY,
                bg=ModernStyle.ACCENT_SUCCESS,
                padx=12,
                pady=5,
                cursor="hand2"
            )
            download_btn.pack(side=tk.LEFT, padx=(0, 8))
            download_btn.bind("<Button-1>", lambda e: on_download(url) if on_download else None)
        else:
            # Open in browser for search links
            open_btn = tk.Label(
                btn_frame,
                text="🔍 Cari di Browser",
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_PRIMARY,
                bg=ModernStyle.ACCENT_INFO,
                padx=12,
                pady=5,
                cursor="hand2"
            )
            open_btn.pack(side=tk.LEFT, padx=(0, 8))
            open_btn.bind("<Button-1>", lambda e: webbrowser.open(url))
        
        # Copy URL button
        copy_btn = tk.Label(
            btn_frame,
            text="📋 Copy URL",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_SECONDARY,
            bg=ModernStyle.BG_INPUT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        copy_btn.pack(side=tk.LEFT)
        copy_btn.bind("<Button-1>", lambda e: self._copy_to_clipboard(url))
    
    def _copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "URL telah disalin ke clipboard!")


class EbookDownloaderGUI:
    """Aplikasi GUI utama untuk Ebook Downloader dengan fitur pencarian."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📚 Ebook Downloader Pro - Search & Download")
        self.root.geometry("1000x800")
        self.root.configure(bg=ModernStyle.BG_PRIMARY)
        self.root.resizable(True, True)
        
        self._center_window()
        
        self.download_folder = Path("downloads")
        self.download_folder.mkdir(exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        self.search_results = []
        self._create_widgets()
        
    def _center_window(self):
        self.root.update_idletasks()
        width = 1000
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        main_frame = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        self._create_header(main_frame)
        self._create_tabs(main_frame)
        self._create_status_bar(main_frame)
    
    def _create_header(self, parent):
        header_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            header_frame,
            text="📚 Ebook Downloader Pro",
            font=ModernStyle.FONT_TITLE,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.BG_PRIMARY
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Cari & Download Ebook dengan Mudah",
            font=ModernStyle.FONT_SUBTITLE,
            fg=ModernStyle.TEXT_SECONDARY,
            bg=ModernStyle.BG_PRIMARY
        )
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))
    
    def _create_tabs(self, parent):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Custom.TNotebook', 
                       background=ModernStyle.BG_PRIMARY,
                       borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.TEXT_SECONDARY,
                       padding=[20, 10],
                       font=ModernStyle.FONT_BODY)
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', ModernStyle.ACCENT_PRIMARY)],
                 foreground=[('selected', ModernStyle.TEXT_PRIMARY)])
        
        self.notebook = ttk.Notebook(parent, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Search
        search_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(search_tab, text="🔍 Pencarian Ebook")
        self._create_search_tab(search_tab)
        
        # Tab 2: Direct Download
        download_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(download_tab, text="⬇️ Download Langsung")
        self._create_download_tab(download_tab)
        
        # Tab 3: Repository Links
        repo_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(repo_tab, text="📖 Sumber Ebook")
        self._create_repository_tab(repo_tab)
    
    def _create_search_tab(self, parent):
        # Info banner
        info_banner = tk.Frame(parent, bg=ModernStyle.ACCENT_WARNING)
        info_banner.pack(fill=tk.X, pady=(10, 10), padx=5)
        
        info_text = tk.Label(
            info_banner,
            text="⚠️ PENTING: Link dengan label 'SEARCH' akan membuka browser, bukan download langsung. "
                 "Cari file PDF di halaman hasil pencarian, lalu copy URL-nya ke tab 'Download Langsung'.",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.BG_PRIMARY,
            bg=ModernStyle.ACCENT_WARNING,
            wraplength=900,
            pady=8,
            padx=10
        )
        info_text.pack(fill=tk.X)
        
        # Search input section
        search_card = tk.Frame(parent, bg=ModernStyle.BG_CARD)
        search_card.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        search_inner = tk.Frame(search_card, bg=ModernStyle.BG_CARD)
        search_inner.pack(fill=tk.X, padx=20, pady=20)
        
        search_title = tk.Label(
            search_inner,
            text="🔍 Cari Ebook / PDF",
            font=ModernStyle.FONT_HEADING,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.BG_CARD
        )
        search_title.pack(anchor=tk.W)
        
        search_desc = tk.Label(
            search_inner,
            text="Masukkan judul buku, penulis, atau kata kunci",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_CARD
        )
        search_desc.pack(anchor=tk.W, pady=(2, 10))
        
        input_row = tk.Frame(search_inner, bg=ModernStyle.BG_CARD)
        input_row.pack(fill=tk.X)
        
        self.search_entry = tk.Entry(
            input_row,
            font=ModernStyle.FONT_BODY,
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=ModernStyle.BG_INPUT,
            highlightcolor=ModernStyle.ACCENT_PRIMARY
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.search_entry.insert(0, "Contoh: Pendidikan Anak Berkebutuhan Khusus")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_entry.bind("<Return>", lambda e: self._start_search())
        
        search_btn = AnimatedButton(
            input_row, 
            text="🔍 Cari", 
            command=self._start_search,
            width=120, 
            height=40,
            bg=ModernStyle.BG_CARD
        )
        search_btn.pack(side=tk.RIGHT)
        
        # Search options
        options_row = tk.Frame(search_inner, bg=ModernStyle.BG_CARD)
        options_row.pack(fill=tk.X, pady=(15, 0))
        
        options_label = tk.Label(
            options_row,
            text="Sumber:",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_SECONDARY,
            bg=ModernStyle.BG_CARD
        )
        options_label.pack(side=tk.LEFT)
        
        self.search_source = tk.StringVar(value="all")
        
        sources = [
            ("Semua", "all"),
            ("Repository Indonesia", "repo_id"),
            ("Google Scholar", "scholar"),
        ]
        
        for text, value in sources:
            rb = tk.Radiobutton(
                options_row,
                text=text,
                variable=self.search_source,
                value=value,
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_SECONDARY,
                bg=ModernStyle.BG_CARD,
                selectcolor=ModernStyle.BG_INPUT,
                activebackground=ModernStyle.BG_CARD,
                activeforeground=ModernStyle.ACCENT_PRIMARY
            )
            rb.pack(side=tk.LEFT, padx=(15, 0))
        
        # Results section
        results_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        results_header = tk.Frame(results_frame, bg=ModernStyle.BG_PRIMARY)
        results_header.pack(fill=tk.X, pady=(0, 10))
        
        self.results_label = tk.Label(
            results_header,
            text="📋 Hasil Pencarian",
            font=ModernStyle.FONT_HEADING,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.BG_PRIMARY
        )
        self.results_label.pack(side=tk.LEFT)
        
        self.results_count = tk.Label(
            results_header,
            text="",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_PRIMARY
        )
        self.results_count.pack(side=tk.LEFT, padx=(10, 0))
        
        # Legend
        legend_frame = tk.Frame(results_header, bg=ModernStyle.BG_PRIMARY)
        legend_frame.pack(side=tk.RIGHT)
        
        legend1 = tk.Label(
            legend_frame,
            text="📥 DIRECT = Download langsung",
            font=(ModernStyle.FONT_FAMILY, 8),
            fg=ModernStyle.ACCENT_SUCCESS,
            bg=ModernStyle.BG_PRIMARY
        )
        legend1.pack(side=tk.LEFT, padx=(0, 15))
        
        legend2 = tk.Label(
            legend_frame,
            text="🔍 SEARCH = Buka di browser",
            font=(ModernStyle.FONT_FAMILY, 8),
            fg=ModernStyle.ACCENT_WARNING,
            bg=ModernStyle.BG_PRIMARY
        )
        legend2.pack(side=tk.LEFT)
        
        # Scrollable results
        results_container = tk.Frame(results_frame, bg=ModernStyle.BG_CARD)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        self.results_canvas = tk.Canvas(
            results_container, 
            bg=ModernStyle.BG_CARD,
            highlightthickness=0
        )
        self.results_scrollbar = ttk.Scrollbar(
            results_container, 
            orient=tk.VERTICAL, 
            command=self.results_canvas.yview
        )
        
        self.results_inner = tk.Frame(self.results_canvas, bg=ModernStyle.BG_CARD)
        
        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)
        
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.results_canvas.create_window(
            (0, 0), 
            window=self.results_inner, 
            anchor=tk.NW
        )
        
        self.results_inner.bind("<Configure>", self._on_results_configure)
        self.results_canvas.bind("<Configure>", self._on_canvas_configure)
        
        self._show_search_placeholder()
    
    def _on_results_configure(self, event):
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.results_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _show_search_placeholder(self):
        for widget in self.results_inner.winfo_children():
            widget.destroy()
        
        placeholder = tk.Label(
            self.results_inner,
            text="💡 Masukkan kata kunci dan klik 'Cari' untuk mencari ebook\n\n"
                 "📌 Tips pencarian:\n"
                 "• Gunakan judul buku yang spesifik\n"
                 "• Tambahkan nama penulis untuk hasil lebih akurat\n"
                 "• Hasil pencarian akan membuka browser\n"
                 "• Setelah menemukan file PDF, copy URL-nya\n"
                 "• Paste URL di tab 'Download Langsung' untuk download",
            font=ModernStyle.FONT_BODY,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_CARD,
            justify=tk.LEFT
        )
        placeholder.pack(pady=40)
    
    def _create_download_tab(self, parent):
        # URL Input card
        url_card = tk.Frame(parent, bg=ModernStyle.BG_CARD)
        url_card.pack(fill=tk.X, pady=(10, 15), padx=5)
        
        url_inner = tk.Frame(url_card, bg=ModernStyle.BG_CARD)
        url_inner.pack(fill=tk.X, padx=20, pady=20)
        
        url_title = tk.Label(
            url_inner,
            text="⬇️ Download dari URL Langsung",
            font=ModernStyle.FONT_HEADING,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.BG_CARD
        )
        url_title.pack(anchor=tk.W)
        
        url_desc = tk.Label(
            url_inner,
            text="Paste URL file PDF/ebook yang sudah Anda temukan dari browser",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_CARD
        )
        url_desc.pack(anchor=tk.W, pady=(2, 10))
        
        # Tips
        tips_frame = tk.Frame(url_inner, bg=ModernStyle.ACCENT_INFO)
        tips_frame.pack(fill=tk.X, pady=(0, 15))
        
        tips_text = tk.Label(
            tips_frame,
            text="💡 Tips: URL yang valid biasanya berakhiran .pdf atau langsung mengarah ke file. "
                 "Contoh: https://repository.upi.edu/files/thesis.pdf",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.ACCENT_INFO,
            wraplength=800,
            pady=8,
            padx=10
        )
        tips_text.pack(fill=tk.X)
        
        url_row = tk.Frame(url_inner, bg=ModernStyle.BG_CARD)
        url_row.pack(fill=tk.X)
        
        self.url_entry = tk.Entry(
            url_row,
            font=ModernStyle.FONT_BODY,
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=ModernStyle.BG_INPUT,
            highlightcolor=ModernStyle.ACCENT_PRIMARY
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.url_entry.insert(0, "https://example.com/ebook.pdf")
        self.url_entry.bind("<FocusIn>", self._on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_focus_out)
        self.url_entry.bind("<Return>", lambda e: self._start_download())
        
        download_btn = AnimatedButton(
            url_row, 
            text="⬇️ Download", 
            command=self._start_download,
            width=140, 
            height=40,
            color=ModernStyle.ACCENT_SUCCESS,
            hover_color="#059669",
            bg=ModernStyle.BG_CARD
        )
        download_btn.pack(side=tk.RIGHT)
        
        # Folder selection
        folder_row = tk.Frame(url_inner, bg=ModernStyle.BG_CARD)
        folder_row.pack(fill=tk.X, pady=(15, 0))
        
        self.folder_label = tk.Label(
            folder_row,
            text=f"📁 Folder: {self.download_folder.absolute()}",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_CARD
        )
        self.folder_label.pack(side=tk.LEFT)
        
        change_folder_btn = tk.Label(
            folder_row,
            text="📂 Ubah Folder",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.ACCENT_PRIMARY,
            bg=ModernStyle.BG_CARD,
            cursor="hand2"
        )
        change_folder_btn.pack(side=tk.LEFT, padx=(15, 0))
        change_folder_btn.bind("<Button-1>", self._change_folder)
        
        open_folder_btn = tk.Label(
            folder_row,
            text="📂 Buka Folder",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.ACCENT_INFO,
            bg=ModernStyle.BG_CARD,
            cursor="hand2"
        )
        open_folder_btn.pack(side=tk.LEFT, padx=(15, 0))
        open_folder_btn.bind("<Button-1>", lambda e: os.startfile(self.download_folder))
        
        # Progress section
        progress_card = tk.Frame(parent, bg=ModernStyle.BG_CARD)
        progress_card.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        progress_inner = tk.Frame(progress_card, bg=ModernStyle.BG_CARD)
        progress_inner.pack(fill=tk.X, padx=20, pady=15)
        
        self.download_status = tk.Label(
            progress_inner,
            text="Status: Siap untuk download",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_SECONDARY,
            bg=ModernStyle.BG_CARD
        )
        self.download_status.pack(anchor=tk.W)
        
        style = ttk.Style()
        style.configure(
            "Download.Horizontal.TProgressbar",
            troughcolor=ModernStyle.BG_INPUT,
            background=ModernStyle.ACCENT_SUCCESS,
            thickness=10
        )
        
        self.progress_bar = ttk.Progressbar(
            progress_inner,
            style="Download.Horizontal.TProgressbar",
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(8, 0))
        
        # Log section
        log_card = tk.Frame(parent, bg=ModernStyle.BG_CARD)
        log_card.pack(fill=tk.BOTH, expand=True, padx=5)
        
        log_inner = tk.Frame(log_card, bg=ModernStyle.BG_CARD)
        log_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        log_header = tk.Frame(log_inner, bg=ModernStyle.BG_CARD)
        log_header.pack(fill=tk.X)
        
        log_title = tk.Label(
            log_header,
            text="📋 Log Aktivitas",
            font=ModernStyle.FONT_HEADING,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.BG_CARD
        )
        log_title.pack(side=tk.LEFT)
        
        clear_btn = tk.Label(
            log_header,
            text="🗑️ Bersihkan",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_CARD,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT)
        clear_btn.bind("<Button-1>", lambda e: self._clear_log())
        
        log_frame = tk.Frame(log_inner, bg=ModernStyle.BG_INPUT)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 9),
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)
        
        self._log("✨ Selamat datang di Ebook Downloader Pro!")
        self._log("💡 Paste URL file PDF/ebook lalu klik Download")
        self._log("⚠️ Pastikan URL mengarah langsung ke file (.pdf, .epub, dll)")
        self._log("-" * 50)
    
    def _create_repository_tab(self, parent):
        info_card = tk.Frame(parent, bg=ModernStyle.BG_CARD)
        info_card.pack(fill=tk.X, pady=(10, 15), padx=5)
        
        info_inner = tk.Frame(info_card, bg=ModernStyle.BG_CARD)
        info_inner.pack(fill=tk.X, padx=20, pady=20)
        
        info_title = tk.Label(
            info_inner,
            text="📖 Sumber Ebook Gratis",
            font=ModernStyle.FONT_HEADING,
            fg=ModernStyle.TEXT_PRIMARY,
            bg=ModernStyle.BG_CARD
        )
        info_title.pack(anchor=tk.W)
        
        info_desc = tk.Label(
            info_inner,
            text="Klik untuk membuka di browser, cari ebook, lalu copy URL file PDF untuk didownload",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_CARD
        )
        info_desc.pack(anchor=tk.W, pady=(2, 0))
        
        # Repository grid
        repos_frame = tk.Frame(parent, bg=ModernStyle.BG_PRIMARY)
        repos_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        repositories = [
            ("🔬 ResearchGate", "https://www.researchgate.net", 
             "Jurnal & Paper", "Download paper ilmiah gratis"),
            ("📚 Scribd", "https://www.scribd.com", 
             "Ebook & Dokumen", "Perpustakaan digital gratis"),
            ("🔍 Google Scholar", "https://scholar.google.com", 
             "Pencarian Akademik", "Cari paper & jurnal"),
            ("🎓 Repository UMJ", "https://repository.umj.ac.id", 
             "Univ. Muhammadiyah JKT", "Skripsi & tesis"),
            ("📖 Repository USD", "https://repository.usd.ac.id", 
             "Univ. Sanata Dharma", "Karya ilmiah"),
            ("🏛️ Perpusnas Digital", "https://e-resources.perpusnas.go.id", 
             "Perpustakaan Nasional", "E-resources WNI"),
            ("📕 Open Library", "https://openlibrary.org", 
             "Internet Archive", "Jutaan buku digital"),
            ("📗 Project Gutenberg", "https://www.gutenberg.org", 
             "Buku Klasik", "60K+ ebook gratis"),
            ("📘 Library Genesis", "https://libgen.is", 
             "Perpustakaan Digital", "Paper akademik"),
            ("🎓 Repository UPI", "http://repository.upi.edu", 
             "Univ. Pendidikan ID", "Karya pendidikan"),
            ("📚 Repository UNY", "https://eprints.uny.ac.id", 
             "Univ. Negeri Yogya", "Repository ilmiah"),
            ("🏫 Repository UGM", "https://etd.repository.ugm.ac.id", 
             "Univ. Gadjah Mada", "Tesis & disertasi"),
        ]
        
        for i, (name, url, subtitle, desc) in enumerate(repositories):
            row = i // 3
            col = i % 3
            
            repo_card = tk.Frame(repos_frame, bg=ModernStyle.BG_CARD, cursor="hand2")
            repo_card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            repos_frame.columnconfigure(col, weight=1)
            repos_frame.rowconfigure(row, weight=1)
            
            inner = tk.Frame(repo_card, bg=ModernStyle.BG_CARD)
            inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
            
            name_label = tk.Label(
                inner,
                text=name,
                font=ModernStyle.FONT_BODY,
                fg=ModernStyle.ACCENT_PRIMARY,
                bg=ModernStyle.BG_CARD
            )
            name_label.pack(anchor=tk.W)
            
            subtitle_label = tk.Label(
                inner,
                text=subtitle,
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_SECONDARY,
                bg=ModernStyle.BG_CARD
            )
            subtitle_label.pack(anchor=tk.W)
            
            desc_label = tk.Label(
                inner,
                text=desc,
                font=(ModernStyle.FONT_FAMILY, 8),
                fg=ModernStyle.TEXT_MUTED,
                bg=ModernStyle.BG_CARD,
                wraplength=200
            )
            desc_label.pack(anchor=tk.W, pady=(3, 0))
            
            for widget in [repo_card, inner, name_label, subtitle_label, desc_label]:
                widget.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
                widget.bind("<Enter>", lambda e, rc=repo_card: rc.configure(bg=ModernStyle.BG_SECONDARY))
                widget.bind("<Leave>", lambda e, rc=repo_card: rc.configure(bg=ModernStyle.BG_CARD))
    
    def _create_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_bar = tk.Label(
            status_frame,
            text="💡 Tips: Cari ebook di Google dengan 'judul buku filetype:pdf site:ac.id'",
            font=ModernStyle.FONT_SMALL,
            fg=ModernStyle.TEXT_MUTED,
            bg=ModernStyle.BG_SECONDARY,
            pady=8
        )
        self.status_bar.pack(fill=tk.X)
    
    # Event handlers
    def _on_search_focus_in(self, event):
        if self.search_entry.get() == "Contoh: Pendidikan Anak Berkebutuhan Khusus":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=ModernStyle.TEXT_PRIMARY)
    
    def _on_search_focus_out(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Contoh: Pendidikan Anak Berkebutuhan Khusus")
            self.search_entry.config(fg=ModernStyle.TEXT_MUTED)
    
    def _on_url_focus_in(self, event):
        if self.url_entry.get() == "https://example.com/ebook.pdf":
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg=ModernStyle.TEXT_PRIMARY)
    
    def _on_url_focus_out(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "https://example.com/ebook.pdf")
            self.url_entry.config(fg=ModernStyle.TEXT_MUTED)
    
    def _change_folder(self, event=None):
        folder = filedialog.askdirectory(title="Pilih Folder Download")
        if folder:
            self.download_folder = Path(folder)
            self.folder_label.config(text=f"📁 Folder: {self.download_folder.absolute()}")
            self._log(f"📁 Folder download diubah ke: {self.download_folder}")
    
    def _log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def _clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self._log("📋 Log dibersihkan")
    
    def _update_status(self, status, color=None):
        self.download_status.config(text=f"Status: {status}")
        if color:
            self.download_status.config(fg=color)
    
    def _update_progress(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()
    
    # Search functions
    def _start_search(self):
        query = self.search_entry.get().strip()
        
        if not query or query == "Contoh: Pendidikan Anak Berkebutuhan Khusus":
            messagebox.showwarning("Peringatan", "Masukkan kata kunci pencarian!")
            return
        
        for widget in self.results_inner.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(
            self.results_inner,
            text="🔄 Membuat link pencarian...",
            font=ModernStyle.FONT_BODY,
            fg=ModernStyle.TEXT_SECONDARY,
            bg=ModernStyle.BG_CARD
        )
        loading_label.pack(pady=30)
        
        self.results_count.config(text="Memproses...")
        self.status_bar.config(text=f"🔍 Mencari: {query}")
        
        thread = threading.Thread(target=self._perform_search, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _perform_search(self, query):
        source = self.search_source.get()
        results = []
        
        try:
            if source == "all" or source == "repo_id":
                results.extend(self._search_indonesian_repos(query))
            
            if source == "all" or source == "scholar":
                results.extend(self._search_google_scholar(query))
            
            self.root.after(0, lambda: self._display_results(results))
            
        except Exception as e:
            self.root.after(0, lambda: self._show_search_error(str(e)))
    
    def _search_google_scholar(self, query):
        """Create Google Scholar search links."""
        results = []
        encoded = quote_plus(query)
        
        results.append({
            'title': f"📚 Cari '{query}' di Google Scholar",
            'url': f"https://scholar.google.com/scholar?q={encoded}",
            'source': 'Scholar',
            'description': 'Cari paper dan jurnal akademik',
            'is_direct': False
        })
        
        results.append({
            'title': f"📄 Cari '{query}' PDF di Google",
            'url': f"https://www.google.com/search?q={encoded}+filetype:pdf",
            'source': 'Google',
            'description': 'Cari file PDF langsung',
            'is_direct': False
        })
        
        return results
    
    def _search_indonesian_repos(self, query):
        """Create Indonesian repository search links."""
        results = []
        encoded = quote_plus(query)
        
        # Direct repo searches
        repos = [
            ("Repository UPI", "repository.upi.edu", "Universitas Pendidikan Indonesia"),
            ("Repository UMJ", "repository.umj.ac.id", "Universitas Muhammadiyah Jakarta"),
            ("Repository UNY", "eprints.uny.ac.id", "Universitas Negeri Yogyakarta"),
            ("Repository UGM", "etd.repository.ugm.ac.id", "Universitas Gadjah Mada"),
        ]
        
        for name, domain, desc in repos:
            results.append({
                'title': f"🎓 Cari '{query}' di {name}",
                'url': f"https://www.google.com/search?q={encoded}+site:{domain}+filetype:pdf",
                'source': 'Repo ID',
                'description': f'Cari PDF di {desc}',
                'is_direct': False
            })
        
        # General Indonesian academic search
        results.append({
            'title': f"🇮🇩 Cari '{query}' di semua universitas Indonesia",
            'url': f"https://www.google.com/search?q={encoded}+site:ac.id+filetype:pdf",
            'source': 'Repo ID',
            'description': 'Cari PDF di semua universitas Indonesia (.ac.id)',
            'is_direct': False
        })
        
        return results
    
    def _display_results(self, results):
        for widget in self.results_inner.winfo_children():
            widget.destroy()
        
        if not results:
            no_results = tk.Label(
                self.results_inner,
                text="😔 Tidak ada hasil ditemukan\n\nCoba kata kunci yang berbeda",
                font=ModernStyle.FONT_BODY,
                fg=ModernStyle.TEXT_MUTED,
                bg=ModernStyle.BG_CARD
            )
            no_results.pack(pady=50)
            self.results_count.config(text="0 hasil")
            return
        
        self.results_count.config(text=f"{len(results)} link pencarian")
        self.status_bar.config(text=f"✅ {len(results)} link pencarian tersedia")
        
        for result in results:
            SearchResultItem(
                self.results_inner,
                title=result['title'],
                url=result['url'],
                source=result['source'],
                description=result.get('description', ''),
                is_direct_download=result.get('is_direct', False),
                on_download=self._download_from_search
            )
    
    def _show_search_error(self, error):
        for widget in self.results_inner.winfo_children():
            widget.destroy()
        
        error_label = tk.Label(
            self.results_inner,
            text=f"❌ Error: {error}\n\nSilakan coba lagi",
            font=ModernStyle.FONT_BODY,
            fg=ModernStyle.ACCENT_ERROR,
            bg=ModernStyle.BG_CARD
        )
        error_label.pack(pady=50)
        self.results_count.config(text="Error")
    
    def _download_from_search(self, url):
        self.notebook.select(1)
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.url_entry.config(fg=ModernStyle.TEXT_PRIMARY)
        self._start_download()
    
    # Download functions
    def _start_download(self):
        url = self.url_entry.get().strip()
        
        if not url or url == "https://example.com/ebook.pdf":
            messagebox.showwarning("Peringatan", "Masukkan URL terlebih dahulu!")
            return
        
        if not url.startswith(('http://', 'https://')):
            messagebox.showwarning("Peringatan", "URL harus dimulai dengan http:// atau https://")
            return
        
        # Check if it's a search URL
        if 'google.com/search' in url or 'scholar.google.com' in url:
            if messagebox.askyesno("URL Pencarian Terdeteksi", 
                "URL ini adalah halaman pencarian Google, bukan file PDF langsung.\n\n"
                "Apakah Anda ingin membuka halaman ini di browser untuk mencari file PDF?\n\n"
                "Setelah menemukan file PDF, copy URL-nya dan paste kembali di sini."):
                webbrowser.open(url)
            return
        
        thread = threading.Thread(target=self._download_file, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _sanitize_filename(self, filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]
    
    def _is_valid_pdf(self, filepath):
        """Check if file is a valid PDF."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(8)
                return header.startswith(b'%PDF')
        except:
            return False
    
    def _download_file(self, url):
        try:
            self._update_status("Menghubungi server...", ModernStyle.ACCENT_WARNING)
            self._log(f"\n📥 Mengunduh: {url}")
            self._update_progress(0)
            
            response = requests.get(url, headers=self.headers, stream=True, timeout=60, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            self._log(f"📋 Content-Type: {content_type}")
            
            # Warning if it's HTML
            if 'text/html' in content_type:
                self._update_status("⚠️ Bukan file PDF!", ModernStyle.ACCENT_WARNING)
                self._log("⚠️ PERINGATAN: Server mengembalikan halaman HTML, bukan file PDF!")
                self._log("   Kemungkinan penyebab:")
                self._log("   - URL adalah halaman web, bukan link download langsung")
                self._log("   - File memerlukan login atau akses khusus")
                self._log("   - Server redirect ke halaman lain")
                self._log("💡 Coba buka URL di browser dan cari link download langsung")
                
                self.root.after(0, lambda: messagebox.showwarning(
                    "Bukan File PDF",
                    "URL ini mengembalikan halaman HTML, bukan file PDF.\n\n"
                    "Kemungkinan penyebab:\n"
                    "• URL adalah halaman web, bukan link download\n"
                    "• File memerlukan login\n\n"
                    "Solusi:\n"
                    "1. Buka URL di browser\n"
                    "2. Cari tombol 'Download PDF'\n"
                    "3. Klik kanan pada tombol download\n"
                    "4. Pilih 'Copy link address'\n"
                    "5. Paste link tersebut di sini"
                ))
                self._update_progress(0)
                return
            
            # Determine filename
            content_disp = response.headers.get('Content-Disposition')
            filename = None
            
            if content_disp and 'filename=' in content_disp:
                matches = re.findall('filename="?([^"]+)"?', content_disp)
                filename = matches[0] if matches else None
            
            if not filename:
                parsed_url = urlparse(url)
                filename = unquote(os.path.basename(parsed_url.path))
            
            if not filename or filename == '' or '.' not in filename:
                if 'pdf' in content_type:
                    filename = 'ebook_downloaded.pdf'
                elif 'epub' in content_type:
                    filename = 'ebook_downloaded.epub'
                else:
                    filename = 'ebook_downloaded.pdf'
            
            filename = self._sanitize_filename(filename)
            filepath = self.download_folder / filename
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            self._update_status("Mengunduh...", ModernStyle.ACCENT_PRIMARY)
            self._log(f"📄 Nama file: {filename}")
            if total_size > 0:
                self._log(f"📊 Ukuran: {total_size / 1024 / 1024:.2f} MB")
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self._update_progress(progress)
            
            self._update_progress(100)
            
            # Validate downloaded file
            is_pdf = self._is_valid_pdf(filepath)
            
            if not is_pdf and filename.endswith('.pdf'):
                self._update_status("⚠️ File bukan PDF valid!", ModernStyle.ACCENT_WARNING)
                self._log("⚠️ File yang didownload BUKAN PDF valid!")
                self._log("   File mungkin berisi halaman HTML atau error")
                
                # Rename to .html for inspection
                new_path = filepath.with_suffix('.html')
                filepath.rename(new_path)
                self._log(f"   File di-rename ke: {new_path.name}")
                
                self.root.after(0, lambda: messagebox.showwarning(
                    "File Bukan PDF",
                    f"File yang didownload bukan PDF valid.\n\n"
                    f"File telah disimpan sebagai:\n{new_path.name}\n\n"
                    f"Buka file tersebut di browser untuk melihat isinya "
                    f"dan cari link download yang benar."
                ))
            else:
                self._update_status("Selesai! ✅", ModernStyle.ACCENT_SUCCESS)
                self._log(f"✅ Berhasil! Disimpan di: {filepath}")
                self.status_bar.config(text=f"✅ Download selesai: {filename}")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sukses", 
                    f"Ebook berhasil didownload!\n\n📁 Lokasi:\n{filepath}"
                ))
            
        except requests.exceptions.Timeout:
            self._update_status("Timeout! ⏱️", ModernStyle.ACCENT_ERROR)
            self._log("❌ Error: Koneksi timeout")
            self.root.after(0, lambda: messagebox.showerror("Error", "Koneksi timeout!"))
            
        except requests.exceptions.HTTPError as e:
            self._update_status("Error! ❌", ModernStyle.ACCENT_ERROR)
            self._log(f"❌ HTTP Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"HTTP Error: {e}"))
            
        except Exception as e:
            self._update_status("Error! ❌", ModernStyle.ACCENT_ERROR)
            self._log(f"❌ Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))
    
    def run(self):
        self.root.mainloop()


def main():
    app = EbookDownloaderGUI()
    app.run()


if __name__ == "__main__":
    main()
