import base64
from typing import Optional
import httpx


class PatternDetectClient:
    """Simple synchronous client for the Truck Inspection API."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.base = base_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout)

    def health(self) -> dict:
        resp = self.client.get(f"{self.base}/health")
        resp.raise_for_status()
        return resp.json()

    def detect(self, file_path: Optional[str] = None, file_bytes: Optional[bytes] = None, filename: str = "image.jpg", conf: float = 0.25, annotated: bool = True) -> dict:
        """POST /detect — returns JSON with detections and optionally base64 annotated image."""
        if file_path is None and file_bytes is None:
            raise ValueError("Provide file_path or file_bytes")

        files = None
        if file_path:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f, "image/jpeg")}
                params = {"conf": conf, "annotated": str(annotated).lower()}
                resp = self.client.post(f"{self.base}/detect", files=files, params=params)
        else:
            files = {"file": (filename, file_bytes, "image/jpeg")}
            params = {"conf": conf, "annotated": str(annotated).lower()}
            resp = self.client.post(f"{self.base}/detect", files=files, params=params)

        resp.raise_for_status()
        return resp.json()

    def detect_and_save_annotated(self, out_path: str, **kwargs) -> dict:
        """Call detect() and save the returned annotated image (if present) to out_path."""
        data = self.detect(**kwargs)
        b64 = data.get("annotated_image_base64")
        if b64:
            img = base64.b64decode(b64)
            with open(out_path, "wb") as f:
                f.write(img)
        return data

    def detect_image_bytes(self, file_path: Optional[str] = None, file_bytes: Optional[bytes] = None, filename: str = "image.jpg", conf: float = 0.25) -> bytes:
        """POST /detect/image — returns raw JPEG bytes (annotated)."""
        if file_path is None and file_bytes is None:
            raise ValueError("Provide file_path or file_bytes")

        if file_path:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f, "image/jpeg")}
                resp = self.client.post(f"{self.base}/detect/image", files=files, params={"conf": conf})
        else:
            files = {"file": (filename, file_bytes, "image/jpeg")}
            resp = self.client.post(f"{self.base}/detect/image", files=files, params={"conf": conf})

        resp.raise_for_status()
        return resp.content

    def close(self):
        self.client.close()


# Convenience: context manager support
class _ClientCtx:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = PatternDetectClient(base_url)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc, tb):
        self.client.close()


def client_ctx(base_url: str = "http://localhost:8000"):
    return _ClientCtx(base_url)
