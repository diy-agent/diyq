<#
.SYNOPSIS
更新 Windows OpenSSH 的 sshd_config 配置文件
.DESCRIPTION
自动备份原有配置，精准修改指定的 SSH 配置项，支持端口、密码登录、Root登录等核心配置
#>




# 管理员权限检测
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Read-Host "按任意键退出..."
    exit 1
}


## ssh server -----------------------
# 启动服务
Start-Service sshd

# 设置开机自动启动
Set-Service -Name sshd -StartupType Automatic

# 验证防火墙规则（默认已创建）
Get-NetFirewallRule -Name *ssh* | Select Name,Enabled

# 创建administrators_authorized_keys文件
New-Item -Path "C:\ProgramData\ssh\administrators_authorized_keys" -ItemType File -Force
# 设置正确的权限（Windows OpenSSH对权限要求极严，否则公钥认证失败）
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /grant "SYSTEM:(F)"
icacls "C:\ProgramData\ssh\administrators_authorized_keys" /grant "BUILTIN\Administrators:(F)"






# 配置文件路径和备份路径
$sshdConfigPath = "$env:ProgramData\ssh\sshd_config"
$backupPath = "$sshdConfigPath.bak_$(Get-Date -Format 'yyyyMMddHHmmss')"

# ====================== 自定义配置项（你可以根据需要修改这里）======================
$newConfig = @{
    "Port"                  = "22"              # SSH端口，建议改为非22端口更安全
    "PasswordAuthentication"= "yes"             # 是否允许密码登录（no为仅密钥登录）
    "PubkeyAuthentication"  = "yes"             # 是否允许密钥登录
    "PermitRootLogin"       = "no"              # 禁止root/管理员直接登录
    "DenyUsers"             = "Administrator"   # 禁止Administrator直接登录
    "AllowUsers"            = "testuser"        # 仅允许指定普通用户登录（替换为你的用户名）
}
# ==================================================================================

try {
    # 1. 检查配置文件是否存在
    if (-not (Test-Path $sshdConfigPath)) {
        throw "sshd_config 文件不存在，请确认已安装 OpenSSH 服务器！"
    }

    # 2. 备份原有配置（避免误操作）
    Copy-Item -Path $sshdConfigPath -Destination $backupPath -Force
    Write-Host "✅ 已备份原有配置到：$backupPath" -ForegroundColor Green

    # 3. 读取原有配置内容
    $configContent = Get-Content -Path $sshdConfigPath -Raw

    # 4. 遍历修改配置项
    foreach ($key in $newConfig.Keys) {
        $value = $newConfig[$key]
        # 正则匹配规则：匹配 "配置项  值" 或 "配置项=值" 或 "#配置项  值"（注释行）
        $regex = "(?m)^(\s*#?\s*)($key)\s*[= ]\s*.+$"
        $replace = "`$2 $value"  # 移除注释，设置新值
        
        if ($configContent -match $regex) {
            # 替换已有配置项
            $configContent = $configContent -replace $regex, $replace
            Write-Host "✅ 已更新配置：$key = $value" -ForegroundColor Green
        }
        else {
            # 原有配置中无此项，追加到文件末尾
            $configContent += "`n$key $value"
            Write-Host "✅ 已新增配置：$key = $value" -ForegroundColor Green
        }
    }

    # 5. 写入修改后的配置
    Set-Content -Path $sshdConfigPath -Value $configContent -Force -Encoding UTF8

    # 6. 重启 SSH 服务使配置生效
    Write-Host "🔄 正在重启 SSH 服务..." -ForegroundColor Cyan
    Restart-Service -Name sshd -Force
    Write-Host "✅ SSH 服务已重启，配置生效！" -ForegroundColor Green
}
catch {
    Write-Host "❌ 操作失败：$($_.Exception.Message)" -ForegroundColor Red
    # 失败时尝试恢复备份（可选）
    if (Test-Path $backupPath) {
        Write-Host "🔧 正在恢复原有配置..." -ForegroundColor Cyan
        Copy-Item -Path $backupPath -Destination $sshdConfigPath -Force
        Restart-Service -Name sshd -Force
        Write-Host "✅ 已恢复原有配置！" -ForegroundColor Green
    }
    Read-Host "按任意键退出..."
    exit 1
}

Write-Host "`n🎉 所有配置更新完成！" -ForegroundColor Green
Read-Host "按任意键退出..."