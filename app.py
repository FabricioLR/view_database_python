from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
import sys
import psycopg2

file = open("urls.txt", "a+")

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("desing/app.ui", self)
        self.tables = []
        self.lines = []
        self.columnsNames = {}
        self.tablesData = {}
        self.currentTable = ""
        self.initUi()
        self.setEvents()
        self.show()

    def initUi(self):
        self.tableWidget = self.findChild(QTableWidget, "tableWidget")
        self.buttonWidget = self.findChild(QPushButton, "connect")
        self.boxWidget = self.findChild(QComboBox, "tableName")
        self.urlsWidget = self.findChild(QComboBox, "urls")

        self.urlWidget = self.findChild(QLineEdit, "url")

        self.messageBox = QMessageBox()

    def setEvents(self):
        self.setUrls()
        self.buttonWidget.clicked.connect(self.conn)
        self.boxWidget.activated.connect(self.setComboBox)
        self.urlsWidget.activated.connect(self.setUrl)

    def setComboBox(self, table):
        try:
            self.boxWidget.clear()
            self.boxWidget.addItems(self.tables)
            self.boxWidget.setCurrentIndex(table)
            self.currentTable = self.tables[table]
            self.setData()
        except Exception as error:
            self.messageBox.about(self, "Error", str(error))

    def setUrls(self):
        try:
            file.seek(0)
            self.lines = file.readlines()
            for index, line in enumerate(self.lines):
                self.lines[index] = line[:len(line) - 1]
            self.urlWidget.setText(self.lines[0])
            self.urlsWidget.clear()
            self.urlsWidget.addItems(self.lines)
            self.urlsWidget.setCurrentIndex(self.lines[0])
        except Exception as error:
            print(error)

    def setUrl(self, url):
        print(self.lines[url - 1])
        self.urlWidget.setText(self.lines[url - 1])

    def setData(self):
        if (self.currentTable != ""):
            self.tableWidget.setColumnCount(len(self.columnsNames[self.currentTable]))
            self.tableWidget.setRowCount(len(self.tablesData[self.currentTable]))
            self.tableWidget.setHorizontalHeaderLabels(tuple(self.columnsNames[self.currentTable]))
            for index0, row in enumerate(self.tablesData[self.currentTable]):
                for index1, value in enumerate(row):
                    self.tableWidget.setItem(index0, index1, QTableWidgetItem(str(value)))

    def conn(self):
        self.tables = []
        self.columnsNames = {}
        self.tablesData = {}
        self.currentTable = ""
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.boxWidget.clear()

        url = self.urlWidget.text()

        host = url[url.find("@") + 1:url.index("/", url.find("@"))]
        database = url[url.index("/", url.find("@")) + 1:]
        username = url[url.find("//") + 2:url.index(":", url.find("//"))]
        password = url[url.index(":", url.find("//")) + 1:url.find("@")]

        try:
            conn = psycopg2.connect(host=host, database=database, user=username, password=password)
            cur = conn.cursor()

            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            
            recset = cur.fetchall()
            for rec in recset:
                if (rec[0] != "SequelizeMeta" and rec[0] != "pg_stat_statements"):
                    self.tables.append(rec[0])
            
            for table in self.tables:
                cur.execute("SELECT * FROM information_schema.columns WHERE table_schema='public' AND table_name='{}'".format(table))
                recset = cur.fetchall()
                self.columnsNames[table] = []
                for rec in recset:
                    self.columnsNames[table].append(rec[3])

            for table in self.tables:
                cur.execute("SELECT * FROM {}".format(table))
                recset = cur.fetchall()
                self.tablesData[table] = []
                for rec in recset:
                    data = []
                    for value in rec:
                        data.append(value)
                    self.tablesData[table].append(data)

            conn.close()

            self.setComboBox(0)

            file.write(url + "\n")
            self.setUrls()
        except Exception as error:
            self.messageBox.about(self, "Error", str(error))

def window():
    app = QApplication(sys.argv)
    win = Ui()
    sys.exit(app.exec_())

window()

file.close()