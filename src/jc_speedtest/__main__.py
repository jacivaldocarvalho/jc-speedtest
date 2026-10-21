"""Allow `python -m jc_speedtest` execution."""

from jc_speedtest.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
