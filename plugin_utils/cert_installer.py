"""
Certificate installer for custom SSL certificates.

This module automatically adds custom certificates from the certs/ folder
to the certifi bundle used by specklepy.
"""

import os
from pathlib import Path
from typing import List


def get_certs_folder() -> Path:
    """Get the path to the certs folder in the plugin directory."""
    plugin_dir = Path(__file__).parent.parent
    certs_dir = plugin_dir / "certs"
    return certs_dir


def find_certificate_files(certs_dir: Path) -> List[Path]:
    """
    Find all certificate files in the certs directory.
    
    Looks for files with .pem, .crt, or .cer extensions.
    """
    if not certs_dir.exists():
        return []
    
    cert_files = []
    for ext in ['.pem', '.crt', '.cer']:
        cert_files.extend(certs_dir.glob(f'*{ext}'))
    
    return cert_files


def install_certificates() -> None:
    """
    Install custom certificates to the certifi bundle.
    
    This function:
    1. Finds all certificate files in the certs/ folder
    2. Locates the certifi cacert.pem file
    3. Appends custom certificates to it (if not already present)
    """
    try:
        import certifi
    except ImportError:
        print("certifi not available, skipping certificate installation")
        return
    
    certs_dir = get_certs_folder()
    cert_files = find_certificate_files(certs_dir)
    
    if not cert_files:
        print(f"No custom certificates found in {certs_dir}")
        return
    
    # Get the certifi bundle path
    certifi_path = Path(certifi.where())
    
    if not certifi_path.exists():
        print(f"Warning: certifi bundle not found at {certifi_path}")
        return
    
    # Read the current certifi bundle
    try:
        with open(certifi_path, 'r', encoding='utf-8') as f:
            existing_certs = f.read()
    except Exception as e:
        print(f"Warning: Could not read certifi bundle: {e}")
        return
    
    # Process each custom certificate
    certs_added = []
    for cert_file in cert_files:
        try:
            with open(cert_file, 'r', encoding='utf-8') as f:
                cert_content = f.read().strip()
            
            # Check if this certificate is already in the bundle
            # We'll use the first line of the cert as an identifier
            cert_lines = [line for line in cert_content.split('\n') if line.strip()]
            if not cert_lines:
                continue
                
            # Check if certificate is already present
            if cert_content in existing_certs:
                print(f"Certificate {cert_file.name} already installed")
                continue
            
            # Append the certificate
            with open(certifi_path, 'a', encoding='utf-8') as f:
                f.write('\n\n')
                f.write(f'# {cert_file.name} - Custom certificate added by Speckle QGIS plugin\n')
                f.write(cert_content)
                f.write('\n')
            
            certs_added.append(cert_file.name)
            print(f"Added custom certificate: {cert_file.name}")
            
        except Exception as e:
            print(f"Warning: Could not install certificate {cert_file.name}: {e}")
    
    if certs_added:
        print(f"Successfully installed {len(certs_added)} custom certificate(s)")
    else:
        print("No new certificates to install")


def ensure_certificates() -> None:
    """
    Main entry point for certificate installation.
    Call this during plugin initialization.
    """
    try:
        install_certificates()
    except Exception as e:
        print(f"Warning: Certificate installation failed: {e}")
        # Don't raise - plugin should still work even if cert installation fails
