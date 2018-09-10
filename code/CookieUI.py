from PyQt5.QtWidgets import QPushButton,QTextEdit,QWidget,QDialog
from PyQt5.uic import loadUi

class CookieUI(QDialog):

    def __init__(self):
        super(QDialog,self).__init__()
        loadUi("Cookie.ui",self)
        self.strCookie=""
        self.text.setPlaceholderText("此处填入网易云音乐帐号cookie，通过music.163.com登陆后获得，具体获取cookie方式根据浏览器不同而不同，请自行解决")
        self.btn_ok.clicked.connect(self.slt_cookie)
        return

    def slt_cookie(self):
        self.cookie=self.text.toPlainText()
        self.close()