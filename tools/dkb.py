from pathlib import Path
import subprocess
import sys


TOOLS = {
    "stats": "stats.py",
    "search": "search.py",
    "validate": "validate_dkb.py",
}


def usage():
    print("Dacia Knowledge Base")
    print()
    print("Usage:")
    print("  python tools/dkb.py stats")
    print("  python tools/dkb.py search <phrase>")
    print("  python tools/dkb.py validate")


def main():

    if len(sys.argv) < 2:
        usage()
        raise SystemExit(1)

    command = sys.argv[1]

    if command not in TOOLS:
        print(f"Unknown command: {command}")
        print()
        usage()
        raise SystemExit(1)

    script = Path(__file__).parent / TOOLS[command]

    subprocess.run(
        [sys.executable, str(script), *sys.argv[2:]],
        check=False,
    )


if __name__ == "__main__":
    main()
