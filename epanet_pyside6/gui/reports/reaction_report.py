"""Reaction Report View."""

from gui.views.report_view import ReportView

class ReactionReport(ReportView):
    """View for displaying reaction report."""
    
    def __init__(self, project, parent=None):
        super().__init__(project, parent)
        self.report_title = "Reaction Report"
        self.setWindowTitle(self.report_title)
        self.refresh()
        
    def refresh(self):
        """Refresh report content."""
        report_text = self.project.engine.report_text
        if not report_text:
            self.set_text("No simulation report available. Please run a simulation first.")
            return
            
        # Look for Reaction related sections
        # "Reaction Info" or "Water Quality"
        
        lines = report_text.splitlines()
        reaction_lines = []
        in_section = False
        found = False
        
        # Keywords to identify reaction section
        keywords = ["Reaction", "Quality", "Source", "Mass Balance"]
        
        for line in lines:
            # Check for section headers
            if any(k in line for k in keywords) and "Page" not in line:
                # Heuristic: Section headers often have dashes below them or are all caps
                # For now, just simple keyword matching
                # But we don't want every line with "Quality"
                
                # EPANET Mass Balance usually starts with "Water Quality Mass Balance"
                if "Water Quality Mass Balance" in line or "Reaction Reporting" in line:
                    in_section = True
                    found = True
            
            if in_section:
                reaction_lines.append(line)
                # End of section?
                # Usually blank lines separate sections.
                # But tables have blank lines inside?
                # Let's just grab the whole block until a new major section starts?
                # Or just grab everything if we found the start.
                
        if found:
            self.set_text("\n".join(reaction_lines))
        else:
            self.set_text("No reaction reporting found in the output. \nMake sure Water Quality is enabled and reactions are defined.")
