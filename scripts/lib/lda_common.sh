#!/usr/bin/env bash
#
# MIT License
#
# Copyright (c) 2025 Jerry Meyer (Tiny Walnut Games)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Living Dev Agent - Common Utilities Library
# Shared logging, color handling, and utility functions for LDA scripts

# Check if already sourced to prevent double-loading
if [[ "${LDA_COMMON_LOADED:-}" == "true" ]]; then
    return 0
fi

# Color configuration - respect NO_COLOR and USE_COLOR environment variables
if [[ "${NO_COLOR:-}" == "1" ]] || [[ "${USE_COLOR:-auto}" == "false" ]] || [[ "${USE_COLOR:-auto}" == "0" ]]; then
    LDA_USE_COLOR=false
elif [[ "${USE_COLOR:-auto}" == "true" ]] || [[ "${USE_COLOR:-auto}" == "1" ]]; then
    LDA_USE_COLOR=true
else
    # Auto-detect color support
    if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && tput colors >/dev/null 2>&1; then
        LDA_USE_COLOR=true
    else
        LDA_USE_COLOR=false
    fi
fi

# Color definitions
if [[ "$LDA_USE_COLOR" == "true" ]]; then
    # Sacred colors for the ritual
    LDA_BLUE='\033[0;34m'
    LDA_CYAN='\033[0;36m'
    LDA_GREEN='\033[0;32m'
    LDA_YELLOW='\033[1;33m'
    LDA_RED='\033[0;31m'
    LDA_PURPLE='\033[0;35m'
    LDA_GOLD='\033[1;33m'
    LDA_NC='\033[0m' # No Color
else
    # No color mode
    LDA_BLUE=''
    LDA_CYAN=''
    LDA_GREEN=''
    LDA_YELLOW=''
    LDA_RED=''
    LDA_PURPLE=''
    LDA_GOLD=''
    LDA_NC=''
fi

# Sacred emojis for the journey
LDA_EMOJI_INFO="🔍"
LDA_EMOJI_SUCCESS="✅"
LDA_EMOJI_WARNING="⚠️"
LDA_EMOJI_ERROR="❌"
LDA_EMOJI_MAGIC="🧙‍♂️"
LDA_EMOJI_SHIELD="🛡️"
LDA_EMOJI_BUTT="🍑"
LDA_EMOJI_SPARKLE="✨"
LDA_EMOJI_SCROLL="📜"
LDA_EMOJI_CROWN="👑"

# Logging functions
lda_log_info() {
    echo -e "${LDA_CYAN}${LDA_EMOJI_INFO} [INFO]${LDA_NC} $1"
}

lda_log_success() {
    echo -e "${LDA_GREEN}${LDA_EMOJI_SUCCESS} [SUCCESS]${LDA_NC} $1"
}

lda_log_warning() {
    echo -e "${LDA_YELLOW}${LDA_EMOJI_WARNING} [WARNING]${LDA_NC} $1"
}

lda_log_error() {
    echo -e "${LDA_RED}${LDA_EMOJI_ERROR} [ERROR]${LDA_NC} $1"
}

lda_log_magic() {
    echo -e "${LDA_PURPLE}${LDA_EMOJI_MAGIC} [MAGIC]${LDA_NC} $1"
}

lda_log_comfort() {
    echo -e "${LDA_GREEN}${LDA_EMOJI_SHIELD} $1${LDA_NC}"
}

lda_log_wisdom() {
    echo -e "${LDA_PURPLE}${LDA_EMOJI_SCROLL} $1${LDA_NC}"
}

lda_log_danger() {
    echo -e "${LDA_RED}${LDA_EMOJI_ERROR} $1${LDA_NC}"
}

lda_log_sacred() {
    echo -e "${LDA_GOLD}${LDA_EMOJI_SPARKLE} $1${LDA_NC}"
}

# Color echo function for custom colors
lda_cecho() {
    local color="$1"
    local message="$2"
    
    if [[ "$LDA_USE_COLOR" == "true" ]]; then
        echo -e "${color}${message}${LDA_NC}"
    else
        echo "$message"
    fi
}

# Die function - exit with error message
lda_die() {
    lda_log_error "$1"
    exit "${2:-1}"
}

# Confirmation prompt
lda_confirm() {
    local prompt="${1:-Are you sure?}"
    local default="${2:-n}"
    
    while true; do
        if [[ "$default" == "y" ]]; then
            read -p "$prompt [Y/n]: " choice
            choice="${choice:-y}"
        else
            read -p "$prompt [y/N]: " choice
            choice="${choice:-n}"
        fi
        
        case "$choice" in
            [Yy]|[Yy][Ee][Ss]) return 0 ;;
            [Nn]|[Nn][Oo]) return 1 ;;
            *) echo "Please answer yes or no." ;;
        esac
    done
}

# Timestamp function
lda_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# ISO timestamp function
lda_timestamp_iso() {
    date '+%Y-%m-%dT%H:%M:%S%z'
}

# JSON escape function
lda_json_escape() {
    local input="$1"
    # Basic JSON string escaping
    echo "$input" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g; s/\n/\\n/g; s/\r/\\r/g'
}

# Check if script is being run non-interactively
lda_is_non_interactive() {
    [[ ! -t 0 ]] || [[ "${LDA_NON_INTERACTIVE:-}" == "true" ]] || [[ "${CI:-}" == "true" ]]
}

# Show banner function
lda_show_banner() {
    local title="$1"
    local subtitle="${2:-}"
    
    echo ""
    lda_cecho "${LDA_GOLD}" "${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}"
    lda_cecho "${LDA_GOLD}" "${LDA_EMOJI_SPARKLE}                                  ${LDA_EMOJI_SPARKLE}"
    lda_cecho "${LDA_GOLD}" "${LDA_EMOJI_SPARKLE}      $title       ${LDA_EMOJI_SPARKLE}"
    if [[ -n "$subtitle" ]]; then
        lda_cecho "${LDA_GOLD}" "${LDA_EMOJI_SPARKLE}      $subtitle       ${LDA_EMOJI_SPARKLE}"
    fi
    lda_cecho "${LDA_GOLD}" "${LDA_EMOJI_SPARKLE}                                  ${LDA_EMOJI_SPARKLE}"
    lda_cecho "${LDA_GOLD}" "${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}${LDA_EMOJI_SPARKLE}"
    echo ""
}

# Mark as loaded
LDA_COMMON_LOADED=true

# Export functions for subshells if needed
export -f lda_log_info lda_log_success lda_log_warning lda_log_error lda_log_magic
export -f lda_log_comfort lda_log_wisdom lda_log_danger lda_log_sacred
export -f lda_cecho lda_die lda_confirm lda_timestamp lda_timestamp_iso
export -f lda_json_escape lda_is_non_interactive lda_show_banner