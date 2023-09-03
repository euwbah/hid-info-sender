import time
import hid
import psutil
import GPUtil

VENDOR_ID = 0xFC32
PRODUCT_ID = 0x0287
USAGE_PAGE = 0xFF60
USAGE = 0x61

while True:
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    devices = [d for d in devices if d['usage_page'] == USAGE_PAGE and d['usage'] == USAGE]
    if len(devices) == 0:
        print("Keyboard not found")
        time.sleep(1)
        continue
    interface = hid.Device(path=devices[0]['path'])

    # 32 bytes report length
    data = [0] * 32

    cpu_percent = max(psutil.cpu_percent(percpu=True))
    # print(f'CPU: {cpu_percent}%')
    ram_percent = psutil.virtual_memory().percent

    data[0] = 1 # first data byte being 1 represents that the packet contains host utilization data.
    data[1] = int(cpu_percent)
    data[2] = int(ram_percent)

    gpus = GPUtil.getGPUs()
    if len(gpus) > 0:
        gpu_percent = gpus[0].load * 100
        gpu_memory_percent = gpus[0].memoryUtil * 100
        gpu_temp = gpus[0].temperature
        data[3] = int(gpu_percent)
        data[4] = int(gpu_memory_percent)
        data[5] = int(gpu_temp)

    # If unable to get GPU info, the data bytes default to 0.

    try:
        hid_request_packet = bytes([0x00] + data)
        interface.write(hid_request_packet)
        # print("Sent packet: " + str(hid_request_packet))
        response_packet = interface.read(32, timeout=1000)
    except hid.HIDException as e:
        print("Keyboard not found")
        time.sleep(1)
    finally:
        interface.close()

    time.sleep(0.5)
