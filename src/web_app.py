import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import tempfile
import os

MODEL_PATH = 'yolov8n.pt'  # will be downloaded by ultralytics if missing

@st.cache_resource
def load_model():
    return YOLO(MODEL_PATH)

st.title('Truck Inspection — Detection PoC')
st.markdown('Upload an image (or use sample) to run YOLOv8 detection and show annotated output.')

model = load_model()

use_sample = st.checkbox('Use sample image (data/sample1.jpg)', value=True)
uploaded_file = st.file_uploader('Upload image', type=['jpg', 'jpeg', 'png'])

image_path = None
if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    tfile.write(uploaded_file.getbuffer())
    image_path = tfile.name
elif use_sample:
    image_path = 'data/sample1.jpg'
else:
    st.info('Upload an image or select the sample image.')

if image_path:
    st.image(image_path, caption='Input image', use_column_width=True)

    st.write('Running detection...')
    results = model.predict(source=image_path, conf=0.25, save=False)
    r = results[0]
    annotated = r.plot()  # RGB array

    st.image(annotated, caption='Annotated', use_column_width=True)

    # show table of detections
    boxes = []
    for box in r.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        boxes.append({'class': cls, 'conf': round(conf, 3), 'xyxy': [round(x, 2) for x in xyxy]})

    if boxes:
        st.subheader('Detections')
        st.table(boxes)
    else:
        st.write('No detections above the confidence threshold.')

st.markdown('---')
st.write('Tip: run `streamlit run src/web_app.py` in the project venv to start the UI')
