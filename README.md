# HID info sender

For sending device utilization stats to my [Sofle RGB keyboard]().

## Setup

- Install latest python
- Install HIDAPI
  - Download the latest compiled dll and lib from https://github.com/libusb/hidapi/releases/
  - On Windows, you will need to 'install' the dll and lib by copying them to `C:\Windows\System32`.
- `pip install hid` - this python package is a wrapper for HIDAPI.
- `pip install psutil`
- `pip install gputil`
- Make this python script run at startup.
