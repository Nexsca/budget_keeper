# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_menu_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainMenuWindow(object):
    def setupUi(self, MainMenuWindow):
        MainMenuWindow.setObjectName("MainMenuWindow")
        MainMenuWindow.resize(1100, 900)
        font = QtGui.QFont()
        font.setFamily("Garamond")
        font.setPointSize(18)
        MainMenuWindow.setFont(font)
        MainMenuWindow.setMouseTracking(False)
        MainMenuWindow.setStyleSheet("background-color: rgb(238, 237, 240);")
        self.centralwidget = QtWidgets.QWidget(MainMenuWindow)
        font = QtGui.QFont()
        font.setFamily("Caviar Dreams")
        font.setPointSize(28)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.centralwidget.setFont(font)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.enter_button = QtWidgets.QPushButton(self.centralwidget)
        self.enter_button.setGeometry(QtCore.QRect(325, 445, 450, 60))
        font = QtGui.QFont()
        font.setFamily("Involve")
        font.setPointSize(18)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.enter_button.setFont(font)
        self.enter_button.setStyleSheet("font: 18pt \"Involve\";\n"
"background-color: rgb(242, 233, 228);\n"
"color: rgb(34, 34, 59);\n"
"border-radius: 15px;\n"
"border: 1px solid #6d6875;")
        self.enter_button.setCheckable(False)
        self.enter_button.setAutoDefault(False)
        self.enter_button.setFlat(False)
        self.enter_button.setObjectName("enter_button")
        self.reg_button = QtWidgets.QPushButton(self.centralwidget)
        self.reg_button.setGeometry(QtCore.QRect(325, 525, 450, 60))
        self.reg_button.setStyleSheet("font: 18pt \"Involve\";\n"
"background-color: rgb(242, 233, 228);\n"
"color: rgb(34, 34, 59);\n"
"border-radius: 15px;\n"
"border: 1px solid #6d6875;")
        self.reg_button.setObjectName("reg_button")
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(90, 40, 240, 50))
        self.logo.setObjectName("logo")
        self.welcome_word = QtWidgets.QLabel(self.centralwidget)
        self.welcome_word.setGeometry(QtCore.QRect(0, 370, 1100, 40))
        self.welcome_word.setStyleSheet("color: rgb(34, 34, 59);\n"
"font: 24pt \"Involve\";")
        self.welcome_word.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_word.setObjectName("welcome_word")
        self.login_icon = QtWidgets.QLabel(self.centralwidget)
        self.login_icon.setGeometry(QtCore.QRect(329, 452, 50, 46))
        self.login_icon.setStyleSheet("background-color: rgb(242, 233, 228);")
        self.login_icon.setObjectName("login_icon")
        self.reg_icon = QtWidgets.QLabel(self.centralwidget)
        self.reg_icon.setGeometry(QtCore.QRect(329, 532, 50, 46))
        self.reg_icon.setStyleSheet("background-color: rgb(242, 233, 228);")
        self.reg_icon.setObjectName("reg_icon")
        self.logo_icon = QtWidgets.QLabel(self.centralwidget)
        self.logo_icon.setGeometry(QtCore.QRect(40, 40, 50, 50))
        self.logo_icon.setObjectName("logo_icon")
        self.word_1 = QtWidgets.QLabel(self.centralwidget)
        self.word_1.setGeometry(QtCore.QRect(40, 120, 115, 50))
        self.word_1.setStyleSheet("font: 34pt \"Involve\";\n"
"color: rgb(34, 34, 59);")
        self.word_1.setObjectName("word_1")
        self.word_3 = QtWidgets.QLabel(self.centralwidget)
        self.word_3.setGeometry(QtCore.QRect(330, 120, 260, 50))
        self.word_3.setStyleSheet("font: 34pt \"Involve\";\n"
"color: rgb(34, 34, 59);")
        self.word_3.setObjectName("word_3")
        self.word_2 = QtWidgets.QLabel(self.centralwidget)
        self.word_2.setGeometry(QtCore.QRect(155, 120, 175, 50))
        self.word_2.setStyleSheet("font: 63 34pt \"Involve SemiBold\";\n"
"color: rgb(229, 152, 155);")
        self.word_2.setObjectName("word_2")
        self.word_4 = QtWidgets.QLabel(self.centralwidget)
        self.word_4.setGeometry(QtCore.QRect(40, 170, 651, 50))
        self.word_4.setStyleSheet("font: 34pt \"Involve\";\n"
"color: rgb(34, 34, 59);")
        self.word_4.setObjectName("word_4")
        MainMenuWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainMenuWindow)
        QtCore.QMetaObject.connectSlotsByName(MainMenuWindow)

    def retranslateUi(self, MainMenuWindow):
        _translate = QtCore.QCoreApplication.translate
        MainMenuWindow.setWindowTitle(_translate("MainMenuWindow", "BudgetKeeper"))
        self.enter_button.setText(_translate("MainMenuWindow", "Войти"))
        self.reg_button.setText(_translate("MainMenuWindow", "Зарегистрироваться"))
        self.logo.setText(_translate("MainMenuWindow", "<html><head/><body><p><img src=\":/logo/app_name_horizontal_350x50.png\"/></p></body></html>"))
        self.welcome_word.setText(_translate("MainMenuWindow", "Войди в свой профиль или зарегистрируйся"))
        self.login_icon.setText(_translate("MainMenuWindow", "<html><head/><body><p><img src=\":/icons/login_icon.png\"/></p></body></html>"))
        self.reg_icon.setText(_translate("MainMenuWindow", "<html><head/><body><p><img src=\":/icons/reg_icon.png\"/></p></body></html>"))
        self.logo_icon.setText(_translate("MainMenuWindow", "<html><head/><body><p><img src=\":/icons/logo_icon_50x50.png\"/></p></body></html>"))
        self.word_1.setText(_translate("MainMenuWindow", "Твоё "))
        self.word_3.setText(_translate("MainMenuWindow", "решение "))
        self.word_2.setText(_translate("MainMenuWindow", "личное "))
        self.word_4.setText(_translate("MainMenuWindow", "для управления финансами"))
import main_menu_logo_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainMenuWindow = QtWidgets.QMainWindow()
    ui = Ui_MainMenuWindow()
    ui.setupUi(MainMenuWindow)
    MainMenuWindow.show()
    sys.exit(app.exec_())
