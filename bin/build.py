import json
import shutil
import subprocess
import sys
import argparse
from pathlib import Path

RELEASES_DIR = Path("releases")
LOGS_DIR = Path("tmp/logs")
PACKAGES_TO_CHECK = [
    "binary-collections",
    "ai-toolkit",
    "eslint-base-config",
    "opencode-plugin-memory",
]

WORKSPACE_PACKAGE_ALIASES = {
    "binary-collections": "binary-collections",
    "ai-toolkit": "@dimaslanjaka/ai-toolkit",
    "eslint-base-config": "@dimaslanjaka/eslint-base-config",
    "cross-spawn": "cross-spawn",
    "git-command-helper": "git-command-helper",
    "openai-local": "anti-api",
    "opencode-plugin-memory": "opencode-agent-memory",
}

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_command_with_log(cmd, cwd=None, log_file=None):
    """Run command and also write output to log file."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    log_path = LOGS_DIR / f"{log_file}.log"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Command: {cmd}\n")
        f.write(f"CWD: {cwd}\n")
        f.write(f"Exit code: {result.returncode}\n")
        f.write("=" * 50 + "\n")
        f.write("STDOUT:\n")
        f.write(result.stdout or "")
        if result.stderr:
            f.write("\nSTDERR:\n")
            f.write(result.stderr or "")

    print(f"Log: {log_path}")

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0

def ensure_releases_dir():
    if not RELEASES_DIR.exists():
        RELEASES_DIR.mkdir(parents=True)
        print(f"Created {RELEASES_DIR} directory")

def clean_old_tarballs():
    # Skip cleaning - preserve existing tarballs
    pass

def build_packages(do_clean=False, package_name=None):
    packages_dir = Path("packages")
    if not packages_dir.exists():
        print("No packages directory found")
        return []

    built_packages = []

    # If a specific package is requested, find it
    if package_name:
        pkg_path = packages_dir / package_name
        if not pkg_path.exists():
            print(f"Error: Package directory not found: {pkg_path}")
            return []
        pkg_paths = [pkg_path]
    else:
        pkg_paths = sorted(packages_dir.iterdir())

    for pkg_path in pkg_paths:
        if not pkg_path.is_dir():
            continue

        pkg_json_path = pkg_path / "package.json"
        if not pkg_json_path.exists():
            continue

        # Read package name from package.json, not folder name
        with open(pkg_json_path, "r", encoding="utf-8") as f:
            pkg_meta = json.load(f)
        pkg_name = pkg_meta.get("name")
        if not pkg_name:
            print(f"Warning: {pkg_path.name}/package.json has no 'name' field, skipping...")
            continue

        print(f"\nProcessing: {pkg_path.name} -> {pkg_name}")
        print("-" * 40)

        if do_clean:
            run_command("npm run clean", cwd=pkg_path)
        success = run_command_with_log("npm run build", cwd=pkg_path, log_file=pkg_path.name)

        if not success:
            print(f"Build failed for {pkg_name}, skipping...")
            continue

        run_command("yarn pack", cwd=pkg_path)

        # yarn pack creates package.tgz in the package directory
        source_tgz = pkg_path / "package.tgz"
        dest_tgz = RELEASES_DIR / f"{pkg_name}.tgz"

        if source_tgz.exists():
            # Ensure parent directory exists (for scoped package names like @scope/name)
            dest_tgz.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_tgz, dest_tgz)
            source_tgz.unlink()  # Remove the original
            built_packages.append(pkg_name)
            print(f"Created: {dest_tgz}")
        else:
            print(f"Warning: Tarball not created at {source_tgz}")

    return built_packages

def _find_tarball_path(pkg_name):
    """Find existing tarball path with fallback logic."""
    releases_tgz = RELEASES_DIR / f"{pkg_name}.tgz"
    if releases_tgz.exists():
        return f"file:./releases/{pkg_name}.tgz"

    # Fallback: check packages/*/release*/<pkg_name>.tgz
    # Use name-based glob to handle scopes correctly
    pkg_simple_name = pkg_name.split('/')[-1]
    root = Path(".")
    for sub in root.glob(f"packages/*/release*/{pkg_simple_name}.tgz"):
        return f"file:./{sub.relative_to('.')}".replace("\\", "/")

    return None

def update_package_json():
    package_json_path = Path("package.json")
    if not package_json_path.exists():
        print("Root package.json not found")
        return

    with open(package_json_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    resolutions = pkg.get("resolutions", {}) if "resolutions" in pkg else {}
    if "resolutions" not in pkg:
        pkg["resolutions"] = resolutions

    for pkg_name in PACKAGES_TO_CHECK:
        alias = WORKSPACE_PACKAGE_ALIASES.get(pkg_name, pkg_name)

        if alias in resolutions:
            # Get actual package name from pkg json to match tarball filename
            # This requires reading package.json again or looking it up
            # For simplicity, look for package.json in packages/
            pkg_meta_path = Path("packages") / pkg_name / "package.json"
            if pkg_meta_path.exists():
                with open(pkg_meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    actual_name = meta.get("name")

                    path = _find_tarball_path(actual_name)
                    if path:
                        resolutions[alias] = path
                        print(f"Updated {alias} -> {path}")
                    else:
                        print(f"Skipped {alias}: no tarball found for {actual_name}")
            else:
                print(f"Skipped {alias}: package meta not found")

    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main():
    parser = argparse.ArgumentParser(description="Build and release script")
    parser.add_argument("package", nargs="?", help="Optional: specific package name to build (e.g., binary-collections)")
    parser.add_argument("--clean", action="store_true", help="Run 'npm run clean' before building")
    args = parser.parse_args()

    print("=" * 50)
    if args.package:
        print(f"Build Script: {args.package}")
    else:
        print("Build and Release Script")
    print("=" * 50)

    ensure_releases_dir()
    clean_old_tarballs()
    built_packages = build_packages(do_clean=args.clean, package_name=args.package)

    print("\n" + "=" * 50)
    print("Done! Tarballs collected in releases:")
    if built_packages:
        for name in built_packages:
            print(f"  - {name}")
    else:
        print("  No tarballs found.")

    update_package_json()

    print("\n" + "=" * 50)
    print("Final resolutions in package.json:")
    print("=" * 50)

if __name__ == "__main__":
    main()