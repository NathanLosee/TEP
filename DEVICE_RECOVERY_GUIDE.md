# Device Recovery Guide

## Overview

The TAP application uses a human-readable UUID system for device registration. Each registered device receives a recovery code in the format: **WORD-WORD-WORD-NUMBER** (e.g., `EAGLE-RIVER-MOUNTAIN-42`).

This recovery code serves dual purposes:
1. **Device Identifier**: Uniquely identifies the device in the system
2. **Recovery Code**: Allows recovery if browser data is cleared

## For Administrators

### Registering a New Device

1. Navigate to **Admin → Registered Devices**
2. Go to the **My Devices** tab
3. Fill in the device name (e.g., "Main Office Terminal")
4. Click **Generate Device UUID** - the system will create a human-readable code
5. Click **Register Device**
6. **Important**: Write down the UUID and physically label the device

### Physical Device Labeling

After registering a device, create a physical label with:

```
DEVICE NAME: Main Office Terminal
RECOVERY CODE: EAGLE-RIVER-MOUNTAIN-42
```

Place this label:
- On the physical device (monitor, computer case)
- Or in a secure location near the device
- Keep a backup copy in your admin records

### Managing Devices

In the **All Devices** tab, you can:
- View all registered devices
- See when each device was last used
- Deactivate devices that are no longer in use
- Copy recovery codes for redistribution

## For Employees

### Device Status

When you access the timeclock, you'll see one of two statuses:

**Internal Device (Registered)**
- You can clock in/out regardless of permissions
- Device name is displayed
- Most reliable for daily use

**External Device (Unregistered)**
- Requires "External Clocking" permission to use
- Must have this permission in your employee account
- Typically used for remote work or mobile access

### Recovering a Lost Registration

If browser data is cleared (cookies, cache), the device will lose its registration. To recover:

1. On the timeclock page, you'll see "External Device" status
2. Click **"Have a recovery code?"**
3. Enter the recovery code from the device label
4. Click **Recover**
5. Device will be re-registered automatically

**Important Notes:**
- The recovery code is case-insensitive (you can type lowercase)
- Make sure to enter it exactly: WORD-WORD-WORD-NUMBER
- If you get an error, double-check the code on the device label
- Contact your administrator if the device label is missing

### Security Features

**Duplicate Session Detection**: If someone tries to use a recovery code that's already active in another browser session on the same computer, the system will block it. This prevents:
- Accidentally registering the same code twice
- Unauthorized recovery attempts on shared computers

## Technical Details

### UUID Format

UUIDs are generated using a curated word list of 120+ common English words combined with a 2-digit number:

- **Format**: WORD1-WORD2-WORD3-NUMBER
- **Example**: EAGLE-RIVER-MOUNTAIN-42
- **Benefits**:
  - Easy to type and remember
  - Less prone to transcription errors than random strings
  - Professional appearance on labels
  - Unique across millions of combinations

### Storage

Device registration is stored in two locations:

1. **localStorage** (persistent):
   - Survives browser restarts
   - Survives tab closures
   - Cleared only when user clears browser data

2. **sessionStorage** (temporary):
   - Used for duplicate detection
   - Cleared when browser is closed
   - Prevents same-session conflicts

### Recovery Process

When recovering a device:

1. System validates the recovery code format
2. Checks if code exists in database
3. Verifies device is active
4. Checks for duplicate session conflicts
5. Updates browser fingerprint to current device
6. Stores UUID in both localStorage and sessionStorage
7. Logs the recovery event

## Troubleshooting

### "Recovery code not found or device is inactive"

**Cause**: The code doesn't exist in the system or was deactivated
**Solution**:
- Verify you typed the code correctly
- Check with administrator if device was deactivated
- Device may need to be re-registered

### "Invalid recovery code format"

**Cause**: Code doesn't match WORD-WORD-WORD-NUMBER pattern
**Solution**:
- Ensure you have 4 parts separated by hyphens
- First 3 parts should be words (all letters)
- Last part should be a 2-digit number

### "This recovery code is already in use"

**Cause**: The code is active in another browser session on this computer
**Solution**:
- Close all other browser windows/tabs with TAP open
- Try recovery again
- If problem persists, restart the browser completely

### Device shows as "External" after working fine

**Cause**: Browser data was cleared (manually or by policy)
**Solution**:
- Use the recovery code from the device label
- If label is missing, contact administrator
- Administrator can look up the code in "All Devices" tab

## Best Practices

### For Administrators

1. **Always label devices immediately** after registration
2. **Keep a backup list** of all device codes
3. **Review devices periodically** and deactivate unused ones
4. **Train employees** on recovery procedures
5. **Document device locations** with their codes

### For Employees

1. **Don't clear browser data** unless necessary
2. **Keep device labels visible** but secure
3. **Report lost labels** to administrator immediately
4. **Don't share recovery codes** between devices
5. **Test recovery** on a non-critical device first if unsure

## Advanced: Browser Fingerprinting

The system uses browser fingerprinting as a **secondary** identification method:

- **Primary**: browser_uuid in localStorage
- **Secondary**: Browser fingerprint (FingerprintJS)

If localStorage is cleared but the device has the same fingerprint, the system can automatically restore the UUID. However:

- Fingerprinting is **unreliable** in standardized environments
- Multiple identical computers may have the same fingerprint
- Recovery codes are the **recommended** recovery method
- Fingerprinting is a convenience feature, not a security feature

## Security Considerations

### UUID as Recovery Code

The UUID itself serves as the recovery code, which means:

**Pros**:
- No separate code to remember/manage
- Simpler system architecture
- One label serves multiple purposes

**Cons**:
- Anyone with the code can recover registration
- Physical security of labels is important

**Mitigation**:
- Recovery updates the fingerprint, so original device loses access
- Event logging tracks all recoveries
- Administrators can deactivate compromised devices
- Session detection prevents same-computer abuse

### Access Control

Device registration is permission-controlled:

- **registered_browser.create**: Can register new devices
- **registered_browser.read**: Can view all devices
- **registered_browser.delete**: Can deactivate devices

Recovery does **not** require authentication - it's designed for employees who may not have admin accounts.
