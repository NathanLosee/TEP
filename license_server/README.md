# TEP License Server

Standalone license generation and verification tool for the TEP (Time Entry Portal) application.

## Overview

This is a separate service/tool for generating and managing licenses for TEP installations. It should be kept separate from the main application deployment and used only by administrators.

**Important:** The private key used for signing licenses should never be deployed with the main application. Only the public key is embedded in the main application for verification.

## Installation

```bash
cd license_server
pip install -r requirements.txt
```

## Usage

### Generate Key Pair (First Time Setup)

Generate a new Ed25519 key pair for license signing:

```bash
python license_tool.py generate-keys
```

This creates:
- `private_key.pem` - Keep this secure! Never share it.
- `public_key.pem` - Embed this in the main application.

After generating, copy the public key content to `src/license/key_generator.py` in the main TEP application.

### Generate a License

To generate a license for a specific machine:

1. Get the machine ID from the TEP application's License Management page
2. Run:

```bash
python license_tool.py generate-license <machine_id>
```

Options:
- `--private-key FILE` - Use a specific private key file
- `--hex` - Output in hex format instead of word format

### Verify a License

To verify a license is valid for a machine:

```bash
python license_tool.py verify-license "LICENSE-KEY" <machine_id>
```

### Convert License Format

To convert between word and hex formats:

```bash
# Word to hex
python license_tool.py convert "WORD-WORD-WORD-..."

# Hex to word
python license_tool.py convert abc123def456...
```

## License Key Formats

Licenses can be in two formats:

1. **Word format** (recommended): 64 words separated by dashes, grouped by spaces
   - Easier to type and verify
   - Example: `APPLE-BAKER-CHARM-DELTA EAGLE-FLAME-GRAPE-HOTEL ...`

2. **Hex format**: 128-character hexadecimal string
   - Compact but harder to type
   - Example: `a1b2c3d4e5f6...`

Both formats are interchangeable and represent the same Ed25519 signature.

## Security Notes

- Keep `private_key.pem` secure and backed up
- Never include the private key in version control
- Never deploy the private key with the main application
- Regularly audit generated licenses
- Consider using a hardware security module (HSM) for production deployments
