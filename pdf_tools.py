import sys
import os
import io
from datetime import datetime
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QHBoxLayout, QLabel,
    QMessageBox, QProgressBar, QComboBox
)
from PyQt5.QtCore import Qt
import fitz  # PyMuPDF
import subprocess

class PDFTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Compression & Merge Tool")
        self.setGeometry(200, 200, 600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add PDFs")
        self.compress_btn = QPushButton("Compress PDFs")
        self.merge_btn = QPushButton("Merge PDFs")
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.compress_btn)
        button_layout.addWidget(self.merge_btn)
        layout.addLayout(button_layout)

        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Preset:"))
        self.profile_combo = QComboBox()
        # Old text profiles
        self.profile_combo.addItem("High Quality (144 DPI / 60% JPEG, Text)")
        self.profile_combo.addItem("Balanced (100 DPI / 40% JPEG, Text)")
        self.profile_combo.addItem("iPhone Optimized (72 DPI / 25% JPEG, Text)")
        self.profile_combo.addItem("Ultra Small (72 DPI / 20% JPEG, Text)")
        # New color profiles
        self.profile_combo.addItem("High Quality Color (144 DPI / 60% JPEG, Color)")
        self.profile_combo.addItem("Balanced Color (100 DPI / 40% JPEG, Color)")
        self.profile_combo.addItem("iPhone Color Optimized (72 DPI / 25% JPEG, Color)")
        self.profile_combo.currentIndexChanged.connect(self.apply_profile)
        profile_layout.addWidget(self.profile_combo)
        layout.addLayout(profile_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_files)
        self.compress_btn.clicked.connect(self.compress_selected)
        self.merge_btn.clicked.connect(self.merge_selected)

    
        self.dpi = 144
        self.quality = 60
        self.color_mode = fitz.csGRAY

    def apply_profile(self, index):
        
        if index == 0:
            self.dpi = 144
            self.quality = 60
            self.color_mode = fitz.csGRAY
        elif index == 1:
            self.dpi = 100
            self.quality = 40
            self.color_mode = fitz.csGRAY
        elif index == 2:
            self.dpi = 72
            self.quality = 25
            self.color_mode = fitz.csGRAY
        elif index == 3:
            self.dpi = 72
            self.quality = 20
            self.color_mode = fitz.csGRAY
        elif index == 4:
            self.dpi = 144
            self.quality = 60
            self.color_mode = fitz.csRGB
        elif index == 5:
            self.dpi = 100
            self.quality = 40
            self.color_mode = fitz.csRGB
        elif index == 6:
            self.dpi = 72
            self.quality = 25
            self.color_mode = fitz.csRGB

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            for f in files:
                if f not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                    self.file_list.addItem(f)

    def open_folder(self, path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def compress_selected(self):
        dpi = self.dpi
        quality = self.quality
        colorspace = self.color_mode

        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not files:
            QMessageBox.warning(self, "Warning", "No files selected.")
            return

        base_dir = os.path.dirname(files[0])
        output_dir = os.path.join(base_dir, "compressed_pdfs")
        os.makedirs(output_dir, exist_ok=True)

        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)

        for i, input_path in enumerate(files):
            filename = os.path.basename(input_path).replace('.pdf', '_compressed.pdf')
            output_path = os.path.join(output_dir, filename)
            try:
                self.compress_pdf(input_path, output_path, dpi, quality, colorspace)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to compress:\n{input_path}\n\n{str(e)}")
            self.progress_bar.setValue(i + 1)

        QMessageBox.information(self, "Done", "All files have been compressed.")
        self.progress_bar.setValue(0)
        self.file_list.clear()
        self.open_folder(output_dir)

    def merge_selected(self):
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not files:
            QMessageBox.warning(self, "Warning", "No files selected.")
            return

        base_dir = os.path.dirname(files[0])
        output_dir = os.path.join(base_dir, "merged_pdfs")
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now().strftime("%Y%m%d")
        i = 1
        while True:
            output_filename = f"{today}_{i}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            if not os.path.exists(output_path):
                break
            i += 1

        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)

        merged = fitz.open()
        for idx, f in enumerate(files):
            try:
                pdf = fitz.open(f)
                merged.insert_pdf(pdf)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to merge:\n{f}\n\n{str(e)}")
            self.progress_bar.setValue(idx + 1)

        merged.save(output_path)
        QMessageBox.information(self, "Done", "Files have been merged.")
        self.progress_bar.setValue(0)
        self.file_list.clear()
        self.open_folder(output_dir)

    def compress_pdf(self, input_path, output_path, dpi, quality, colorspace):
        A4_WIDTH = int(8.27 * dpi)
        A4_HEIGHT = int(11.69 * dpi)

        doc = fitz.open(input_path)
        new_doc = fitz.open()
        for page in doc:
            pix = page.get_pixmap(dpi=dpi, colorspace=colorspace)
            mode = "RGB" if colorspace == fitz.csRGB else "L"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format="JPEG", quality=quality)
            img_bytes = img_bytes_io.getvalue()

            new_page = new_doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)
            rect = fitz.Rect(0, 0, A4_WIDTH, A4_HEIGHT)
            new_page.insert_image(rect, stream=img_bytes)

        new_doc.save(output_path, deflate=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFTool()
    window.show()
    sys.exit(app.exec_())