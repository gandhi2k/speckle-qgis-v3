# Extract SSL certificate from Speckle server
# Usage: .\get-certificate.ps1 -ServerUrl "speckle.abo-wind.de" [-Port 443]

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerUrl,
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 443
)

$ErrorActionPreference = "Stop"

# Remove protocol if present
$ServerUrl = $ServerUrl -replace "^https?://", ""

Write-Host "Extracting certificate from $ServerUrl`:$Port..." -ForegroundColor Cyan

try {
    # Create TCP connection
    $tcpClient = New-Object System.Net.Sockets.TcpClient($ServerUrl, $Port)
    $sslStream = New-Object System.Net.Security.SslStream($tcpClient.GetStream(), $false, {$true})
    
    # Perform SSL handshake
    $sslStream.AuthenticateAsClient($ServerUrl)
    
    # Get the certificate
    $cert = $sslStream.RemoteCertificate
    
    if ($cert) {
        # Export certificate in PEM format
        $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
        $certBase64 = [Convert]::ToBase64String($certBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
        
        # Sanitize server name for filename
        $safeName = $ServerUrl -replace "[^a-zA-Z0-9\-\.]", "-"
        $outputPath = Join-Path $PSScriptRoot "$safeName.pem"
        
        # Write PEM file
        $pemContent = @"
-----BEGIN CERTIFICATE-----
$certBase64
-----END CERTIFICATE-----
"@
        
        Set-Content -Path $outputPath -Value $pemContent -Encoding ASCII
        
        Write-Host "✓ Certificate saved to: $outputPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "Certificate Details:" -ForegroundColor Yellow
        Write-Host "  Subject: $($cert.Subject)"
        Write-Host "  Issuer:  $($cert.Issuer)"
        Write-Host "  Valid:   $($cert.GetEffectiveDateString()) to $($cert.GetExpirationDateString())"
        Write-Host ""
        Write-Host "The certificate will be automatically loaded when you restart QGIS." -ForegroundColor Green
    }
    else {
        Write-Host "✗ Could not retrieve certificate" -ForegroundColor Red
    }
    
    # Cleanup
    $sslStream.Close()
    $tcpClient.Close()
}
catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "If you are behind a proxy or firewall, you may need to:" -ForegroundColor Yellow
    Write-Host "  1. Export the certificate manually from your browser"
    Write-Host "  2. Save it to this folder as a .pem file"
    exit 1
}
