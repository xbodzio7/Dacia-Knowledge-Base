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
    print()
    print("Commands:")
    for command in sorted(TOOLS):
        print(f"  {command}")
    print("  help")


def main():

    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        usage()
        return

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
