"""
Native macOS dialogs using AppKit for Apple-approved UI
"""
from AppKit import (
    NSAlert,
    NSSecureTextField,
    NSTextField,
    NSInformationalAlertStyle,
    NSWarningAlertStyle,
    NSCriticalAlertStyle,
    NSView,
    NSMakeRect,
)


def show_password_dialog(title="Set Password", message="Enter a password:", default_value=""):
    """
    Show native macOS password dialog with secure text field
    
    Args:
        title: Dialog title
        message: Informative text
        default_value: Default password value (optional)
    
    Returns:
        Password string if OK clicked, None if Cancel
    """
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    alert.setAlertStyle_(NSInformationalAlertStyle)
    
    # Secure password input field
    password_field = NSSecureTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 200, 24))
    if default_value:
        password_field.setStringValue_(default_value)
    
    alert.setAccessoryView_(password_field)
    
    alert.addButtonWithTitle_("OK")
    alert.addButtonWithTitle_("Cancel")
    
    # Make password field first responder (focused)
    alert.window().makeFirstResponder_(password_field)
    
    response = alert.runModal()
    
    if response == 1000:
        return password_field.stringValue()
    
    return None


def show_text_input_dialog(title, message, default_value="", placeholder=""):
    """
    Show native macOS text input dialog
    
    Args:
        title: Dialog title
        message: Informative text
        default_value: Default text value
        placeholder: Placeholder text (optional)
    
    Returns:
        Text string if OK clicked, None if Cancel
    """
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    alert.setAlertStyle_(NSInformationalAlertStyle)
    
    # Text input field
    text_field = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 200, 24))
    if default_value:
        text_field.setStringValue_(str(default_value))
    if placeholder:
        text_field.setPlaceholderString_(placeholder)
    
    alert.setAccessoryView_(text_field)
    
    alert.addButtonWithTitle_("OK")
    alert.addButtonWithTitle_("Cancel")
    
    # Make text field first responder (focused)
    alert.window().makeFirstResponder_(text_field)
    
    response = alert.runModal()
    
    if response == 1000:
        return text_field.stringValue()
    
    return None


def show_alert(title, message, style="informational"):
    """
    Show native macOS alert dialog
    
    Args:
        title: Alert title
        message: Alert message
        style: "informational", "warning", or "critical"
    
    Returns:
        True if OK clicked, False otherwise
    """
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    
    # Set alert style
    if style == "warning":
        alert.setAlertStyle_(NSWarningAlertStyle)
    elif style == "critical":
        alert.setAlertStyle_(NSCriticalAlertStyle)
    else:
        alert.setAlertStyle_(NSInformationalAlertStyle)
    
    alert.addButtonWithTitle_("OK")
    
    response = alert.runModal()
    return response == 1000


def show_confirm_dialog(title, message, ok_button="OK", cancel_button="Cancel"):
    """
    Show native macOS confirmation dialog
    
    Args:
        title: Dialog title
        message: Dialog message
        ok_button: Text for OK button
        cancel_button: Text for Cancel button
    
    Returns:
        True if OK clicked, False if Cancel
    """
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    alert.setAlertStyle_(NSInformationalAlertStyle)
    
    alert.addButtonWithTitle_(ok_button)
    alert.addButtonWithTitle_(cancel_button)
    
    response = alert.runModal()
    return response == 1000

