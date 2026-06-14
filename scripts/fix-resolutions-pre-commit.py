#!/usr/bin/env python3
import json
import os
import sys

def main():
    # Paths relative to root where the pre-commit runs
    pkg_path = 'package.json'
    res_path = 'package-resolutions.json'
    
    if not os.path.exists(res_path):
        print(f"[fix-resolutions] {res_path} not found, skipping.")
        return

    try:
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
        
        with open(res_path, 'r', encoding='utf-8') as f:
            res = json.load(f)
            
        if 'resolutions' not in pkg:
            pkg['resolutions'] = {}
            
        # Object.assign(package.json['resolutions'], package-resolutions.json)
        pkg['resolutions'].update(res)
        
        with open(pkg_path, 'w', encoding='utf-8') as f:
            json.dump(pkg, f, indent=2, ensure_ascii=False)
            f.write('\n')
            
        print(f"[fix-resolutions] Successfully merged {res_path} into {pkg_path}")
    except Exception as e:
        print(f"[fix-resolutions] Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
