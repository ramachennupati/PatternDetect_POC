from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import tempfile
import os
import base64
from typing import List

app = FastAPI(title='Truck Inspection API')

# Allow cross-origin requests for simple browser demo (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = 'yolov8n.pt'
model = None


@app.on_event('startup')
def startup_event():
    global model
    model = YOLO(MODEL_PATH)  # loads / downloads model on first run


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/detect')
async def detect(file: UploadFile = File(...), conf: float = 0.25, annotated: bool = True):
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=400, detail='file must be an image')

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        tmp_path = tmp.name

    # Run prediction
    results = model.predict(source=tmp_path, conf=conf, save=False)
    r = results[0]

    # Build JSON response
    detections = []
    for box in r.boxes:
        xyxy = box.xyxy[0].tolist()
        detections.append({'xyxy': [round(float(x), 2) for x in xyxy], 'conf': float(box.conf[0]), 'cls': int(box.cls[0])})

    response = {'detections': detections}

    if annotated:
        annotated_img = r.plot()  # RGB
        # encode to JPEG bytes
        annotated_bgr = cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR)
        _, img_bytes = cv2.imencode('.jpg', annotated_bgr)
        b64 = base64.b64encode(img_bytes.tobytes()).decode('ascii')
        response['annotated_image_base64'] = b64

    # cleanup
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return JSONResponse(response)


@app.post('/detect/image')
async def detect_return_image(file: UploadFile = File(...), conf: float = 0.25):
    """Returns annotated image bytes (image/jpeg) so it can be displayed directly."""
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=400, detail='file must be an image')

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        tmp_path = tmp.name

    results = model.predict(source=tmp_path, conf=conf, save=False)
    r = results[0]
    annotated_img = r.plot()
    annotated_bgr = cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR)
    _, img_bytes = cv2.imencode('.jpg', annotated_bgr)

    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return StreamingResponse(iter([img_bytes.tobytes()]), media_type='image/jpeg')
