# 1. 权限与路径准备
$isAdmin = $false
try {
    $myId = [Security.Principal.WindowsIdentity]::GetCurrent()
    $myPrincipal = New-Object Security.Principal.WindowsPrincipal($myId)
    $isAdmin = $myPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
} catch {
    $isAdmin = $false
}

if (-not $isAdmin) {
    Write-Warning "请以管理员权限运行此脚本 (Run as Administrator)"
    exit
}

$scriptPath = $MyInvocation.MyCommand.Definition
$taskName = "AppLab_WSL_Resume_Task"
$logPath = "$env:SystemDrive\AppLab_WSL_Setup.log"

# 启动日志
Start-Transcript -Path $logPath -Append -ErrorAction SilentlyContinue

Write-Host "--- AppLab 自动化部署: WSL2 ---" -ForegroundColor Cyan

# 2. 检查功能开启状态 (幂等处理)
$features = @("Microsoft-Windows-Subsystem-Linux", "VirtualMachinePlatform")
$restartRequired = $false

foreach ($feature in $features) {
    $state = Get-WindowsOptionalFeature -Online -FeatureName $feature
    if ($state.State -ne "Enabled") {
        Write-Host "正在启用 $feature..." -ForegroundColor Yellow
        Enable-WindowsOptionalFeature -Online -FeatureName $feature -All -NoRestart
        $restartRequired = $true
    } else {
        Write-Host "功能已存在: $feature" -ForegroundColor Green
    }
}

# 3. 核心逻辑：判断是否需要配置重启后执行
if ($restartRequired) {
    Write-Host "检测到功能变更，正在配置重启自动续传任务..." -ForegroundColor Yellow
    
    # 构建重启后执行的参数
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Compatibility Win8
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
    
    Write-Host "系统将在 10 秒后重启..." -ForegroundColor Red
    Start-Sleep -Seconds 10
    Restart-Computer -Force
    Stop-Transcript
    exit
}

# 4. 阶段 B：重启后的后续操作
Write-Host "正在执行重启后配置 (阶段 B)..." -ForegroundColor Green

# 等待网络就绪
Write-Host "正在检查网络连接..."
$retryCount = 0
while ($retryCount -lt 20) {
    if (Test-Connection -ComputerName www.baidu.com -Count 1 -Quiet) { break }
    Write-Host "等待网络就绪... ($retryCount/20)"
    Start-Sleep -Seconds 3
    $retryCount++
}

# 安装/更新 WSL 内核
Write-Host "正在安装/更新 WSL 核心组件..." -ForegroundColor Cyan
try {
    # 方案 1: 尝试使用 winget (Server 2025 推荐)
    Write-Host "尝试通过 winget 安装 Microsoft.WSL..."
    winget install --id Microsoft.WSL --source winget --exact --accept-package-agreements --accept-source-agreements --silent
    
    if ($LASTEXITCODE -ne 0) {
        # 方案 2: 回退到 wsl --update
        Write-Host "Winget 失败，尝试 wsl --update..."
        wsl --update --web-download
    }
} catch {
    Write-Warning "自动安装失败，请检查网络环境或腾讯云安全组设置。"
}

# 设置默认版本
Write-Host "配置 WSL2 为默认版本..."
wsl --set-default-version 2

# 5. 清理：自杀逻辑（删除计划任务）
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Write-Host "安装完成，正在清理自动化任务..." -ForegroundColor Cyan
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Write-Host "WSL2 环境已完全就绪！" -ForegroundColor Green
Stop-Transcript