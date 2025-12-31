import os
import shutil
import subprocess
import sys

"""Pytest conftest to ensure sample images exist before tests run.
If `data/samples` is empty or missing, invoke `scripts/generate_samples.py`.
Also ensures `data/sample1.jpg` exists (some tests expect that path).
"""


def pytest_sessionstart(session):
    out_dir = os.path.join("data", "samples")
    if not os.path.exists(out_dir) or not os.listdir(out_dir):
        cmd = [sys.executable, "scripts/generate_samples.py", "--out", out_dir, "--count", "3"]
        print("Generating sample images for tests...", file=sys.stderr)
        subprocess.check_call(cmd)

    src = os.path.join(out_dir, "sample1.jpg")
    dst = os.path.join("data", "sample1.jpg")
    # copy sample1 into data/sample1.jpg if a top-level sample isn't present
    if not os.path.exists(dst) and os.path.exists(src):
        shutil.copy(src, dst)
