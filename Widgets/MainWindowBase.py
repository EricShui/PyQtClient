#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2019年1月9日
@author: Irony
@site: https://pyqt5.com https://github.com/892768447
@email: 892768447@qq.com
@file: Widgets.MainWindowBase
@description: 
"""
from multiprocessing import Process
import os
import webbrowser

from PyQt5.QtCore import pyqtSlot, QThreadPool, Qt, QUrl
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebPage

from Utils import Constants
from Utils.CommonUtil import Signals
from Utils.NetworkAccessManager import NetworkAccessManager
from Utils.SortFilterModel import SortFilterModel
from Utils.ThemeManager import ThemeManager
from Widgets.ToolTip import ToolTip


__Author__ = "Irony"
__Copyright__ = "Copyright (c) 2019"


def runCode(file):
    import sys
    import os  # @Reimport
    import runpy
    dirPath = os.path.dirname(file)
    sys.argv = [file]
    sys.path.insert(0, dirPath)
    os.chdir(dirPath)
    runpy.run_path(file, run_name='__main__')


class MainWindowBase:

    def _initUi(self):
        """初始UI"""
        self.setupUi(self)
        # 绑定返回顶部提示框
        ToolTip.bind(self.buttonBackToUp)
        # 隐藏进度条
        self.progressBar.setVisible(False)
        # 隐藏还原按钮
        self.buttonNormal.setVisible(False)
        # 隐藏目录树的滑动条
        self.treeViewCatalogs.verticalScrollBar().setVisible(False)
        # 加载主题
        ThemeManager.loadTheme(self)
        # 加载鼠标样式
        ThemeManager.loadCursor(self.widgetMain)
        ThemeManager.setPointerCursors(self)
        # 安装事件过滤器用于还原鼠标样式
        self.widgetMain.installEventFilter(self)

    def _initModel(self):
        """设置目录树Model"""
        self._dmodel = QStandardItemModel(self.treeViewCatalogs)
        self._fmodel = SortFilterModel(self.treeViewCatalogs)
        self._fmodel.setSourceModel(self._dmodel)
        self.treeViewCatalogs.setModel(self._fmodel)
        # 安装事件过滤器捕捉鼠标进入离开事件
        self.treeViewCatalogs.installEventFilter(self)

    def _initThread(self):
        """初始化线程池"""
        # 创建线程池,最多5个线程
        self._runnables = set()  # QRunnable任务集合
        self._threadPool = QThreadPool(self)
        self._threadPool.setMaxThreadCount(5)

    def _initSignals(self):
        """初始化信号槽"""
        self.webViewContent.loadStarted.connect(self.showProgressBar)
        self.webViewContent.loadFinished.connect(self.hideProgressBar)
        self.webViewContent.loadFinished.connect(self.renderReadme)
        self.webViewContent.linkClicked.connect(self.onLinkClicked)
        # 绑定全局信号槽
        Signals.progressBarShowed.connect(
            self.showProgressBar, type=Qt.QueuedConnection)
        Signals.itemAdded.connect(self.onItemAdded, type=Qt.QueuedConnection)
        Signals.runnableFinished.connect(
            self.onRunnableFinished, type=Qt.QueuedConnection)

    def _initWebView(self):
        """初始化网页"""
        settings = self.webViewContent.settings()
        # 设置默认编码
        settings.setDefaultTextEncoding('UTF-8')
        # 开启开发人员工具
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        page = self.webViewContent.page()
        # 设置链接可以点击
        page.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        # 使用自定义的网络请求类(方便处理一些链接点击)
        page.setNetworkAccessManager(NetworkAccessManager(self.webViewContent))

        # 加载readme
        self.webViewContent.load(QUrl.fromLocalFile(
            os.path.abspath(Constants.HomeFile)))

    def _runFile(self, file):
        """子进程运行文件
        :param file:    文件
        """
        p = Process(target=runCode, args=(os.path.abspath(file),))
        p.start()

    def _runJs(self, code):
        """执行js
        :param code:
        """
        self.webViewContent.page().mainFrame().evaluateJavaScript(code)

    def onLinkClicked(self, url):
        """加载网址
        :param url:
        """
        self.webViewContent.load(QUrl(url))

    def showProgressBar(self, visible=True):
        """显示进度条
        """
        self.progressBar.setVisible(visible)

    def hideProgressBar(self, _=False):
        """隐藏进度条
        """
        self.progressBar.setVisible(False)

    @pyqtSlot()
    def on_buttonSkin_clicked(self):
        """选择主题样式
        """
        pass

    @pyqtSlot()
    def on_buttonMinimum_clicked(self):
        """最小化
        """
        self.showMinimized()

    @pyqtSlot()
    def on_buttonMaximum_clicked(self):
        """最大化
        """
        self.showMaximized()

    @pyqtSlot()
    def on_buttonNormal_clicked(self):
        """还原
        """
        self.showNormal()

    @pyqtSlot()
    def on_buttonClose_clicked(self):
        """关闭
        """
        self.close()

    @pyqtSlot()
    def on_buttonHead_clicked(self):
        """点击头像
        """
        if Constants._Github == None:
            self.initLogin()
        else:
            self.renderReadme()

    def on_lineEditSearch_textChanged(self, text):
        """过滤筛选
        """
        self._fmodel.setFilterRegExp(text)

    @pyqtSlot()
    def on_buttonSearch_clicked(self):
        """点击搜索按钮
        """
        pass

    @pyqtSlot()
    def on_buttonGithub_clicked(self):
        """点击项目按钮
        """
        webbrowser.open_new_tab(Constants.UrlProject)

    @pyqtSlot()
    def on_buttonQQ_clicked(self):
        """点击QQ按钮
        """
        webbrowser.open(Constants.UrlQQ)

    @pyqtSlot()
    def on_buttonGroup_clicked(self):
        """点击群按钮
        """
        webbrowser.open(Constants.UrlGroup)

    @pyqtSlot()
    def on_buttonBackToUp_clicked(self):
        """点击返回按钮
        """
        self._runJs('backToUp();')