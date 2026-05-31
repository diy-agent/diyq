#!/usr/bin/env bash

set -o errtrace  # -E trap inherited in sub script
set -o errexit   # -e
set -o functrace # -T If set, any trap on DEBUG and RETURN are inherited by shell functions
set -o pipefail  # default pipeline status==last command status, If set, status=any command fail

## 开启globstar模式，允许使用**匹配所有子目录,bash4特性，默认是关闭的
shopt -s globstar

# Get the real path of the script directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$ROOT_DIR/sha.common.sh"

# 全局命令不要进入到_c目录
cd "$ROOT_DIR"

####################################################################################
# app script
# 应用项目补充的公共脚本，不在bake维护范围
# 此位置以上的全都是bake工具脚本，copy走可以直接用，之下的为项目特定cmd，自己弄
####################################################################################


sync() {
  files() {
    run ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub
  }

  app() {
    run mise use -g git-lfs
    # Git LFS 会把自身的钩子脚本安装到你的用户级 Git 配置中（对应 ~/.gitconfig 文件），这是全局生效的
    run git lfs install
  } 

  all() {
    files
    app
  }
}


##########################################
# app cmd script
# 应用的命令脚本
##########################################


info() {
  basic() {
    echo "## me"
    echo "ROOT_DIR  : $ROOT_DIR";
  }
}

update() { 
  self() {
    _install_sha
  }
}


####################################################
# app entry script & _root cmd
####################################################
# alias docker=podman

sha "$@"
