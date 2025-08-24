# HID info sender

Python script to add features to my [QMK keymap for the Sofle RGB keyboard](https://github.com/euwbah/sofle_rgb_qmk/tree/master/keyboards/sofle/keymaps/euwbah).

## Features

- Device utilization stats (CPU, RAM, GPU, Integrated GPU, Temperatures)
- Date & Time
- Control External Monitor Brightness & Contrast (via DDC/CI)

Works on Windows only. See [byte format](#byte-format) for the data format to port this to other OSes.

## Setup

I was using Python 3.13.7 on x64 from python.org.

- Install latest Python for windows. Make sure you have the `py` command/launcher available in your terminal.
- Install HIDAPI
  - Download the latest compiled dll and lib from [libusb/hidapi releases](https://github.com/libusb/hidapi/releases/)
  - On Windows, you will need to 'install' the `.dll` and `.lib` by copying the appropriate dlls to `C:\Windows\System32`. On 64-bit Windows, use the ones in the x64 folder.
- Install Open Hardware Monitor (for CPU temp)
  - Download the latest zip from [openhardwaremonitor.org](https://openhardwaremonitor.org/downloads/)
  - Run the .exe once with admin rights, make sure it works.
  - Copy the `OpenHardwareMonitorLib.dll` from the install directory to the same directory as this script.
- `py -m pip install hid psutil pythonnet monitorcontrol git+https://github.com/MagicalTux/gputil.git@patch-1` or if you use `uv`, `uv pip install --system <packages>`
  - `hid`: this python package is a wrapper for HIDAPI.
  - `psutil` - For CPU usage.
  - `pythonnet` - For injecting the Open Hardware Monitor dll.
  - `monitorcontrol` - For external monitor control
  - `gputil` - For GPU usage stats. Python 3.12 removed `distutils` from stdlib, which broke gputil,
    and the original maintainer abandoned the project. This fork has a simple fix.
- Run the python script as admin. See [Automated startup](#automated-startup).

## Automated startup

You will need to use a [ridiculous hack](https://stackoverflow.com/a/67300159/4298510) to schedule this python script to run silently in the background upon log in, while giving access to external monitor brightness control.

- Open Task Scheduler
- Create a new task, name it something like "Forward HID Info at startup", or something memorable and indicative.
- **General** tab: check **Run only when user is logged on**, and **Run with highest privileges**.
- **Triggers** tab: create a new trigger, **At startup**, and make sure **Enabled** is checked.
- **Actions** tab: set action to **Start a program**
  - Program/script: `C:\Windows\System32\cmd.exe` (or wherever cmd.exe is located. Use `where.exe cmd` command to find out)
  - Add arguments: `/c start /min "" powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\path\to\forward_hid_info.ps1"`.
  The `\path\to\forward_hid_info.ps1` should point to the `forward_hid_info.ps1` script in this repo. [See explanation here](https://stackoverflow.com/a/67300159/4298510)
- Test that the scheduled task works.
  - In the right pane, click on "Enable all tasks history"
  - Select the "Forward HID Info at startup" task in the list of scheduled tasks
  - Click "Run" in the right pane.
  - Check the history tab of this task and make sure the "Action started" task category is logged.
  - If there's an error, it will show up in the "Last Run Result" column.
  - Restart computer to check that the task runs upon log in.
- After testing, "Disable all tasks history".

**Note**: To stop/restart the Python script, open Task Manager, search for 'py.exe', right click and select 'End task'. Ending the task from Task Scheduler doesn't work.

If there's an easier way to do this, please let me know. Things I have tried and didn't work:

- The "Run even when user is not logged on" trick to run a powershell script in the background does not allow access to external monitor brightness control (security reasons)
- Using `pyw.exe` instead of `py.exe` flashes a console window every 300ms or so (this has something to do with the **OpenHardwareMonitorLib.dll** injection)

## Bugs

- After flashing both sides of the keyboard, HIDAPI may throw the 'Device not connected' error, even if the keyboard is connected. To go around this, restart the script. In task scheduler, select the "Forward HID Info" script, click "End" then "Run".

## Byte format

1. Fixed to `0x01` (identifies this custom data packet)
2. CPU utilization percentage
3. CPU temperature percentage (30-100C -> 0-100%)
4. RAM utilization percentage
5. GPU0 utilization percentage
6. GPU0 memory utilization percentage
7. GPU0 temperature percentage (30-100C -> 0-100%)
8. GPU1 utilization percentage
9. Placeholder (set to `0x00`)
10. Placeholder (set to `0x00`)
11. current month (1-12)
12. current day of the month (1-31)
13. current day of the week (0-6: Monday-Sunday)
14. current hour (0-23)
15. current minute (0-59)
16. current second (0-59)

Bytes 17-32 are unused. (HID reports are fixed to 32 bytes).

NOTE: In this implementation, an extra `0x00` byte is prepended to the packet to signify to windows/HIDAPI that it is a HID request packet, offsetting the bytes sent to the HIDAPI call. This extra byte does not get sent to the keyboard. This may or may not be necessary on other OSes/other HIDAPI wrappers/libs.

If any of the above values can't be retrieved, the corresponding byte should be set to `0x00`.
