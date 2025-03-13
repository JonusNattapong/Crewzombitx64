import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import asyncio
import logging
import threading
from ttkthemes import ThemedTk
from tktooltip import ToolTip
import traceback
from typing import Dict, Any

from main import (
    setup_argument_parser, get_preset_config, WebCrawler,
    RateLimiter, ContentExtractor, DataExporter,
    ProxyManager, ProgressTracker, ascii_art
)

class CrawlerGUI:
    def __init__(self, args):
        self.args = args
        self.root = ThemedTk(theme="arc")  # Modern theme
        self.root.title("Crew4lX64 Web Crawler")
        self.root.geometry("900x700")
        self.config = {}
        self.setup_styles()
        self.create_menu()
        self.setup_ui()
        self.setup_tooltips()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Config", command=self.load_config)
        file_menu.add_command(label="Save Config", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Crew4lX64 Web Crawler", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # URL Frame
        url_frame = ttk.LabelFrame(main_frame, text="URL Configuration", padding=10)
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(url_frame, text="Target URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(url_frame, width=70)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)

        # Basic Options Frame
        basic_frame = ttk.LabelFrame(main_frame, text="Basic Options", padding=10)
        basic_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Preset selection
        ttk.Label(basic_frame, text="Preset:").grid(row=0, column=0, sticky=tk.W)
        self.preset_combo = ttk.Combobox(basic_frame, values=[
            'basic', 'aggressive', 'stealth', 'api', 'archive', 'custom'
        ])
        self.preset_combo.set('basic')
        self.preset_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.preset_combo.bind('<<ComboboxSelected>>', self.on_preset_change)
        
        # Depth selection
        ttk.Label(basic_frame, text="Crawl Depth:").grid(row=1, column=0, sticky=tk.W)
        self.depth_spinbox = ttk.Spinbox(basic_frame, from_=1, to=5, width=5)
        self.depth_spinbox.set(2)
        self.depth_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5)

        # Browser Options Frame
        browser_frame = ttk.LabelFrame(main_frame, text="Browser Options", padding=10)
        browser_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.browser_var = tk.BooleanVar()
        self.headless_var = tk.BooleanVar(value=True)
        self.scroll_var = tk.BooleanVar()
        
        ttk.Checkbutton(browser_frame, text="Use Browser", 
                       variable=self.browser_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(browser_frame, text="Headless Mode", 
                       variable=self.headless_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(browser_frame, text="Auto-scroll", 
                       variable=self.scroll_var).grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(browser_frame, text="Wait Time (s):").grid(row=1, column=0, sticky=tk.W)
        self.wait_time_entry = ttk.Entry(browser_frame, width=5)
        self.wait_time_entry.insert(0, "2.0")
        self.wait_time_entry.grid(row=1, column=1, sticky=tk.W)

        # Output Options Frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Options", padding=10)
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(output_frame, text="Format:").grid(row=0, column=0, sticky=tk.W)
        self.output_format = ttk.Combobox(output_frame, values=['json', 'csv', 'md', 'html', 'all'])
        self.output_format.set('json')
        self.output_format.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(output_frame, text="Directory:").grid(row=1, column=0, sticky=tk.W)
        self.output_dir = ttk.Entry(output_frame, width=50)
        self.output_dir.insert(0, 'scraped_output')
        self.output_dir.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(output_frame, text="Browse", 
                  command=self.browse_output_dir).grid(row=1, column=2)

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, length=300,
                                          mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, columnspan=3)

        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Start Crawling", 
                  command=self.start_crawl).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Stop", 
                  command=self.stop_crawl).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear Log",
                  command=self.clear_log).grid(row=0, column=2, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def setup_tooltips(self):
        tooltips = {
            self.url_entry: "Enter the target URL to crawl",
            self.preset_combo: "Select a predefined configuration preset",
            self.depth_spinbox: "Set how deep the crawler should go (1-5)",
            self.browser_var: "Enable browser-based crawling for JavaScript-heavy sites",
            self.headless_var: "Run browser without GUI",
            self.scroll_var: "Automatically scroll pages to load dynamic content",
            self.wait_time_entry: "Time to wait for dynamic content to load",
            self.output_format: "Choose the format for exported data",
            self.output_dir: "Select where to save the crawled data"
        }
        
        for widget, text in tooltips.items():
            ToolTip(widget, text)

    # ... Add remaining methods for functionality (load_config, save_config, etc.) ...
