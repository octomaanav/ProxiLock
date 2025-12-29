# Proxi-Lock

Proxi-Lock is a small menu bar utility that locks and unlocks your Mac by proximity of your iPhone, Apple Watch, or any other Bluetooth Low Energy device.

**Please note:** This app is not distributed on the Mac App Store. You can find it here for free!

## Features

- **No companion app required** - Works with any BLE device that periodically transmits signal
- **Automatic unlock** - Unlocks your Mac when the BLE device is near, without entering password
- **Automatic lock** - Locks your Mac when the BLE device moves away
- **Smart proximity detection** - Uses RSSI (signal strength) thresholds to determine near/far states
- **Consecutive FAR detection** - Requires multiple consecutive "far" readings before locking to prevent false locks
- **Lock-only mode** - Option to lock when device moves away but never auto-unlock
- **Screen saver lock** - Option to use screen saver instead of system lock
- **Password securely stored** - Your password is stored in macOS Keychain
- **Sleep/wake handling** - Automatically handles system sleep and wake events

## Requirements

- A Mac with Bluetooth Low Energy support
- macOS 10.13 (High Sierra) or later
- iPhone 5s or newer, Apple Watch (all), or another BLE device that has static MAC address and transmits signal periodically

## Installation

### Manual Installation

1. Download the latest release from the [Releases](https://github.com/yourusername/proxi-lock/releases) page
2. Unzip the downloaded file
3. Move `Proxi-Lock.app` to your Applications folder
4. Open the app (you may need to right-click and select "Open" the first time due to macOS security)

### Building from Source

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Build the app:
   ```bash
   ./build_app.sh
   ```
5. The app will be in the `dist` folder

## Setting Up

On the first launch, Proxi-Lock will ask for the following permissions, which you must grant:

| Permission | How to Enable |
|------------|---------------|
| **Bluetooth** | Go to **System Settings > Privacy & Security > Bluetooth** (or **System Preferences > Security & Privacy > Privacy > Bluetooth** on older macOS). Make sure Proxi-Lock is checked. |
| **Accessibility** | Go to **System Settings > Privacy & Security > Accessibility** (or **System Preferences > Security & Privacy > Privacy > Accessibility** on older macOS). Click the lock icon to unlock, then check the box next to Proxi-Lock. |
| **Automation** | Go to **System Settings > Privacy & Security > Automation** (or **System Preferences > Security & Privacy > Privacy > Automation** on older macOS). Find Proxi-Lock in the list and ensure "System Events" is checked. You may also be prompted when Proxi-Lock first tries to use automation - click "OK" or "Allow". |
| **Keychain** | When Proxi-Lock requests access to Keychain, a dialog will appear. You must choose **Always Allow** (not "Allow Once" or "Deny") because the password is needed while the screen is locked. You can also manage this in **System Settings > Privacy & Security > Passwords** (or **Keychain Access** app). |

**NOTE:** The number of permissions required increases with each version of macOS, so if you are using an older OS, you may not be asked for one or more permissions.

Then it will ask for your login password to unlock the lock screen. It will be stored safely in Keychain.

Finally, from the menu bar icon, select **Devices**. It starts scanning nearby BLE devices. Select your device, and you're done!

## Options

| Option | Description |
|--------|-------------|
| **Start/Stop Monitoring** | Start or stop the proximity detection monitoring |
| **Unlocking threshold (near)** | Bluetooth signal strength (RSSI) to unlock. Larger (less negative) value indicates that the BLE device needs to be closer to the Mac to unlock. Default: -30 dBm |
| **Locking threshold (far)** | Bluetooth signal strength (RSSI) to lock. Smaller (more negative) value indicates that the BLE device needs to be farther away from the Mac to lock. Default: -70 dBm |
| **Max unlocking RSSI** | Maximum RSSI value for unlocking. Must be between the locking and unlocking thresholds. This prevents unlocking when the device is too far away even if it's technically "near". Default: -50 dBm |
| **Consecutive FAR required** | Number of consecutive "far" readings required before locking. This prevents false locks from temporary signal drops. Default: 5 |
| **Use Screen Saver Lock** | If enabled, Proxi-Lock launches screensaver instead of locking. For this option to work properly, you need to set "Require password immediately after sleep or screen saver begins" option in Security & Privacy preference pane. |
| **Lock Only Mode** | If enabled, Proxi-Lock will lock when the device moves away but will never auto-unlock. This is useful if you want proximity-based locking but prefer to unlock manually. |
| **Set Password** | If you changed your login password, use this to update the stored password in Keychain. |

## How It Works

Proxi-Lock continuously scans for your selected BLE device and measures the signal strength (RSSI). Based on the RSSI values:

- **NEAR**: When the device is close (RSSI above the "near" threshold), the Mac unlocks automatically
- **MID**: When the device is at a medium distance (between thresholds), no action is taken
- **FAR**: When the device is far away (RSSI below the "far" threshold), the Mac locks after the required number of consecutive "far" readings

The consecutive FAR counter prevents false locks from temporary signal drops. The counter resets whenever the device comes back to "NEAR" or "MID" state.

## Troubleshooting

### Can't find my device in the list

If your BLE device is not from Apple, Proxi-Lock may not be able to find the device name. If that is the case, your device is displayed as a UUID (long hexadecimal numbers and hyphens). To identify the device, try moving the device closer to or farther away from the Mac and see if the RSSI (dB value) changes accordingly.

If you don't see any device in the list, try resetting the Bluetooth module:

1. Hold **Shift + Option** and click the Bluetooth icon in the menubar or Control Center
2. Click **Reset the Bluetooth module**

In macOS 12 Monterey or later, this option is no longer available. Instead, type the command below in Terminal:

```bash
sudo pkill bluetoothd
```

This command will ask your login password.

### It fails to unlock

1. Make sure Proxi-Lock is turned on in **System Preferences > Security & Privacy > Privacy > Accessibility**. If it is already on, try turning it off and on again.

2. If it asks for permission to access its own password in Keychain, you must choose **Always Allow**, because it is needed while the screen is locked.

3. Check that your device is selected in the Devices menu and monitoring is started.

4. Verify that the RSSI values are appropriate for your setup. You may need to adjust the thresholds.

### Frequent false locks

1. Increase the **Consecutive FAR required** value. This requires more consecutive "far" readings before locking.

2. Adjust the **Locking threshold (far)** to a more negative value (e.g., -80 dBm instead of -70 dBm) so the device needs to be farther away before locking.

3. Check for interference from other Bluetooth devices or 2.4GHz WiFi.

## Notes on MAC Address

Unlike classic Bluetooth, Bluetooth Low Energy devices can use private MAC addresses. That private address can be random and can be changed from time to time.

Recent smart devices, both iOS and Android, tend to use private addresses that change every 15 minutes or so. This is probably to prevent tracking.

On the other hand, in order for Proxi-Lock to track your device, its MAC address must be static.

Fortunately, on Apple devices, if you are signed in with the same Apple ID as your Mac, the MAC address is resolved to the true (public) address.

For other devices, including Android, the way to resolve the address is unknown. If your non-Apple device changes its MAC address over time, unfortunately Proxi-Lock can't support it.

To check if the MAC address is resolved correctly, compare the MAC address displayed in the Device scan list of Proxi-Lock with the one that is displayed on your device.

## Security Considerations

- Your password is stored securely in macOS Keychain
- **IMPORTANT:** Proxi-Lock **only unlocks if the screen was locked by Proxi-Lock itself** (not if you manually locked it). This is a security feature to prevent unauthorized unlocking. If you manually lock your Mac (e.g., using Cmd+Ctrl+Q or the Apple menu), Proxi-Lock will not automatically unlock it - you must unlock it manually.
- The app requires Accessibility permissions to unlock the screen, which is a standard requirement for automation tools
- Always keep your Mac and Proxi-Lock updated to the latest version

## Credits

Built with:
- [rumps](https://github.com/jaredks/rumps) - Ridiculously Uncomplicated macOS Python Statusbar Apps
- [bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy platform Agnostic Klient
- [py2app](https://github.com/ronaldoussoren/py2app) - Create standalone Mac OS X applications with Python

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

