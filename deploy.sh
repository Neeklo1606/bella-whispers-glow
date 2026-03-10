#!/bin/bash
# Wrapper: runs deployment/deploy.sh
# Ensures git-tracked deploy script is always used
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/deployment/deploy.sh"
