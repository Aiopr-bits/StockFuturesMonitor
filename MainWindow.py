import sys
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from StockFuturesMonitor import StockFuturesMonitor

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        # 使用self.resource_path调用成员函数
        ui_file = self.resource_path('MainWindow.ui')
        uic.loadUi(ui_file, self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.widget_2.hide()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # 初始化不透明度
        self._opacity = 1
        self.setWindowOpacity(self._opacity)

        # 创建QTimer成员变量
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)

        # 限制lineEdit_2只能输入正浮点数
        validator = QtGui.QDoubleValidator(0.0, float('inf'), 2)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.lineEdit_2.setValidator(validator)

        # 创建系统托盘
        self.create_tray_icon()

        self.radioButton.toggled.connect(self.on_radioButton_toggled)
        self.radioButton_2.toggled.connect(self.on_radioButton_2_toggled)
        self.radioButton.setChecked(True)

        self.lineEdit.installEventFilter(self)
        self.lineEdit_2.installEventFilter(self)
        self.pushButton.clicked.connect(self.onPushButtonClicked)
        self.pushButton_2.clicked.connect(self.onPushButton2Clicked)
        self._is_dragging = False
        self._drag_pos = None

        # 连接调色板按钮
        self.pushButton_3.clicked.connect(self.change_background_color)
        self.pushButton_4.clicked.connect(self.change_font_color)
        self.load_color_settings()

    def resource_path(self, relative_path):
        """获取资源文件的绝对路径，支持PyInstaller打包"""
        try:
            # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def on_radioButton_toggled(self, checked):
        """当第一个单选按钮被选中时，设置lineEdit和lineEdit_2的占位符文本"""
        if checked:
            self.lineEdit.setPlaceholderText("159659")
            self.lineEdit_2.setPlaceholderText("1")
            self.lineEdit.clear()
            self.lineEdit_2.clear()

    def on_radioButton_2_toggled(self, checked):
        """当第二个单选按钮被选中时，设置lineEdit和lineEdit_2的占位符文本"""
        if checked:
            self.lineEdit.setPlaceholderText("NQ")
            self.lineEdit_2.setPlaceholderText("1")
            self.lineEdit.clear()
            self.lineEdit_2.clear()

    def eventFilter(self, obj, event):
        """事件过滤器，用于处理lineEdit和lineEdit_2的焦点事件"""
        if event.type() == QtCore.QEvent.FocusIn:
            if obj in [self.lineEdit, self.lineEdit_2]:
                obj.clear()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于拖动窗口"""
        if event.button() == QtCore.Qt.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于拖动窗口"""
        if self._is_dragging and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，结束拖动窗口"""
        self._is_dragging = False
        event.accept()

    def onPushButtonClicked(self):
        """处理按钮点击事件，显示第二个窗口并开始定时器"""
        self.widget_2.show()
        self.widget.hide()
        self.setFocus()

        # 获取lineEdit_2中的浮点数，如果为空则使用占位符文本
        text = self.lineEdit_2.text()
        if text == "":
            text = self.lineEdit_2.placeholderText()

        try:
            timeRefreshesValue = float(text)
            self.timer.start(int(timeRefreshesValue * 1000))
        except ValueError:
            # 如果转换失败，使用默认值1秒
            self.timer.start(1000)

    def onPushButton2Clicked(self):
        """处理第二个按钮点击事件，隐藏第二个窗口并停止定时器"""
        self.hide()

    def keyPressEvent(self, event):
        """处理键盘按下事件"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.widget_2.hide()
            self.widget.show()
            self.timer.stop()
        elif event.key() == QtCore.Qt.Key_Up:
            # 上箭头提升不透明度
            self._opacity = min(1.0, self._opacity + 0.1)
            self.setWindowOpacity(self._opacity)
        elif event.key() == QtCore.Qt.Key_Down:
            # 下箭头降低不透明度
            self._opacity = max(0, self._opacity - 0.1)
            self.setWindowOpacity(self._opacity)

    def on_timer_timeout(self):
        """定时器超时事件处理"""
        self.resize(100, 30)
        text = self.lineEdit.text().strip()
        if text == "":
            text = self.lineEdit.placeholderText()

        if self.radioButton.isChecked():
            stockData = StockFuturesMonitor.get_stock_data(text)

            if 'error' in stockData:
                QtWidgets.QMessageBox.warning(self, "错误", stockData['error'])
                esc_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
                self.keyPressEvent(esc_event)

            else:
                current_price = stockData['current_price']
                change_amount = stockData['change_amount']
                change_percent = stockData['change_percent']

                self.label_3.setText(f" {current_price:.3f}  {change_amount:.3f}  {change_percent:.5f}%")

        elif self.radioButton_2.isChecked():
            futuresData = StockFuturesMonitor.get_futures_data(text)

            if 'error' in futuresData:
                QtWidgets.QMessageBox.warning(self, "错误", futuresData['error'])
                esc_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
                self.keyPressEvent(esc_event)
            else:
                current_price = futuresData['current_price']
                change_amount = futuresData['change_amount']
                change_percent = futuresData['change_percent']

                self.label_3.setText(f" {current_price:.3f}  {change_amount:.3f}  {change_percent:.5f}%")

    def create_tray_icon(self):
        """创建系统托盘图标和菜单"""
        # 创建托盘图标
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        # 使用self.resource_path获取图标路径
        icon_path = self.resource_path('res/icon.jpg')
        self.tray_icon.setIcon(QtGui.QIcon(icon_path))

        # 创建托盘菜单
        tray_menu = QtWidgets.QMenu()

        # 显示窗口选项
        show_action = tray_menu.addAction("显示窗口")
        show_action.triggered.connect(self.show_window)

        # 隐藏窗口选项
        hide_action = tray_menu.addAction("隐藏窗口")
        hide_action.triggered.connect(self.hide_window)

        # 分隔线
        tray_menu.addSeparator()

        # 退出程序选项
        quit_action = tray_menu.addAction("退出程序")
        quit_action.triggered.connect(QtWidgets.QApplication.quit)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)

        # 左键点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # 左键点击
            self.show_window()

    def show_window(self):
        """显示窗口"""
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_window(self):
        """隐藏窗口"""
        self.hide()

    def closeEvent(self, event):
        """重写关闭事件，最小化到托盘而不是退出"""
        event.ignore()
        self.hide()
        # 可选：显示托盘消息提示
        self.tray_icon.showMessage(
            "程序已最小化",
            "程序已最小化到系统托盘，左键点击图标可重新显示窗口",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )

    def style_dialog_buttons(self, dialog):
        """为对话框中的所有按钮设置样式"""
        button_style = """
            QPushButton {
                background-color: rgb(255, 255, 255);
                border: 1px solid rgb(122, 122, 122);
                border-radius: 2px;
                min-width: 60px;
                min-height: 20px;
            }

            QPushButton:hover {
                background-color: rgb(242, 242, 242);
            }

            QPushButton:pressed {
                background-color: rgb(235, 235, 235);
            }
        """

        # 查找对话框中的所有QPushButton并递归查找子控件
        def apply_style_to_buttons(widget):
            for child in widget.children():
                if isinstance(child, QtWidgets.QPushButton):
                    child.setStyleSheet(button_style)
                elif hasattr(child, 'children'):
                    apply_style_to_buttons(child)

        apply_style_to_buttons(dialog)

        # 同时直接设置findChildren找到的按钮
        buttons = dialog.findChildren(QtWidgets.QPushButton)
        for button in buttons:
            button.setStyleSheet(button_style)

    def change_background_color(self):
        """点击按钮弹出调色板设置背景颜色"""
        current_color = QtCore.Qt.white
        # 尝试获取当前背景颜色
        try:
            current_style = self.styleSheet()
            if 'background-color:' in current_style:
                color_start = current_style.find('background-color:') + len('background-color:')
                color_end = current_style.find(';', color_start)
                if color_end == -1:
                    color_end = len(current_style)
                color_name = current_style[color_start:color_end].strip()
                current_color = QtGui.QColor(color_name)
        except:
            current_color = QtCore.Qt.white

        # 创建自定义的QColorDialog
        color_dialog = QtWidgets.QColorDialog(current_color, self)
        color_dialog.setWindowTitle("选择背景颜色")

        # 显示对话框后查找并设置按钮样式
        QtCore.QTimer.singleShot(0, lambda: self.style_dialog_buttons(color_dialog))

        if color_dialog.exec_() == QtWidgets.QDialog.Accepted:
            color = color_dialog.currentColor()
            # 保持原有的字体颜色，只改变背景颜色
            font_color = self.get_current_font_color()
            new_style = f"background-color: {color.name()}; color: {font_color};"
            self.setStyleSheet(new_style)
            self.save_color_settings(background_color=color.name())

    def change_font_color(self):
        """点击按钮弹出调色板设置字体颜色"""
        current_color = QtCore.Qt.black
        # 尝试获取当前字体颜色
        try:
            current_style = self.styleSheet()
            if 'color:' in current_style:
                # 查找字体颜色（不是背景颜色）
                parts = current_style.split(';')
                for part in parts:
                    if 'color:' in part and 'background-color:' not in part:
                        color_name = part.split('color:')[1].strip()
                        current_color = QtGui.QColor(color_name)
                        break
        except:
            current_color = QtCore.Qt.black

        # 创建自定义的QColorDialog
        color_dialog = QtWidgets.QColorDialog(current_color, self)
        color_dialog.setWindowTitle("选择字体颜色")

        # 显示对话框后查找并设置按钮样式
        QtCore.QTimer.singleShot(0, lambda: self.style_dialog_buttons(color_dialog))

        if color_dialog.exec_() == QtWidgets.QDialog.Accepted:
            color = color_dialog.currentColor()
            # 保持原有的背景颜色，只改变字体颜色
            background_color = self.get_current_background_color()
            new_style = f"background-color: {background_color}; color: {color.name()};"
            self.setStyleSheet(new_style)
            self.save_color_settings(font_color=color.name())

    def get_current_background_color(self):
        """获取当前背景颜色"""
        try:
            current_style = self.styleSheet()
            if 'background-color:' in current_style:
                color_start = current_style.find('background-color:') + len('background-color:')
                color_end = current_style.find(';', color_start)
                if color_end == -1:
                    color_end = len(current_style)
                return current_style[color_start:color_end].strip()
        except:
            pass
        return '#ffffff'  # 默认白色

    def get_current_font_color(self):
        """获取当前字体颜色"""
        try:
            current_style = self.styleSheet()
            if 'color:' in current_style:
                parts = current_style.split(';')
                for part in parts:
                    if 'color:' in part and 'background-color:' not in part:
                        return part.split('color:')[1].strip()
        except:
            pass
        return '#000000'  # 默认黑色

    def save_color_settings(self, background_color=None, font_color=None):
        """保存颜色设置到配置文件"""
        try:
            import json
            config_file = self.resource_path('config.json')

            # 读取现有配置
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {}

            # 更新颜色设置
            if background_color:
                config['background_color'] = background_color
            if font_color:
                config['font_color'] = font_color

            # 保存配置
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存颜色设置失败: {e}")

    def load_color_settings(self):
        """从配置文件加载颜色设置"""
        try:
            import json
            config_file = self.resource_path('config.json')
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                background_color = config.get('background_color', '#ffffff')
                font_color = config.get('font_color', '#000000')
                style = f"background-color: {background_color}; color: {font_color};"
                self.setStyleSheet(style)
        except Exception:
            # 如果加载失败，使用默认颜色
            self.setStyleSheet("background-color: #ffffff; color: #000000;")