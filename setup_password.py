#!/usr/bin/env python3
"""Setup script to store Mac password in keychain for auto-unlock"""

import subprocess
import getpass
import sys

KEYCHAIN_ITEM = "proxi-lock-password"

def setup_password():
    """Store password in macOS keychain"""
    print("=" * 50)
    print("Proxi-Lock Password Setup")
    print("=" * 50)
    print("\nThis will store your Mac password securely in the macOS keychain.")
    print("The password will be used to automatically unlock your Mac when your phone comes near.")
    print("\n⚠️  Security Note: Your password is stored in the macOS keychain, which is encrypted.")
    print("   Only this script can access it, and it requires your user account.\n")
    
    password = getpass.getpass("Enter your Mac password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("❌ Passwords don't match!")
        sys.exit(1)
    
    try:
        # Check if password already exists
        try:
            subprocess.run([
                "security",
                "find-generic-password",
                "-a", getpass.getuser(),
                "-s", KEYCHAIN_ITEM
            ], check=True, capture_output=True)
            # If we get here, password exists - update it
            subprocess.run([
                "security",
                "add-generic-password",
                "-a", getpass.getuser(),
                "-s", KEYCHAIN_ITEM,
                "-w", password,
                "-U"  # Update existing
            ], check=True, capture_output=True)
            print("✅ Password updated in keychain")
        except subprocess.CalledProcessError:
            # Password doesn't exist - create it
            subprocess.run([
                "security",
                "add-generic-password",
                "-a", getpass.getuser(),
                "-s", KEYCHAIN_ITEM,
                "-w", password
            ], check=True, capture_output=True)
            print("✅ Password stored in keychain")
        
        print("\n📝 Next steps:")
        print("   1. Grant Accessibility permissions to Terminal/Python:")
        print("      System Settings → Privacy & Security → Accessibility")
        print("   2. Run your main script: python main.py")
        print("\n🔒 Your password is stored securely in the macOS keychain.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to store password: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_password()

