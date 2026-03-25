$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile("https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-windows-x64.zip", "sonar-scanner.zip")
Write-Host "Descarga completada"