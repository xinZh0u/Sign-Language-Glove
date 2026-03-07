# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListView, QPushButton,
    QSizePolicy, QSlider, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(641, 613)
        self.verticalLayout_4 = QVBoxLayout(Widget)
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(Widget)
        self.label_5.setObjectName(u"label_5")
        font = QFont()
        font.setPointSize(14)
        font.setItalic(False)
        self.label_5.setFont(font)

        self.horizontalLayout_7.addWidget(self.label_5)

        self.lineEditSearch = QLineEdit(Widget)
        self.lineEditSearch.setObjectName(u"lineEditSearch")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditSearch.sizePolicy().hasHeightForWidth())
        self.lineEditSearch.setSizePolicy(sizePolicy)

        self.horizontalLayout_7.addWidget(self.lineEditSearch)


        self.verticalLayout_3.addLayout(self.horizontalLayout_7)

        self.gestureListView = QListView(Widget)
        self.gestureListView.setObjectName(u"gestureListView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.gestureListView.sizePolicy().hasHeightForWidth())
        self.gestureListView.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.gestureListView)


        self.horizontalLayout_6.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_6 = QLabel(Widget)
        self.label_6.setObjectName(u"label_6")
        font1 = QFont()
        font1.setPointSize(12)
        self.label_6.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_6)

        self.labelId = QLabel(Widget)
        self.labelId.setObjectName(u"labelId")
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        self.labelId.setFont(font2)

        self.horizontalLayout_4.addWidget(self.labelId)

        self.line = QFrame(Widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_4.addWidget(self.line)

        self.label_3 = QLabel(Widget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.label_3)

        self.lineEditName = QLineEdit(Widget)
        self.lineEditName.setObjectName(u"lineEditName")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineEditName.sizePolicy().hasHeightForWidth())
        self.lineEditName.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.lineEditName)

        self.pushButtonGestureNew = QPushButton(Widget)
        self.pushButtonGestureNew.setObjectName(u"pushButtonGestureNew")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButtonGestureNew.sizePolicy().hasHeightForWidth())
        self.pushButtonGestureNew.setSizePolicy(sizePolicy4)

        self.horizontalLayout_4.addWidget(self.pushButtonGestureNew)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(Widget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy5)

        self.horizontalLayout_5.addWidget(self.label_4)

        self.comboBoxRecord = QComboBox(Widget)
        self.comboBoxRecord.setObjectName(u"comboBoxRecord")

        self.horizontalLayout_5.addWidget(self.comboBoxRecord)

        self.pushButtonRecordNew = QPushButton(Widget)
        self.pushButtonRecordNew.setObjectName(u"pushButtonRecordNew")

        self.horizontalLayout_5.addWidget(self.pushButtonRecordNew)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButtonRecordSave = QPushButton(Widget)
        self.pushButtonRecordSave.setObjectName(u"pushButtonRecordSave")

        self.horizontalLayout_3.addWidget(self.pushButtonRecordSave)

        self.pushButtonRecordDel = QPushButton(Widget)
        self.pushButtonRecordDel.setObjectName(u"pushButtonRecordDel")

        self.horizontalLayout_3.addWidget(self.pushButtonRecordDel)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButtonRecordStart = QPushButton(Widget)
        self.pushButtonRecordStart.setObjectName(u"pushButtonRecordStart")

        self.horizontalLayout.addWidget(self.pushButtonRecordStart)

        self.pushButtonRecordEnd = QPushButton(Widget)
        self.pushButtonRecordEnd.setObjectName(u"pushButtonRecordEnd")

        self.horizontalLayout.addWidget(self.pushButtonRecordEnd)

        self.pushButtonRecordReview = QPushButton(Widget)
        self.pushButtonRecordReview.setObjectName(u"pushButtonRecordReview")

        self.horizontalLayout.addWidget(self.pushButtonRecordReview)


        self.verticalLayout_5.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.verticalLayout_5)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSliderPosStart = QSlider(Widget)
        self.horizontalSliderPosStart.setObjectName(u"horizontalSliderPosStart")
        self.horizontalSliderPosStart.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_2.addWidget(self.horizontalSliderPosStart)

        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.horizontalSliderPosEnd = QSlider(Widget)
        self.horizontalSliderPosEnd.setObjectName(u"horizontalSliderPosEnd")
        self.horizontalSliderPosEnd.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_2.addWidget(self.horizontalSliderPosEnd)

        self.pushButtonClearLog = QPushButton(Widget)
        self.pushButtonClearLog.setObjectName(u"pushButtonClearLog")

        self.horizontalLayout_2.addWidget(self.pushButtonClearLog)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.logBrowser = QTextBrowser(Widget)
        self.logBrowser.setObjectName(u"logBrowser")

        self.verticalLayout.addWidget(self.logBrowser)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.horizontalLayout_6.addLayout(self.verticalLayout_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_6)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"\u624b\u52bf\u5f55\u5236", None))
        self.label_5.setText(QCoreApplication.translate("Widget", u"\u624b\u52bf\u5217\u8868", None))
        self.label_6.setText(QCoreApplication.translate("Widget", u"id:", None))
        self.labelId.setText(QCoreApplication.translate("Widget", u"0", None))
        self.label_3.setText(QCoreApplication.translate("Widget", u"\u624b\u52bf\u540d\u79f0:", None))
        self.pushButtonGestureNew.setText(QCoreApplication.translate("Widget", u"\u65b0\u52a8\u4f5c", None))
        self.label_4.setText(QCoreApplication.translate("Widget", u"\u5f55\u5236\u6b21\u6570:", None))
        self.pushButtonRecordNew.setText(QCoreApplication.translate("Widget", u"\u65b0\u5f55\u5236", None))
        self.pushButtonRecordSave.setText(QCoreApplication.translate("Widget", u"\u4fdd\u5b58", None))
        self.pushButtonRecordDel.setText(QCoreApplication.translate("Widget", u"\u5220\u9664", None))
        self.pushButtonRecordStart.setText(QCoreApplication.translate("Widget", u"\u5f55\u5236", None))
        self.pushButtonRecordEnd.setText(QCoreApplication.translate("Widget", u"\u7ed3\u675f\u5f55\u5236", None))
        self.pushButtonRecordReview.setText(QCoreApplication.translate("Widget", u"\u56de\u653e", None))
        self.label.setText(QCoreApplication.translate("Widget", u"\u8d77\u59cb\u4f4d\u7f6e", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"\u7ed3\u675f\u4f4d\u7f6e", None))
        self.pushButtonClearLog.setText(QCoreApplication.translate("Widget", u"\u6e05\u7a7a\u65e5\u5fd7", None))
    # retranslateUi

