import unittest
from main import UnmannedAircraft
from enums import *

class TestUnmannedAircraft(unittest.TestCase):
    """Unit tests for the UnmannedAircraft class"""

    def test_basic_id(self):
        """Test Basic ID information encoding and decoding"""
        ua = UnmannedAircraft(
            id="DRONE001",
            id_type=IDType.SERIAL_NUMBER,
            ua_type=UAType.MULTIROTOR
        )
        basic_id_msg = ua.encode_basic_id()

        decoded_ua = UnmannedAircraft()
        decoded_ua.decode_message(basic_id_msg)

        self.assertEqual(ua, decoded_ua)

    def test_location(self):
        """Test Location vector information encoding and decoding"""
        ua = UnmannedAircraft(
            operational_status=OperationalStatus.AIRBORNE,
            height_type=HeightType.ABOVE_TAKEOFF,
            direction=180.0,
            horizontal_speed=15.0,
            vertical_speed=2.0,
            latitude=39.9042,
            longitude=116.4074,
            pressure_altitude=100.0,
            geodetic_altitude=100.0,
            height=50.0,
            geodetic_accuracy=VerticalAccuracy.WITHIN_3m,
            horizontal_accuracy=HorizontalAccuracy.WITHIN_3m,
            pressure_accuracy=VerticalAccuracy.WITHIN_3m,
            speed_accuracy=SpeedAccuracy.WITHIN_1mps,
            timestamp_accuracy=0.1
        )
        location_msg = ua.encode_location()

        decoded_ua = UnmannedAircraft()
        decoded_ua.decode_message(location_msg)

        self.assertEqual(ua, decoded_ua)

    def test_self_id(self):
        """Test Self ID (operational description) encoding and decoding"""
        ua = UnmannedAircraft(
            description_type=DescriptionType.TEXT_DESCRIPTION,
            description="Test Drone"
        )
        self_id_msg = ua.encode_self_id()

        decoded_ua = UnmannedAircraft()
        decoded_ua.decode_message(self_id_msg)

        self.assertEqual(ua, decoded_ua)

    def test_system(self):
        """Test System information encoding and decoding"""
        ua = UnmannedAircraft(
            classification_type=ClassificationType.EUROPEAN_UNION,
            operator_location_source_type=OperatorLocationSourceType.DYNAMIC,
            operator_latitude=39.9042,
            operator_longitude=116.4074,
            area_count=5,
            area_radius=100.0,
            area_ceiling=120.0,
            area_floor=0.0,
            eu_ua_category=EUUACategory.OPEN,
            eu_ua_class=EUUAClass.CLASS_1,
            operator_altitude=0.0
        )
        system_msg = ua.encode_system()

        decoded_ua = UnmannedAircraft()
        decoded_ua.decode_message(system_msg)

        self.assertEqual(ua, decoded_ua)

    def test_operator_id(self):
        """Test Operator ID information encoding and decoding"""
        ua = UnmannedAircraft(
            operator_id_type=OperatorIDType.OPERATOR_ID,
            operator_id="+86 12345678900"
        )
        operator_id_msg = ua.encode_operator_id()

        decoded_ua = UnmannedAircraft()
        decoded_ua.decode_message(operator_id_msg)

        self.assertEqual(ua, decoded_ua)

    def test_pack(self):
        """Test Pack message encoding and decoding"""
        ua = UnmannedAircraft(
            id="DRONE001",
            id_type=IDType.SERIAL_NUMBER,
            ua_type=UAType.MULTIROTOR,
            operational_status=OperationalStatus.AIRBORNE,
            height_type=HeightType.ABOVE_TAKEOFF,
            direction=180.0,
            horizontal_speed=15.0,
            vertical_speed=2.0,
            latitude=39.9042,
            longitude=116.4074,
            pressure_altitude=100.0,
            geodetic_altitude=100.0,
            height=50.0,
            geodetic_accuracy=VerticalAccuracy.WITHIN_3m,
            horizontal_accuracy=HorizontalAccuracy.WITHIN_3m,
            pressure_accuracy=VerticalAccuracy.WITHIN_3m,
            speed_accuracy=SpeedAccuracy.WITHIN_1mps,
            timestamp_accuracy=0.1,
            classification_type=ClassificationType.EUROPEAN_UNION,
            operator_location_source_type=OperatorLocationSourceType.DYNAMIC,
            operator_latitude=39.9042,
            operator_longitude=116.4074,
            area_count=5,
            area_radius=100.0,
            area_ceiling=120.0,
            area_floor=0.0,
            eu_ua_category=EUUACategory.OPEN,
            eu_ua_class=EUUAClass.CLASS_1,
            operator_altitude=0.0
        )
        messages = [
            MessageType.BASIC_ID,
            MessageType.LOCATION,
            MessageType.SYSTEM
        ]
        pack_msg = ua.encode_pack(messages)

        decoded_ua = UnmannedAircraft()
        decoded_ua.decode_message(pack_msg)

        self.assertEqual(ua, decoded_ua)

if __name__ == "__main__":
    unittest.main()
