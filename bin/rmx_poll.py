import sys
from pathlib import Path, PurePosixPath
import subprocess

symbols = list("@.-_")
alpha = list("abcdefghijklmnopqrstuvwxyz")
number = list("0123456789")
__dirname = PurePosixPath(Path(__file__).parent.resolve())


def populate_patterns(target: str):
    second_pool = alpha + number

    base = PurePosixPath(target)

    return [str(base / f"{s}{c}*") for s in symbols for c in second_pool]


def spawn_rmx(paths: list[str]):
    # Break the 1,440 paths into smaller groups of 50 paths each
    batch_size = 50

    print(f"Total paths to process: {len(paths)}")

    for i in range(0, len(paths), batch_size):
        batch = paths[i:i + batch_size]

        # Build the command for just this small group
        cmd = [sys.executable, f"{__dirname}/rmx.py"] + batch

        current_batch_num = (i // batch_size) + 1
        total_batches = (len(paths) + batch_size - 1) // batch_size
        print(f"Running batch {current_batch_num}/{total_batches}...")

        # Run the smaller command safely
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Show output if there is any
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

def main():
    targets = sys.argv[1:]

    if not targets:
        print("Usage: python script.py <target1> <target2> ...")
        sys.exit(1)

    result = []
    for t in targets:
        fp_path = Path(t)
        if fp_path.is_dir():
            for item in fp_path.iterdir():
                if "node_modules" in str(item):
                    result.extend(populate_patterns(str(item)))
        result.extend(populate_patterns(t))
    spawn_rmx(result)


if __name__ == "__main__":
    main()
