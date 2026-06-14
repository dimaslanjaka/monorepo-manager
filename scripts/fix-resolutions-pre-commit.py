#!/usr/bin/env python3
import json
import os
import sys
import shutil
import subprocess

def main():
    # Paths relative to root where the pre-commit runs
    pkg_path = 'package.json'
    res_path = 'package-resolutions.json'
    tmp_path = 'tmp/package.json'

    if not os.path.exists(res_path):
        print(f"[fix-resolutions] {res_path} not found, skipping.")
        return

    try:
        # Ensure tmp directory exists
        os.makedirs('tmp', exist_ok=True)

        # 1. Backup original package.json to tmp/package.json
        shutil.copy2(pkg_path, tmp_path)

        # 2. Read and modify resolutions
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)

        with open(res_path, 'r', encoding='utf-8') as f:
            res = json.load(f)

        if 'resolutions' not in pkg:
            pkg['resolutions'] = {}

        # Object.assign(package.json['resolutions'], package-resolutions.json)
        pkg['resolutions'].update(res)

        with open(pkg_path, 'w', encoding='utf-8', newline='') as f:
            json.dump(pkg, f, indent=2, ensure_ascii=False)
            f.write('\n')

        # 3. Git add package.json
        subprocess.run(['git', 'add', pkg_path], check=True, capture_output=True)

        # 4. Restore tmp/package.json to package.json
        shutil.copy2(tmp_path, pkg_path)

        print(f"[fix-resolutions] Successfully merged {res_path} into {pkg_path} and staged for commit")
    except Exception as e:
        print(f"[fix-resolutions] Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

