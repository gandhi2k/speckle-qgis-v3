# Custom SSL Certificates

This folder contains custom SSL certificates that will be automatically added to the plugin's certificate bundle.

## Adding Your Server's Certificate

To add your Speckle server's certificate:

### Option 1: Using OpenSSL (Recommended)

```bash
openssl s_client -showcerts -connect speckle.abo-wind.de:443 </dev/null 2>/dev/null | openssl x509 -outform PEM > certs/speckle-abo-wind.pem
```

### Option 2: Using Browser

1. Visit your Speckle server in a browser (e.g., https://speckle.abo-wind.de)
2. Click the padlock icon in the address bar
3. View the certificate details
4. Export the certificate in PEM format (Base64 encoded)
5. Save it to this folder with a `.pem` or `.crt` extension

### Option 3: Using PowerShell (Windows)

```powershell
$webRequest = [Net.HttpWebRequest]::Create("https://speckle.abo-wind.de")
try { $webRequest.GetResponse() } catch {}
$cert = $webRequest.ServicePoint.Certificate
$bytes = $cert.Export([Security.Cryptography.X509Certificates.X509ContentType]::Cert)
Set-Content -Path "certs\speckle-abo-wind.pem" -Value "-----BEGIN CERTIFICATE-----" -Encoding ASCII
Set-Content -Path "certs\speckle-abo-wind.pem" -Value ([Convert]::ToBase64String($bytes, [Base64FormattingOptions]::InsertLineBreaks)) -Encoding ASCII -Append
Add-Content -Path "certs\speckle-abo-wind.pem" -Value "-----END CERTIFICATE-----" -Encoding ASCII
```

## Certificate Format

All certificate files should be in PEM format (text-based, Base64 encoded).
Supported file extensions: `.pem`, `.crt`, `.cer`

## How It Works

When the plugin starts, it automatically:
1. Scans this folder for certificate files
2. Adds them to the certifi certificate bundle used by specklepy
3. Enables secure connections to your custom Speckle servers

No manual intervention required after placing the certificates here.
