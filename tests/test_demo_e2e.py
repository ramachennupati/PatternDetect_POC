import subprocess
import time
import sys
import shutil
import pytest

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


def start_proc(cmd, cwd=None):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)


def wait_for_port(host, port, timeout=15.0):
    import socket
    import time as _time
    start = _time.time()
    while _time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            _time.sleep(0.2)
    return False


@pytest.mark.skipif(sync_playwright is None, reason="playwright not installed - install via 'pip install playwright' and run 'playwright install chromium'")
def test_demo_e2e():
    """End-to-end smoke test: start API + static demo, open demo in headless browser, upload image, assert annotated image appears."""
    api_port = 8003
    demo_port = 8004

    # Start API server and static demo server
    api_cmd = [sys.executable, "-m", "uvicorn", "src.api:app", "--host", "127.0.0.1", "--port", str(api_port)]
    demo_cmd = [sys.executable, "-m", "http.server", str(demo_port), "--directory", "demo"]

    api_proc = start_proc(api_cmd)
    demo_proc = start_proc(demo_cmd)

    try:
        assert wait_for_port("127.0.0.1", api_port, timeout=20), "API did not start"
        assert wait_for_port("127.0.0.1", demo_port, timeout=5), "Demo server did not start"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{demo_port}")
            page.fill("#baseUrl", f"http://127.0.0.1:{api_port}")

            # upload sample image
            page.set_input_files('#file', 'data/sample1.jpg')
            page.click('#run')

            # wait for annotated image to appear
            page.wait_for_selector('#imgOut img', timeout=20000)
            img = page.query_selector('#imgOut img')
            assert img is not None

            browser.close()

    finally:
        # cleanup
        if api_proc.poll() is None:
            api_proc.terminate()
            try:
                api_proc.wait(timeout=3)
            except Exception:
                api_proc.kill()
        if demo_proc.poll() is None:
            demo_proc.terminate()
            try:
                demo_proc.wait(timeout=3)
            except Exception:
                demo_proc.kill()
