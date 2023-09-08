import time
from datetime import datetime
import hid
import psutil
import GPUtil
from monitorcontrol import monitorcontrol, InputSource
import sys
import os
import clr
clr.AddReference('./OpenHardwareMonitorLib')


from OpenHardwareMonitor.Hardware import Computer

LOG_FILE_PATH = './log.txt'

def log(message, overwrite=False):
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    message = f'{timestamp} {message}\n'
    mode = 'w' if overwrite else 'a'
    with open(LOG_FILE_PATH, mode) as f:
        f.write(message)

this_file_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(this_file_dir)

log('Starting HID info forwarder for euwbah\'s Sofle RGB keymap', overwrite=True)
log(f'Opening in pwd: {os.getcwd()}')

# Set these to match OpenHardwareMonitor.Hardware.IHardware.Name
# (Names can be printed with `print(Computer.Hardware[i].Name)`)
CPU_SEARCH = 'Ryzen'
AMD_GPU_SEARCH = 'Radeon'
NVIDIA_GPU_SEARCH = 'GeForce'

CPU_TEMP_SEARCH = 'temperature/0'
AMD_GPU_UTIL_SEARCH = 'load/0'

VENDOR_ID = 0xFC32
PRODUCT_ID = 0x0287
USAGE_PAGE = 0xFF60
USAGE = 0x61

keyboard_not_found_displayed = False

computer = Computer()
computer.CPUEnabled = True
computer.GPUEnabled = True
computer.Open()

cpu_hardware = [h for h in computer.Hardware if CPU_SEARCH in h.Name]
cpu_hardware = cpu_hardware[0] if len(cpu_hardware) > 0 else None
amd_gpu_hardware = [h for h in computer.Hardware if AMD_GPU_SEARCH in h.Name]
amd_gpu_hardware = amd_gpu_hardware[0] if len(amd_gpu_hardware) > 0 else None

while True:
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    devices = [d for d in devices if d['usage_page'] == USAGE_PAGE and d['usage'] == USAGE]
    if len(devices) == 0:
        if not keyboard_not_found_displayed:
            log("Keyboard not found")
            keyboard_not_found_displayed = True
        time.sleep(1)
        continue
    interface = hid.Device(path=devices[0]['path'])

    # 32 bytes report length
    data = [0] * 32

    cpu_percent = max(psutil.cpu_percent(percpu=True))
    # print(f'CPU: {cpu_percent}%')
    ram_percent = psutil.virtual_memory().percent

    """
    Byte format (0-indexed):
    0: 0x01 to signify that this packet contains host utilization data
    1: CPU utilization percentage
    2: CPU temperature percentage (30-100C -> 0-100%)
    3: RAM utilization percentage
    4: GPU0 utilization percentage
    5: GPU0 memory utilization percentage
    6: GPU0 temperature percentage (30-100C -> 0-100%)
    7: GPU1 utilization percentage
    8: Unused/placeholder
    9: Unused/placeholder
    10: current month (1-12)
    11: current day of the month (1-31)
    12: current day of the week (0-6: Monday-Sunday)
    13: current hour (0-23)
    14: current minute (0-59)
    15: current second (0-59)

    If any of the above values can't be retrieved, the corresponding byte will be set to 0x00.
    """

    data[0] = 1 # first data byte being 1 represents that the packet contains host utilization data.
    data[1] = int(cpu_percent)
    if cpu_hardware is not None:
        cpu_hardware.Update()
        cpu_temp = [s for s in cpu_hardware.Sensors if CPU_TEMP_SEARCH in str(s.Identifier)]
        cpu_temp = cpu_temp[0].Value if len(cpu_temp) > 0 else None
        if cpu_temp is not None:
            data[2] = int((cpu_temp - 30) * 100/70)
    data[3] = int(ram_percent)

    gpus = GPUtil.getGPUs()
    if len(gpus) > 0:
        gpu_percent = gpus[0].load * 100
        gpu_memory_percent = gpus[0].memoryUtil * 100
        gpu_temp = gpus[0].temperature
        data[4] = int(gpu_percent)
        data[5] = int(gpu_memory_percent)
        data[6] = int((gpu_temp - 30) * 100/70) # 30-100C -> 0-100%

    if amd_gpu_hardware is not None:
        amd_gpu_hardware.Update()
        gpu1_util = [s for s in amd_gpu_hardware.Sensors if AMD_GPU_UTIL_SEARCH in str(s.Identifier)]
        gpu1_util = gpu1_util[0].Value if len(gpu1_util) > 0 else None
        if gpu1_util is not None:
            data[7] = int(gpu1_util)

    # send date & time info

    current_time = time.localtime()
    data[10] = current_time.tm_mon
    data[11] = current_time.tm_mday
    data[12] = current_time.tm_wday
    data[13] = current_time.tm_hour
    data[14] = current_time.tm_min
    data[15] = current_time.tm_sec

    try:
        # NOTE: An extra 0x00 byte is prepended to the packet to signify to windows/HIDAPI that it is a
        # HID request packet. This may or may not be necessary on other OSes.
        hid_request_packet = bytes([0x00] + data)
        interface.write(hid_request_packet)
        # print("Sent packet: " + [int(b) for b in hid_request_packet])
        response_packet = interface.read(32, timeout=250)
        if response_packet and response_packet[0] == 0x01:
            mon_brightness, mon_contrast = response_packet[1], response_packet[2]

            monitors = monitorcontrol.get_monitors()
            ext_mon = None
            for m in monitors:
                with m:
                    if m.get_input_source() != InputSource.OFF:
                        ext_mon = m
                        break
            if ext_mon is not None:
                with ext_mon:
                    ext_mon.set_luminance(mon_brightness)
                    ext_mon.set_contrast(mon_contrast)
        keyboard_not_found_displayed = False
    except hid.HIDException as e:
        if not keyboard_not_found_displayed and 'not connected' in str(e):
            log(f"Keyboard not found: {e}")
            keyboard_not_found_displayed = True
        else:
            log(f"Could not send packet: {e}")
        time.sleep(1)
    except Exception as e:
        log(f"Error: {type(e).__name__} {e}")
        time.sleep(1)
    finally:
        interface.close()

    time.sleep(0.1)
