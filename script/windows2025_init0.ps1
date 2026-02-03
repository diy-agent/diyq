winget install --id Google.Chrome --source winget --silent --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.VisualStudioCode --source winget --silent --accept-package-agreements --accept-source-agreements

Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux" -All -NoRestart