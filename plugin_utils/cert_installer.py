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
    return plugin_dir / "certs"


def find_certificate_files(certs_dir: Path) -> List[Path]:
    """Find all certificate files in the certs directory."""
    if not certs_dir.exists():
        return []

    cert_files: List[Path] = []
    for ext in (".pem", ".crt", ".cer"):
        cert_files.extend(certs_dir.glob(f"*{ext}"))
    return cert_files


def get_runtime_requests_bundle() -> Path | None:
    """Return the CA bundle requests will use if requests is already importable."""
    try:
        import requests

        bundle = Path(requests.certs.where())
        print(f"Runtime requests module: {requests.__file__}")
        print(f"Runtime requests bundle: {bundle}")
        return bundle
    except Exception as error:
        print(f"Runtime requests bundle could not be determined: {error}")
        return None


def get_speckle_certifi_paths() -> List[Path]:
    """Get all certifi bundle paths relevant for this plugin."""
    certifi_paths: List[Path] = []

    runtime_bundle = get_runtime_requests_bundle()
    if runtime_bundle and runtime_bundle.exists():
        certifi_paths.append(runtime_bundle)
        print(f"Found runtime requests bundle: {runtime_bundle}")

    speckle_base = (
        Path(os.path.expanduser("~"))
        / "AppData"
        / "Roaming"
        / "Speckle"
        / "connector_installations"
    )

    for connector_dir in ("QGISv3", "QGIS"):
        certifi_in_connector = speckle_base / connector_dir / "certifi" / "cacert.pem"
        if certifi_in_connector.exists():
            certifi_paths.append(certifi_in_connector)
            print(f"Found certifi bundle in Speckle connector: {certifi_in_connector}")

    try:
        import certifi

        system_certifi = Path(certifi.where())
        if system_certifi.exists() and system_certifi not in certifi_paths:
            certifi_paths.append(system_certifi)
            print(f"Found system certifi bundle: {system_certifi}")
    except ImportError:
        pass

    return certifi_paths


def get_preferred_ca_bundle(certifi_paths: List[Path]) -> Path | None:
    """Choose the bundle that should be forced via environment variables."""
    runtime_bundle = get_runtime_requests_bundle()
    if runtime_bundle and runtime_bundle.exists():
        return runtime_bundle

    for bundle in certifi_paths:
        if bundle.exists():
            return bundle

    return None


def configure_tls_environment(bundle_path: Path) -> None:
    """Force requests/urllib3/ssl to use a known CA bundle."""
    bundle = str(bundle_path)
    os.environ["REQUESTS_CA_BUNDLE"] = bundle
    os.environ["CURL_CA_BUNDLE"] = bundle
    os.environ["SSL_CERT_FILE"] = bundle
    print(f"Configured REQUESTS_CA_BUNDLE={bundle}")
    print(f"Configured CURL_CA_BUNDLE={bundle}")
    print(f"Configured SSL_CERT_FILE={bundle}")


def install_certificates_to_bundle(certifi_path: Path, cert_files: List[Path]) -> int:
    """Install certificates to a specific certifi bundle."""
    if not certifi_path.exists():
        print(f"Warning: certifi bundle not found at {certifi_path}")
        return 0

    try:
        existing_certs = certifi_path.read_text(encoding="utf-8")
    except Exception as error:
        print(f"Warning: Could not read certifi bundle at {certifi_path}: {error}")
        return 0

    certs_added = 0
    for cert_file in cert_files:
        try:
            cert_content = cert_file.read_text(encoding="utf-8").strip()
            if not cert_content:
                continue

            if cert_content in existing_certs:
                print(f"  Certificate {cert_file.name} already installed")
                continue

            with certifi_path.open("a", encoding="utf-8") as file_handle:
                file_handle.write("\n\n")
                file_handle.write(
                    f"# {cert_file.name} - Custom certificate added by Speckle QGIS plugin\n"
                )
                file_handle.write(cert_content)
                file_handle.write("\n")

            existing_certs += f"\n\n{cert_content}\n"
            certs_added += 1
            print(f"  Added custom certificate: {cert_file.name}")
        except Exception as error:
            print(f"  Warning: Could not install certificate {cert_file.name}: {error}")

    return certs_added


def install_certificates() -> None:
    """Install custom certificates to all detected certifi bundles."""
    certs_dir = get_certs_folder()
    cert_files = find_certificate_files(certs_dir)

    if not cert_files:
        print(f"No custom certificates found in {certs_dir}")
        return

    print(f"Found {len(cert_files)} certificate(s) to install:")
    for cert_file in cert_files:
        print(f"  - {cert_file.name}")

    certifi_paths = get_speckle_certifi_paths()
    if not certifi_paths:
        print("Warning: No certifi bundles found")
        return

    total_added = 0
    for certifi_path in certifi_paths:
        print(f"Installing to: {certifi_path}")
        total_added += install_certificates_to_bundle(certifi_path, cert_files)

    if total_added > 0:
        print(
            f"Successfully installed {total_added} custom certificate(s) across {len(certifi_paths)} bundle(s)"
        )
    else:
        print("No new certificates to install (all already present)")

    preferred_bundle = get_preferred_ca_bundle(certifi_paths)
    if preferred_bundle:
        configure_tls_environment(preferred_bundle)
    else:
        print("Warning: Could not determine preferred CA bundle for runtime TLS configuration")


def ensure_certificates() -> None:
    """Main entry point for certificate installation."""
    try:
        print("=" * 60)
        print("Speckle QGIS: Installing custom SSL certificates")
        print("=" * 60)
        install_certificates()
        print("=" * 60)
    except Exception as error:
        print(f"Warning: Certificate installation failed: {error}")
        import traceback

        traceback.print_exc()
