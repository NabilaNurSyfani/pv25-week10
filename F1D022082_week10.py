import sys
import sqlite3
import csv
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMenuBar, QAction, QFileDialog, QTabWidget, QMessageBox, QInputDialog, QHeaderView)

class BukuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Week 10 - Manajemen Buku")
        self.setGeometry(200, 200, 700, 500)

        self.conn = sqlite3.connect("katalog.db")
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                pengarang TEXT,
                tahun INTEGER)
        """)
        self.conn.commit()
        self.initUI()

    def initUI(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        # Menu File
        fileMenu = self.menuBar.addMenu("File")
        saveAction = QAction("Simpan", self)
        exportAction = QAction("Ekspor ke CSV", self)
        exitAction = QAction("Keluar", self)
        saveAction.triggered.connect(self.saveData)
        exportAction.triggered.connect(self.exportCSV)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exportAction)
        fileMenu.addAction(exitAction)

        # Menu Edit
        editMenu = self.menuBar.addMenu("Edit")
        searchAction = QAction("Cari Judul", self)
        deleteAction = QAction("Hapus Data", self)
        autoFillAction = QAction("Auto Fill", self)
        dictationAction = QAction("Start Dictation", self)
        emojiAction = QAction("Emoji & Symbol", self)
        deleteAction.triggered.connect(self.deleteData)
        autoFillAction.triggered.connect(self.autoFill)
        searchAction.triggered.connect(self.focusSearch)
        editMenu.addAction(searchAction)
        editMenu.addAction(deleteAction)
        editMenu.addAction(autoFillAction)
        editMenu.addAction(dictationAction)
        editMenu.addAction(emojiAction)

        # Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab Data Buku
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Data Buku")
        tab1_layout = QVBoxLayout()
        form_layout = QVBoxLayout()
        form_layout.addSpacing(10)

        # Judul
        judul_layout = QHBoxLayout()
        judul_label = QLabel("Judul:")
        judul_label.setFixedWidth(100)
        self.judulInput = QLineEdit()
        self.judulInput.setFixedSize(280, 25)
        judul_layout.addWidget(judul_label)
        judul_layout.addWidget(self.judulInput)
        form_layout.addLayout(judul_layout)

        # Pengarang
        pengarang_layout = QHBoxLayout()
        pengarang_label = QLabel("Pengarang:")
        pengarang_label.setFixedWidth(100)
        self.pengarangInput = QLineEdit()
        self.pengarangInput.setFixedSize(280, 25)
        pengarang_layout.addWidget(pengarang_label)
        pengarang_layout.addWidget(self.pengarangInput)
        form_layout.addLayout(pengarang_layout)

        # Tahun
        tahun_layout = QHBoxLayout()
        tahun_label = QLabel("Tahun:")
        tahun_label.setFixedWidth(100)
        self.tahunInput = QLineEdit()
        self.tahunInput.setFixedSize(280, 25)
        tahun_layout.addWidget(tahun_label)
        tahun_layout.addWidget(self.tahunInput)
        form_layout.addLayout(tahun_layout)

        # Tombol Simpan
        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()
        self.saveButton = QPushButton("Simpan")
        self.saveButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.saveButton.setFixedSize(80, 30) 
        self.saveButton.clicked.connect(self.saveData)
        save_button_layout.addWidget(self.saveButton)
        save_button_layout.addStretch()
        form_layout.addLayout(save_button_layout)
        tab1_layout.addLayout(form_layout)

        # Tombol Cari
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Cari judul...")
        self.searchBox.textChanged.connect(self.loadData)
        tab1_layout.addWidget(self.searchBox)

        # Tabel
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #999;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #999;
                font-weight: bold;
            }
        """)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellDoubleClicked.connect(self.editCell)
        tab1_layout.addWidget(self.table)

        # Tombol Hapus
        delete_button_layout = QHBoxLayout()
        delete_button_layout.addStretch()
        self.deleteButton = QPushButton("Hapus Data")
        self.deleteButton.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.deleteButton.setFixedSize(100, 30)
        self.deleteButton.clicked.connect(self.deleteData)
        delete_button_layout.addWidget(self.deleteButton)
        delete_button_layout.addStretch()
        tab1_layout.addLayout(delete_button_layout)

        # Label identitas 
        identitas_label = QLabel("Nabila Nur Syfani|F1D022082")
        identitas_label.setAlignment(Qt.AlignRight)
        tab1_layout.addWidget(identitas_label)
        self.tab1.setLayout(tab1_layout)

        # Tab Ekspor
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "Ekspor")
        layout2 = QVBoxLayout()
        label = QLabel("Klik 'Ekspor ke CSV' dari menu File untuk mengekspor data.")
        label.setAlignment(Qt.AlignCenter)
        layout2.addWidget(label)
        self.tab2.setLayout(layout2)
        self.loadData()

    def saveData(self):
        judul = self.judulInput.text()
        pengarang = self.pengarangInput.text()
        tahun = self.tahunInput.text()
        if judul and pengarang and tahun:
            self.c.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)", (judul, pengarang, tahun))
            self.conn.commit()
            self.judulInput.clear()
            self.pengarangInput.clear()
            self.tahunInput.clear()
            self.loadData()

    def loadData(self):
        filter_text = self.searchBox.text()
        if filter_text:
            self.c.execute("SELECT * FROM buku WHERE judul LIKE ?", (f"%{filter_text}%",))
        else:
            self.c.execute("SELECT * FROM buku")
        rows = self.c.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(rows):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data))) 
        self.table.setColumnWidth(0, 50)   
        self.table.setColumnWidth(1, 300)  
        self.table.setColumnWidth(2, 200) 
        self.table.setColumnWidth(3, 100)   

    def editCell(self, row, column):
        id_item = self.table.item(row, 0)
        if id_item is None:
            return
        id_val = id_item.text()
        new_val, ok = QInputDialog.getText(self, "Edit", f"Ubah nilai {self.table.horizontalHeaderItem(column).text()}:", QLineEdit.Normal, self.table.item(row, column).text())
        if ok:
            column_name = ["id", "judul", "pengarang", "tahun"][column]
            self.c.execute(f"UPDATE buku SET {column_name} = ? WHERE id = ?", (new_val, id_val))
            self.conn.commit()
            self.loadData()

    def deleteData(self):
        selected = self.table.currentRow()
        if selected >= 0:
            id_item = self.table.item(selected, 0)
            if id_item:
                self.c.execute("DELETE FROM buku WHERE id = ?", (id_item.text(),))
                self.conn.commit()
                self.loadData()

    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if path:
            self.c.execute("SELECT * FROM buku")
            rows = self.c.fetchall()
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(rows)
            QMessageBox.information(self, "Berhasil", "Data berhasil diekspor ke CSV.")

    def autoFill(self):
        self.judulInput.setText("")
        self.pengarangInput.setText("")
        self.tahunInput.setText("")

    def focusSearch(self):
        self.searchBox.setFocus()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BukuApp()
    window.show()
    sys.exit(app.exec_())