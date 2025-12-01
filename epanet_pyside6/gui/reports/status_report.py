"""Status Report View."""

from gui.views.report_view import ReportView

class StatusReport(ReportView):
    """View for displaying simulation status report."""
    
    def __init__(self, project, parent=None):
        super().__init__(project, parent)
        self.report_title = "Status Report"
        self.setWindowTitle(self.report_title)
        self.refresh()
        
    def refresh(self):
        """Refresh report content."""
        report_text = self.project.engine.report_text
        if not report_text:
            self.set_text("No simulation report available. Please run a simulation first.")
            return
            
        # Extract Log section
        # Usually from start to "Link Results:" or "Node Results:" or "Energy Usage:"
        # Or just take the first N lines if we can't find sections?
        # Better: Take everything until the first dashed line that is NOT part of the header?
        
        lines = report_text.splitlines()
        log_lines = []
        
        # Stop keywords
        stop_keywords = ["Node Results", "Link Results", "Energy Usage", "Network Table"]
        
        for line in lines:
            if any(k in line for k in stop_keywords):
                break
            log_lines.append(line)
            
        self.set_text("\n".join(log_lines))
