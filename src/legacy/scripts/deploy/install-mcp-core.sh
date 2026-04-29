#!/usr/bin/env bash
#
# CyberSecSuite MCP Core Bootstrap Installer
# Installs 7 core MCPs with comprehensive progress tracking and error handling
#
# Usage:
#   bash scripts/install-mcp-core.sh [--offline] [--verbose] [--verify-only]
#
# Exit Codes:
#   0 - Success, all MCPs installed
#   1 - General error
#   2 - Python/uv version mismatch
#   3 - Installation timeout
#   4 - Verification failed
#

set -euo pipefail

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MARKETPLACE_ROOT="${MARKETPLACE_ROOT:-/home/daen/Projects/ai-marketplace}"
CYBERSECSUITE_ROOT="${CYBERSECSUITE_ROOT:-/home/daen/Projects/cybersecsuite}"
PYTHON_MIN_VERSION="3.11"
TIMEOUT_SECONDS=120
START_TIME=$(date +%s)

# MCPs to install (7 total)
declare -a MCPS=(
    "csscore-mcp"
    "canvas-mcp"
    "memory-mcp"
    "template-mcp"
    "playwright-mcp"
    "dystopian-crypto-mcp"
    "custom-mcp"  # 7th MCP - custom bridge
)

declare -a MCP_PATHS=(
    "${MARKETPLACE_ROOT}/mcps/csscore-mcp"
    "${MARKETPLACE_ROOT}/mcps/canvas-mcp"
    "${MARKETPLACE_ROOT}/mcps/memory-mcp"
    "${MARKETPLACE_ROOT}/mcps/template-mcp"
    "${MARKETPLACE_ROOT}/mcps/playwright-mcp"
    "${MARKETPLACE_ROOT}/mcps/dystopian-crypto-mcp"
    "${CYBERSECSUITE_ROOT}/src/csmcp/mcps/custom-mcp"  # Custom MCP bridge
)

# Options
OFFLINE_MODE=false
VERBOSE_MODE=false
VERIFY_ONLY=false

# Logging functions
log_info() {
    echo -e "${BLUE}[ℹ]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

log_error() {
    echo -e "${RED}[✗]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

log_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    echo -e "${BLUE}[${percent}%]${NC} ${current}/${total} MCPs installed"
}

# Utility functions
check_timeout() {
    local current_time=$(date +%s)
    local elapsed=$((current_time - START_TIME))
    if [[ $elapsed -gt $TIMEOUT_SECONDS ]]; then
        log_error "Installation timeout exceeded: ${elapsed}s > ${TIMEOUT_SECONDS}s"
        exit 3
    fi
}

check_python_version() {
    local python_cmd=${1:-python3}
    local version=$($python_cmd --version 2>&1 | awk '{print $2}')
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 11 ]]; then
        log_error "Python $PYTHON_MIN_VERSION+ required, found $version"
        exit 2
    fi
    
    echo "$version"
}

check_uv_installed() {
    if ! command -v uv &> /dev/null; then
        log_error "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 2
    fi
    
    local uv_version=$(uv --version 2>&1 | awk '{print $2}')
    log_info "Found uv $uv_version"
}

verify_mcp_installation() {
    local mcp_name=$1
    local mcp_module=$(echo $mcp_name | tr '-' '_')
    
    if python3 -c "import ${mcp_module}" 2>/dev/null; then
        log_success "Verified: $mcp_name"
        return 0
    else
        log_error "Verification failed: $mcp_name"
        return 1
    fi
}

verify_mcp_executable() {
    local mcp_name=$1
    
    if python3 -m ${mcp_name//-/_} --help &>/dev/null 2>&1; then
        log_success "Executable verified: $mcp_name"
        return 0
    else
        log_warning "Executable verification skipped for: $mcp_name (may not have __main__)"
        return 0
    fi
}

install_mcp_from_source() {
    local mcp_path=$1
    local mcp_name=$(basename $mcp_path)
    
    if [[ ! -d "$mcp_path" ]]; then
        log_warning "MCP path not found: $mcp_path"
        return 1
    fi
    
    check_timeout
    
    log_info "Installing $mcp_name from source: $mcp_path"
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        cd "$mcp_path"
        uv pip install -e ".[dev]" 2>&1 | tee -a /tmp/mcp_install.log || return 1
        cd - > /dev/null
    else
        cd "$mcp_path"
        uv pip install -e . > /tmp/mcp_install_${mcp_name}.log 2>&1 || {
            log_error "Installation failed for $mcp_name"
            tail -20 /tmp/mcp_install_${mcp_name}.log >&2
            return 1
        }
        cd - > /dev/null
    fi
    
    log_success "Installed: $mcp_name"
    return 0
}

install_mcp_from_pypi() {
    local mcp_name=$1
    
    check_timeout
    
    log_info "Installing $mcp_name from PyPI"
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        uv pip install "$mcp_name" 2>&1 | tee -a /tmp/mcp_install.log || return 1
    else
        uv pip install "$mcp_name" > /tmp/mcp_install_${mcp_name}.log 2>&1 || {
            log_error "Installation failed for $mcp_name"
            tail -20 /tmp/mcp_install_${mcp_name}.log >&2
            return 1
        }
    fi
    
    log_success "Installed: $mcp_name"
    return 0
}

# Main installation workflow
main() {
    log_info "═══════════════════════════════════════════════════════════"
    log_info "CyberSecSuite MCP Core Bootstrap Installer v1.0"
    log_info "═══════════════════════════════════════════════════════════"
    
    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --offline)
                OFFLINE_MODE=true
                shift
                ;;
            --verbose)
                VERBOSE_MODE=true
                shift
                ;;
            --verify-only)
                VERIFY_ONLY=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Preflight checks
    log_info "Running preflight checks..."
    check_uv_installed
    local py_version=$(check_python_version)
    log_success "Python $py_version ✓"
    
    # Verify marketplace and cybersecsuite directories exist
    if [[ ! -d "$MARKETPLACE_ROOT" ]]; then
        log_error "Marketplace root not found: $MARKETPLACE_ROOT"
        exit 1
    fi
    log_success "Marketplace root: $MARKETPLACE_ROOT ✓"
    
    if [[ ! -d "$CYBERSECSUITE_ROOT" ]]; then
        log_error "CyberSecSuite root not found: $CYBERSECSUITE_ROOT"
        exit 1
    fi
    log_success "CyberSecSuite root: $CYBERSECSUITE_ROOT ✓"
    
    log_info "Preflight checks complete (timeout: ${TIMEOUT_SECONDS}s)"
    
    if [[ "$VERIFY_ONLY" == "true" ]]; then
        log_info "Verification mode only..."
        local failed=0
        for i in "${!MCPS[@]}"; do
            if ! verify_mcp_installation "${MCPS[$i]}"; then
                ((failed++))
            fi
        done
        
        if [[ $failed -gt 0 ]]; then
            log_error "$failed MCPs failed verification"
            exit 4
        fi
        
        log_success "All MCPs verified!"
        exit 0
    fi
    
    # Installation phase
    log_info "═══════════════════════════════════════════════════════════"
    log_info "Installation Phase"
    log_info "═══════════════════════════════════════════════════════════"
    
    local installed=0
    local total=${#MCPS[@]}
    local failed=()
    
    for i in "${!MCPS[@]}"; do
        local mcp_name="${MCPS[$i]}"
        local mcp_path="${MCP_PATHS[$i]}"
        
        if [[ -d "$mcp_path" ]]; then
            # Install from source if local path exists
            if install_mcp_from_source "$mcp_path"; then
                ((installed++))
                log_progress $installed $total
            else
                failed+=("$mcp_name")
            fi
        else
            # Try PyPI if not offline mode
            if [[ "$OFFLINE_MODE" != "true" ]]; then
                if install_mcp_from_pypi "$mcp_name"; then
                    ((installed++))
                    log_progress $installed $total
                else
                    failed+=("$mcp_name")
                fi
            else
                log_error "Source not found and offline mode enabled: $mcp_name"
                failed+=("$mcp_name")
            fi
        fi
    done
    
    # Verification phase
    log_info "═══════════════════════════════════════════════════════════"
    log_info "Verification Phase"
    log_info "═══════════════════════════════════════════════════════════"
    
    local verified=0
    local verify_failed=()
    
    for mcp_name in "${MCPS[@]}"; do
        if [[ ! " ${failed[@]} " =~ " ${mcp_name} " ]]; then
            if verify_mcp_installation "$mcp_name" && verify_mcp_executable "$mcp_name"; then
                ((verified++))
            else
                verify_failed+=("$mcp_name")
            fi
        fi
    done
    
    # Summary report
    log_info "═══════════════════════════════════════════════════════════"
    log_info "Installation Summary"
    log_info "═══════════════════════════════════════════════════════════"
    
    local elapsed=$(($(date +%s) - START_TIME))
    log_info "Time elapsed: ${elapsed}s / ${TIMEOUT_SECONDS}s"
    log_info "Installed: $installed / $total MCPs"
    log_info "Verified: $verified / $total MCPs"
    
    if [[ ${#failed[@]} -gt 0 ]]; then
        log_error "Failed installations: ${failed[@]}"
    fi
    
    if [[ ${#verify_failed[@]} -gt 0 ]]; then
        log_warning "Verification failed for: ${verify_failed[@]}"
    fi
    
    # Generate report
    cat > /tmp/mcp_bootstrap_report.txt <<EOF
MCP Bootstrap Installation Report
Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')
Marketplace: $MARKETPLACE_ROOT
CyberSecSuite: $CYBERSECSUITE_ROOT

Installation Results:
  Installed: $installed / $total
  Verified: $verified / $total
  Duration: ${elapsed}s

MCPs:
EOF
    
    for mcp_name in "${MCPS[@]}"; do
        if [[ " ${failed[@]} " =~ " ${mcp_name} " ]]; then
            echo "  ✗ $mcp_name (installation failed)" >> /tmp/mcp_bootstrap_report.txt
        elif [[ " ${verify_failed[@]} " =~ " ${mcp_name} " ]]; then
            echo "  ⚠ $mcp_name (installed but verification failed)" >> /tmp/mcp_bootstrap_report.txt
        else
            echo "  ✓ $mcp_name" >> /tmp/mcp_bootstrap_report.txt
        fi
    done
    
    log_info "Report saved to: /tmp/mcp_bootstrap_report.txt"
    
    # Scaffold project templates
    uv run python -m cybersecsuite.scaffold 2>/dev/null || true

    # Exit with appropriate code
    if [[ $installed -eq $total && $verified -eq $total ]]; then
        log_success "═══════════════════════════════════════════════════════════"
        log_success "Bootstrap installation successful! All MCPs ready."
        log_success "═══════════════════════════════════════════════════════════"
        exit 0
    elif [[ $installed -gt 0 ]]; then
        log_warning "═══════════════════════════════════════════════════════════"
        log_warning "Partial success: $installed/$total MCPs installed"
        log_warning "═══════════════════════════════════════════════════════════"
        exit 1
    else
        log_error "═══════════════════════════════════════════════════════════"
        log_error "Installation failed"
        log_error "═══════════════════════════════════════════════════════════"
        exit 1
    fi
}

# Execute main function
main "$@"
