import json
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QHeaderView, QTableWidgetItem, QMessageBox, \
    QAbstractItemView
from PyQt5.uic import loadUi

import Netease163Manager


class UI(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        loadUi("gui.ui", self)
        self.initData()
        self.initUI()
        self.initBinding()

        pass

    def initUI(self):
        self.setWindowTitle('Netease163Music-tool for Sony Player v1.0 ------  By BM_Recluse')
        self.setLayout(self.mainLayout)
        self.pathWidget.setLayout(self.pathLayout)
        self.pushWidget.setLayout(self.pushLayout)
        self.txt_musicDir.setPlaceholderText('网易云音乐本地下载目录')
        self.txt_playerDir.setPlaceholderText('索尼播放器目录')
        self.ListID.setPlaceholderText('歌单ID')
        self.txt_musicDir.setText(self.m_musicDir)
        self.txt_playerDir.setText(self.m_playerDir)

        self.tableWidget.setColumnWidth(0, 40)
        self.tableWidget.setColumnWidth(3, 80)
        self.tableWidget.setColumnWidth(4, 80)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # self.txt_musicDir.setText('d:\\Mr.Shi\\163music')
        # self.ListID.setText('615146628')

        pass

    def initData(self):
        try:
            hFile = open("config.cfg", 'r')
            tmp = hFile.read(1024)
            data = ''
            while len(tmp) > 0:
                data += tmp
                tmp = hFile.read(1024)
            info = json.loads(data)
            self.m_musicDir = info['musicDir']
            self.m_playerDir = info['playerDir']
            hFile.close()
        except BaseException:
            self.m_musicDir = ''
            self.m_playerDir = ''
        return;
        pass

    def initBinding(self):
        self.btn_chooseMusicPath.clicked.connect(self.slot_chooseMusicPath)
        self.btn_choosePlayerPath.clicked.connect(self.slot_choosePlayerPath)
        self.btn_findMusic.clicked.connect(self.slot_findMusic)
        pass

    def slot_chooseMusicPath(self):
        dir = QFileDialog.getExistingDirectory()
        self.txt_musicDir.setText(dir)
        pass

    def slot_choosePlayerPath(self):
        dir = QFileDialog.getExistingDirectory()
        self.txt_playerDir.setText(dir)
        pass

    def slot_findMusic(self):
        findPath = self.txt_musicDir.text()
        listid = self.ListID.text()
        if len(findPath) == 0 or len(listid) == 0:
            print("dsfsdf")
            QMessageBox.critical(self, "提示", '信息不完整')
            return

        self.writeConfig(findPath, self.txt_playerDir.text())

        list1, list2 = Netease163Manager.getMusicAbsPathList(findPath, listid)
        # tips = str('歌单名：%s   创建者：%s') % (ListName, Creator)
        # self.ListInfo.setText(tips)
        self.tableWidget.setRowCount(len(list1))
        sn = 0
        for i in range(len(list1)):
            if list1[i] == None:
                for it in list2:
                    if it['No'] == i:
                        sn = i + 1
                        name = it['Name']
                        path = ''
                        isMusic = False
                        break
            else:
                sn = list1[i]['No'] + 1
                name = list1[i]['Name']
                path = list1[i]['Path']
                isMusic = True
            tmp = u'成功'
            if not isMusic:
                tmp = u'失败'
            # self.itemList[i][4] = QTableWidgetItem(tmp)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str("%d") % sn))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(path))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(tmp))
        pass

    def writeConfig(self, _musicDir, _playerDir):
        try:
            hFile = open("config.cfg", 'w+')
            data = {"musicDir": _musicDir, "playerDir": _playerDir}
            info = json.dumps(data)
            hFile.write(str(info))
            hFile.close()
        except BaseException:
            pass
        return


qApp = QApplication(sys.argv)
win = UI()
win.show()
sys.exit(qApp.exec())
