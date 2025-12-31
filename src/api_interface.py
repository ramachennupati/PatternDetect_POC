import streamlit as st
from api_client import PatternDetectClient
import io
from PIL import Image
import base64

st.set_page_config(page_title="API Interface — Truck PoC", layout="centered")
st.title("Truck Inspection — REST API Interface")

base_url = st.text_input("API base URL", value="http://localhost:8000")

client = PatternDetectClient(base_url.rstrip("/"))

with st.form("detect_form"):
    uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"]) 
    conf = st.slider("Confidence threshold", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    endpoint = st.radio("Endpoint", options=["/detect (JSON + base64)", "/detect/image (raw JPEG)"])
    submit = st.form_submit_button("Run")

if submit:
    if not uploaded:
        st.warning("Please upload an image file")
    else:
        img_bytes = uploaded.read()
        if endpoint.startswith("/detect/image"):
            try:
                out_bytes = client.detect_image_bytes(file_bytes=img_bytes, filename=uploaded.name, conf=conf)
                st.image(out_bytes, caption="Annotated image (from API)")
            except Exception as e:
                st.error(f"API error: {e}")
        else:
            try:
                data = client.detect(file_bytes=img_bytes, filename=uploaded.name, conf=conf, annotated=True)
                st.subheader("Detections (JSON)")
                st.json(data.get("detections", []))
                b64 = data.get("annotated_image_base64")
                if b64:
                    img = base64.b64decode(b64)
                    st.image(img, caption="Annotated image (from API)")
            except Exception as e:
                st.error(f"API error: {e}")

st.markdown("---")
st.markdown("**Tips:** Ensure the API is running (e.g. `uvicorn src.api:app --host 0.0.0.0 --port 8000`) before using this interface.")
