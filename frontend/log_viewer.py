from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCharFormat, QColor, QFont
from typing import List, Optional
from datetime import datetime


class LogViewer(QWidget):
    """Widget for displaying sync operation logs."""

    # Signals
    closeRequested = Signal()
    exportRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sync_result = None
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header with title and controls
        header = self._create_header()
        layout.addLayout(header)

        # Summary section
        self.summary_widget = self._create_summary_section()
        layout.addWidget(self.summary_widget)

        # Filter controls
        filter_layout = self._create_filter_controls()
        layout.addLayout(filter_layout)

        # Log display area
        self.log_text = self._create_log_display()
        layout.addWidget(self.log_text)

        # Footer with action buttons
        footer = self._create_footer()
        layout.addLayout(footer)

        self.setMinimumSize(600, 400)

    def _create_header(self) -> QHBoxLayout:
        """Create the header section with title and close button."""
        layout = QHBoxLayout()

        title = QLabel("Sync Log")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setToolTip("Close Logs")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                font-size: 32pt;
                padding-bottom: 4px;
            }
            QPushButton:hover {
                border: 2px solid #4d4d4d;
                background-color: #2d2d2d;
            }
            QPushButton:pressed {
                background-color: #3d3d3d;
            }
        """)
        close_btn.clicked.connect(self.closeRequested.emit)
        layout.addWidget(close_btn)

        return layout

    def _create_summary_section(self) -> QWidget:
        """Create the summary information section."""
        widget = QWidget()
        widget.setObjectName("summaryWidget")  # Give it a unique name for styling
        layout = QVBoxLayout(widget)

        # Summary labels
        self.duration_label = QLabel("Duration: --")
        self.server_count_label = QLabel("Server Assets: --")
        self.local_count_label = QLabel("Local Assets: --")
        self.posted_label = QLabel("Posted: --")
        self.missing_label = QLabel("Missing Locally: --")
        self.error_label = QLabel("Errors: --")

        # Style the summary section
        widget.setStyleSheet("""
            QWidget#summaryWidget {
                background-color: #404040;
                border-radius: 5px;
                padding: 10px;
            }
            QWidget#summaryWidget QLabel {
                font-size: 12px;
                color: #dedede;
                background-color: transparent;
                font-weight: 500;
            }
        """)

        # Add labels to layout
        summary_grid = QHBoxLayout()
        summary_grid.addWidget(self.duration_label)
        summary_grid.addWidget(self.server_count_label)
        summary_grid.addWidget(self.local_count_label)
        summary_grid.addWidget(self.posted_label)
        summary_grid.addWidget(self.missing_label)
        summary_grid.addWidget(self.error_label)

        layout.addLayout(summary_grid)

        return widget

    def _create_filter_controls(self) -> QHBoxLayout:
        """Create filter controls for log levels."""
        layout = QHBoxLayout()

        filter_label = QLabel("Filter by level:")
        layout.addWidget(filter_label)

        self.level_filter = QComboBox()
        self.level_filter.addItems(["All", "INFO", "SUCCESS", "WARNING", "ERROR"])
        self.level_filter.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.level_filter)

        layout.addStretch()

        # Entry count
        self.entry_count_label = QLabel("Entries: 0")
        layout.addWidget(self.entry_count_label)

        return layout

    def _create_log_display(self) -> QTextEdit:
        """Create the main log display area."""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Set monospace font for better log readability
        font = QFont("Courier New", 14)
        text_edit.setFont(font)

        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
            }
        """)

        return text_edit

    def _create_footer(self) -> QHBoxLayout:
        """Create footer with action buttons."""
        layout = QHBoxLayout()

        layout.addStretch()

        self.export_btn = QPushButton("Export Log")
        self.export_btn.clicked.connect(self.exportRequested.emit)
        layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_log)
        layout.addWidget(self.clear_btn)

        return layout

    def set_sync_result(self, sync_result):
        """
        Set the sync result to display.

        Args:
            sync_result: SyncResult object from sync operation
        """
        self.sync_result = sync_result
        self._update_summary()
        self._update_log_display()

    def _update_summary(self):
        """Update the summary section with sync result data."""
        if not self.sync_result:
            self.duration_label.setText(f"Duration: None")
            self.server_count_label.setText(f"Server Assets: None")
            self.local_count_label.setText(f"Local Assets: None")
            self.posted_label.setText(f"Posted: None")
            self.missing_label.setText(f"Missing Locally: None")
            self.error_label.setText(f"Errors: None")

        summary = self.sync_result.get_summary()

        duration = summary.get('duration_seconds', 0)
        self.duration_label.setText(f"Duration: {duration:.2f}s")
        self.server_count_label.setText(f"Server Assets: {summary.get('server_asset_count', 0)}")
        self.local_count_label.setText(f"Local Assets: {summary.get('local_asset_count', 0)}")
        self.posted_label.setText(f"Posted: {summary.get('assets_posted', 0)}")
        self.missing_label.setText(f"Missing Locally: {summary.get('assets_missing_locally', 0)}")

        error_count = summary.get('error_count', 0)
        self.error_label.setText(f"Errors: {error_count}")

        if error_count > 0:
            self.error_label.setStyleSheet("""
                font-size: 12px;
                color: #e31717;
                background-color: transparent;
                font-weight: bold;
            """)
        else:
            self.error_label.setStyleSheet("")

    def _update_log_display(self, filter_level: str = "All"):
        """
        Update the log display with filtered entries.

        Args:
            filter_level: Log level to filter by ("All", "INFO", "SUCCESS", "WARNING", "ERROR")
        """
        if not self.sync_result:
            return

        self.log_text.clear()

        entries = self.sync_result.log_entries

        # Filter entries if needed
        if filter_level != "All":
            entries = [e for e in entries if e.level.value == filter_level]

        # Update entry count
        self.entry_count_label.setText(f"Entries: {len(entries)}")

        # Add entries to display
        for entry in entries:
            self._append_log_entry(entry)

    def _append_log_entry(self, entry):
        """
        Append a single log entry to the display with appropriate formatting.

        Args:
            entry: SyncLogEntry object
        """
        # Color coding based on log level
        colors = {
            "INFO": "#569cd6",  # Blue
            "SUCCESS": "#4ec9b0",  # Green
            "WARNING": "#dcdcaa",  # Yellow
            "ERROR": "#f48771"  # Red
        }

        color = colors.get(entry.level.value, "#d4d4d4")

        # Format timestamp
        time_str = entry.timestamp.strftime('%H:%M:%S')

        # Build HTML formatted entry
        html = f'<span style="color: #858585;">[{time_str}]</span> '
        html += f'<span style="color: {color}; font-weight: bold;">[{entry.level.value}]</span> '

        if entry.asset_path:
            html += f'<span style="color: #ce9178;">[{entry.asset_path}]</span> '

        html += f'<span style="color: #d4d4d4;">{entry.message}</span>'

        self.log_text.append(html)

    def _on_filter_changed(self, level: str):
        """Handle filter level change."""
        self._update_log_display(level)

    def _clear_log(self):
        """Clear the log display."""
        self.log_text.clear()
        self.sync_result = None
        self._update_summary()
        self.entry_count_label.setText("Entries: 0")

    def show_widget(self):
        """Show this widget."""
        self.show()

    def hide_widget(self):
        """Hide this widget."""
        self.hide()

    def export_log_to_file(self, file_path: str):
        """
        Export the current log to a text file.

        Args:
            file_path: Path to save the log file
        """
        if not self.sync_result:
            return

        try:
            with open(file_path, 'w') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("SYNC LOG\n")
                f.write("=" * 80 + "\n\n")

                # Write summary
                summary = self.sync_result.get_summary()
                f.write("SUMMARY:\n")
                for key, value in summary.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n" + "=" * 80 + "\n\n")

                # Write log entries
                f.write("LOG ENTRIES:\n\n")
                for entry in self.sync_result.log_entries:
                    f.write(f"{entry}\n")

        except Exception as e:
            print(f"Error exporting log: {e}")
