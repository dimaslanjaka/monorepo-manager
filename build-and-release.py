import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RELEASES_DIR = Path("releases")
LOGS_DIR = Path("tmp/logs")
PACKAGES_TO_CHECK = [
    "binary-collections",
    "ai-toolkit",
    "eslint-base-config",
    "cross-spawn",
    "git-command-helper",
    "openai-local",
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
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_command_with_log(cmd, cwd=None, log_file=None):
    """Run command and also write output to log file."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"{log_file}_{timestamp}.log"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Command: {cmd}\n")
        f.write(f"CWD: {cwd}\n")
        f.write(f"Exit code: {result.returncode}\n")
        f.write("=" * 50 + "\n")
        f.write("STDOUT:\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
    
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

def build_packages():
    packages_dir = Path("packages")
    if not packages_dir.exists():
        print("No packages directory found")
        return []

    built_packages = []

    for pkg_path in sorted(packages_dir.iterdir()):
        if not pkg_path.is_dir():
            continue

        package_json = pkg_path / "package.json"
        if not package_json.exists():
            continue

        print(f"\nProcessing: {pkg_path.name}")
        print("-" * 40)

        run_command("yarn clean", cwd=pkg_path)
        success = run_command_with_log("yarn build", cwd=pkg_path, log_file=pkg_path.name)
        
        if not success:
            print(f"Build failed for {pkg_path.name}, skipping...")
            continue

        run_command("yarn pack", cwd=pkg_path)

        # yarn pack creates package.tgz in the package directory
        source_tgz = pkg_path / "package.tgz"
        dest_tgz = RELEASES_DIR / f"{pkg_path.name}.tgz"

        if source_tgz.exists():
            shutil.copy2(source_tgz, dest_tgz)
            source_tgz.unlink()  # Remove the original
            built_packages.append(pkg_path.name)
            print(f"Created: {dest_tgz}")
        else:
            print(f"Warning: Tarball not created at {source_tgz}")

    return built_packages

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
        tarball = RELEASES_DIR / f"{pkg_name}.tgz"
        tarball_ref = f"file:./releases/{pkg_name}.tgz"
        workspace_ref = "workspace:^"

        if alias in resolutions:
            if tarball.exists():
                resolutions[alias] = tarball_ref
                print(f"Updated {alias} -> {tarball_ref}")
            else:
                resolutions[alias] = workspace_ref
                print(f"Reset {alias} -> {workspace_ref}")

    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main():
    print("=" * 50)
    print("Build and Release Script")
    print("=" * 50)

    ensure_releases_dir()
    clean_old_tarballs()
    built_packages = build_packages()

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