#!/usr/bin/env python3
"""Refresh all installed git-sourced skills to their latest published versions."""
import subprocess
import sys

res = subprocess.run(["npx", "-y", "skills", "update", "-g"])
sys.exit(res.returncode)
