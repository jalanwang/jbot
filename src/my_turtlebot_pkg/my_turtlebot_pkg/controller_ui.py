# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'controller.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.pb_go = QPushButton(self.centralwidget)
        self.pb_go.setObjectName(u"pb_go")
        self.pb_go.setGeometry(QRect(160, 30, 89, 91))
        font = QFont()
        font.setPointSize(32)
        self.pb_go.setFont(font)
        self.pb_left = QPushButton(self.centralwidget)
        self.pb_left.setObjectName(u"pb_left")
        self.pb_left.setGeometry(QRect(60, 130, 89, 91))
        self.pb_left.setFont(font)
        self.pb_stop = QPushButton(self.centralwidget)
        self.pb_stop.setObjectName(u"pb_stop")
        self.pb_stop.setGeometry(QRect(160, 130, 89, 91))
        self.pb_stop.setFont(font)
        self.pb_right = QPushButton(self.centralwidget)
        self.pb_right.setObjectName(u"pb_right")
        self.pb_right.setGeometry(QRect(260, 130, 89, 91))
        self.pb_right.setFont(font)
        self.pb_back = QPushButton(self.centralwidget)
        self.pb_back.setObjectName(u"pb_back")
        self.pb_back.setGeometry(QRect(160, 230, 89, 91))
        self.pb_back.setFont(font)
        self.monitoring_screen = QListWidget(self.centralwidget)
        self.monitoring_screen.setObjectName(u"monitoring_screen")
        self.monitoring_screen.setGeometry(QRect(420, 10, 361, 561))
        self.pb_triangle = QPushButton(self.centralwidget)
        self.pb_triangle.setObjectName(u"pb_triangle")
        self.pb_triangle.setGeometry(QRect(50, 400, 141, 91))
        font1 = QFont()
        font1.setPointSize(24)
        self.pb_triangle.setFont(font1)
        self.pb_square = QPushButton(self.centralwidget)
        self.pb_square.setObjectName(u"pb_square")
        self.pb_square.setGeometry(QRect(230, 400, 141, 91))
        self.pb_square.setFont(font1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 370, 151, 20))
        font2 = QFont()
        font2.setPointSize(20)
        self.label.setFont(font2)
        self.label.setAlignment(Qt.AlignCenter)
        self.txt_distance = QLabel(self.centralwidget)
        self.txt_distance.setObjectName(u"txt_distance")
        self.txt_distance.setGeometry(QRect(50, 500, 321, 17))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 28))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pb_go.setText(QCoreApplication.translate("MainWindow", u"w", None))
        self.pb_left.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.pb_stop.setText(QCoreApplication.translate("MainWindow", u"S", None))
        self.pb_right.setText(QCoreApplication.translate("MainWindow", u"D", None))
        self.pb_back.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.pb_triangle.setText(QCoreApplication.translate("MainWindow", u"Trangle", None))
        self.pb_square.setText(QCoreApplication.translate("MainWindow", u"Square", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Action!", None))
        self.txt_distance.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

