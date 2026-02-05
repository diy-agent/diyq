# ==============================
# AppLab 环境初始化脚本 (Windows Server)
# 作者: Chen Peng
# 日期: 2026-02-05
# ==============================

# --- 前置检查：管理员权限 ---

# 管理员权限检测
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Read-Host "按任意键退出..."
    exit 1
}

# --- 安装 mise 到安全目录 ---
& {
    Write-Host "📦 正在安装 mise..." -ForegroundColor Cyan
    $miseDir = "C:\Tools\mise"
    $null = New-Item -Path $miseDir -ItemType Directory -Force
    winget install jdx.mise --location $miseDir --silent --accept-package-agreements --accept-source-agreements

    # 添加 shims 到用户 PATH
    $shimPath = "$env:LOCALAPPDATA\mise\shims"
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $userPath.Contains($shimPath)) {
        $newPath = $userPath + ";" + $shimPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "✅ 已添加 mise shim 到用户 PATH" -ForegroundColor Green
        # 注意：新 PATH 对当前会话无效，需重启终端或手动刷新
    }
}



## mise 环境初始化 -----------------------

# 重新安装 mise 到指定目录 ，默认路径有安全问题无法安装
New-Item -Path "c:\Tools\mise" -ItemType Directory -Force
winget install jdx.mise --location "c:\Tools\mise"

# 读取当前用户的 PATH 变量
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
# mise shim 路径
$miseShimPath = "C:\Users\Administrator\AppData\Local\mise\shims"

# 检查路径是否已存在，避免重复添加
if (-not $currentPath.Contains($miseShimPath)) {
    $newPath = $currentPath + ";" + $miseShimPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "mise shim 路径已添加到 PATH：$miseShimPath"
} else {
    Write-Host "mise shim 路径已存在于 PATH 中，无需重复添加"
}


# --- 部署 win-acme（官方 ZIP 方式，不依赖 dotnet tool, win-acme也没有winget包）---
& {
    $version = "2.2.9.1701"  # 请根据 https://github.com/win-acme/win-acme/releases 检查最新版
    $installPath = "C:\Tools\win-acme"
    $zipFile = "$env:TEMP\win-acme.zip"

    Write-Host "⬇️ 正在下载 win-acme v$version..." -ForegroundColor Cyan
    # 修复：移除 URL 中的多余空格
    $url = "https://github.com/win-acme/win-acme/releases/download/v$version/win-acme.v$version.x64.trimmed.zip"

    try {
        Invoke-WebRequest -Uri $url -OutFile $zipFile -UseBasicParsing
        $null = New-Item -ItemType Directory -Force -Path $installPath
        Expand-Archive -Path $zipFile -DestinationPath $installPath -Force
        Write-Host "✅ win-acme 已部署到 $installPath" -ForegroundColor Green
    } catch {
        Write-Error "❌ 下载或解压 win-acme 失败: $_"
        exit 1
    }
}


mise use -g uv


# 5. 其他
winget install --id Google.Chrome --source winget --silent --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.VisualStudioCode --source winget --silent --accept-package-agreements --accept-source-agreements


