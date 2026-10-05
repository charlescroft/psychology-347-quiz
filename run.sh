#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${SCRIPT_DIR}/.venv/bin/python"

if [ ! -f "${VENV_PYTHON}" ]; then
    echo "[!] Virtualenv python not found at ${VENV_PYTHON}. Using system python3..."
    PYTHON_CMD="python3"
else
    PYTHON_CMD="${VENV_PYTHON}"
fi

export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
exec "${PYTHON_CMD}" "${SCRIPT_DIR}/main.py" "$@"
