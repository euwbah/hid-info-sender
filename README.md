# HID info sender

For sending device utilization stats to my [QMK keymap for the Sofle RGB keyboard](https://github.com/euwbah/sofle_rgb_qmk/tree/master/keyboards/sofle/keymaps/euwbah).

Works on Windows only.

## Setup

- Install latest Python for windows. Make sure you have the `py` command/launcher available in your terminal.
- Install HIDAPI
  - Download the latest compiled dll and lib from https://github.com/libusb/hidapi/releases/
  - On Windows, you will need to 'install' the `.dll` and `.lib` by copying the appropriate dlls to `C:\Windows\System32`. On 64-bit Windows, use the ones in the x64 folder.
- Install Open Hardware Monitor (for CPU temp)
  - Download the latest zip from https://openhardwaremonitor.org/downloads/
  - Run the .exe once with admin rights, make sure it works.
  - Copy the `OpenHardwareMonitorLib.dll` from the install directory to the same directory as this script.
- `pip install hid` - this python package is a wrapper for HIDAPI.
- `pip install psutil` - For CPU usage.
- `pip install pythonnet` - For injecting the Open Hardware Monitor dll.
- Make this python script run as administrator at startup. The method below uses Task Scheduler which lets this python script run silently in the background.
  - Open Task Scheduler
  - Create a new task, name it something like "Forward HID Info at startup", or something memorable so that you will know to remove the scheduled task once this program is no longer needed at startup.
  - In the "General" tab, check "Run whether user is logged on or not", and "Run with highest privileges".
  - In the "Triggers" tab, create a new trigger, "At startup", and make sure "Enabled" is checked.
  - In the "Actions" tab, set action to "Start a program"
    - Program/script: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
    - Add arguments: `-ExecutionPolicy Bypass -File "C:\path\to\forward_hid_info.ps1"`. The path must point to the included `forward_hid_info.ps1` script in this repo.
  - Test that the scheduled task works.
    - In the right pane, click on "Enable all tasks history"
    - Select the "Forward HID Info at startup" task, and click "Run" in the right pane.
    - Check the history tab of this task and make sure the "Action started" task category is logged.
    - If there's an error, it will show up in the "Last Run Result" column.
