import json
import sys
import Moudle163
import SonyManager
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QHeaderView, QTableWidgetItem, QMessageBox, \
	QAbstractItemView
from PyQt5.uic import loadUi

import StateCode
import _thread


class UI(QWidget):
	def __init__ (self):
		super(QWidget, self).__init__()
		loadUi("gui.ui", self)
		self.list = [None]
		self.listName = ''
		self.listCreator = ''
		self.initData()
		self.initUI()
		self.initBinding()
		return

	def initUI (self):
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
		self.tableWidget.setColumnWidth(5, 80)
		self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
		self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
		self.tableWidget.verticalHeader().setVisible(False)
		self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

		self.btn_findLocalMusic.setEnabled(False)
		self.btn_Lrc.setEnabled(False)
		return

	def initData (self):
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
		return

	def initBinding (self):
		self.btn_chooseMusicPath.clicked.connect(self.slot_chooseMusicPath)
		self.btn_choosePlayerPath.clicked.connect(self.slot_choosePlayerPath)
		self.btn_findMusic.clicked.connect(self.slot_findMusic)
		self.btn_copyMusic.clicked.connect(self.slot_copyMusic)
		self.btn_findLocalMusic.clicked.connect(self.slot_findLocalMusic)
		self.btn_Lrc.clicked.connect(self.slot_createLrc)
		return

	def slot_chooseMusicPath (self):
		dir = QFileDialog.getExistingDirectory()
		self.txt_musicDir.setText(dir)
		return

	def slot_choosePlayerPath (self):
		dir = QFileDialog.getExistingDirectory()
		self.txt_playerDir.setText(dir)
		return

	def slot_findMusic (self):
		self.btn_Lrc.setEnabled(False)
		findPath = self.txt_musicDir.text()
		listid = self.ListID.text()
		if len(findPath) == 0 or len(listid) == 0:
			QMessageBox.critical(self, "提示", '信息不完整')
			return
		self.tableWidget.clearSpans()
		self.writeConfig(self.txt_musicDir.text(), self.txt_playerDir.text())

		_thread.start_new_thread(Moudle163.RequestList, (listid, self.CallBack))
		return

	def slot_copyMusic (self):
		self.writeConfig(self.txt_musicDir.text(), self.txt_playerDir.text())
		for it in self.list:
			print(it)
		_thread.start_new_thread(SonyManager.CopyMusic,
								 (self.list, self.txt_playerDir.text(), self.CallBack))
		return

	def slot_findLocalMusic (self):
		path = self.txt_musicDir.text()
		self.label_state.setText("正在匹配当中...")
		_thread.start_new_thread(Moudle163.FindLocalMusic, (path, self.list, self.CallBack))
		return

	# 生成歌词按钮
	def slot_createLrc (self):
		_thread.start_new_thread(Moudle163.RequestLrc, (self.list, self.CallBack))
		return

	# 写入配置文件
	def writeConfig (self, _musicDir, _playerDir):
		try:
			hFile = open("config.cfg", 'w+')
			data = {"musicDir": _musicDir, "playerDir": _playerDir}
			info = json.dumps(data)
			hFile.write(str(info))
			hFile.close()
		except BaseException as e:
			QMessageBox.critical(self, '提示', str(e))
		return

	# 显示歌单信息
	def listShowInTable (self, args):
		try:
			tips = str('歌单名：%s   创建者：%s') % (str(args['listname']), str(args['creator']))
			self.listName = args['listname']
			self.listCreator = args['creator']
			self.ListInfo.setText(tips)
			self.tableWidget.clearSpans()
			self.list = args['list']
			num = len(self.list)
			self.tableWidget.setRowCount(num)
			for sn in range(num):
				it = self.list[sn]
				song = it['song']
				singer = it['singer']
				no = it['no']
				name = str("%s - %s" % (singer, song))
				self.tableWidget.setItem(sn, 0, QTableWidgetItem(str("%d") % no))
				self.tableWidget.setItem(sn, 1, QTableWidgetItem(name))

			self.btn_findLocalMusic.setEnabled(True)
		except BaseException as e:
			QMessageBox.critical(self, '错误', str(e))
		return

	# 匹配地址显示
	def pathShowInTable (self, args):
		no = args['no']
		path = args['path']
		self.tableWidget.setItem(no, 2, QTableWidgetItem(path))
		self.tableWidget.setItem(no, 3, QTableWidgetItem('匹配'))
		self.tableWidget.setCurrentCell(no, 2)
		for i in range(len(self.list)):
			if self.list[i]['no'] == no:
				self.list[i]['path'] = path
				break
		return

	# 歌词匹配状态显示
	def lrcShowInTable (self, args):
		self.tableWidget.setItem(args['no'], 4, QTableWidgetItem(str("匹配")))
		self.list[args['no']]['lrc'] = args['lrc']
		self.tableWidget.setCurrentCell(args['no'], 4)
		return

	def copyState (self, args):
		self.tableWidget.setItem(args['no'], 5, QTableWidgetItem("导入完成"))
		self.tableWidget.setCurrentCell(args['no'], 5)
		self.label_state.setText(str('《%s-%s》导入完成') % (args['singer'], args['song']))
		return

	def UnknowError (self, args):
		self.label_state.setText("未知错误")
		return

	def finishedCopy (self):
		self.label_state.setText("音频导入完成")
		_thread.start_new_thread(SonyManager.CreateM3u_inside,
								 (self.txt_playerDir.text(), self.list, self.listName, self.CallBack))
		return

	def finishedM3U (self):
		self.label_state.setText("播放列表创建完成")
		return

	# 回调函数
	def CallBack (self, code, args):
		if code == StateCode.CallBackCode.MUSIC_LIST_RETURN:
			self.listShowInTable(args)
			pass
		elif code == StateCode.CallBackCode.MUSIC_PATH_RETURN:
			self.pathShowInTable(args)
			pass
		elif code == StateCode.CallBackCode.MUSIC_PATH_END:
			self.label_state.setText("本地音频匹配完成")
			self.btn_Lrc.setEnabled(True)
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
		return


qApp = QApplication(sys.argv)
win = UI()
win.show()
sys.exit(qApp.exec())

# 111007305
# 615146628
