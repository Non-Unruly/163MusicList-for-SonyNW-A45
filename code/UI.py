import json
import sys
import Moudle163
import SonyManager
import time
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QHeaderView, QTableWidgetItem, QMessageBox, \
    QAbstractItemView, QFileDialog
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtGui import QStandardItem
from PyQt5.uic import loadUi
import CookieUI
import Manager
import StateCode
import threading


class UI(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        loadUi("gui.ui", self)
        self.list = [None]
        self.listName = ''
        self.listCreator = ''
        self.cookie = ''
        self.initData()
        self.initUI()
        self.initBinding()

        return

    def initUI(self):
        self.ListInfo.setText("无节操测试版版本，不定时抽风，如有BUG，纯属故意")
        self.label_state.setText("本工具仅做个人学习使用，免费共享")
        self.setWindowTitle('索尼walkman导入网易云歌单歌词工具v0.233 ------  By BM_Recluse')
        self.setLayout(self.mainLayout)
        self.pathWidget.setLayout(self.pathLayout)
        self.pushWidget.setLayout(self.pushLayout)
        self.txt_musicDir.setPlaceholderText('网易云音乐本地下载目录')
        self.txt_playerDir.setPlaceholderText('索尼播放器目录（MUSIC目录）')
        self.ListID.setPlaceholderText('网易云歌单链接')
        self.txt_musicDir.setText(self.m_musicDir)
        self.txt_playerDir.setText(self.m_playerDir)

        self.tableWidget.setColumnWidth(0, 40)
        # self.tableWidget.setColumnWidth(1, 200)
        # self.tableWidget.setColumnWidth(2, 320)
        self.tableWidget.setColumnWidth(3, 80)
        self.tableWidget.setColumnWidth(4, 80)
        self.tableWidget.setColumnWidth(5, 80)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.btn_findLocalMusic.setEnabled(False)
        self.btn_Lrc.setEnabled(False)

        return

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
            self.cookie = info['cookie']
            hFile.close()
        except BaseException:
            self.m_musicDir = ''
            self.m_playerDir = ''
        return

    def initBinding(self):
        self.btn_chooseMusicPath.clicked.connect(self.slot_chooseMusicPath)
        self.btn_choosePlayerPath.clicked.connect(self.slot_choosePlayerPath)
        self.btn_findMusic.clicked.connect(self.slot_findMusic)
        self.btn_copyMusic.clicked.connect(self.slot_copyMusic)
        self.btn_findLocalMusic.clicked.connect(self.slot_findLocalMusic)
        self.btn_Lrc.clicked.connect(self.slot_createLrc)
        self.tableWidget.cellDoubleClicked.connect(self.slot_tableDClicked)
        self.btn_cookie.clicked.connect(self.slot_cookie)
        self.btn_Edit.clicked.connect(self.slot_editor)
        return

    def slot_cookie(self):
        self.getCookie = CookieUI.CookieUI()
        if len(self.cookie) > 0:
            self.getCookie.hasCookie(self.cookie)
        self.getCookie.exec()
        self.cookie = self.getCookie.cookie
        self.getCookie.deleteLater()
        pass

    def slot_chooseMusicPath(self):
        dir = QFileDialog.getExistingDirectory()
        self.txt_musicDir.setText(dir)
        return

    def slot_choosePlayerPath(self):
        dir = QFileDialog.getExistingDirectory()
        self.txt_playerDir.setText(dir)
        return

    def slot_findMusic(self):
        self.list.clear()
        self.btn_Lrc.setEnabled(False)
        findPath = self.txt_musicDir.text()
        listid = self.ListID.text()
        if len(findPath) == 0 or len(listid) == 0:
            QMessageBox.critical(self, "提示", '信息不完整')
            return
        # https://music.163.com/playlist?id=1983803378&userid=94727845
        index = listid.find('id=')
        if index == -1:
            self.CallBack(StateCode.CallBackCode.UNKNOW_ERROR, None)
            return
        index += 3
        idstr = ''
        while True:
            if index >= len(listid):
                break
            if ord(listid[index]) >= ord('0') and ord(listid[index]) <= ord('9'):
                idstr += listid[index]
                index += 1
            else:
                break
        self.tableWidget.clearSpans()
        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()
        self.writeConfig(self.txt_musicDir.text(), self.txt_playerDir.text())

        threading._start_new_thread(Moudle163.RequestList, (idstr, self.cookie, self.CallBack))
        return

    def slot_copyMusic(self):
        self.writeConfig(self.txt_musicDir.text(), self.txt_playerDir.text())
        threading._start_new_thread(SonyManager.CopyMusic,
                                    (self.list, self.txt_playerDir.text(), self.CallBack))
        return

    def slot_editor(self):
        dlg = Manager.Manager()
        dlg.exec()
        return

    def slot_findLocalMusic(self):
        try:
            path = self.txt_musicDir.text()
            self.label_state.setText("正在匹配当中...")
            threading._start_new_thread(Moudle163.FindLocalMusic, (path, self.list, self.CallBack))
        except BaseException as e:
            print(e)
        return

    # 生成歌词按钮
    def slot_createLrc(self):
        threading._start_new_thread(Moudle163.RequestLrc, (self.list, self.CallBack))
        return

    # 双击表格
    def slot_tableDClicked(self, row, col):
        print("double clicked: ", row, col)
        lst = Moudle163.FileFormat.copy()
        format = " *.".join(lst)
        dialogFormat = "Music(" + format + ")"
        file = QFileDialog.getOpenFileName(self, "手动指定音频文件", self.m_musicDir, dialogFormat)[0]
        if len(file) == 0:
            return
        print(file)
        # print(self.list)
        no = row
        print(no)
        if no == self.list[no]["no"]:
            self.list[no]["path"] = file
        self.tableWidget.setItem(row, col, QTableWidgetItem(file))
        pass

    # 写入配置文件
    def writeConfig(self, _musicDir, _playerDir):
        try:
            hFile = open("config.cfg", 'w+')
            data = {"musicDir": _musicDir, "playerDir": _playerDir, "cookie": self.cookie}
            info = json.dumps(data)
            hFile.write(str(info))
            hFile.close()
        except BaseException as e:
            QMessageBox.critical(self, '提示', str(e))
        return

    # 显示歌单信息
    def listShowInTable(self, args):
        try:
            tips = str('歌单名：%s   创建者：%s') % (str(args['listname']), str(args['creator']))
            self.listName = args['listname']
            self.listCreator = args['creator']
            self.ListInfo.setText(tips)
            self.tableWidget.clearSpans()
            self.list = args['list']
            num = len(self.list)
            if num < 10:
                self.tableWidget.setRowCount(10)
            else:
                self.tableWidget.setRowCount(num)
            for sn in range(num):
                it = self.list[sn]
                song = it['song']
                singer = it['singer']
                no = it['no']
                name = str("%s - %s" % (singer, song))
                self.tableWidget.setItem(sn, 0, QTableWidgetItem(str("%d") % no))
                self.tableWidget.setItem(sn, 1, QTableWidgetItem(name))
                self.tableWidget.setRowHeight(num, 15)
            self.btn_findLocalMusic.setEnabled(True)
        except BaseException as e:
            QMessageBox.critical(self, '错误', str(e))
        return

    # 匹配地址显示
    def pathShowInTable(self, args):
        try:
            no = args['no']
            path = args['path']
            self.tableWidget.setItem(no, 2, QTableWidgetItem(path))
            self.tableWidget.setItem(no, 3, QTableWidgetItem('匹配'))
            self.tableWidget.setCurrentCell(no, 0)
            # self.tableWidget.setCurrentCell(no, 2)
            for i in range(len(self.list)):
                if self.list[i]['no'] == no:
                    self.list[i]['path'] = path
                    break
        except BaseException as e:
            print(e)
        return

    # 歌词匹配状态显示
    def lrcShowInTable(self, args):
        try:
            self.tableWidget.setItem(args['no'], 4, QTableWidgetItem(str("匹配")))
            self.list[args['no']]['lrc'] = args['lrc']
            self.tableWidget.setCurrentCell(args['no'], 4)
        except BaseException as e:
            print(e)
        return

    def copyState(self, args):
        self.tableWidget.setItem(args['no'], 5, QTableWidgetItem("导入完成"))
        self.tableWidget.setCurrentCell(args['no'], 5)
        self.label_state.setText(str('《%s-%s》导入完成') % (args['singer'], args['song']))
        return

    def UnknowError(self, args):
        self.label_state.setText("未知错误")
        self.writeLog('未知错误', str(args))
        return

    # 完成歌曲导入
    def finishedCopy(self):
        self.label_state.setText("音频导入完成")
        threading._start_new_thread(SonyManager.CreateM3U_inside,
                                    (self.txt_playerDir.text(), self.list, self.listName, self.CallBack))
        return

    # 播放列表创建成功
    def finishedM3U(self):
        self.label_state.setText("播放列表创建完成")
        return

    # 无歌词信息
    def noLrc(self, args):
        print(args)
        no = args['no']
        self.tableWidget.setItem(no, 4, QTableWidgetItem('纯音乐'))
        self.tableWidget.setCurrentCell(no, 4)
        return

    # 匹配歌词出现错误
    def errorLrc(self, args):
        print(args)
        music = args['music']
        errorinfo = args['info']
        no = music['no']
        self.tableWidget.setItem(no, 4, QTableWidgetItem('无歌词'))
        self.tableWidget.setCurrentCell(no, 4)
        self.writeLog('errorLog', str(errorinfo))
        return

    # 日志
    def writeLog(self, flag, _str):
        try:
            timestr = time.asctime(time.localtime(time.time()))
            hFile = open('log.txt', 'a')
            info = str("%s  %s  %s" % (str(timestr), flag, _str))
            hFile.write(info)
            hFile.write('\n')
            hFile.close()
        except BaseException as e:
            self.label_state.setText("日志错误" + str(e))
        return

    def finishedFindMusic(self):
        try:
            self.label_state.setText("本地音频匹配完成，双击表格手动修改本地音频位置")
            self.btn_Lrc.setEnabled(True)
            for it in self.list:
                if len(it['path']) == 0:
                    self.tableWidget.setItem(it['no'], 3, QTableWidgetItem('未找到本地音频'))
            self.tableWidget.show()
        except BaseException as e:
            print(e)
        return

    # 回调函数
    def CallBack(self, code, args):
        mutex = threading.Lock()
        mutex.acquire()
        if code == StateCode.CallBackCode.MUSIC_LIST_RETURN:
            self.listShowInTable(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_PATH_RETURN:
            self.pathShowInTable(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_PATH_END:
            self.finishedFindMusic()
            pass
        elif code == StateCode.CallBackCode.MUSIC_SERACH_CURRENT:
            self.label_state.setText(str("正在查找：%s") % (args))
            pass
        elif code == StateCode.CallBackCode.MUSIC_LRC_RETURN:
            self.label_state.setText(str("正在匹配歌词：%s - %s") % (args['singer'], args['song']))
            self.lrcShowInTable(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_LRC_FINISHED:
            self.label_state.setText("歌词生成完成")
            pass
        elif code == StateCode.CallBackCode.UNKNOW_ERROR:
            self.UnknowError(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_COPY_FILE:
            self.copyState(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_COPY_ERROR:
            self.UnknowError(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_COPY_FINISHED:
            self.finishedCopy()
            pass
        elif code == StateCode.CallBackCode.PLAYER_M2U_FINISHED:
            self.finishedM3U()
            pass
        elif code == StateCode.CallBackCode.MUSIC_LRC_NONE:
            self.noLrc(args)
            pass
        elif code == StateCode.CallBackCode.MUSIC_LRC_ERROR:
            self.errorLrc(args)
            pass
        mutex.release()
        return


qApp = QApplication(sys.argv)
win = UI()
win.show()
sys.exit(qApp.exec())

# 111007305
# 615146628
