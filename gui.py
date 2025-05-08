import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QComboBox,
                           QPushButton, QTextEdit, QGroupBox, QGridLayout,
                           QSpinBox, QDoubleSpinBox, QTabWidget, QFrame,
                           QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor, QIcon
from main import UnmannedAircraft
from enums import *
import os

class HexEditor(QTextEdit):
    """十六进制编辑器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas", 18))  # 使用等宽字体
        self.setReadOnly(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 隐藏水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 隐藏垂直滚动条

        # 设置背景色和边框
        self.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QTextEdit:focus {
                border: 1px solid #4a90e2;
            }
        """)

        # 设置占位符文本
        self.setPlaceholderText("输入25字节的十六进制数据，例如：0F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")

        # 连接文本变化信号
        self.textChanged.connect(self.format_text)

    def format_text(self):
        """格式化十六进制文本"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # 移除所有空格
        text = self.toPlainText().replace(" ", "")

        # 转换为大写
        text = text.upper()

        # 每两个字符添加一个空格
        formatted_text = " ".join(text[i:i+2] for i in range(0, len(text), 2))

        # 如果文本不同，更新文本
        if formatted_text != self.toPlainText():
            self.setPlainText(formatted_text)
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

    def get_bytes(self):
        """获取字节数据"""
        text = self.toPlainText().replace(" ", "")
        if len(text) != 50:  # 25字节 = 50个十六进制字符
            return None
        try:
            return bytes.fromhex(text)
        except ValueError:
            return None

    def set_bytes(self, data):
        """设置字节数据"""
        if data:
            self.setPlainText(data.hex().upper())
            self.format_text()

class RemoteIDGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("无人机远程识别消息编解码工具")
        self.setMinimumSize(900, 600)

        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "drone.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建主布局
        layout = QVBoxLayout(main_widget)

        # 创建标签页
        self.tab_widget = QTabWidget()

        # 创建各个消息类型的标签页
        self.basic_id_tab = self.create_basic_id_tab()
        self.location_tab = self.create_location_tab()
        self.self_id_tab = self.create_self_id_tab()
        self.system_tab = self.create_system_tab()

        # 添加标签页
        self.tab_widget.addTab(self.basic_id_tab, "基本ID信息")
        self.tab_widget.addTab(self.location_tab, "位置向量信息")
        self.tab_widget.addTab(self.self_id_tab, "运行描述信息")
        self.tab_widget.addTab(self.system_tab, "系统信息")

        # 添加标签页到主布局
        layout.addWidget(self.tab_widget)

        # 设置默认值
        self.set_default_values()

    def create_basic_id_tab(self):
        """创建基本ID信息标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # 左侧：输入区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(400)  # 设置固定宽度

        # 基本ID信息
        basic_id_group = QGroupBox("基本ID信息")
        basic_id_layout = QGridLayout()
        basic_id_layout.setSpacing(10)
        basic_id_layout.setContentsMargins(10, 15, 10, 15)

        basic_id_layout.addWidget(QLabel("ID类型:"), 0, 0)
        self.id_type_combo = QComboBox()
        self.id_type_combo.setMinimumHeight(30)
        self.id_type_combo.addItems([t.name for t in IDType])
        basic_id_layout.addWidget(self.id_type_combo, 0, 1)

        basic_id_layout.addWidget(QLabel("无人机类型:"), 1, 0)
        self.ua_type_combo = QComboBox()
        self.ua_type_combo.setMinimumHeight(30)
        self.ua_type_combo.addItems([t.name for t in UAType])
        basic_id_layout.addWidget(self.ua_type_combo, 1, 1)

        basic_id_layout.addWidget(QLabel("识别码:"), 2, 0)
        self.id_edit = QTextEdit()
        self.id_edit.setMinimumHeight(60)  # 设置最小高度
        self.id_edit.setMaximumHeight(100)  # 设置最大高度
        basic_id_layout.addWidget(self.id_edit, 2, 1)

        basic_id_group.setLayout(basic_id_layout)
        left_layout.addWidget(basic_id_group)

        # 添加按钮
        button_layout = QHBoxLayout()
        self.basic_id_encode_button = QPushButton("编码")
        self.basic_id_encode_button.clicked.connect(lambda: self.encode_message(MessageType.BASIC_ID))
        button_layout.addWidget(self.basic_id_encode_button)

        self.basic_id_decode_button = QPushButton("解码")
        self.basic_id_decode_button.clicked.connect(lambda: self.decode_message(MessageType.BASIC_ID))
        button_layout.addWidget(self.basic_id_decode_button)

        left_layout.addLayout(button_layout)

        # 右侧：显示区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 报文（十六进制字节码）
        encoded_group = QGroupBox("报文（十六进制字节码）")
        encoded_group.setFixedHeight(200)
        encoded_layout = QVBoxLayout()
        self.basic_id_encoded_text = HexEditor()
        encoded_layout.addWidget(self.basic_id_encoded_text)
        encoded_group.setLayout(encoded_layout)
        right_layout.addWidget(encoded_group)

        # 解码得到的消息
        decoded_group = QGroupBox("解码得到的消息")
        decoded_layout = QVBoxLayout()
        self.basic_id_decoded_text = QTextEdit()
        self.basic_id_decoded_text.setReadOnly(True)
        decoded_layout.addWidget(self.basic_id_decoded_text)
        decoded_group.setLayout(decoded_layout)
        right_layout.addWidget(decoded_group)

        # 添加左右两侧到布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        return tab

    def create_location_tab(self):
        """创建位置向量信息标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # 左侧：输入区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(400)  # 设置固定宽度

        # 位置向量信息
        location_group = QGroupBox("位置向量信息")
        location_layout = QGridLayout()
        location_layout.setSpacing(10)
        location_layout.setContentsMargins(10, 15, 10, 15)

        location_layout.addWidget(QLabel("运行状态:"), 0, 0)
        self.operational_status_combo = QComboBox()
        self.operational_status_combo.setMinimumHeight(30)
        self.operational_status_combo.addItems([s.name for s in OperationalStatus])
        location_layout.addWidget(self.operational_status_combo, 0, 1)

        location_layout.addWidget(QLabel("高度类型:"), 1, 0)
        self.height_type_combo = QComboBox()
        self.height_type_combo.setMinimumHeight(30)
        self.height_type_combo.addItems([t.name for t in HeightType])
        location_layout.addWidget(self.height_type_combo, 1, 1)

        location_layout.addWidget(QLabel("航迹角(度):"), 2, 0)
        self.direction_spin = QSpinBox()
        self.direction_spin.setMinimumHeight(30)
        self.direction_spin.setRange(0, 359)
        location_layout.addWidget(self.direction_spin, 2, 1)

        location_layout.addWidget(QLabel("地速(m/s):"), 3, 0)
        self.horizontal_speed_spin = QDoubleSpinBox()
        self.horizontal_speed_spin.setMinimumHeight(30)
        self.horizontal_speed_spin.setRange(0, 254.25)
        self.horizontal_speed_spin.setSingleStep(0.25)
        location_layout.addWidget(self.horizontal_speed_spin, 3, 1)

        location_layout.addWidget(QLabel("垂直速度(m/s):"), 4, 0)
        self.vertical_speed_spin = QDoubleSpinBox()
        self.vertical_speed_spin.setMinimumHeight(30)
        self.vertical_speed_spin.setRange(-62, 62)
        self.vertical_speed_spin.setSingleStep(0.5)
        location_layout.addWidget(self.vertical_speed_spin, 4, 1)

        location_layout.addWidget(QLabel("纬度:"), 5, 0)
        self.latitude_spin = QDoubleSpinBox()
        self.latitude_spin.setMinimumHeight(30)
        self.latitude_spin.setMinimumWidth(200)
        self.latitude_spin.setRange(-90, 90)
        self.latitude_spin.setSingleStep(0.0000001)
        self.latitude_spin.setDecimals(7)
        location_layout.addWidget(self.latitude_spin, 5, 1)

        location_layout.addWidget(QLabel("经度:"), 6, 0)
        self.longitude_spin = QDoubleSpinBox()
        self.longitude_spin.setMinimumHeight(30)
        self.longitude_spin.setMinimumWidth(200)
        self.longitude_spin.setRange(-180, 180)
        self.longitude_spin.setSingleStep(0.0000001)
        self.longitude_spin.setDecimals(7)
        location_layout.addWidget(self.longitude_spin, 6, 1)

        location_layout.addWidget(QLabel("气压高度(m):"), 7, 0)
        self.pressure_altitude_spin = QDoubleSpinBox()
        self.pressure_altitude_spin.setMinimumHeight(30)
        self.pressure_altitude_spin.setRange(-1000, 31767)
        self.pressure_altitude_spin.setSingleStep(0.5)
        location_layout.addWidget(self.pressure_altitude_spin, 7, 1)

        location_layout.addWidget(QLabel("几何高度(m):"), 8, 0)
        self.geodetic_altitude_spin = QDoubleSpinBox()
        self.geodetic_altitude_spin.setMinimumHeight(30)
        self.geodetic_altitude_spin.setRange(-1000, 31767)
        self.geodetic_altitude_spin.setSingleStep(0.5)
        location_layout.addWidget(self.geodetic_altitude_spin, 8, 1)

        location_layout.addWidget(QLabel("距地高度(m):"), 9, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setMinimumHeight(30)
        self.height_spin.setRange(-1000, 31767)
        self.height_spin.setSingleStep(0.5)
        location_layout.addWidget(self.height_spin, 9, 1)

        # 添加精度相关字段
        location_layout.addWidget(QLabel("几何高度精度:"), 10, 0)
        self.geodetic_accuracy_combo = QComboBox()
        self.geodetic_accuracy_combo.setMinimumHeight(30)
        self.geodetic_accuracy_combo.addItems([t.name for t in VerticalAccuracy])
        location_layout.addWidget(self.geodetic_accuracy_combo, 10, 1)

        location_layout.addWidget(QLabel("水平精度:"), 11, 0)
        self.horizontal_accuracy_combo = QComboBox()
        self.horizontal_accuracy_combo.setMinimumHeight(30)
        self.horizontal_accuracy_combo.addItems([t.name for t in HorizontalAccuracy])
        location_layout.addWidget(self.horizontal_accuracy_combo, 11, 1)

        location_layout.addWidget(QLabel("气压高度精度:"), 12, 0)
        self.pressure_accuracy_combo = QComboBox()
        self.pressure_accuracy_combo.setMinimumHeight(30)
        self.pressure_accuracy_combo.addItems([t.name for t in VerticalAccuracy])
        location_layout.addWidget(self.pressure_accuracy_combo, 12, 1)

        location_layout.addWidget(QLabel("速度精度:"), 13, 0)
        self.speed_accuracy_combo = QComboBox()
        self.speed_accuracy_combo.setMinimumHeight(30)
        self.speed_accuracy_combo.addItems([t.name for t in SpeedAccuracy])
        location_layout.addWidget(self.speed_accuracy_combo, 13, 1)

        location_layout.addWidget(QLabel("时间戳精度(秒):"), 14, 0)
        self.timestamp_accuracy_spin = QDoubleSpinBox()
        self.timestamp_accuracy_spin.setMinimumHeight(30)
        self.timestamp_accuracy_spin.setRange(0, 1.5)
        self.timestamp_accuracy_spin.setSingleStep(0.1)
        location_layout.addWidget(self.timestamp_accuracy_spin, 14, 1)

        location_group.setLayout(location_layout)
        left_layout.addWidget(location_group)

        # 添加按钮
        button_layout = QHBoxLayout()
        self.location_encode_button = QPushButton("编码")
        self.location_encode_button.clicked.connect(lambda: self.encode_message(MessageType.LOCATION))
        button_layout.addWidget(self.location_encode_button)

        self.location_decode_button = QPushButton("解码")
        self.location_decode_button.clicked.connect(lambda: self.decode_message(MessageType.LOCATION))
        button_layout.addWidget(self.location_decode_button)

        left_layout.addLayout(button_layout)

        # 右侧：显示区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 报文（十六进制字节码）
        encoded_group = QGroupBox("报文（十六进制字节码）")
        encoded_group.setFixedHeight(200)
        encoded_layout = QVBoxLayout()
        self.location_encoded_text = HexEditor()
        encoded_layout.addWidget(self.location_encoded_text)
        encoded_group.setLayout(encoded_layout)
        right_layout.addWidget(encoded_group)

        # 解码得到的消息
        decoded_group = QGroupBox("解码得到的消息")
        decoded_layout = QVBoxLayout()
        self.location_decoded_text = QTextEdit()
        self.location_decoded_text.setReadOnly(True)
        decoded_layout.addWidget(self.location_decoded_text)
        decoded_group.setLayout(decoded_layout)
        right_layout.addWidget(decoded_group)

        # 添加左右两侧到布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        return tab

    def create_self_id_tab(self):
        """创建运行描述信息标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # 左侧：输入区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(400)  # 设置固定宽度

        # 运行描述信息
        self_id_group = QGroupBox("运行描述信息")
        self_id_layout = QGridLayout()
        self_id_layout.setSpacing(10)
        self_id_layout.setContentsMargins(10, 15, 10, 15)

        self_id_layout.addWidget(QLabel("描述类型:"), 0, 0)
        self.description_type_combo = QComboBox()
        self.description_type_combo.setMinimumHeight(30)
        self.description_type_combo.addItems([t.name for t in DescriptionType])
        self_id_layout.addWidget(self.description_type_combo, 0, 1)

        self_id_layout.addWidget(QLabel("描述:"), 1, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(60)  # 设置最小高度
        self.description_edit.setMaximumHeight(100)  # 设置最大高度
        self_id_layout.addWidget(self.description_edit, 1, 1)

        self_id_group.setLayout(self_id_layout)
        left_layout.addWidget(self_id_group)

        # 添加按钮
        button_layout = QHBoxLayout()
        self.self_id_encode_button = QPushButton("编码")
        self.self_id_encode_button.clicked.connect(lambda: self.encode_message(MessageType.SELF_ID))
        button_layout.addWidget(self.self_id_encode_button)

        self.self_id_decode_button = QPushButton("解码")
        self.self_id_decode_button.clicked.connect(lambda: self.decode_message(MessageType.SELF_ID))
        button_layout.addWidget(self.self_id_decode_button)

        left_layout.addLayout(button_layout)

        # 右侧：显示区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 报文（十六进制字节码）
        encoded_group = QGroupBox("报文（十六进制字节码）")
        encoded_group.setFixedHeight(200)
        encoded_layout = QVBoxLayout()
        self.self_id_encoded_text = HexEditor()
        encoded_layout.addWidget(self.self_id_encoded_text)
        encoded_group.setLayout(encoded_layout)
        right_layout.addWidget(encoded_group)

        # 解码得到的消息
        decoded_group = QGroupBox("解码得到的消息")
        decoded_layout = QVBoxLayout()
        self.self_id_decoded_text = QTextEdit()
        self.self_id_decoded_text.setReadOnly(True)
        decoded_layout.addWidget(self.self_id_decoded_text)
        decoded_group.setLayout(decoded_layout)
        right_layout.addWidget(decoded_group)

        # 添加左右两侧到布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        return tab

    def create_system_tab(self):
        """创建系统信息标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # 左侧：输入区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(400)  # 设置固定宽度

        # 系统信息
        system_group = QGroupBox("系统信息")
        system_layout = QGridLayout()
        system_layout.setSpacing(10)
        system_layout.setContentsMargins(10, 15, 10, 15)

        system_layout.addWidget(QLabel("等级分类归属地区:"), 0, 0)
        self.classification_type_combo = QComboBox()
        self.classification_type_combo.setMinimumHeight(30)
        self.classification_type_combo.addItems([t.name for t in ClassificationType])
        system_layout.addWidget(self.classification_type_combo, 0, 1)

        system_layout.addWidget(QLabel("控制站位置类型:"), 1, 0)
        self.operator_location_source_type_combo = QComboBox()
        self.operator_location_source_type_combo.setMinimumHeight(30)
        self.operator_location_source_type_combo.addItems([t.name for t in OperatorLocationSourceType])
        system_layout.addWidget(self.operator_location_source_type_combo, 1, 1)

        system_layout.addWidget(QLabel("控制站纬度:"), 2, 0)
        self.operator_latitude_spin = QDoubleSpinBox()
        self.operator_latitude_spin.setMinimumHeight(30)
        self.operator_latitude_spin.setMinimumWidth(200)
        self.operator_latitude_spin.setRange(-90, 90)
        self.operator_latitude_spin.setSingleStep(0.0000001)
        self.operator_latitude_spin.setDecimals(7)
        system_layout.addWidget(self.operator_latitude_spin, 2, 1)

        system_layout.addWidget(QLabel("控制站经度:"), 3, 0)
        self.operator_longitude_spin = QDoubleSpinBox()
        self.operator_longitude_spin.setMinimumHeight(30)
        self.operator_longitude_spin.setMinimumWidth(200)
        self.operator_longitude_spin.setRange(-180, 180)
        self.operator_longitude_spin.setSingleStep(0.0000001)
        self.operator_longitude_spin.setDecimals(7)
        system_layout.addWidget(self.operator_longitude_spin, 3, 1)

        system_layout.addWidget(QLabel("运行区域内航空器数量:"), 4, 0)
        self.area_count_spin = QSpinBox()
        self.area_count_spin.setMinimumHeight(30)
        self.area_count_spin.setRange(1, 65535)
        system_layout.addWidget(self.area_count_spin, 4, 1)

        system_layout.addWidget(QLabel("运行区域半径(m):"), 5, 0)
        self.area_radius_spin = QDoubleSpinBox()
        self.area_radius_spin.setMinimumHeight(30)
        self.area_radius_spin.setRange(0, 2554)
        self.area_radius_spin.setSingleStep(10)
        system_layout.addWidget(self.area_radius_spin, 5, 1)

        system_layout.addWidget(QLabel("运行区域高度上限(m):"), 6, 0)
        self.area_ceiling_spin = QDoubleSpinBox()
        self.area_ceiling_spin.setMinimumHeight(30)
        self.area_ceiling_spin.setRange(-1000, 31767)
        self.area_ceiling_spin.setSingleStep(0.5)
        system_layout.addWidget(self.area_ceiling_spin, 6, 1)

        system_layout.addWidget(QLabel("运行区域高度下限(m):"), 7, 0)
        self.area_floor_spin = QDoubleSpinBox()
        self.area_floor_spin.setMinimumHeight(30)
        self.area_floor_spin.setRange(-1000, 31767)
        self.area_floor_spin.setSingleStep(0.5)
        system_layout.addWidget(self.area_floor_spin, 7, 1)

        system_layout.addWidget(QLabel("控制站高度(m):"), 8, 0)
        self.operator_altitude_spin = QDoubleSpinBox()
        self.operator_altitude_spin.setMinimumHeight(30)
        self.operator_altitude_spin.setRange(-1000, 31767)
        self.operator_altitude_spin.setSingleStep(0.5)
        system_layout.addWidget(self.operator_altitude_spin, 8, 1)

        # 在系统信息标签页中添加无人机类别和等级字段
        self.eu_ua_widgets = []  # 存储欧盟相关控件
        self.china_ua_widgets = []  # 存储中国相关控件

        # 欧盟无人机类别和等级
        eu_ua_category_label = QLabel("欧盟无人机类别:")
        system_layout.addWidget(eu_ua_category_label, 9, 0)
        self.eu_ua_category_combo = QComboBox()
        self.eu_ua_category_combo.setMinimumHeight(30)
        self.eu_ua_category_combo.addItems([t.name for t in EUUACategory])
        system_layout.addWidget(self.eu_ua_category_combo, 9, 1)

        eu_ua_class_label = QLabel("欧盟无人机等级:")
        system_layout.addWidget(eu_ua_class_label, 10, 0)
        self.eu_ua_class_combo = QComboBox()
        self.eu_ua_class_combo.setMinimumHeight(30)
        self.eu_ua_class_combo.addItems([t.name for t in EUUAClass])
        system_layout.addWidget(self.eu_ua_class_combo, 10, 1)

        self.eu_ua_widgets.extend([
            eu_ua_category_label, self.eu_ua_category_combo,
            eu_ua_class_label, self.eu_ua_class_combo
        ])

        # 中国无人机类别和等级
        china_ua_category_label = QLabel("中国无人机类别:")
        system_layout.addWidget(china_ua_category_label, 11, 0)
        self.china_ua_category_combo = QComboBox()
        self.china_ua_category_combo.setMinimumHeight(30)
        self.china_ua_category_combo.addItems([t.name for t in ChinaUACategory])
        system_layout.addWidget(self.china_ua_category_combo, 11, 1)

        china_ua_class_label = QLabel("中国无人机等级:")
        system_layout.addWidget(china_ua_class_label, 12, 0)
        self.china_ua_class_combo = QComboBox()
        self.china_ua_class_combo.setMinimumHeight(30)
        self.china_ua_class_combo.addItems([t.name for t in ChinaUAClass])
        system_layout.addWidget(self.china_ua_class_combo, 12, 1)

        self.china_ua_widgets.extend([
            china_ua_category_label, self.china_ua_category_combo,
            china_ua_class_label, self.china_ua_class_combo
        ])

        # 连接分类类型变化信号
        self.classification_type_combo.currentTextChanged.connect(self.on_classification_type_changed)

        # 初始化显示状态
        self.on_classification_type_changed(self.classification_type_combo.currentText())

        system_group.setLayout(system_layout)
        left_layout.addWidget(system_group)

        # 添加按钮
        button_layout = QHBoxLayout()
        self.system_encode_button = QPushButton("编码")
        self.system_encode_button.clicked.connect(lambda: self.encode_message(MessageType.SYSTEM))
        button_layout.addWidget(self.system_encode_button)

        self.system_decode_button = QPushButton("解码")
        self.system_decode_button.clicked.connect(lambda: self.decode_message(MessageType.SYSTEM))
        button_layout.addWidget(self.system_decode_button)

        left_layout.addLayout(button_layout)

        # 右侧：显示区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 报文（十六进制字节码）
        encoded_group = QGroupBox("报文（十六进制字节码）")
        encoded_group.setFixedHeight(200)
        encoded_layout = QVBoxLayout()
        self.system_encoded_text = HexEditor()
        encoded_layout.addWidget(self.system_encoded_text)
        encoded_group.setLayout(encoded_layout)
        right_layout.addWidget(encoded_group)

        # 解码得到的消息
        decoded_group = QGroupBox("解码得到的消息")
        decoded_layout = QVBoxLayout()
        self.system_decoded_text = QTextEdit()
        self.system_decoded_text.setReadOnly(True)
        decoded_layout.addWidget(self.system_decoded_text)
        decoded_group.setLayout(decoded_layout)
        right_layout.addWidget(decoded_group)

        # 添加左右两侧到布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        return tab

    def on_classification_type_changed(self, text):
        """响应等级分类归属地区变化"""
        # 隐藏所有相关控件
        for widget in self.eu_ua_widgets + self.china_ua_widgets:
            widget.hide()

        # 根据选择显示对应控件
        if text == "EUROPEAN_UNION":
            for widget in self.eu_ua_widgets:
                widget.show()
        elif text == "CHINA":
            for widget in self.china_ua_widgets:
                widget.show()

    def set_default_values(self):
        """设置默认值"""
        self.id_type_combo.setCurrentText("SERIAL_NUMBER")
        self.ua_type_combo.setCurrentText("MULTIROTOR")
        self.id_edit.setText("DRONE001")
        self.operational_status_combo.setCurrentText("AIRBORNE")
        self.height_type_combo.setCurrentText("ABOVE_TAKEOFF")
        self.direction_spin.setValue(180)
        self.horizontal_speed_spin.setValue(15.0)
        self.vertical_speed_spin.setValue(0.0)
        self.latitude_spin.setValue(39.9042)
        self.longitude_spin.setValue(116.4074)
        self.pressure_altitude_spin.setValue(100.0)
        self.geodetic_altitude_spin.setValue(100.0)
        self.height_spin.setValue(50.0)
        self.description_type_combo.setCurrentText("TEXT_DESCRIPTION")
        self.description_edit.setText("Test Drone")
        self.classification_type_combo.setCurrentText("CHINA")
        self.operator_location_source_type_combo.setCurrentText("DYNAMIC")
        self.operator_latitude_spin.setValue(39.9042)
        self.operator_longitude_spin.setValue(116.4074)
        self.area_count_spin.setValue(5)
        self.area_radius_spin.setValue(100.0)
        self.area_ceiling_spin.setValue(120.0)
        self.area_floor_spin.setValue(0.0)
        self.operator_altitude_spin.setValue(0.0)
        self.geodetic_accuracy_combo.setCurrentText("WITHIN_3m")
        self.horizontal_accuracy_combo.setCurrentText("WITHIN_3m")
        self.pressure_accuracy_combo.setCurrentText("WITHIN_3m")
        self.speed_accuracy_combo.setCurrentText("WITHIN_1mps")
        self.timestamp_accuracy_spin.setValue(0.1)
        self.eu_ua_category_combo.setCurrentText("OPEN")
        self.eu_ua_class_combo.setCurrentText("CLASS_1")
        self.china_ua_category_combo.setCurrentText("OPEN")
        self.china_ua_class_combo.setCurrentText("MINI")

    def encode_message(self, message_type):
        """编码消息"""
        try:
            # 创建无人机对象
            ua = UnmannedAircraft(
                id=self.id_edit.toPlainText().strip(),
                id_type=getattr(IDType, self.id_type_combo.currentText()),
                ua_type=getattr(UAType, self.ua_type_combo.currentText()),
                operational_status=getattr(OperationalStatus, self.operational_status_combo.currentText()),
                height_type=getattr(HeightType, self.height_type_combo.currentText()),
                direction=self.direction_spin.value(),
                horizontal_speed=self.horizontal_speed_spin.value(),
                vertical_speed=self.vertical_speed_spin.value(),
                latitude=self.latitude_spin.value(),
                longitude=self.longitude_spin.value(),
                pressure_altitude=self.pressure_altitude_spin.value(),
                geodetic_altitude=self.geodetic_altitude_spin.value(),
                height=self.height_spin.value(),
                description_type=getattr(DescriptionType, self.description_type_combo.currentText()),
                description=self.description_edit.toPlainText().strip(),
                classification_type=getattr(ClassificationType, self.classification_type_combo.currentText()),
                operator_location_source_type=getattr(OperatorLocationSourceType, self.operator_location_source_type_combo.currentText()),
                operator_latitude=self.operator_latitude_spin.value(),
                operator_longitude=self.operator_longitude_spin.value(),
                area_count=self.area_count_spin.value(),
                area_radius=self.area_radius_spin.value(),
                area_ceiling=self.area_ceiling_spin.value(),
                area_floor=self.area_floor_spin.value(),
                operator_altitude=self.operator_altitude_spin.value(),
                geodetic_accuracy=getattr(VerticalAccuracy, self.geodetic_accuracy_combo.currentText()),
                horizontal_accuracy=getattr(HorizontalAccuracy, self.horizontal_accuracy_combo.currentText()),
                pressure_accuracy=getattr(VerticalAccuracy, self.pressure_accuracy_combo.currentText()),
                speed_accuracy=getattr(SpeedAccuracy, self.speed_accuracy_combo.currentText()),
                timestamp_accuracy=self.timestamp_accuracy_spin.value(),
                eu_ua_category=getattr(EUUACategory, self.eu_ua_category_combo.currentText()),
                eu_ua_class=getattr(EUUAClass, self.eu_ua_class_combo.currentText()),
                china_ua_category=getattr(ChinaUACategory, self.china_ua_category_combo.currentText()),
                china_ua_class=getattr(ChinaUAClass, self.china_ua_class_combo.currentText())
            )

            # 根据消息类型编码
            if message_type == MessageType.BASIC_ID:
                encoded_data = ua.encode_basic_id()
                self.basic_id_encoded_text.set_bytes(encoded_data)
            elif message_type == MessageType.LOCATION:
                encoded_data = ua.encode_location()
                self.location_encoded_text.set_bytes(encoded_data)
            elif message_type == MessageType.SELF_ID:
                encoded_data = ua.encode_self_id()
                self.self_id_encoded_text.set_bytes(encoded_data)
            elif message_type == MessageType.SYSTEM:
                encoded_data = ua.encode_system()
                self.system_encoded_text.set_bytes(encoded_data)
            else:
                raise ValueError(f"不支持的消息类型: {message_type}")

        except Exception as e:
            # 使用消息框显示错误信息
            QMessageBox.critical(self, "编码错误", str(e))

    def decode_message(self, message_type):
        """解码消息"""
        try:
            # 获取报文（十六进制字节码）
            if message_type == MessageType.BASIC_ID:
                encoded_text = self.basic_id_encoded_text
                decoded_text = self.basic_id_decoded_text
            elif message_type == MessageType.LOCATION:
                encoded_text = self.location_encoded_text
                decoded_text = self.location_decoded_text
            elif message_type == MessageType.SELF_ID:
                encoded_text = self.self_id_encoded_text
                decoded_text = self.self_id_decoded_text
            elif message_type == MessageType.SYSTEM:
                encoded_text = self.system_encoded_text
                decoded_text = self.system_decoded_text
            else:
                raise ValueError(f"不支持的消息类型: {message_type}")

            # 获取字节数据
            encoded_data = encoded_text.get_bytes()
            if encoded_data is None:
                raise ValueError("无效的十六进制数据，请确保输入25字节的十六进制数据")

            # 创建无人机对象并解码
            ua = UnmannedAircraft()
            ua.decode_message(encoded_data)

            # 显示解码得到的消息
            if message_type == MessageType.BASIC_ID:
                decoded_text.setText(f"""基本ID信息:
ID类型: {ua.id_type.name}
无人机类型: {ua.ua_type.name}
识别码: {ua.id}""")
            elif message_type == MessageType.LOCATION:
                decoded_text.setText(f"""位置向量信息:
运行状态: {ua.operational_status.name}
高度类型: {ua.height_type.name}
航迹角: {ua.direction}度
地速: {ua.horizontal_speed} m/s
垂直速度: {ua.vertical_speed} m/s
纬度: {ua.latitude}度
经度: {ua.longitude}度
气压高度: {ua.pressure_altitude} m
几何高度: {ua.geodetic_altitude} m
距地高度: {ua.height} m
几何高度精度: {ua.geodetic_accuracy.name}
水平精度: {ua.horizontal_accuracy.name}
气压高度精度: {ua.pressure_accuracy.name}
速度精度: {ua.speed_accuracy.name}
时间戳精度: {ua.timestamp_accuracy} 秒""")
            elif message_type == MessageType.SELF_ID:
                decoded_text.setText(f"""运行描述信息:
描述类型: {ua.description_type.name}
描述: {ua.description}""")
            elif message_type == MessageType.SYSTEM:
                ua_class_info = ""
                if ua.classification_type == ClassificationType.EUROPEAN_UNION:
                    ua_class_info = f"""欧盟无人机类别: {ua.eu_ua_category.name}
欧盟无人机等级: {ua.eu_ua_class.name}"""
                elif ua.classification_type == ClassificationType.CHINA:
                    ua_class_info = f"""中国无人机类别: {ua.china_ua_category.name}
中国无人机等级: {ua.china_ua_class.name}"""

                decoded_text.setText(f"""系统信息:
等级分类归属地区: {ua.classification_type.name}
控制站位置类型: {ua.operator_location_source_type.name}
控制站纬度: {ua.operator_latitude}度
控制站经度: {ua.operator_longitude}度
运行区域内航空器数量: {ua.area_count}
运行区域半径: {ua.area_radius} m
运行区域高度上限: {ua.area_ceiling} m
运行区域高度下限: {ua.area_floor} m
控制站高度: {ua.operator_altitude} m
{ua_class_info}""")

        except Exception as e:
            if message_type == MessageType.BASIC_ID:
                self.basic_id_decoded_text.setText(f"解码错误: {str(e)}")
            elif message_type == MessageType.LOCATION:
                self.location_decoded_text.setText(f"解码错误: {str(e)}")
            elif message_type == MessageType.SELF_ID:
                self.self_id_decoded_text.setText(f"解码错误: {str(e)}")
            elif message_type == MessageType.SYSTEM:
                self.system_decoded_text.setText(f"解码错误: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RemoteIDGUI()
    window.show()
    sys.exit(app.exec())
