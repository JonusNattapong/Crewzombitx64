#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import queue
import signal
import threading
import sys

from Crew4lX64.main import main

class CrawlerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Crew4lX64 Web Crawler")
        self.root.geometry("800x600")
        self.config = {}
        self.output_text = None
        self.progress_bar = None
        self.progress_value = tk.IntVar()
        self.setup_ui()
        self.crawl_thread = None
        self.terminate_crawl = False
        self.log_queue = queue.Queue()  # Create instance variable for log queue
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) to gracefully terminate the crawl."""
        if self.crawl_thread and self.crawl_thread.is_alive():
            self.terminate_crawl = True
            print("Terminating crawler...")
            self.enable_ui()
            self.log_message("Crawling terminated.")
        self.root.quit()

    def setup_ui(self):
        ttk.Label(self.root, text="URL:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(self.root, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(self.root, text="Preset:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.preset_combo = ttk.Combobox(
            self.root, values=['basic', 'aggressive', 'stealth', 'api', 'archive', 'custom']
        )
        self.preset_combo.set('basic')
        self.preset_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.root, text="Depth:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.depth_var = tk.StringVar(value='2')
        self.depth_spinbox = ttk.Spinbox(self.root, from_=1, to=5, width=5, textvariable=self.depth_var)
        self.depth_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.root, text="Output Format:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_format_combo = ttk.Combobox(self.root, values=['json', 'csv', 'md', 'html', 'all'])
        self.output_format_combo.set('json')
        self.output_format_combo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.root, text="Output Directory:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_dir_entry = ttk.Entry(self.root, width=50)
        self.output_dir_entry.insert(0, 'scraped_output')
        self.output_dir_entry.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(self.root, text="Browse", command=self.browse_output_dir).grid(
            row=4, column=2, padx=5, pady=5
        )

        browser_frame = ttk.LabelFrame(self.root, text="Browser Options", padding=10)
        browser_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.use_browser_var = tk.BooleanVar()
        self.use_browser_check = ttk.Checkbutton(
            browser_frame, text="Use Browser", variable=self.use_browser_var
        )
        self.use_browser_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.headless_var = tk.BooleanVar(value=True)
        self.headless_check = ttk.Checkbutton(
            browser_frame, text="Headless Mode", variable=self.headless_var
        )
        self.headless_check.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.scroll_var = tk.BooleanVar()
        self.scroll_check = ttk.Checkbutton(browser_frame, text="Auto-Scroll", variable=self.scroll_var)
        self.scroll_check.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        ttk.Label(browser_frame, text="Wait Time (seconds):").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.wait_time_entry = ttk.Entry(browser_frame, width=5)
        self.wait_time_entry.insert(0, '2.0')
        self.wait_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.root, text="Proxy File:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.proxy_file_entry = ttk.Entry(self.root, width=50)
        self.proxy_file_entry.grid(row=6, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(self.root, text="Browse", command=self.browse_proxy_file).grid(
            row=6, column=2, padx=5, pady=5
        )

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=300, mode="determinate", variable=self.progress_value
        )
        self.progress_bar.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(self.root, text="Output:").grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_text = tk.Text(self.root, wrap=tk.WORD, height=10, width=70)
        self.output_text.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(self.root, command=self.output_text.yview)
        scrollbar.grid(row=9, column=3, sticky=(tk.N, tk.S))
        self.output_text['yscrollcommand'] = scrollbar.set

        ttk.Button(self.root, text="Start Crawling", command=self.start_crawl).grid(
            row=10, column=0, columnspan=3, padx=5, pady=10
        )
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(9, weight=1)

    def browse_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, path)

    def browse_proxy_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.proxy_file_entry.delete(0, tk.END)
            self.proxy_file_entry.insert(0, file_path)

    def start_crawl(self):
        """Collects configuration and starts the crawl."""
        self.config = {
            'url': self.url_entry.get(),
            'preset': self.preset_combo.get(),
            'depth': int(self.depth_spinbox.get()),
            'output_format': self.output_format_combo.get(),
            'output_dir': self.output_dir_entry.get(),
            'browser': self.use_browser_var.get(),
            'headless': self.headless_var.get(),
            'scroll': self.scroll_var.get(),
            'wait_time': float(self.wait_time_entry.get()),
            'proxy_file': self.proxy_file_entry.get(),
            'use_cache': True,
            'rich': True,
            'quiet': True,  # Suppress ASCII art and other console output
        }
        if not self.config['url']:
            messagebox.showerror("Error", "URL cannot be empty.")
            return

        self.terminate_crawl = False
        self.disable_ui()
        self.log_queue = queue.Queue()  # Reset queue before starting new crawl
        self.run_crawl()

    def disable_ui(self):
        """Disables UI elements during crawl."""
        self.url_entry.config(state=tk.DISABLED)
        self.preset_combo.config(state=tk.DISABLED)
        self.depth_spinbox.config(state=tk.DISABLED)
        self.output_format_combo.config(state=tk.DISABLED)
        self.output_dir_entry.config(state=tk.DISABLED)
        self.use_browser_check.config(state=tk.DISABLED)
        self.headless_check.config(state=tk.DISABLED)
        self.scroll_check.config(state=tk.DISABLED)
        self.wait_time_entry.config(state=tk.DISABLED)
        self.proxy_file_entry.config(state=tk.DISABLED)

    def enable_ui(self):
        """Enables UI elements after crawl."""
        self.url_entry.config(state=tk.NORMAL)
        self.preset_combo.config(state=tk.NORMAL)
        self.depth_spinbox.config(state=tk.NORMAL)
        self.output_format_combo.config(state=tk.NORMAL)
        self.output_dir_entry.config(state=tk.NORMAL)
        self.use_browser_check.config(state=tk.NORMAL)
        self.headless_check.config(state=tk.NORMAL)
        self.scroll_check.config(state=tk.NORMAL)
        self.wait_time_entry.config(state=tk.NORMAL)
        self.proxy_file_entry.config(state=tk.NORMAL)

    def handle_log(self, message):
        """Handler for log messages that puts them in the queue."""
        self.log_queue.put(message)

    def run_crawl(self):
        """Runs the crawl in a separate thread."""
        self.crawl_thread = threading.Thread(
            target=main,
            args=(self.config, self.handle_log),  # Pass the handler method instead of queue.put directly
            daemon=True
        )
        self.crawl_thread.start()
        self.check_queue()

    def check_queue(self):
        """Checks the queue for log messages and updates the GUI."""
        try:
            while True:
                try:
                    message = self.log_queue.get_nowait()
                    self.log_message(message)
                except queue.Empty:
                    break
        except:
            pass

        if self.terminate_crawl or not self.crawl_thread.is_alive():
            self.enable_ui()
            if self.terminate_crawl:
                self.log_message("Crawling terminated.")
            else:
                self.log_message("Crawling finished.")
            return

        self.root.after(100, self.check_queue)

    def log_message(self, message):
        """Logs messages to the output text area."""
        self.output_text.insert(tk.END, str(message) + "\n")
        self.output_text.see(tk.END)

def launch_gui():
    """Launch the GUI directly."""
    app = CrawlerGUI()
    app.root.mainloop()

if __name__ == "__main__":
    launch_gui()
