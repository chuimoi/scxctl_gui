import sys
import subprocess
import ast
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt


class SCXCtlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("scxctl GUI")
        self.setMinimumSize(500, 500)

        # Zone de sortie
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # Boutons
        self.refresh_btn = QPushButton("🔄 Get 🔄")
        self.refresh_btn.setFixedWidth(80)  # petit
        self.set_btn = QPushButton("⚙️ Set ⚙️")
        self.stop_btn = QPushButton("⛔ Stop ⛔")
        self.stop_btn.setFixedWidth(80)  # petit

        # Combos / champs
        self.sched_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["auto", "gaming", "powersave", "lowlatency", "server"])
        self.args_input = QLineEdit()
        self.args_input.setPlaceholderText("Arguments (ex: -v,--performance)")

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Scheduler:"))
        layout.addWidget(self.sched_combo)
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.mode_combo)
        layout.addWidget(QLabel("Arguments:"))
        layout.addWidget(self.args_input)

        # Ligne Get / Set / Stop
        btn_line = QHBoxLayout()
        btn_line.addWidget(self.refresh_btn)
        btn_line.addWidget(self.set_btn)
        btn_line.addWidget(self.stop_btn)
        layout.addLayout(btn_line)

        layout.addWidget(self.output)
        self.setLayout(layout)

        # Connexions
        self.refresh_btn.clicked.connect(self.get_status)
        self.set_btn.clicked.connect(self.set_scheduler)
        self.stop_btn.clicked.connect(self.stop_scheduler)
        self.sched_combo.currentTextChanged.connect(self.on_scheduler_changed)

        self.list_schedulers()

    def run_command(self, args: list[str]) -> str:
        try:
            result = subprocess.run(["scxctl"] + args, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Erreur: {e.stderr.strip() or e.stdout.strip()}"

    def update_selection_from_status(self, output: str):
        text_lower = output.strip().lower()
        if "no scx scheduler running" in text_lower:
            idx = self.sched_combo.findText("default", Qt.MatchFlag.MatchFixedString)
            if idx != -1:
                self.sched_combo.setCurrentIndex(idx)
            self.mode_combo.setCurrentIndex(0)
            return

        if text_lower.startswith("running"):
            active_sched = None
            active_mode = None

            parts = output.split()
            if len(parts) >= 2:
                active_sched = parts[1].strip().lower()

            if " in " in output.lower():
                try:
                    after_in = output.lower().split(" in ", 1)[1]
                    active_mode = after_in.split()[0].strip().lower()
                except IndexError:
                    active_mode = None

            if active_sched:
                idx_sched = self.sched_combo.findText(active_sched, Qt.MatchFlag.MatchFixedString)
                if idx_sched != -1:
                    self.sched_combo.setCurrentIndex(idx_sched)
            if active_mode:
                idx_mode = self.mode_combo.findText(active_mode, Qt.MatchFlag.MatchFixedString)
                if idx_mode != -1:
                    self.mode_combo.setCurrentIndex(idx_mode)

    def get_status(self):
        output = self.run_command(["get"])
        self.append_output("get", output)
        self.update_selection_from_status(output)
        return output

    def list_schedulers(self):
        # Remplissage silencieux sans affichage de 'list' au démarrage
        output = self.run_command(["list"])
        self.sched_combo.clear()
        self.sched_combo.addItem("default")  # option spéciale stop

        for line in output.splitlines():
            if "supported schedulers:" in line:
                try:
                    sched_list = line.split("supported schedulers:")[1].strip()
                    schedulers = ast.literal_eval(sched_list)
                    for sched in schedulers:
                        self.sched_combo.addItem(sched)
                except Exception as e:
                    self.append_output("parse_error", f"Erreur de parsing : {e}")

        status = self.run_command(["get"])
        self.update_selection_from_status(status)

    def set_scheduler(self):
        sched = self.sched_combo.currentText().strip().lower()
        mode = self.mode_combo.currentText()
        args = self.args_input.text()

        if not sched:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un scheduler.")
            return

        if sched == "default":
            self.stop_scheduler()
            return

        status_output = self.run_command(["get"])
        status_lower = status_output.lower()

        if "no scx scheduler running" in status_lower:
            cmd = ["start", "-s", sched]
        else:
            running_line = ""
            for line in status_output.splitlines():
                if line.lower().startswith("running"):
                    running_line = line
                    break

            active_sched = None
            active_mode = None
            if running_line:
                parts = running_line.split()
                if len(parts) >= 2:
                    active_sched = parts[1].strip().lower()
                if " in " in running_line.lower():
                    try:
                        after_in = running_line.lower().split(" in ", 1)[1]
                        active_mode = after_in.split()[0].strip().lower()
                    except IndexError:
                        active_mode = None

            if active_sched == sched and (mode.strip().lower() or "") == (active_mode or ""):
                QMessageBox.information(self, "Info", f"Scheduler '{sched}' déjà actif avec ce mode.")
                return

            cmd = ["switch", "-s", sched]

        if mode:
            cmd += ["-m", mode]
        if args:
            cmd += ["-a", args]

        output = self.run_command(cmd)
        self.append_output(cmd[0], output)

    def stop_scheduler(self):
        output = self.run_command(["stop"])
        self.append_output("stop", output)
        idx = self.sched_combo.findText("default", Qt.MatchFlag.MatchFixedString)
        if idx != -1:
            self.sched_combo.setCurrentIndex(idx)
        self.mode_combo.setCurrentIndex(0)

    def on_scheduler_changed(self, text: str):
        is_default = (text.strip().lower() == "default")
        self.mode_combo.setEnabled(not is_default)
        self.args_input.setEnabled(not is_default)

    def append_output(self, cmd, text):
        self.output.append(f"[{cmd}]\n{text}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SCXCtlGUI()
    gui.show()
    sys.exit(app.exec())
