"""Legal disclaimer dialog for the ROMs Downloader."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt

from ..utils import ConfigManager, APP_NAME

DISCLAIMER_TEXT = """
<h2>LEGAL DISCLAIMER</h2>

<p>This software is a tool for organizing and downloading ROM files from
Internet Archive, a non-profit digital library dedicated to preservation.</p>

<h3>IMPORTANT:</h3>
<ul>
<li><b>Only download ROMs for games you legally own physical copies of.</b></li>
<li>Downloading copyrighted material without owning the original may be
illegal in your jurisdiction.</li>
<li>This software does not host, store, or distribute any ROM files.</li>
<li>The developers of this software are not responsible for how you
use this tool.</li>
<li>By using this software, you agree to comply with all applicable
laws and regulations regarding ROM usage in your country.</li>
</ul>

<p>Internet Archive hosts these files for preservation and research
purposes. Please respect copyright holders and support game
developers by purchasing games you enjoy.</p>

<h3>Disclaimer of Warranty</h3>
<p>This software is provided "as is" without warranty of any kind,
express or implied. Use at your own risk.</p>
"""


class DisclaimerDialog(QDialog):
    """Dialog displaying the legal disclaimer."""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager

        self.setWindowTitle(f"{APP_NAME} - Legal Disclaimer")
        self.setMinimumSize(550, 450)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the disclaimer dialog UI."""
        layout = QVBoxLayout(self)

        # Disclaimer text
        text_browser = QTextBrowser()
        text_browser.setHtml(DISCLAIMER_TEXT)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)

        # Accept checkbox
        self.accept_check = QCheckBox("I understand and accept these terms")
        layout.addWidget(self.accept_check)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.accept_btn = QPushButton("Accept")
        self.accept_btn.setEnabled(False)
        self.accept_btn.clicked.connect(self._accept_disclaimer)
        btn_layout.addWidget(self.accept_btn)

        layout.addLayout(btn_layout)

        # Connect checkbox to enable button
        self.accept_check.stateChanged.connect(self._on_checkbox_changed)

    def _on_checkbox_changed(self, state: int) -> None:
        """Handle checkbox state change."""
        self.accept_btn.setEnabled(state == Qt.CheckState.Checked.value)

    def _accept_disclaimer(self) -> None:
        """Accept the disclaimer and close."""
        self.config.accept_disclaimer()
        self.accept()
