# ==============================
# AppLab 环境初始化脚本 (Windows Server)
# 作者: Chen Peng
# 日期: 2026-02-05
# 版本: 2.0 (函数式重构)
# ==============================

# 保证程序(包括外部程序)非0退出即脚本终止异常exit
$ErrorActionPreference = 'Stop'


# 确保 WinGet 链接目录在 PATH 中, WinGet只在第一次安装包后把自己的可执行文件路径添加到 PATH 中，但要开新Shell才生效，我们补一下

# --- 函数定义 ---

# 检查管理员权限，不满足则直接退出
function _Check-IsAdmin {
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
        Read-Host "按任意键退出..."
        exit 1
    }
}

# 将目录添加到用户 PATH (如果不存在) - 内部函数
function _Add-ToUserPath {
    param(
        [string]$PathToAdd
    )

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not ($userPath -split ';').Contains($PathToAdd)) {
        $newPath = $userPath + ";" + $PathToAdd
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "✅ 已将 '$PathToAdd' 添加到用户 PATH。" -ForegroundColor Green
        Write-Host "   注意：新的 PATH 对当前会话无效，需重启终端或手动刷新环境变量。" -ForegroundColor Yellow


    } else {
        Write-Host "ℹ️ 路径 '$PathToAdd' 已存在于用户 PATH 中，无需添加。" -ForegroundColor Gray
    }
}


# 安装常用软件，没有在mise的
function Install-WingetPkgs {
    Write-Host "--- 💻 install Winget软件 ---" -ForegroundColor Cyan
    
    # winget install Google.Chrome              --silent --accept-source-agreements --accept-package-agreements
    winget install Microsoft.VisualStudioCode --silent --accept-source-agreements --accept-package-agreements
}


# 安装和配置 mise
function Install-Mise {
    Write-Host "--- 📦 正在安装和配置 mise ---" -ForegroundColor Cyan
    winget install jdx.mise  --silent --accept-package-agreements --accept-source-agreements
    $miseDir = "c:\tools\mise"
    # 添加 mise shims 到用户 PATH
    _Add-ToUserPath -PathToAdd "$env:LOCALAPPDATA\mise\shims"
    $env:Path += ";$env:LOCALAPPDATA\Microsoft\WinGet\Links"

    
    Write-Host "--- 📦 正在安装mise 相关包 ---" -ForegroundColor Cyan
    mise use -g uv

}

# 部署 win-acme
function Install-WinAcme {
    Write-Host "--- ⬇️ 正在部署 win-acme ---" -ForegroundColor Cyan
    $version = "2.2.9.1701"  # 请根据 https://github.com/win-acme/win-acme/releases 检查最新版
    $installPath = "c:\tools\win-acme"
    $zipFile = "$env:TEMP\win-acme.zip"
    $url = "https://github.com/win-acme/win-acme/releases/download/v$version/win-acme.v$version.x64.pluggable.zip"

    Write-Host "正在下载 win-acme v$version..."
    Invoke-WebRequest -Uri $url -OutFile $zipFile -UseBasicParsing -ErrorAction Stop
    
    Write-Host "正在解压到 $installPath..."
    if (-not (Test-Path -Path $installPath)) {
        New-Item -ItemType Directory -Force -Path $installPath -ErrorAction Stop | Out-Null
    }
    Expand-Archive -Path $zipFile -DestinationPath $installPath -Force -ErrorAction Stop
    
    Write-Host "✅ win-acme 已成功部署到 $installPath" -ForegroundColor Green
}

# --- 主逻辑 ---
function Main {
    # 1. 检查管理员权限（不满足则直接退出）
    _Check-IsAdmin

    Write-Host "=================================" -ForegroundColor Yellow
    Write-Host "  环境初始化开始" -ForegroundColor Yellow
    Write-Host "=================================" -ForegroundColor Yellow

    # 5. 安装其他常用软件
    Install-WingetPkgs


    # 2. 安装和配置 mise
    Install-Mise

    # 3. 部署 win-acme
    Install-WinAcme

    Write-Host "=================================" -ForegroundColor Green
    Write-Host "  🎉 环境初始化完成！" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Read-Host "按任意键退出..."
}

# --- 脚本执行入口 ---
Main