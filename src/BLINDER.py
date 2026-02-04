"""
BLINDER - A tool for blinding files for data analysis.

This module provides a GUI application for anonymizing and renaming files
with a secure mapping key.
"""

import random
import shutil
import tkinter as tk
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

import pandas as pd


@dataclass
class BlindingConfig:
    """Configuration for file blinding operation."""

    source_path: Path
    file_suffix: str
    append: bool = False

    def __post_init__(self):
        """Validate configuration."""
        if not self.source_path.exists():
            raise ValueError(f"Directory does not exist: {self.source_path}")
        if not self.file_suffix.startswith("."):
            raise ValueError(f"File suffix must start with '.': {self.file_suffix}")


class FileBlinder:
    """Handles file blinding operations."""

    KEY_FILENAME = "key.csv"
    BLINDED_DIR_NAME = "blinded"

    def __init__(self, config: BlindingConfig) -> None:
        """Initialize FileBlinder with configuration."""
        self.config = config
        self.blinded_path = config.source_path / self.BLINDED_DIR_NAME
        self.key_path = self.blinded_path / self.KEY_FILENAME

    def get_files(self) -> list[Path]:
        """Get sorted list of files matching the suffix."""
        return sorted(self.config.source_path.glob(f"*{self.config.file_suffix}"))

    def validate_state(self) -> str:
        """
        Validate the blinding state.

        Returns:
            Status string: 'ready', 'exists', or error message.
        """
        files = self.get_files()
        if not files:
            return f"No files found with suffix {self.config.file_suffix}"

        if not self.blinded_path.exists():
            return "ready"

        blinded_files = list(self.blinded_path.glob(f"*{self.config.file_suffix}"))
        if blinded_files:
            return "exists"

        if self.key_path.exists():
            return "exists"

        return "ready"

    def _create_file_mapping(self, files: list[Path]) -> dict[str, str]:
        """Create mapping of original to blinded filenames."""
        indices = list(range(len(files)))
        random.shuffle(indices)

        offset = 0
        if self.config.append and self.blinded_path.exists():
            existing_files = list(self.blinded_path.glob(f"*{self.config.file_suffix}"))
            offset = len(existing_files)

        return {
            file.name: f"{idx + 1 + offset:04d}{file.suffix}"
            for file, idx in zip(files, indices)
        }

    def _update_key_file(self, file_mapping: dict[str, str]) -> None:
        """Update the key.csv file with new mappings."""
        self.blinded_path.mkdir(exist_ok=True)

        new_key = pd.DataFrame(
            {
                "OriginalFile": list(file_mapping.keys()),
                "BlindedFile": list(file_mapping.values()),
                "Date": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            }
        )

        if self.config.append and self.key_path.exists():
            old_key = pd.read_csv(self.key_path, sep="\t")
            new_key = pd.concat([old_key, new_key], ignore_index=True)

        new_key.to_csv(self.key_path, index=False, sep="\t")

    @staticmethod
    def _copy_file(source: Path, destination: Path) -> None:
        """Copy file from source to destination."""
        shutil.copy(source, destination)

    def blind(self, progress_callback) -> None:
        """
        Blind files by copying and renaming them.

        Args:
            progress_callback: Function to call with (processed, total) updates.
        """
        files = self.get_files()
        file_mapping = self._create_file_mapping(files)
        self._update_key_file(file_mapping)

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self._copy_file,
                    self.config.source_path / original,
                    self.blinded_path / blinded,
                )
                for original, blinded in file_mapping.items()
            ]

            for idx, future in enumerate(futures, 1):
                future.result()
                progress_callback(idx, len(futures))


class BlinderApp:
    """GUI application for BLINDER."""

    VERSION = "0.4.0"
    GITHUB_URL = "https://github.com/felixS27/BLINDER/blob/main/README.md"
    WINDOW_TITLE = "BLINDER - Blinding files for data analysis"

    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self._setup_window()
        self._create_widgets()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title(self.WINDOW_TITLE)
        height_min = 250
        width_min = 600
        self.root.minsize(width_min, height_min)
        self.root.geometry(f"{width_min}x{height_min}+550+300")
        ttk.Style().theme_use("default")

    def _create_widgets(self) -> None:
        """Create and layout all GUI widgets."""
        # Directory input
        tk.Label(self.root, text="File directory").grid(
            row=0, column=0, padx=5, pady=5, sticky="E"
        )
        self.dir_entry = tk.Entry(self.root, bd=1, relief=tk.FLAT)
        self.dir_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(
            self.root, text="Browse", command=self._browse_directory, relief=tk.RAISED
        ).grid(row=0, column=2, padx=5, pady=5)

        # File suffix input
        tk.Label(self.root, text="File suffix (e.g.: .tif/.lif/.czi/...)").grid(
            row=1, column=0, padx=5, pady=5, sticky="E"
        )
        self.suffix_entry = tk.Entry(self.root, bd=1, relief=tk.FLAT)
        self.suffix_entry.grid(row=1, column=1, padx=5, pady=5)

        # Start button
        tk.Button(
            self.root,
            text="Start Blinding Data!",
            command=self._start_blinding,
            relief=tk.RAISED,
        ).grid(row=2, column=1, padx=5, pady=5)

        # Status label
        self.status_label = tk.Label(self.root, text="Ready for action.")
        self.status_label.grid(row=3, column=1, padx=5, pady=5)

        # Counter label
        self.counter_label = tk.Label(self.root, text="Processed 0 out of 0 files")
        self.counter_label.grid(row=4, column=1, padx=5, pady=5)

        # Footer buttons
        tk.Button(
            self.root, text="Help/About", command=self._open_webpage, relief=tk.RAISED
        ).grid(row=5, column=0, padx=5, pady=5)

        tk.Label(
            self.root, text="Powered by Felix Schneider", font=("Arial", 9, "italic")
        ).grid(row=5, column=1, padx=5, pady=5)

        tk.Button(
            self.root, text="Close BLINDER.", command=self.root.quit, relief=tk.RAISED
        ).grid(row=5, column=2, padx=5, pady=5)

        tk.Label(
            self.root, text=f"Version {self.VERSION}", font=("Arial", 9, "italic")
        ).grid(row=6, column=1, padx=5, pady=5)

    def _browse_directory(self) -> None:
        """Open directory selection dialog."""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def _update_status(self, message: str, color: str = "black") -> None:
        """Update status label."""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()

    def _update_counter(self, processed: int, total: int) -> None:
        """Update file counter label."""
        self.counter_label.config(text=f"Processed {processed} out of {total} files")
        self.root.update_idletasks()

    def _start_blinding(self) -> None:
        """Initiate the blinding process."""
        try:
            config = BlindingConfig(
                source_path=Path(self.dir_entry.get()),
                file_suffix=self.suffix_entry.get(),
            )
        except ValueError as e:
            self._show_error(str(e), stage=0)
            return

        blinder = FileBlinder(config)
        state = blinder.validate_state()

        if state.startswith(("No files", "Directory")):
            self._show_error(state, stage=0)
        elif state == "exists":
            self._show_conflict_dialog(blinder)
        else:
            self._blind_files(blinder, append=False)

    def _blind_files(self, blinder: FileBlinder, append: bool = False) -> None:
        """Execute the blinding operation."""
        blinder.config.append = append
        self._update_status("Processing...", color="orange")
        self._update_counter(0, len(blinder.get_files()))

        try:
            blinder.blind(self._update_counter)
            self._update_status("Finished!", color="green")
        except Exception as e:
            self._update_status(f"Error: {e}", color="red")

    def _show_error(self, message: str, stage: int = 0) -> None:
        """Show error dialog."""
        error_window = tk.Toplevel(self.root)
        error_window.title("Warning!")
        error_window.focus()
        error_window.grab_set()

        if stage == 0:
            error_window.geometry("280x150+550+300")
            tk.Label(error_window, text="Blinding not possible!").grid(
                row=0, column=0, padx=5, pady=5
            )
            tk.Label(error_window, text=message).grid(row=1, column=0, padx=5, pady=5)
            tk.Label(
                error_window, text="Please fix the error and restart blinding."
            ).grid(row=2, column=0, padx=5, pady=5)
            tk.Button(error_window, text="Close", command=error_window.destroy).grid(
                row=3, column=0, padx=5, pady=5
            )

    def _show_conflict_dialog(self, blinder: FileBlinder) -> None:
        """Show dialog when blinded folder already exists."""
        conflict_window = tk.Toplevel(self.root)
        conflict_window.title("Warning!")
        conflict_window.focus()
        conflict_window.grab_set()
        conflict_window.geometry("330x180+550+300")

        for i in range(3):
            conflict_window.grid_columnconfigure(i, minsize=10, weight=0)

        tk.Label(
            conflict_window, text="Directory already contains a blinded folder!"
        ).grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        tk.Label(
            conflict_window,
            text="The folder contains already blinded data.",
        ).grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        tk.Label(
            conflict_window,
            text="""Please choose if you want to overwrite the files,
                \nappend new files or abort blinding.""",
        ).grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        tk.Button(
            conflict_window,
            text="Overwrite",
            command=lambda: self._handle_conflict(
                conflict_window, blinder, append=False
            ),
        ).grid(row=3, column=0, padx=5, pady=5, sticky="E")

        tk.Button(
            conflict_window,
            text="Append",
            command=lambda: self._handle_conflict(
                conflict_window, blinder, append=True
            ),
        ).grid(row=3, column=1, padx=5, pady=5)

        tk.Button(conflict_window, text="Abort", command=conflict_window.destroy).grid(
            row=3, column=2, padx=5, pady=5, sticky="W"
        )

    def _handle_conflict(
        self, window: tk.Toplevel, blinder: FileBlinder, append: bool
    ) -> None:
        """Handle conflict resolution."""
        window.destroy()
        self._blind_files(blinder, append=append)

    @staticmethod
    def _open_webpage() -> None:
        """Open GitHub page in web browser."""
        webbrowser.open(BlinderApp.GITHUB_URL)


def main():
    """Run the application."""
    root = tk.Tk()
    BlinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
