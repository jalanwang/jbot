# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'turtlebot_controller.ui'
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
    QPushButton, QSizePolicy, QStackedWidget, QTextEdit,
    QWidget)
from . import logo_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(645, 526)
        self.stackedWidget = QStackedWidget(Form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(20, 30, 601, 471))
        self.Page_main = QWidget()
        self.Page_main.setObjectName(u"Page_main")
        self.go_BP = QPushButton(self.Page_main)
        self.go_BP.setObjectName(u"go_BP")
        self.go_BP.setGeometry(QRect(130, 310, 121, 81))
        self.go_AP = QPushButton(self.Page_main)
        self.go_AP.setObjectName(u"go_AP")
        self.go_AP.setGeometry(QRect(350, 310, 121, 81))
        self.Title = QTextEdit(self.Page_main)
        self.Title.setObjectName(u"Title")
        self.Title.setEnabled(True)
        self.Title.setGeometry(QRect(170, 40, 261, 61))
        font = QFont()
        font.setBold(True)
        font.setItalic(False)
        self.Title.setFont(font)
        self.Title.setMouseTracking(True)
        self.Title.setAcceptDrops(True)
        self.Title.setReadOnly(True)
        self.logo = QLabel(self.Page_main)
        self.logo.setObjectName(u"logo")
        self.logo.setGeometry(QRect(190, 110, 221, 161))
        self.logo.setMaximumSize(QSize(797, 652))
        self.logo.setAutoFillBackground(False)
        original_pixmap = QPixmap(u":/newPrefix/image.png")
        scaled_pixmap = original_pixmap.scaled(
            self.logo.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.logo.setScaledContents(False)
        self.logo.setPixmap(scaled_pixmap)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(self.Page_main)
        self.page_Button = QWidget()
        self.page_Button.setObjectName(u"page_Button")
        self.label = QLabel(self.page_Button)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 10, 131, 51))
        self.btn_Go = QPushButton(self.page_Button)
        self.btn_Go.setObjectName(u"btn_Go")
        self.btn_Go.setGeometry(QRect(250, 130, 95, 81))
        self.btn_Stop = QPushButton(self.page_Button)
        self.btn_Stop.setObjectName(u"btn_Stop")
        self.btn_Stop.setGeometry(QRect(250, 220, 95, 81))
        self.btn_Back = QPushButton(self.page_Button)
        self.btn_Back.setObjectName(u"btn_Back")
        self.btn_Back.setGeometry(QRect(250, 310, 95, 81))
        self.btn_TRight = QPushButton(self.page_Button)
        self.btn_TRight.setObjectName(u"btn_TRight")
        self.btn_TRight.setGeometry(QRect(350, 220, 95, 81))
        self.btn_TLeft = QPushButton(self.page_Button)
        self.btn_TLeft.setObjectName(u"btn_TLeft")
        self.btn_TLeft.setGeometry(QRect(150, 220, 95, 81))
        self.btn_MP = QPushButton(self.page_Button)
        self.btn_MP.setObjectName(u"btn_MP")
        self.btn_MP.setGeometry(QRect(500, 10, 81, 41))
        font1 = QFont()
        font1.setBold(True)
        self.btn_MP.setFont(font1)
        self.stackedWidget.addWidget(self.page_Button)
        self.page_Auto = QWidget()
        self.page_Auto.setObjectName(u"page_Auto")
        self.label_6 = QLabel(self.page_Auto)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(30, 10, 131, 51))
        self.list_Dlog = QListWidget(self.page_Auto)
        self.list_Dlog.setObjectName(u"list_Dlog")
        self.list_Dlog.setGeometry(QRect(90, 130, 421, 301))
        self.label_7 = QLabel(self.page_Auto)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(90, 106, 81, 21))
        self.label_7.setFont(font1)
        self.btn_autoStart = QPushButton(self.page_Auto)
        self.btn_autoStart.setObjectName(u"btn_autoStart")
        self.btn_autoStart.setGeometry(QRect(380, 100, 61, 25))
        self.btn_MP_3 = QPushButton(self.page_Auto)
        self.btn_MP_3.setObjectName(u"btn_MP_3")
        self.btn_MP_3.setGeometry(QRect(500, 10, 81, 41))
        self.btn_MP_3.setFont(font1)
        self.btn_autoStop = QPushButton(self.page_Auto)
        self.btn_autoStop.setObjectName(u"btn_autoStop")
        self.btn_autoStop.setGeometry(QRect(450, 100, 61, 25))
        self.stackedWidget.addWidget(self.page_Auto)

        self.retranslateUi(Form)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Turtlebot_Controller", None))
        self.go_BP.setText(QCoreApplication.translate("Form", u"\uc218\ub3d9 \uc8fc\ud589", None))
        self.go_AP.setText(QCoreApplication.translate("Form", u"\uc790\uc728 \uc8fc\ud589", None))
        self.Title.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">SF-ONE</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">(TurtleBot \uc548\uc804\uad00\ub9ac \uc2dc\uc2a4\ud15c)</span></p></body></html>", None))
        self.logo.setText("")
        self.label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:700;\">\uc218\ub3d9 \uc8fc\ud589</span></p></body></html>", None))
        self.btn_Go.setText(QCoreApplication.translate("Form", u"Go", None))
        self.btn_Stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.btn_Back.setText(QCoreApplication.translate("Form", u"Back", None))
        self.btn_TRight.setText(QCoreApplication.translate("Form", u"Turn Right", None))
        self.btn_TLeft.setText(QCoreApplication.translate("Form", u"Turn Left", None))
        self.btn_MP.setText(QCoreApplication.translate("Form", u"Main", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:700;\">\uc790\uc728 \uc8fc\ud589</span></p></body></html>", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\uc8fc\ud589 \uc0c1\ud0dc", None))
        self.btn_autoStart.setText(QCoreApplication.translate("Form", u"Start", None))
        self.btn_MP_3.setText(QCoreApplication.translate("Form", u"Main", None))
        self.btn_autoStop.setText(QCoreApplication.translate("Form", u"Stop", None))
    # retranslateUi

