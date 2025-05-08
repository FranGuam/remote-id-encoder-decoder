import struct
from dataclasses import dataclass
from typing import Tuple, List
from datetime import datetime

from enums import *

PROTOCOL_VERSION = 0x2

@dataclass
class UnmannedAircraft:
    # 基本ID信息 (Message Type 0x0)
    id_type: IDType = IDType.NONE  # ID类型
    ua_type: UAType = UAType.NONE  # 无人机类型
    id: str = ""  # 识别码

    # 位置向量信息 (Message Type 0x1)
    operational_status: OperationalStatus = OperationalStatus.UNDECLARED  # 运行状态
    height_type: HeightType = HeightType.ABOVE_TAKEOFF  # 高度类型
    direction: int = 0  # 航迹角（0-359度）
    horizontal_speed: float = 0.0  # 地速（水平速度）
    vertical_speed: float = 0.0  # 垂直速度
    latitude: float = 0.0  # 纬度
    longitude: float = 0.0  # 经度
    pressure_altitude: float = -1000.0  # 气压高度
    geodetic_altitude: float = -1000.0  # 几何高度
    height: float = -1000.0  # 距地高度
    geodetic_accuracy: VerticalAccuracy = VerticalAccuracy.UNKNOWN  # 几何高度精度
    horizontal_accuracy: HorizontalAccuracy = HorizontalAccuracy.UNKNOWN  # 水平精度
    pressure_accuracy: VerticalAccuracy = VerticalAccuracy.UNKNOWN  # 气压高度精度
    speed_accuracy: SpeedAccuracy = SpeedAccuracy.UNKNOWN  # 速度精度
    timestamp_accuracy: float = 0.0  # 时间戳精度

    # 认证信息 (Message Type 0x2)

    # 运行描述信息 (Message Type 0x3)
    description_type: DescriptionType = DescriptionType.TEXT_DESCRIPTION  # 描述类型
    description: str = ""  # 描述

    # 系统信息 (Message Type 0x4)
    classification_type: ClassificationType = ClassificationType.UNDECLARED  # 等级分类归属地区
    operator_location_source_type: OperatorLocationSourceType = OperatorLocationSourceType.TAKE_OFF  # 控制站位置类型
    operator_latitude: float = 0.0  # 控制站纬度
    operator_longitude: float = 0.0  # 控制站经度
    area_count: int = 1  # 运行区域内航空器数量
    area_radius: float = 0.0  # 运行区域半径
    area_ceiling: float = -1000.0  # 运行区域高度上限
    area_floor: float = -1000.0  # 运行区域高度下限
    eu_ua_category: EUUACategory = EUUACategory.UNDEFINED  # 欧盟无人机类别
    eu_ua_class: EUUAClass = EUUAClass.UNDEFINED  # 欧盟无人机等级
    china_ua_category: ChinaUACategory = ChinaUACategory.UNDEFINED  # 中国无人机类别
    china_ua_class: ChinaUAClass = ChinaUAClass.MINI  # 中国无人机等级
    operator_altitude: float = -1000.0  # 控制站高度

    # 控制站ID信息 (Message Type 0x5)
    operator_id: str = ""  # 控制站ID
    operator_id_type: OperatorIDType = OperatorIDType.OPERATOR_ID  # 控制站ID类型

    def _create_header(self, message_type: MessageType) -> bytes:
        """创建报文头，高4位为消息类型，低4位为协议版本"""
        header = (message_type.value << 4) | PROTOCOL_VERSION
        return struct.pack('>B', header)

    def encode_basic_id(self) -> bytes:
        """编码基本ID报文 (Message Type 0x0)"""
        header = self._create_header(MessageType.BASIC_ID)
        type_byte = ((self.id_type.value & 0x0F) << 4) | (self.ua_type.value & 0x0F)
        id_bytes = self.id.encode('ascii')
        if len(id_bytes) > 20:
            raise ValueError("识别码必须小于20字节")
        id_bytes = id_bytes.ljust(20, b'\0')
        reserved = b'\x00\x00\x00'

        message = struct.pack('>B20s3s',
                            type_byte,
                            id_bytes,
                            reserved)

        return header + message

    def encode_location(self) -> bytes:
        """编码位置向量报文 (Message Type 0x1)"""
        header = self._create_header(MessageType.LOCATION)

        if self.direction < 180 and self.direction >= 0:
            ew_direction_segment = EWDirectionSegment.BELOW_180
            direction_byte = self.direction
        elif self.direction >= 180 and self.direction < 360:
            ew_direction_segment = EWDirectionSegment.ABOVE_180
            direction_byte = int(self.direction - 180)
        else:
            raise ValueError("航迹角必须在0-360度之间")

        if self.horizontal_speed < 0:
            raise ValueError("地速必须大于0")
        if self.horizontal_speed <= 255 * 0.25:
            speed_multiplier = SpeedMultiplier.MULTIPLIER_0p25
            speed_byte = round(self.horizontal_speed / 0.25)
        elif self.horizontal_speed < 254.25:
            speed_multiplier = SpeedMultiplier.MULTIPLIER_0p75
            speed_byte = round((self.horizontal_speed - 255 * 0.25) / 0.75)
        else:
            speed_multiplier = SpeedMultiplier.MULTIPLIER_0p75
            speed_byte = 254

        status_byte = (
            ((self.operational_status.value & 0x0F) << 4) |
            (0x0 << 3) |  # 第5位保留，设为0
            ((self.height_type.value & 0x01) << 2) |
            ((ew_direction_segment.value & 0x01) << 1) |
            (speed_multiplier.value & 0x01)
        )

        if abs(self.vertical_speed) > 62:
            raise ValueError("垂直速度必须小于 62 m/s")
        if abs(self.latitude) > 90:
            raise ValueError("纬度必须小于 90 度")
        if abs(self.longitude) > 180:
            raise ValueError("经度必须小于 180 度")
        if self.pressure_altitude < -1000 or self.pressure_altitude > 31767:
            raise ValueError("气压高度必须在-1000-31767米之间")
        if self.geodetic_altitude < -1000 or self.geodetic_altitude > 31767:
            raise ValueError("几何高度必须在-1000-31767米之间")
        if self.height < -1000 or self.height > 31767:
            raise ValueError("距地高度必须在-1000-31767米之间")
        if self.timestamp_accuracy < 0 or self.timestamp_accuracy > 1.5:
            raise ValueError("时间戳精度必须在0-1.5秒之间")

        accuracy_byte1 = (
            ((self.geodetic_accuracy.value & 0x0F) << 4) |
            (self.horizontal_accuracy.value & 0x0F)
        )
        accuracy_byte2 = (
            ((self.pressure_accuracy.value & 0x0F) << 4) |
            (self.speed_accuracy.value & 0x0F)
        )

        now = datetime.now()
        timestamp = int(now.minute * 600 + now.second * 10 + now.microsecond // 100000)

        accuracy_byte3 = (
            (0x00 << 4) |  # 高四位保留，设为0
            (round(self.timestamp_accuracy * 10) & 0x0F)
        )
        reserved_byte = 0x00

        message = struct.pack('<BBBbiiHHHBBHBB',
                            status_byte,
                            direction_byte,
                            speed_byte,
                            round(self.vertical_speed / 0.5),
                            round(self.latitude * 1e7),
                            round(self.longitude * 1e7),
                            round((self.pressure_altitude + 1000) / 0.5),
                            round((self.geodetic_altitude + 1000) / 0.5),
                            round((self.height + 1000) / 0.5),
                            accuracy_byte1,
                            accuracy_byte2,
                            timestamp,
                            accuracy_byte3,
                            reserved_byte
                            )

        return header + message

    def encode_auth(self) -> bytes:
        """编码认证报文 (Message Type 0x2)"""
        raise NotImplementedError("认证报文编码未实现")

    def encode_self_id(self) -> bytes:
        """编码运行描述报文 (Message Type 0x3)"""
        header = self._create_header(MessageType.SELF_ID)

        description_bytes = self.description.encode('ascii')
        if len(description_bytes) > 23:
            raise ValueError("描述必须小于23字节")
        description_bytes = description_bytes.ljust(23, b'\0')

        message = struct.pack('>B23s',
                            self.description_type.value,
                            description_bytes)

        return header + message

    def encode_system(self) -> bytes:
        """编码系统报文 (Message Type 0x4)"""
        header = self._create_header(MessageType.SYSTEM)

        flag_byte = (
            (0x0 << 5) |  # 高3位保留，设为0
            ((self.classification_type.value & 0x07) << 2) |
            (self.operator_location_source_type.value & 0x03)
        )

        if abs(self.operator_latitude) > 90:
            raise ValueError("控制站纬度必须小于 90 度")
        if abs(self.operator_longitude) > 180:
            raise ValueError("控制站经度必须小于 180 度")
        if self.area_count < 1 or self.area_count > 65535:
            raise ValueError("运行区域内航空器数量必须在1-65535之间")
        if self.area_radius < 0 or self.area_radius > 2554:
            raise ValueError("运行区域半径必须在0-2554米之间")
        if self.area_ceiling < -1000 or self.area_ceiling > 31767:
            raise ValueError("运行区域高度上限必须在-1000-31767米之间")
        if self.area_floor < -1000 or self.area_floor > 31767:
            raise ValueError("运行区域高度下限必须在-1000-31767米之间")

        if self.classification_type == ClassificationType.EUROPEAN_UNION:
            ua_classification_byte = (
                (self.eu_ua_category.value & 0x0F) << 4 |
                (self.eu_ua_class.value & 0x0F)
            )
        elif self.classification_type == ClassificationType.CHINA:
            ua_classification_byte = (
                (self.china_ua_category.value & 0x0F) << 4 |
                (self.china_ua_class.value & 0x0F)
            )
        else:
            ua_classification_byte = 0x00

        if self.operator_altitude < -1000 or self.operator_altitude > 31767:
            raise ValueError("控制站高度必须在-1000-31767米之间")

        reserved_byte = 0x00

        message = struct.pack('<BiiHBHHBHIB',
                            flag_byte,
                            round(self.operator_latitude * 1e7),
                            round(self.operator_longitude * 1e7),
                            self.area_count,
                            round(self.area_radius / 10),
                            round((self.area_ceiling + 1000) / 0.5),
                            round((self.area_floor + 1000) / 0.5),
                            ua_classification_byte,
                            round((self.operator_altitude + 1000) / 0.5),
                            int(datetime.now().timestamp()) - 1546300800,
                            reserved_byte
                            )

        return header + message

    def encode_operator_id(self) -> bytes:
        """编码控制站ID报文 (Message Type 0x5)"""
        header = self._create_header(MessageType.OPERATOR_ID)
        operator_id_bytes = self.operator_id.encode('ascii')
        if len(operator_id_bytes) > 20:
            raise ValueError("控制站ID必须小于20字节")
        operator_id_bytes = operator_id_bytes.ljust(20, b'\0')
        reserved = b'\x00\x00\x00'

        message = struct.pack('>B20s3s',
                              self.operator_id_type.value,
                              operator_id_bytes,
                              reserved)

        return header + message

    def encode_pack(self, messages: List[MessageType]) -> bytes:
        """编码打包报文 (Message Type 0xF)"""
        header = self._create_header(MessageType.PACK)
        length = 0x19
        if len(messages) > 9:
            raise ValueError("打包中报文数量最多为9个")

        message = struct.pack('<bb', length, len(messages))
        for message_type in messages:
            if message_type == MessageType.BASIC_ID:
                message += self.encode_basic_id()
            elif message_type == MessageType.LOCATION:
                message += self.encode_location()
            elif message_type == MessageType.AUTH:
                message += self.encode_auth()
            elif message_type == MessageType.SELF_ID:
                message += self.encode_self_id()
            elif message_type == MessageType.SYSTEM:
                message += self.encode_system()
            elif message_type == MessageType.OPERATOR_ID:
                message += self.encode_operator_id()
            else:
                raise ValueError(f"未知的报文类型: {message_type}")
        return header + message

    def _parse_header(self, header: int) -> Tuple[MessageType, int]:
        """解析报文头，返回消息类型和协议版本"""
        message_type = (header >> 4) & 0x0F
        protocol_version = header & 0x0F
        return MessageType(message_type), protocol_version

    def _decode_basic_id(self, data: bytes) -> None:
        """解码基本ID报文，直接更新当前对象的属性值"""

        type_byte = data[1]
        self.id_type = IDType((type_byte >> 4) & 0x0F)
        self.ua_type = UAType(type_byte & 0x0F)

        self.id = data[2:22].decode('ascii').rstrip('\0')

        # 保留字节（3字节）暂时不使用
        # reserved = data[22:25]

    def _decode_location(self, data: bytes) -> None:
        """解码位置向量报文，直接更新当前对象的属性值"""

        (status_byte, direction_byte, speed_byte, speed_vertical,
         latitude, longitude, pressure_altitude, geodetic_altitude, height,
         accuracy_byte1, accuracy_byte2, timestamp, accuracy_byte3, reserved_byte) = struct.unpack('<BBBbiiHHHBBHBB', data[1:26])

        self.operational_status = OperationalStatus((status_byte >> 4) & 0x0F)
        self.height_type = HeightType((status_byte >> 2) & 0x01)
        ew_direction_segment = EWDirectionSegment((status_byte >> 1) & 0x01)
        speed_multiplier = SpeedMultiplier(status_byte & 0x01)

        if ew_direction_segment == EWDirectionSegment.BELOW_180:
            self.direction = direction_byte
        else:
            self.direction = direction_byte + 180

        if speed_multiplier == SpeedMultiplier.MULTIPLIER_0p25:
            self.horizontal_speed = speed_byte * 0.25
        else:
            self.horizontal_speed = 255 * 0.25 + speed_byte * 0.75

        self.vertical_speed = speed_vertical * 0.5
        self.latitude = latitude / 1e7
        self.longitude = longitude / 1e7
        self.pressure_altitude = pressure_altitude * 0.5 - 1000
        self.geodetic_altitude = geodetic_altitude * 0.5 - 1000
        self.height = height * 0.5 - 1000

        self.geodetic_accuracy = VerticalAccuracy((accuracy_byte1 >> 4) & 0x0F)
        self.horizontal_accuracy = HorizontalAccuracy(accuracy_byte1 & 0x0F)
        self.pressure_accuracy = VerticalAccuracy((accuracy_byte2 >> 4) & 0x0F)
        self.speed_accuracy = SpeedAccuracy(accuracy_byte2 & 0x0F)
        self.timestamp_accuracy = (accuracy_byte3 & 0x0F) / 10

    def _decode_auth(self, data: bytes) -> None:
        """解码认证报文，直接更新当前对象的属性值"""
        raise NotImplementedError("认证报文解码未实现")

    def _decode_self_id(self, data: bytes) -> None:
        """解码运行描述报文，直接更新当前对象的属性值"""

        self.description_type = DescriptionType(data[1])
        self.description = data[2:25].decode('ascii').rstrip('\0')

    def _decode_system(self, data: bytes) -> None:
        """解码系统报文，直接更新当前对象的属性值"""

        (flag_byte, operator_latitude, operator_longitude, area_count, area_radius,
         area_ceiling, area_floor, ua_classification_byte, operator_altitude,
         timestamp, reserved_byte) = struct.unpack('<BiiHBHHBHIB', data[1:25])

        # 解析flag_byte
        self.classification_type = ClassificationType((flag_byte >> 2) & 0x07)
        self.operator_location_source_type = OperatorLocationSourceType(flag_byte & 0x03)

        # 解析坐标和运行区域信息
        self.operator_latitude = operator_latitude / 1e7
        self.operator_longitude = operator_longitude / 1e7
        self.area_count = area_count
        self.area_radius = area_radius * 10
        self.area_ceiling = area_ceiling * 0.5 - 1000
        self.area_floor = area_floor * 0.5 - 1000

        # 解析欧盟无人机分类信息
        if self.classification_type == ClassificationType.EUROPEAN_UNION:
            self.eu_ua_category = EUUACategory((ua_classification_byte >> 4) & 0x0F)
            self.eu_ua_class = EUUAClass(ua_classification_byte & 0x0F)
        elif self.classification_type == ClassificationType.CHINA:
            self.china_ua_category = ChinaUACategory((ua_classification_byte >> 4) & 0x0F)
            self.china_ua_class = ChinaUAClass(ua_classification_byte & 0x0F)

        # 解析控制站高度
        self.operator_altitude = operator_altitude * 0.5 - 1000

    def _decode_operator_id(self, data: bytes) -> None:
        """解码控制站ID报文，直接更新当前对象的属性值"""

        self.operator_id_type = OperatorIDType(data[1])
        self.operator_id = data[2:22].decode('ascii').rstrip('\0')
        # reserved = data[22:25]

    def decode_message(self, data: bytes) -> None:
        """解码任意类型的报文，直接更新当前对象的属性值"""
        if not data:
            raise ValueError("空数据")

        message_type, protocol_version = self._parse_header(data[0])
        if protocol_version > PROTOCOL_VERSION:
            raise ValueError(f"协议版本不兼容: {protocol_version}，当前版本: {PROTOCOL_VERSION}")

        if message_type == MessageType.PACK:
            length = data[1]
            if length != 25:
                raise ValueError("打包中每个报文的长度不符合要求")
            num_messages = data[2]
            if num_messages > 9:
                raise ValueError("打包中报文数量最多为9个")
            for i in range(num_messages):
                self.decode_message(data[3 + i * 25:3 + (i + 1) * 25])
            return

        if len(data) != 25:
            raise ValueError("数据长度不符合要求")

        if message_type == MessageType.BASIC_ID:
            return self._decode_basic_id(data)
        elif message_type == MessageType.LOCATION:
            return self._decode_location(data)
        elif message_type == MessageType.AUTH:
            return self._decode_auth(data)
        elif message_type == MessageType.SELF_ID:
            return self._decode_self_id(data)
        elif message_type == MessageType.SYSTEM:
            return self._decode_system(data)
        elif message_type == MessageType.OPERATOR_ID:
            return self._decode_operator_id(data)
        else:
            raise ValueError(f"未知的报文类型: {message_type}")
