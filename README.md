# Unmanned Aircraft Remote ID Message Encoder/Decoder

A Python-based tool for encoding and decoding Remote ID messages for unmanned aircraft systems (UAS).

## Features

- **Message Encoding/Decoding**: Supports encoding and decoding of various Remote ID message types:
  - Basic ID Message: Provides ID for UA, characterizes the type of ID, and identifies the type of UA
  - Location Message: Provides location, altitude, direction, and speed of UA
  - Authentication Message: Provides authentication data for the UA (Not implemented yet)
  - Self-ID Message: Message that can be used by Operators to identify themselves and the purpose of an operation
  - System Message: Includes Remote Pilot location and multiple aircraft information (group) if applicable, and additional system information
  - Operator ID: Provides operator ID information
  - Message Pack: A payload mechanism for combining the messages above into a single message pack.

- **User-Friendly GUI**: Includes a graphical interface built with PyQt6 for easy interaction with the encoding/decoding functionality.

- **Comprehensive Enumerations**: Includes detailed enumerations for various aircraft types, operational statuses, accuracy levels, and more.

## Requirements

- Python 3.10 or higher
- PyQt6 (for the GUI component)

## Usage

### GUI Application

Run the GUI application to encode and decode messages through a user-friendly interface:

```
python gui.py
```

### Programmatic Usage

You can also use the library programmatically in your own Python code:

```python
from main import UnmannedAircraft
from enums import IDType, UAType

# Create an aircraft object
aircraft = UnmannedAircraft(
    id="DRONE001",
    id_type=IDType.SERIAL_NUMBER,
    ua_type=UAType.MULTIROTOR
)

# Encode a basic ID message
message = aircraft.encode_basic_id()

# Decode a message
decoded_aircraft = UnmannedAircraft()
decoded_aircraft.decode_message(message)
```

## Reference

[1] Standard Specification for Remote ID and Tracking (ASTM F3411-22a)

[2] 中国民用航空局《民用微轻小型无人驾驶航空器运行识别最低性能要求（试行）》

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
