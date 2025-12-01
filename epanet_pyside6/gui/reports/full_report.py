"""Full Report View."""

from gui.views.report_view import ReportView

class FullReport(ReportView):
    """View for displaying the full simulation report."""
    
    def __init__(self, project, parent=None):
        super().__init__(project, parent)
        self.report_title = "Full Report"
        self.setWindowTitle(self.report_title)
        self.refresh()
        
    def refresh(self):
        """Refresh report content."""
        if self.project.engine.report_text:
            self.set_text(self.project.engine.report_text)
        else:
            self.set_text("No simulation report available. Please run a simulation first.")
