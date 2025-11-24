"""Reaction report widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit
)

class ReactionReport(QWidget):
    """Reaction report window."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Reaction Report")
        self.resize(600, 400)
        
        self.setup_ui()
        self.generate_report()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontFamily("Courier New") # Monospace for alignment
        layout.addWidget(self.text_edit)
        
    def generate_report(self):
        """Generate reaction report text."""
        if not self.project.has_results():
            self.text_edit.setText("No simulation results available.")
            return
            
        results = self.project.engine.results
        
        report = []
        report.append("Reaction Report")
        report.append("===============")
        report.append("")
        
        # Check for quality results
        if 'quality' in results.node:
            report.append("Water Quality Analysis")
            report.append("-" * 30)
            
            # Average quality by node
            avg_quality = results.node['quality'].mean()
            report.append(f"Average Quality by Node:")
            for node_id, val in avg_quality.items():
                report.append(f"  Node {node_id}: {val:.4f}")
            report.append("")
            
        if 'reaction_rate' in results.link:
            report.append("Reaction Rates")
            report.append("-" * 30)
            
            # Average reaction rate by link
            avg_rate = results.link['reaction_rate'].mean()
            report.append(f"Average Reaction Rate by Link:")
            for link_id, val in avg_rate.items():
                report.append(f"  Link {link_id}: {val:.4f}")
                
        if not report:
            report.append("No reaction or quality data found in results.")
            
        self.text_edit.setText("\n".join(report))
