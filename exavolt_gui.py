import os
import sys
import subprocess
import threading
import shutil
import json

from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QLabel, \
    QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, \
    QTableWidget, QTableWidgetItem, QAbstractScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtCore import QEventLoop

import lib.metadata_loader
import exavolt

FILE_COLUMN_INDEX = 4

class ExavoltGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Define class attribute for script check
        self.script_running = False

        # Set window title and size
        self.setWindowTitle('Exavolt Mod Tool')
        self.resize(800, 600)

        # Create layout for input ISO file path and browse button
        input_iso_layout = QHBoxLayout()
        self.input_iso_line_edit = QLineEdit(self)
        self.input_iso_browse_button = QPushButton('Browse', self)
        self.input_iso_browse_button.clicked.connect(self.browse_input_iso)
        input_iso_layout.addWidget(QLabel('Input ISO:', self))
        input_iso_layout.addWidget(self.input_iso_line_edit)
        input_iso_layout.addWidget(self.input_iso_browse_button)

        # Create list widget for selecting mods
        self.mod_table = QTableWidget(self)
        self.populate_mod_table()
        mod_table_layout = QVBoxLayout()
        mod_table_layout.addWidget(QLabel('Load Order (Top Installs First):', self))
        mod_table_layout.addWidget(self.mod_table)

        # Enable drag and drop for the mod list widget
        self.mod_table.verticalHeader().setSectionsMovable(True)
        self.mod_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        # Create "Refresh" button to refresh the mod list
        self.refresh_button = QPushButton('Refresh Mods List', self)
        self.refresh_button.clicked.connect(self.refresh_mod_table)
        # Set the refresh button size and alignment
        self.refresh_button.setFixedSize(100, 20)


        # Create checkboxes for optional flags
        self.extract_only_checkbox = QCheckBox('Extract ISO Only', self)
        self.no_rebuild_checkbox = QCheckBox('No Rebuild', self)

        # Create "Run" button to execute exavolt.py script
        self.run_button = QPushButton('Run', self)
        self.run_button.resize(100, 40)
        self.run_button.clicked.connect(self.run)

        # Create "Save" and "Load" buttons
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_load_order)
        self.load_button = QPushButton('Load', self)
        self.load_button.clicked.connect(self.restore_load_order)
        # Set the save/load button size and alignment
        self.save_button.setFixedSize(100, 20)
        self.load_button.setFixedSize(100, 20)

        # Load and display splash image
        self.splash_label = QLabel(self)
        self.splash_pixmap = QPixmap('splash.png')
        self.splash_label.setPixmap(self.splash_pixmap)
        self.splash_label.setAlignment(Qt.AlignCenter)
        self.splash_label.resize(0, self.splash_pixmap.height())

        # Create main layout and add elements
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splash_label)
        main_layout.addLayout(input_iso_layout)
        main_layout.addLayout(mod_table_layout)
        main_layout.addWidget(self.refresh_button)
        main_layout.addWidget(self.save_button)
        main_layout.addWidget(self.load_button)
        main_layout.addWidget(self.extract_only_checkbox)
        main_layout.addWidget(self.no_rebuild_checkbox)
        main_layout.addWidget(self.run_button)
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def refresh_mod_table(self):
        # Clear the current items in the mod list
        self.mod_table.clear()
        self.mod_table.setRowCount(0)
        # Repopulate the mod list
        self.populate_mod_table()

    def browse_input_iso(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select Input ISO', '', 'ISO Files (*.iso)', options=options)
        if file_name:
            self.input_iso_line_edit.setText(file_name)

    def get_files_in_rows(self):
        files = []
        header = self.mod_table.verticalHeader()
        for row in range(self.mod_table.rowCount()):
          it = self.mod_table.item(header.logicalIndex(row), FILE_COLUMN_INDEX)
          files.append(it.text())
        return files

    def run(self):
        # Set script_running flag to prevent multiple instances of the script from running
        self.script_running = True

        # Get input ISO path and mod list
        input_iso = self.input_iso_line_edit.text()
        if not input_iso:
            print('Error: No input ISO specified')
            return
        mods = self.get_files_in_rows()

        exavolt.execute(input_iso, 'mod.iso', "",
            self.extract_only_checkbox.isChecked(),
            self.no_rebuild_checkbox.isChecked(),
            mods)

    def populate_mod_table(self):
        # Check if "Exavolt Packages" directory exists
        packages_dir = 'Exavolt Packages'
        if not os.path.isdir(packages_dir):
            return

        row_index = 0
        columns = ["Title", "Author", "Campaign Levels", "Multiplayer Levels", "File"]
        self.mod_table.setColumnCount(len(columns))
        self.mod_table.setHorizontalHeaderLabels(columns)
        mod_metadatas = lib.metadata_loader.collect_mods(packages_dir)
        for mod_metadata in mod_metadatas:
          mod_summary = mod_metadata.summary()
          self.mod_table.insertRow(row_index)
          self.mod_table.setItem(row_index, 0, QTableWidgetItem(mod_summary["Title"]))
          self.mod_table.setItem(row_index, 1, QTableWidgetItem(mod_summary["Author"]))
          self.mod_table.setItem(row_index, 2, QTableWidgetItem(str(mod_summary["Campaign Levels"])))
          self.mod_table.setItem(row_index, 3, QTableWidgetItem(str(mod_summary["Multiplayer Levels"])))
          self.mod_table.setItem(row_index, FILE_COLUMN_INDEX, QTableWidgetItem(mod_metadata.zip_file_path))
          row_index += 1
        self.mod_table.resizeColumnsToContents()
        self.mod_table.resizeRowsToContents()

    def save_load_order(self):
        # Create a file dialog to let the user specify the file to save to
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Load Order", "Load Orders/", "JSON Files (*.json)", options=options)

        # Create a dictionary to store the mod list data
        data = {
            "mods": []
        }

        # Iterate through the items in the mod list
        for i in range(self.mod_table.count()):
            item = self.mod_table.item(i)
            mod = {
                "text": item.text(),
                "file": item.text(),
                "checked": item.checkState() == Qt.Checked
            }
            data["mods"].append(mod)

        # Write the data to the specified file
        with open(file_name, "w") as f:
            json.dump(data, f)

    def restore_load_order(self):
        # Create a file dialog to let the user select the file to load
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Load Order", "Load Orders/", "JSON Files (*.json)")

        # Load the data from the specified file
        with open(file_name, "r") as f:
            data = json.load(f)

        # Clear the current mod list
        self.mod_table.clear()

        # Check the JSON data for any missing entries
        missing_mods = []
        for mod in data["mods"]:
            # Check if the mod file is present in the Exavolt Packages directory
            if not os.path.exists("Exavolt Packages/{}".format(mod["file"])):
                missing_mods.append(mod["file"])
            else:
                # Add the mod to the mod list
                item = QListWidgetItem(mod["text"])
                item.setCheckState(Qt.Checked if mod["checked"] else Qt.Unchecked)
                self.mod_table.addItem(item)

        # Display a warning if there are any missing mods
        if missing_mods:
            missing_mods_string = "\n".join(missing_mods)
            self.display_warning("These mods were not found and were removed from the load order:\n{}".format(missing_mods_string))

        # Add any new mods to the mod list
        for file in os.listdir("Exavolt Packages"):
            file_found = False
            for mod in data["mods"]:
                if mod["file"] == file:
                    file_found = True
                    break
                if not file_found:
                    # Add the new mod to the mod list
                    item = QListWidgetItem(file)
                    item.setCheckState(Qt.Unchecked)
                    self.mod_table.addItem(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExavoltGUI()
    ex.show()
    sys.exit(app.exec_())
