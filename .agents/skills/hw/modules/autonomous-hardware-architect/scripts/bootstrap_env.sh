#!/usr/bin/env bash
# bootstrap_env.sh — Idempotent environment checker and installer for
# autonomous-hardware-architect (KiCad CLI, Freerouting, Java, Python EDA/CAD, Firmware tools).

set -euo pipefail

MODE="check"
JSON_OUT=0
DRY_RUN=0
VENV_DIR="${HOME}/.gemini/hardware-venv"
FREEROUTING_DIR="${HOME}/.local/share/freerouting"
FREEROUTING_VERSION="2.0.1"
FREEROUTING_URL="https://github.com/freerouting/freerouting/releases/download/v${FREEROUTING_VERSION}/freerouting-${FREEROUTING_VERSION}.jar"
FREEROUTING_JAR="${FREEROUTING_DIR}/freerouting-${FREEROUTING_VERSION}.jar"

usage() {
  cat <<'EOF'
Usage: bootstrap_env.sh [--check | --install] [--dry-run] [--json] [--venv DIR]

Options:
  --check     Idempotently inspect installed EDA, CAD, autorouting, and firmware tools (default)
  --install   Install missing tools via Homebrew/apt + isolated uv/pip venv (~/.gemini/hardware-venv)
  --dry-run   Show commands that --install would execute without modifying the system
  --json      Emit structured JSON report to stdout
  --venv DIR  Override target Python virtual environment directory
  -h, --help  Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) MODE="check"; shift ;;
    --install) MODE="install"; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --json) JSON_OUT=1; shift ;;
    --venv) VENV_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

run_or_echo() {
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo "[DRY-RUN] $*" >&2
  else
    "$@"
  fi
}

find_kicad_cli() {
  if command -v kicad-cli >/dev/null 2>&1; then
    command -v kicad-cli
  elif [[ -x "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" ]]; then
    echo "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
  else
    echo ""
  fi
}

find_kicad_python() {
  if [[ -x "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3" ]]; then
    echo "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
  elif python3 -c "import pcbnew" >/dev/null 2>&1; then
    command -v python3
  else
    echo ""
  fi
}

find_java() {
  if command -v java >/dev/null 2>&1 && java -version >/dev/null 2>&1; then
    command -v java
  elif [[ -x "/opt/homebrew/opt/openjdk/bin/java" ]]; then
    echo "/opt/homebrew/opt/openjdk/bin/java"
  else
    echo ""
  fi
}

find_freerouting() {
  if command -v freerouting >/dev/null 2>&1; then
    command -v freerouting
  elif [[ -f "${FREEROUTING_JAR}" ]]; then
    echo "${FREEROUTING_JAR}"
  elif [[ -f "${FREEROUTING_DIR}/freerouting.jar" ]]; then
    echo "${FREEROUTING_DIR}/freerouting.jar"
  else
    echo ""
  fi
}

if [[ "${MODE}" == "install" ]]; then
  OS_NAME="$(uname -s)"
  if [[ -z "$(find_kicad_cli)" ]]; then
    if [[ "${OS_NAME}" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
      run_or_echo brew install --cask kicad
    elif [[ "${OS_NAME}" == "Linux" ]] && command -v apt-get >/dev/null 2>&1; then
      run_or_echo sudo apt-get update
      run_or_echo sudo apt-get install -y kicad
    fi
  fi

  if [[ -z "$(find_java)" ]]; then
    if [[ "${OS_NAME}" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
      run_or_echo brew install openjdk
    elif [[ "${OS_NAME}" == "Linux" ]] && command -v apt-get >/dev/null 2>&1; then
      run_or_echo sudo apt-get install -y default-jre-headless
    fi
  fi

  if ! command -v dtc >/dev/null 2>&1; then
    if [[ "${OS_NAME}" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
      run_or_echo brew install dtc
    elif [[ "${OS_NAME}" == "Linux" ]] && command -v apt-get >/dev/null 2>&1; then
      run_or_echo sudo apt-get install -y device-tree-compiler
    fi
  fi

  if [[ -z "$(find_freerouting)" ]]; then
    run_or_echo mkdir -p "${FREEROUTING_DIR}"
    run_or_echo curl -fsSL "${FREEROUTING_URL}" -o "${FREEROUTING_JAR}"
    run_or_echo ln -sf "${FREEROUTING_JAR}" "${FREEROUTING_DIR}/freerouting.jar"
  fi

  if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    if command -v uv >/dev/null 2>&1; then
      run_or_echo uv venv "${VENV_DIR}"
    else
      run_or_echo python3 -m venv "${VENV_DIR}"
    fi
  fi

  PY_PKGS=(skidl kicad-skip build123d trimesh esptool)
  if command -v uv >/dev/null 2>&1; then
    run_or_echo uv pip install --python "${VENV_DIR}/bin/python" "${PY_PKGS[@]}"
  else
    run_or_echo "${VENV_DIR}/bin/pip" install --upgrade pip
    run_or_echo "${VENV_DIR}/bin/pip" install "${PY_PKGS[@]}"
  fi
fi

KICAD_CLI_PATH="$(find_kicad_cli)"
KICAD_PY_PATH="$(find_kicad_python)"
JAVA_PATH="$(find_java)"
FREEROUTING_PATH="$(find_freerouting)"
DTC_PATH="$(command -v dtc || true)"
UV_PATH="$(command -v uv || true)"
SHASUM_PATH="$(command -v shasum || command -v sha256sum || true)"

TARGET_PY="python3"
if [[ -x "${VENV_DIR}/bin/python" ]]; then
  TARGET_PY="${VENV_DIR}/bin/python"
fi

check_py_mod() {
  local mod="$1"
  if "${TARGET_PY}" -c "import ${mod}" >/dev/null 2>&1; then
    echo "true"
  elif python3 -c "import ${mod}" >/dev/null 2>&1; then
    echo "true"
  else
    echo "false"
  fi
}

HAS_SKIDL="$(check_py_mod skidl)"
HAS_SKIP="$(check_py_mod skip)"
HAS_BUILD123D="$(check_py_mod build123d)"
HAS_CADQUERY="$(check_py_mod cadquery)"
HAS_TRIMESH="$(check_py_mod trimesh)"
HAS_ESPTOOL="$(check_py_mod esptool)"

READY="true"
if [[ -z "${KICAD_CLI_PATH}" || -z "${FREEROUTING_PATH}" || ( "${HAS_BUILD123D}" == "false" && "${HAS_CADQUERY}" == "false" ) ]]; then
  READY="false"
fi

if [[ "${JSON_OUT}" -eq 1 ]]; then
  python3 - \
    "${MODE}" "${DRY_RUN}" "${READY}" "${VENV_DIR}" \
    "${KICAD_CLI_PATH}" "${KICAD_PY_PATH}" "${JAVA_PATH}" "${FREEROUTING_PATH}" \
    "${DTC_PATH}" "${UV_PATH}" "${SHASUM_PATH}" \
    "${HAS_SKIDL}" "${HAS_SKIP}" "${HAS_BUILD123D}" "${HAS_CADQUERY}" "${HAS_TRIMESH}" "${HAS_ESPTOOL}" <<'PY'
import json
import sys

(
    mode, dry_run, ready, venv_dir,
    kicad_cli, kicad_py, java_bin, freerouting,
    dtc_bin, uv_bin, shasum_bin,
    has_skidl, has_skip, has_build123d, has_cadquery, has_trimesh, has_esptool
) = sys.argv[1:]

to_bool = lambda s: s == "true"

missing = []
if not kicad_cli:
    missing.append("kicad-cli")
if not java_bin:
    missing.append("java")
if not freerouting:
    missing.append("freerouting")
if not (to_bool(has_skidl) or to_bool(has_skip)):
    missing.append("skidl_or_kicad_skip")
if not (to_bool(has_build123d) or to_bool(has_cadquery)):
    missing.append("build123d_or_cadquery")

report = {
    "mode": mode,
    "dry_run": dry_run == "1",
    "ready_for_full_pipeline": to_bool(ready) and len(missing) == 0,
    "venv_dir": venv_dir,
    "binaries": {
        "kicad_cli": kicad_cli or None,
        "kicad_python_pcbnew": kicad_py or None,
        "java": java_bin or None,
        "freerouting": freerouting or None,
        "dtc": dtc_bin or None,
        "uv": uv_bin or None,
        "sha256_tool": shasum_bin or None,
    },
    "python_modules": {
        "skidl": to_bool(has_skidl),
        "kicad_skip": to_bool(has_skip),
        "build123d": to_bool(has_build123d),
        "cadquery": to_bool(has_cadquery),
        "trimesh": to_bool(has_trimesh),
        "esptool": to_bool(has_esptool),
    },
    "missing_components": missing,
    "install_hint": "bash scripts/bootstrap_env.sh --install" if missing else None,
}
print(json.dumps(report, indent=2))
PY
else
  echo "=== Autonomous Hardware Architect Toolchain Status ==="
  echo "  kicad-cli        : ${KICAD_CLI_PATH:-MISSING}"
  echo "  pcbnew python    : ${KICAD_PY_PATH:-MISSING}"
  echo "  java             : ${JAVA_PATH:-MISSING}"
  echo "  freerouting      : ${FREEROUTING_PATH:-MISSING}"
  echo "  dtc              : ${DTC_PATH:-MISSING}"
  echo "  sha256 utility   : ${SHASUM_PATH:-MISSING}"
  echo "  skidl            : ${HAS_SKIDL}"
  echo "  kicad-skip       : ${HAS_SKIP}"
  echo "  build123d        : ${HAS_BUILD123D}"
  echo "  cadquery         : ${HAS_CADQUERY}"
  echo "  trimesh          : ${HAS_TRIMESH}"
  echo "  esptool          : ${HAS_ESPTOOL}"
  echo "  Pipeline Ready   : ${READY}"
fi
