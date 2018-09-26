import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QTableWidgetItem, QMessageBox, \
    QAbstractItemView, QFileDialog, QCheckBox, QGridLayout
from PyQt5.QtCore import QAbstractTableModel, Qt, QEvent
from PyQt5.QtGui import QStandardItem
from PyQt5.uic import loadUi


class Manager(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        loadUi("ManagerUI.ui", self)

        self.initData()
        self.initUI()
        self.initBinding()

        self.tableWidget.viewport().installEventFilter(self)

        self.slt_loadM3U()
        return

    def initData(self):
        self.line = 0

        return

    def initUI(self):
        self.setWindowTitle("Manager")
        self.resize(800, 500)
        self.tableWidget.setColumnWidth(0, 40)
        self.tableWidget.setColumnWidth(1, 40)

        self.tableWidget.setAlternatingRowColors(True)

        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.setAcceptDrops(True)
        return

    def initBinding(self):
        self.btn_load.clicked.connect(self.slt_loadM3U)
        self.btn_allSelect.clicked.connect(self.slt_allSelect)
        self.btn_invertSelect.clicked.connect(self.slt_invertSelect)
        return

    def slt_loadM3U(self):
        self.line = 0
        self.tableWidget.clearContents()
        m3uPath = QFileDialog.getOpenFileName(self, "Open M3U", "", "M3U(*.m3u)")
        if m3uPath == None or m3uPath[0] == "":
            return
        path = "/".join(m3uPath[0].split("/")[0:-1]) + "/"
        print(path)

        try:
            f = open(m3uPath[0], "rt+", encoding="utf-8")
            if f == None:
                self.log.setText("打开文件失败")
                return
            while True:
                data = f.readline(1024)
                if len(data) == 0:
                    break;
                if "#EXTINF:," in data:
                    name = f.readline(1024)
                    self.tableWidget.setRowCount(self.line + 1)
                    self.tableWidget.setRowHeight(self.line + 1, 40)
                    fpath = path + name
                    if name == "\n":
                        name = "空项"
                        fpath = "空项"
                    self.tableWidget.setItem(self.line, 1, QTableWidgetItem(str(self.line)))
                    self.tableWidget.setItem(self.line, 2, QTableWidgetItem(name))
                    self.tableWidget.setItem(self.line, 3, QTableWidgetItem(fpath))
                    w = QWidget()
                    layout = QGridLayout()
                    layout.addWidget(QCheckBox())
                    w.setLayout(layout)
                    layout.setVerticalSpacing(0)
                    w.setFixedSize(40, 31)
                    self.tableWidget.setCellWidget(self.line, 0, w)
                    self.line += 1

        except Exception as e:
            self.log.setText("打开文件失败")
            print(e)
        return

    def slt_delChoose(self):
        return

    def slt_allSelect(self):
        for i in range(0, self.line):
            self.tableWidget.cellWidget(i, 0).layout().itemAt(0).widget().setCheckState(Qt.Checked)
        return

    def slt_invertSelect(self):
        for i in range(0, self.line):
            self.tableWidget.cellWidget(i, 0).layout().itemAt(0).widget().setCheckState(Qt.Unchecked)
        return

    def slt_OK(self):
        return

    def eventFilter(self, obj, event):
        if obj == self.tableWidget.viewport():
            if event.type() == QEvent.DragEnter:
                pass
            if event.type() == QEvent.DragMove:
                pass
            if event.type() == QEvent.DragLeave:
                pass
            if event.type() == QEvent.Drop:
                print("drop")
                itemList = self.tableWidget.selectedItems()
                srcRows = []
                for item in itemList:
                    row = self.tableWidget.row(item)
                    if row in srcRows:
                        continue
                    else:
                        srcRows.append(row)
                dstRow = self.tableWidget.row(self.tableWidget.itemAt(event.pos()))  # 落下行
                print(srcRows, dstRow)
                self.changeOrder(srcRows, dstRow)
                return True
        return False

    def changeOrder(self, srcRows, dstRow):
        
        # items = []
        # count = 0
        # for i in srcRows:
        #     cols = []
        #     cols.append(self.tableWidget.cellWidget(i, 0))
        #     cols.append(self.tableWidget.item(i, 1))
        #     cols.append(self.tableWidget.item(i, 2))
        #     cols.append(self.tableWidget.item(i, 3))
        #     items.append(cols)
        #     if i < dstRow:
        #         count += 1
        #
        # srcRows.reverse()
        # for i in srcRows:
        #     print("removerow ", i)
        #     self.tableWidget.removeRow(i)
        #
        # for i in srcRows:
        #     self.tableWidget.insertRow(dstRow - count + 1)
        # print(count)
        # print(items)
        # for i in range(len(srcRows)):
        #     print(i)
        #     self.tableWidget.setCellWidget(dstRow - count + 1 + i, 0, items[i][0])
        #     self.tableWidget.setItem(dstRow - count + 1 + i, 1, items[i][1])
        #     self.tableWidget.setItem(dstRow - count + 1 + i, 2, items[i][2])
        #     self.tableWidget.setItem(dstRow - count + 1 + i, 3, items[i][3])
        return


qApp = QApplication(sys.argv)
win = Manager()
win.show()
sys.exit(qApp.exec())
