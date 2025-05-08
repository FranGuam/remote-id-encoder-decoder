from enum import Enum


class MessageType(Enum):
    BASIC_ID = 0x0
    LOCATION = 0x1
    AUTH = 0x2
    SELF_ID = 0x3
    SYSTEM = 0x4
    OPERATOR_ID = 0x5
    PACK = 0xF

class IDType(Enum):
    NONE = 0x0
    SERIAL_NUMBER = 0x1
    CAA_ASSIGNED_REGISTRATION_ID = 0x2
    UTM_ASSIGNED_UUID = 0x3
    SPECIFIC_SESSION_ID = 0x4

class UAType(Enum):
    NONE = 0x0  # 无
    NOT_DECLARED = 0x0  # 未声明
    AEROPLANE = 0x1  # 固定翼飞机
    HELICOPTER = 0x2  # 直升机
    MULTIROTOR = 0x2  # 多旋翼
    GYROPLANE = 0x3  # 自转旋翼机
    HYBRID_LIFT = 0x4  # 混合升力
    ORNITHOPTER = 0x5  # 扑翼机
    GLIDER = 0x6  # 滑翔机
    KITE = 0x7  # 风筝
    FREE_BALLOON = 0x8  # 自由气球
    CAPTIVE_BALLOON = 0x9  # 系留气球
    AIRSHIP = 0xA  # 飞艇
    FREE_FALL = 0xB  # 自由落体
    PARACHUTE = 0xB  # 降落伞
    ROCKET = 0xC  # 火箭
    TETHERED_POWERED_AIRCRAFT = 0xD  # 系留动力航空器
    GROUND_OBSTACLE = 0xE  # 地面障碍物
    OTHER = 0xF  # 其他

class OperationalStatus(Enum):
    UNDECLARED = 0x0
    GROUND = 0x1
    AIRBORNE = 0x2
    EMERGENCY = 0x3
    REMOTE_ID_SYSTEM_FAILURE = 0x4
    RESERVED = 0x5

class HeightType(Enum):
    ABOVE_TAKEOFF = 0x0
    AGL = 0x1

class EWDirectionSegment(Enum):
    BELOW_180 = 0x0
    ABOVE_180 = 0x1

class SpeedMultiplier(Enum):
    MULTIPLIER_0p25 = 0x0
    MULTIPLIER_0p75 = 0x1

class HorizontalAccuracy(Enum):
    UNKNOWN = 0x0
    BEYOND_10NM = 0x0
    WITHIN_10NM = 0x1
    WITHIN_4NM = 0x2
    WITHIN_2NM = 0x3
    WITHIN_1NM = 0x4
    WITHIN_0p5NM = 0x5
    WITHIN_0p3NM = 0x6
    WITHIN_0p1NM = 0x7
    WITHIN_0p05NM = 0x8
    WITHIN_30m = 0x9
    WITHIN_10m = 0xA
    WITHIN_3m = 0xB
    WITHIN_1m = 0xC
    RESERVED = 0xD

class VerticalAccuracy(Enum):
    UNKNOWN = 0x0
    BEYOND_150m = 0x0
    WITHIN_150m = 0x1
    WITHIN_45m = 0x2
    WITHIN_25m = 0x3
    WITHIN_10m = 0x4
    WITHIN_3m = 0x5
    WITHIN_1m = 0x6
    RESERVED = 0x7

class SpeedAccuracy(Enum):
    UNKNOWN = 0x0
    BEYOND_10mps = 0x0
    WITHIN_10mps = 0x1
    WITHIN_3mps = 0x2
    WITHIN_1mps = 0x3
    WITHIN_0p3mps = 0x4
    RESERVED = 0x5

class DescriptionType(Enum):
    TEXT_DESCRIPTION = 0x00
    EMERGENCY_DESCRIPTION = 0x01
    EXTENDED_STATUS_DESCRIPTION = 0x02
    RESERVED = 0x03
    PRIVATE = 0xC9

class OperatorLocationSourceType(Enum):
    TAKE_OFF = 0x0
    DYNAMIC = 0x1
    FIXED = 0x2

class ClassificationType(Enum):
    UNDECLARED = 0x0
    EUROPEAN_UNION = 0x1
    CHINA = 0x2
    RESERVED = 0x3

class EUUACategory(Enum):
    UNDEFINED = 0x0
    OPEN = 0x1
    SPECIFIC = 0x2
    CERTIFIED = 0x3
    RESERVED = 0x4

class EUUAClass(Enum):
    UNDEFINED = 0x0
    CLASS_0 = 0x1
    CLASS_1 = 0x2
    CLASS_2 = 0x3
    CLASS_3 = 0x4
    CLASS_4 = 0x5
    CLASS_5 = 0x6
    CLASS_6 = 0x7
    RESERVED = 0x8

class ChinaUACategory(Enum):
    UNDEFINED = 0x0  # 未定义
    OPEN = 0x1  # 开放类
    SPECIFIC = 0x2  # 特许类
    CERTIFIED = 0x3  # 审定类
    RESERVED = 0x4  # 预留

class ChinaUAClass(Enum):
    MINI = 0x0  # 微型
    LIGHT = 0x1  # 轻型
    SMALL = 0x2  # 小型
    OTHER = 0x3  # 其他
    RESERVED = 0x4  # 预留

class AuthenticationType(Enum):
    NONE = 0x0
    UAS_ID_SIGNATURE = 0x1
    OPERATOR_ID_SIGNATURE = 0x2
    MESSAGE_SET_SIGNATURE = 0x3
    AUTHENTICATION_PROVIDED_BY_NETWORK_REMOTE_ID = 0x4
    SPECIFIC_AUTHENTICATION_METHOD = 0x5
    RESERVED = 0x6
    PRIVATE = 0xA

class OperatorIDType(Enum):
    OPERATOR_ID = 0x00
    RESERVED = 0x01
    PRIVATE = 0xC9
