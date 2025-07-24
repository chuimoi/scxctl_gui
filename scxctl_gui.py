import sys
import subprocess
import ast
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QHBoxLayout, QMessageBox
)

class SCXCtlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("scxctl GUI")
        self.setMinimumSize(500, 500)

        # Widgets
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.refresh_btn = QPushButton("🔄 Get 🔄")
        self.list_btn = QPushButton("📜 List 📜")

        self.sched_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["", "auto", "gaming", "powersave", "lowlatency", "server"])
        self.args_input = QLineEdit()
        self.args_input.setPlaceholderText("Arguments (ex: -v,--performance)")

        self.start_btn = QPushButton("▶️ Start ▶️")
        self.switch_btn = QPushButton("🔁 Switch 🔁")
        self.stop_btn = QPushButton("⛔ Stop ⛔")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Scheduler:"))
        layout.addWidget(self.sched_combo)
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.mode_combo)
        layout.addWidget(QLabel("Arguments:"))
        layout.addWidget(self.args_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.switch_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.list_btn)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("Sortie de scxctl :"))
        layout.addWidget(self.output)

        self.setLayout(layout)

        # Connexions
        self.refresh_btn.clicked.connect(self.get_status)
        self.list_btn.clicked.connect(self.list_schedulers)
        self.start_btn.clicked.connect(self.start_scheduler)
        self.switch_btn.clicked.connect(self.switch_scheduler)
        self.stop_btn.clicked.connect(self.stop_scheduler)

        self.list_schedulers()
        self.get_status()

    def run_command(self, args: list[str]) -> str:
        try:
            result = subprocess.run(["scxctl"] + args, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Erreur: {e.stderr.strip() or e.stdout.strip()}"

    def get_status(self):
        output = self.run_command(["get"])
        self.append_output("get", output)

    def list_schedulers(self):
        output = self.run_command(["list"])
        self.append_output("list", output)
        self.sched_combo.clear()
        self.sched_combo.addItem("")  # vide par défaut

        # Extraire les schedulers depuis la ligne unique
        for line in output.splitlines():
            if "supported schedulers:" in line:
                try:
                    sched_list = line.split("supported schedulers:")[1].strip()
                    schedulers = ast.literal_eval(sched_list)
                    for sched in schedulers:
                        self.sched_combo.addItem(sched)
                except Exception as e:
                    self.append_output("parse_error", f"Erreur de parsing : {e}")

    def start_scheduler(self):
        sched = self.sched_combo.currentText()
        mode = self.mode_combo.currentText()
        args = self.args_input.text()

        if not sched:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un scheduler.")
            return

        cmd = ["start", "-s", sched]
        if mode:
            cmd += ["-m", mode]
        if args:
            cmd += ["-a", args]

        output = self.run_command(cmd)
        self.append_output("start", output)

    def switch_scheduler(self):
        sched = self.sched_combo.currentText()
        mode = self.mode_combo.currentText()
        args = self.args_input.text()

        cmd = ["switch"]
        if sched:
            cmd += ["-s", sched]
        if mode:
            cmd += ["-m", mode]
        if args:
            cmd += ["-a", args]

        output = self.run_command(cmd)
        self.append_output("switch", output)

    def stop_scheduler(self):
        output = self.run_command(["stop"])
        self.append_output("stop", output)

    def append_output(self, cmd, text):
        self.output.append(f"[{cmd}]\n{text}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SCXCtlGUI()
    gui.show()
    sys.exit(app.exec())
