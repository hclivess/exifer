import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QListWidget, 
                           QHBoxLayout, QLineEdit, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt, QDateTime
from datetime import datetime
import os
import subprocess
import platform

class MetadataEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files = []
        self.exiftool_path = self.find_exiftool()
        self.init_ui()

    def find_exiftool(self):
        """Find ExifTool executable in various locations."""
        # Check in same directory as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(script_dir, 'exiftool'),
            os.path.join(script_dir, 'exiftool.exe'),
            'exiftool',  # System PATH
            '/usr/bin/exiftool',  # Common Unix location
            '/usr/local/bin/exiftool'  # Common macOS location
        ]

        # On Windows, also check for .exe extension
        if platform.system() == 'Windows':
            possible_paths.extend([
                os.path.join(script_dir, 'exiftool(-k).exe'),
                'exiftool.exe',
            ])

        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, '-ver'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return path
            except FileNotFoundError:
                continue
            except Exception:
                continue

        return None

    def init_ui(self):
        self.setWindowTitle('File Metadata Editor')
        self.setMinimumWidth(600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Mode selection
        mode_widget = QWidget()
        mode_layout = QHBoxLayout(mode_widget)
        
        self.simple_mode_btn = QPushButton('Simple Mode')
        self.simple_mode_btn.setCheckable(True)
        self.simple_mode_btn.setChecked(True)  # Default to simple mode
        mode_layout.addWidget(self.simple_mode_btn)
        
        self.full_mode_btn = QPushButton('Full Metadata Mode')
        self.full_mode_btn.setCheckable(True)
        if not self.exiftool_path:
            self.full_mode_btn.setEnabled(False)
            self.full_mode_btn.setToolTip("ExifTool not found. Install ExifTool to enable full metadata editing.")
        mode_layout.addWidget(self.full_mode_btn)
        
        # Connect mode buttons to ensure only one is checked at a time
        self.simple_mode_btn.clicked.connect(lambda: self.mode_button_clicked('simple'))
        self.full_mode_btn.clicked.connect(lambda: self.mode_button_clicked('full'))
        
        mode_layout.addStretch()
        layout.addWidget(mode_widget)

        # File selection button
        select_btn = QPushButton('Select Files')
        select_btn.clicked.connect(self.select_files)
        layout.addWidget(select_btn)

        # Date/Time inputs
        date_widget = QWidget()
        date_layout = QGridLayout(date_widget)
        
        date_layout.addWidget(QLabel('Date:'), 0, 0)
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText('YYYY-MM-DD')
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.date_edit.setText(current_date)
        date_layout.addWidget(self.date_edit, 0, 1)

        date_layout.addWidget(QLabel('Time:'), 0, 2)
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText('HH:MM:SS')
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_edit.setText(current_time)
        date_layout.addWidget(self.time_edit, 0, 3)

        now_btn = QPushButton('Set to Now')
        now_btn.clicked.connect(self.set_current_datetime)
        date_layout.addWidget(now_btn, 0, 4)

        # Sequential timing options
        interval_widget = QWidget()
        interval_layout = QHBoxLayout(interval_widget)
        
        self.sequential_cb = QPushButton('Sequential Times')
        self.sequential_cb.setCheckable(True)
        interval_layout.addWidget(self.sequential_cb)
        
        interval_layout.addWidget(QLabel('Interval (seconds):'))
        self.interval_spinbox = QLineEdit()
        self.interval_spinbox.setText('60')
        self.interval_spinbox.setFixedWidth(60)
        interval_layout.addWidget(self.interval_spinbox)
        
        interval_layout.addStretch()
        date_layout.addWidget(interval_widget, 1, 0, 1, 5)

        layout.addWidget(date_widget)

        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dragMoveEvent = self.dragMoveEvent
        self.file_list.dropEvent = self.dropEvent
        layout.addWidget(self.file_list)

        # Bottom buttons
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        
        clear_btn = QPushButton('Clear List')
        clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(clear_btn)
        
        remove_btn = QPushButton('Remove Selected')
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)
        
        process_btn = QPushButton('Process Files')
        process_btn.clicked.connect(self.process_files)
        btn_layout.addWidget(process_btn)
        
        layout.addWidget(btn_widget)

        self.setGeometry(300, 300, 600, 400)
        self.show()

    def select_files(self):
        """Open file dialog to select files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Process",
            "",
            "All Files (*)"
        )
        
        for file_path in files:
            if file_path not in self.files:
                self.files.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))

    def set_current_datetime(self):
        """Set the date and time fields to current time."""
        now = datetime.now()
        self.date_edit.setText(now.strftime('%Y-%m-%d'))
        self.time_edit.setText(now.strftime('%H:%M:%S'))

    def remove_selected(self):
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            del self.files[row]

    def clear_files(self):
        """Clear all files from the list."""
        self.file_list.clear()
        self.files.clear()

    def mode_button_clicked(self, mode):
        """Handle mode selection button clicks."""
        if mode == 'simple':
            self.simple_mode_btn.setChecked(True)
            self.full_mode_btn.setChecked(False)
        else:
            self.simple_mode_btn.setChecked(False)
            self.full_mode_btn.setChecked(True)

    def dragEnterEvent(self, event):
        """Handle drag enter events for file drag and drop."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events for file drag and drop."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events for file drag and drop."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file_path in files:
            if os.path.isfile(file_path) and file_path not in self.files:
                self.files.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))

    def process_files(self):
        """Process all files in the list."""
        if not self.files:
            QMessageBox.warning(self, "Warning", "No files to process.")
            return

        try:
            # Parse date and time
            date_str = self.date_edit.text()
            time_str = self.time_edit.text()
            base_datetime = datetime.strptime(
                f"{date_str} {time_str}", 
                "%Y-%m-%d %H:%M:%S"
            )
            
            # Sort files if using sequential times
            working_files = self.files.copy()
            if self.sequential_cb.isChecked():
                working_files.sort(key=lambda x: os.path.basename(x).lower())
                try:
                    interval_seconds = int(self.interval_spinbox.text())
                except ValueError:
                    QMessageBox.warning(self, "Warning", "Invalid interval value. Using 60 seconds.")
                    interval_seconds = 60

            total_files = len(working_files)
            processed_files = 0
            errors = []

            for i, file in enumerate(working_files):
                if self.sequential_cb.isChecked():
                    current_datetime = base_datetime.timestamp() + (i * interval_seconds)
                    current_dt = datetime.fromtimestamp(current_datetime)
                else:
                    current_dt = base_datetime

                try:
                    if self.simple_mode_btn.isChecked():
                        self.modify_file_dates(file, current_dt)
                    else:
                        self.modify_metadata(file, current_dt)
                    processed_files += 1
                except Exception as e:
                    errors.append(f"Error processing {os.path.basename(file)}: {str(e)}")

            # Show results
            if errors:
                error_message = "\n".join(errors)
                QMessageBox.warning(
                    self,
                    "Partial Success",
                    f"Processed {processed_files} out of {total_files} files.\n\nErrors:\n{error_message}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully processed all {total_files} files!"
                )

            self.clear_files()

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid date/time format: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def modify_file_dates(self, file_path, timestamp):
        """Modify only file system dates."""
        try:
            file_timestamp = timestamp.timestamp()
            os.utime(file_path, (file_timestamp, file_timestamp))
            
            # Handle creation time for different platforms
            if platform.system() == 'Windows':
                powershell_cmd = f'(Get-Item "{file_path}").CreationTime = (Get-Date "{timestamp}")'
                subprocess.run(['powershell', '-Command', powershell_cmd], check=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['SetFile', '-d', timestamp.strftime("%m/%d/%Y %H:%M:%S"), file_path], check=True)
                
        except Exception as e:
            raise Exception(f"Error modifying file dates: {str(e)}")

    def modify_metadata(self, file_path, timestamp):
        """Modify file metadata using ExifTool."""
        if not self.exiftool_path:
            raise Exception("ExifTool not found. Please install ExifTool first.")
            
        date_str = timestamp.strftime("%Y:%m:%d %H:%M:%S")
        
        exiftool_args = [
            self.exiftool_path,
            '-overwrite_original',
            f'-AllDates="{date_str}"',
            f'-FileModifyDate="{date_str}"',
            f'-FileCreateDate="{date_str}"',
            f'-CreateDate="{date_str}"',
            f'-ModifyDate="{date_str}"',
            f'-DateTimeOriginal="{date_str}"',
            f'-MediaCreateDate="{date_str}"',
            f'-MediaModifyDate="{date_str}"',
            f'-TrackCreateDate="{date_str}"',
            f'-TrackModifyDate="{date_str}"',
            file_path
        ]

        try:
            result = subprocess.run(
                exiftool_args,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Also update filesystem timestamps
            self.modify_file_dates(file_path, timestamp)
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"ExifTool error: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    ex = MetadataEditor()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
