import asyncio
from bleak import BleakScanner

TARGET_NAME = "Manav"  # change if needed

def detection_callback(device, advertisement_data):
    if device.name == TARGET_NAME:
        print(f"{device.address} | {device.name} | RSSI={advertisement_data.rssi}")

async def main():
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    print(scanner)
    print("Scanning...")
    await asyncio.sleep(50)
    await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
