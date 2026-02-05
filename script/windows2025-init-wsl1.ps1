
# 管理员权限检测
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Read-Host "按任意键退出..."
    exit 1
}

# 必须安装最新的版本，不然wsl命令会自己要求安装
winget install --id Microsoft.WSL --source winget --exact --accept-package-agreements --accept-source-agreements --silent
Write-Host "---  环境初始化: 正在配置 WSL1 兼容模式 ---" -ForegroundColor Cyan

# 2. 检查并开启系统功能 (WSL1 仅需此项)
# $features = @("Microsoft-Windows-Subsystem-Linux")
$features = @("Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform")
$needsRestart = $false

foreach ($f in $features) {
    $state = Get-WindowsOptionalFeature -Online -FeatureName $f
    if ($state.State -ne "Enabled") {
        Write-Host "正在开启组件: $f ..." -ForegroundColor Yellow
        Enable-WindowsOptionalFeature -Online -FeatureName $f -All -NoRestart
        $needsRestart = $true
    }else {
        Write-Host "已开启组件: $f ..."
    }
}

bcdedit /set hypervisorlaunchtype auto

# 3. 重启逻辑处理
if ($needsRestart) {
    Write-Host "`n[!重要!] 系统组件已更新，必须重启服务器后才能安装 Linux 分发版。" -ForegroundColor Red
    Write-Host "请重启后再次运行此脚本，或手动执行: wsl --install -d Ubuntu --web-download" -ForegroundColor Yellow
    # 如果在 AppLab 自动化流程中，可以取消下面这一行的注释实现自动重启
    Restart-Computer -Force
    exit
}

# 4. 安装wsl

# 腾讯云cvm不支持二次虚拟化，即无法安装wsl2，只能降级到1
wsl --set-default-version 1
wsl --list --online
wsl --install -d Ubuntu-24.04 