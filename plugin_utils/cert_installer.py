"""
Certificate installer for custom SSL certificates.

This module automatically adds custom certificates from the certs/ folder
to the certifi bundle used by specklepy.
"""

import os
import sys
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


def get_speckle_certifi_paths() -> List[Path]:
    """
    Get all possible certifi bundle paths.
    
    Returns paths to certifi bundles in:
    1. Speckle connector installation directory
    2. System certifi (fallback)
    """
    certifi_paths = []
    
    # First, try to find certifi in the Speckle connector installation
    speckle_base = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Speckle" / "connector_installations"
    
    for connector_dir in ["QGISv3", "QGIS"]:
        certifi_in_connector = speckle_base / connector_dir / "certifi" / "cacert.pem"
        if certifi_in_connector.exists():
            certifi_paths.append(certifi_in_connector)
            print(f"Found certifi bundle in Speckle connector: {certifi_in_connector}")
    
    # Also try to import certifi and get its path
    try:
        import certifi
        system_certifi = Path(certifi.where())
        if system_certifi.exists() and system_certifi not in certifi_paths:
            certifi_paths.append(system_certifi)
            print(f"Found system certifi bundle: {system_certifi}")
    except ImportError:
        pass
    
    return certifi_paths


def install_certificates_to_bundle(certifi_path: Path, cert_files: List[Path]) -> int:
    """
    Install certificates to a specific certifi bundle.
    
    Returns the number of certificates added.
    """
    if not certifi_path.exists():
        print(f"Warning: certifi bundle not found at {certifi_path}")
        return 0
    
    # Read the current certifi bundle
    try:
        with open(certifi_path, 'r', encoding='utf-8') as f:
            existing_certs = f.read()
    except Exception as e:
        print(f"Warning: Could not read certifi bundle at {certifi_path}: {e}")
        return 0
    
    # Process each custom certificate
    certs_added = 0
    for cert_file in cert_files:
        try:
            with open(cert_file, 'r', encoding='utf-8') as f:
                cert_content = f.read().strip()
            
            # Check if this certificate is already in the bundle
            cert_lines = [line for line in cert_content.split('\n') if line.strip()]
            if not cert_lines:
                continue
                
            # Check if certificate is already present
            if cert_content in existing_certs:
                print(f"  Certificate {cert_file.name} already installed")
                continue
            
            # Append the certificate
            with open(certifi_path, 'a', encoding='utf-8') as f:
                f.write('\n\n')
                f.write(f'# {cert_file.name} - Custom certificate added by Speckle QGIS plugin\n')
                f.write(cert_content)
                f.write('\n')
            
            certs_added += 1
            print(f"  Added custom certificate: {cert_file.name}")
            
        except Exception as e:
            print(f"  Warning: Could not install certificate {cert_file.name}: {e}")
    
    return certs_added


def install_certificates() -> None:
    """
    Install custom certificates to all certifi bundles.
    
    This function:
    1. Finds all certificate files in the certs/ folder
    2. Locates all certifi cacert.pem files (Speckle connector + system)
    3. Appends custom certificates to them (if not already present)
    """
    certs_dir = get_certs_folder()
    cert_files = find_certificate_files(certs_dir)
    
    if not cert_files:
        print(f"No custom certificates found in {certs_dir}")
        return
    
    print(f"Found {len(cert_files)} certificate(s) to install:")
    for cert_file in cert_files:
        print(f"  - {cert_file.name}")
    
    # Get all certifi bundle paths
    certifi_paths = get_speckle_certifi_paths()
    
    if not certifi_paths:
        print("Warning: No certifi bundles found")
        return
    
    # Install to each bundle
    total_added = 0
    for certifi_path in certifi_paths:
        print(f"Installing to: {certifi_path}")
        added = install_certificates_to_bundle(certifi_path, cert_files)
        total_added += added
    
    if total_added > 0:
        print(f"Successfully installed {total_added} custom certificate(s) across {len(certifi_paths)} bundle(s)")
    else:
        print("No new certificates to install (all already present)")


def ensure_certificates() -> None:
    """
    Main entry point for certificate installation.
    Call this during plugin initialization.
    """
    try:
        print("=" * 60)
        print("Speckle QGIS: Installing custom SSL certificates")
        print("=" * 60)
        install_certificates()
        print("=" * 60)
    except Exception as e:
        print(f"Warning: Certificate installation failed: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise - plugin should still work even if cert installation fails
            
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
