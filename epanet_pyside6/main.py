"""Main application entry point."""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Run the EPANET PySide6 application."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("EPANET 2.2")
    app.setOrganizationName("US EPA")
    app.setApplicationVersion("2.2.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())

    
if __name__ == "__main__":
    main()
