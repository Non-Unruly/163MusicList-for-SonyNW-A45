import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QTableWidgetItem, QMessageBox, \
    QAbstractItemView, QFileDialog, QCheckBox, QGridLayout, QDialog
from PyQt5.QtCore import QAbstractTableModel, Qt, QEvent
from PyQt5.QtGui import QStandardItem
from PyQt5.uic import loadUi


class Manager(QDialog):
    def __init__(self):
        super(QWidget, self).__init__()
        loadUi("ManagerDialog.ui", self)

        self.initData()
        self.initUI()
        self.initBinding()

        self.tableWidget.viewport().installEventFilter(self)

        return

    def initData(self):
        self.line = 0
        self.m3upath = ""
        self.dir = ""
        return

    def initUI(self):
        self.btn_clearNone.setEnabled(False)
        self.btn_delChoose.setEnabled(False)

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
        self.btn_delChoose.clicked.connect(self.slt_delChoose)
        self.btn_allSelect.clicked.connect(self.slt_allSelect)
        self.btn_clearNone.clicked.connect(self.slt_clearNone)
        self.btn_ok.clicked.connect(self.slt_OK)
        return

    def slt_loadM3U(self):
        self.line = 0
        self.tableWidget.clearContents()
        m3uPath = QFileDialog.getOpenFileName(self, "Open M3U", "", "M3U(*.m3u)")
        if m3uPath == None or m3uPath[0] == "":
            return
        path = "/".join(m3uPath[0].split("/")[0:-1]) + "/"
        print(path)
        self.dir = path
        self.m3upath = m3uPath[0]
        print(self.m3upath)
        print("=======")
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
                    self.btn_clearNone.setEnabled(True)
                    self.btn_delChoose.setEnabled(True)
            f.close()
        except Exception as e:
            self.log.setText("打开文件失败")
            print(e)
        return

    def slt_delChoose(self):
        lst = []
        x = self.line - 1
        while True:
            if x <= -1:
                break
            if self.tableWidget.cellWidget(x, 0).layout().itemAt(0).widget().checkState() == Qt.Checked:
                lst.append(self.tableWidget.item(x, 3).text())
                self.tableWidget.removeRow(x)
                self.line = self.line - 1
            x = x - 1

        for x in range(0, self.line):
            self.tableWidget.item(x, 1).setText(str(x))

        try:
            for path in lst:
                if os.path.exists(path):
                    if path[-1] == "\n":
                        path = path[0:-1]
                    os.remove(path)
                lrc = ".".join(path.split(".")[0:-1]) + ".lrc"
                if os.path.exists(lrc):
                    os.remove(lrc)
        except Exception as e:
            print(e)
        return

    def slt_allSelect(self):
        for i in range(0, self.line):
            self.tableWidget.cellWidget(i, 0).layout().itemAt(0).widget().setCheckState(Qt.Checked)
        return

    def slt_invertSelect(self):
        for i in range(0, self.line):
            if self.tableWidget.cellWidget(i, 0).layout().itemAt(0).widget().checkState() == Qt.Checked:
                self.tableWidget.cellWidget(i, 0).layout().itemAt(0).widget().setCheckState(Qt.Unchecked)
            else:
                self.tableWidget.cellWidget(i, 0).layout().itemAt(0).widget().setCheckState(Qt.Checked)
        return

    def slt_OK(self):
        if self.m3upath == "":
            self.close()
            return
        try:
            f = open(self.m3upath, "w+", encoding="utf-8")
            f.write("#EXTM3U\n")
            for i in range(0, self.line):
                if self.tableWidget.item(i, 3).text() == "空项":
                    continue
                file = self.tableWidget.item(i, 3).text().split("/")
                dirs = self.dir.split("/")
                for x in dirs:
                    if x in file:
                        file.remove(x)
                f.write("#EXTINF:,\n")
                f.write("/".join(file))
            f.close()
            self.close()
        except Exception as e:
            print(e)
        return

    def slt_clearNone(self):
        rows = []
        for i in range(0, self.line):
            if self.tableWidget.item(i, 2).text() == "空项" and self.tableWidget.item(i, 3).text() == "空项":
                rows.append(i)
        rows.sort(reverse=True)
        for x in rows:
            self.tableWidget.removeRow(x)
            self.line = self.line - 1
        for i in range(self.line):
            self.tableWidget.item(i, 1).setText(str(i))
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
                self.changeOrder(srcRows, dstRow)
                return True
        return False

    def changeOrder(self, srcRows, dstRow):
        items = []
        # 选中的条目放入列表
        for row in srcRows:
            rowitems = []
            rowitems.append(self.tableWidget.cellWidget(row, 0))
            rowitems.append(self.tableWidget.item(row, 1))
            rowitems.append(self.tableWidget.item(row, 2))
            rowitems.append(self.tableWidget.item(row, 3))
            items.append(rowitems)

        # 复制选中的条目生成新的行
        for x in range(len(srcRows)):
            self.tableWidget.insertRow(dstRow + x)
            self.tableWidget.setCellWidget(dstRow + x, 0, items[x][0])
            self.tableWidget.setItem(dstRow + x, 1, QTableWidgetItem(items[x][1].text()))
            self.tableWidget.setItem(dstRow + x, 2, QTableWidgetItem(items[x][2].text()))
            self.tableWidget.setItem(dstRow + x, 3, QTableWidgetItem(items[x][3].text()))

        # 将旧的选中条目删除
        for preItem in items:
            row = self.tableWidget.row(preItem[1])
            self.tableWidget.removeRow(row)

        # 重新编号
        for no in range(self.line):
            self.tableWidget.item(no, 1).setText(str(no))
        return
