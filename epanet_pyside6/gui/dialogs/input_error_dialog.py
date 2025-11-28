"""Dialog to display input file errors."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QDialogButtonBox
)

class InputErrorDialog(QDialog):
    """Dialog to display input file errors."""

    def __init__(self, errors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input File Error")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText("\n".join(errors))
        self.layout.addWidget(self.text_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

