#!/usr/bin/env bash
# shellcheck disable=SC2329  # 忽略函数未被使用的警告

## 开启globstar模式,允许使用**匹配所有子目录,bash4特性,默认是关闭的
shopt -s globstar

# On Mac OS, readlink -f doesn't work, so use._real_path get the real path of the file
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/" && pwd)

print_info() {
  echo -e "\e[44;37m$1\e[0m"
}
print_error() {
  echo -e "\e[44;37m$1\e[0m"
}


# color text : ref: https://m3.material.io/styles/color
#_print "success"   "Cloud resource created successfully."
#_print "error"     "Failed to connect to AWS instance."
#_print "warning"   "High cost alert: Instance is running on high-spec."
#_print "info"      "Deploying AI model to cluster..."
#_print "primary"   "AppHub is ready for configuration."
#_print "secondary" "Processing background tasks..."
#_print "tertiary"   "current workspace: $ROOT_DIR"
#_print "neutral"   "Help to email support@applab."
_print() {
    local type="$1"
    shift
    local text="$*"

    local type_lower=$(echo "$type" | tr '[:upper:]' '[:lower:]')

    case "$type_lower" in
        "success")   color_code="38;5;255;48;5;28;1"  ;; # 森林绿
        "error")     color_code="38;5;255;48;5;124;1" ;; # 砖红
        "warning")   color_code="38;5;16;48;5;214;1"  ;; # 琥珀黄 (黑字)
        "info")      color_code="38;5;255;48;5;31;1"  ;; # 钢蓝
        "primary")   color_code="38;5;255;48;5;55;1"  ;; # 深紫 (M3 Primary)
        "secondary") color_code="38;5;255;48;5;66;1"  ;; # 灰青 (M3 Secondary)
        "tertiary")  color_code="38;5;255;48;5;23;1"  ;; # 深青 (M3 Tertiary - Deep Teal)
        "neutral")   color_code="38;5;255;48;5;243;1" ;; # 中灰
        *)           color_code="38;5;255;48;5;243;1" ;; # 默认
    esac
    printf "\033[%sm%b\033[0m" "$color_code" "$text"
}

# 清晰的函数调用日志,替代 `set -x` 功能
#
# Usage:   run <some cmd>
# Example: run docker compose up
#
# 假设你的./sake 脚本里有个函数：
# up() {
#   run docker compose up;  # ./sake 的 22行
# }
# 运行`./sake up`后打印日志：
# 🔵 ./sake:22 up() ▶︎【/home/ubuntu/current_work_dir$ docker compose up】
# 你可以清晰的看到:
#   - 在脚本的哪一行: ./sake:22
#   - 哪个函数: up()
#   - 在哪个工作目录: /home/ubuntu/current_work_dir
#   - 执行了什么: docker compose up
# 在vscode中，按住macbook的cmd键,点终端上输出的'./sake:106', 可以让编辑器跳转到对应的脚本行，很方便
# 获取调用栈的原理：
#   `caller 0`输出为`22 foo ./sake`，即调用run函数的调用栈信息：行号、函数,脚本
run() {
  local caller_script=$(caller 0 | awk '{print $3}')
    # shellcheck disable=SC2001
  local caller_script=$(echo "$caller_script" | sed "s@^$HOME@~@" )

  local caller_line=$(caller 0 | awk '{print $1}')
  # 把 /home/ubuntu/current_work_dir 替换为 ~/current_work_dir 短格式
  # 使用 @ 作为分隔符,避免与路径中的 / 冲突
  # shellcheck disable=SC2001
  local show_pwd=$(echo "$PWD" | sed "s@^$HOME@~@" )
  local color_caller=$(_print secondary "$caller_script:$caller_line ${FUNCNAME[1]}() ")
  local color_pwd=$(_print info "$show_pwd$ " )
  local color_cmd=$(_print primary "$*")
  echo "$color_caller$color_pwd$color_cmd" >&2
  "$@"
}

_install_sha() {
  local sha_url="https://github.com/chen56/sha/raw/main/sha.bash"
  local vendor_dir="$ROOT_DIR/vendor"
  local target_file="$vendor_dir/sha.bash"
  local temp_file

  run mkdir -p "$vendor_dir"

  # Create a temporary file in the system's temporary directory
  temp_file=$(mktemp)
  run curl -L -o "$temp_file" "$sha_url"

  # Check if the downloaded file is a valid bash script
  if ! head -n 1 "$temp_file" | grep -q '#!/usr/bin/env bash'; then
    _print error "Error: Downloaded file does not appear to be a bash script (missing shebang)." >&2
    _print error "Content of downloaded file (first 10 lines):" >&2
    head -n 10 "$temp_file" >&2
    rm "$temp_file"
    exit 1
  fi

  # If checks pass, move the temporary file to the target location
  run mv "$temp_file" "$target_file"
  _print success "sha.bash installed successfully to $target_file"
}

if ! [[ -f "$ROOT_DIR/vendor/sha.bash" ]]; then
  _install_sha
fi

# shellcheck source=../vendor/sha.bash
source "$ROOT_DIR/vendor/sha.bash"

##################################################
# 每个项目的公共命令集
##################################################

clean() (
  run rm -rf .venv
  run rm -rf .ruff_cache
  run rm -rf ./**/build
  run rm -rf ./**/__pycache__
  run rm -rf ./**/dist
  run rm -rf ./**/*.egg-info
  run rm -rf .pytest_cache
)