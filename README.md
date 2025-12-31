# Truck Inspection PoC (YOLOv8 + OpenCV)

Quick Proof-of-Concept to run object detection (Ultralytics YOLO) and template matching (OpenCV).

## Quick start (Windows PowerShell)

1. Open PowerShell in the project folder:
```powershell
cd 'c:\Users\kisho\OneDrive\Desktop\truck-inspection-poc'
```

2. Run the setup script (this creates a venv, installs packages, and downloads sample images):
```powershell
.\setup.ps1
```

3. Activate the venv:
```powershell
. .\.venv\Scripts\Activate.ps1
```

4. Run detection:
```powershell
python src\detect.py --source data/sample1.jpg --output outputs/detect_out.jpg
```

5. Run the Streamlit web UI (uploads + detection):
```powershell
streamlit run src/web_app.py
```

6. Run template matching (uses `data/template.png` vs `data/sample1.jpg` as example):
```powershell
python src\template_match.py --image data/sample1.jpg --template data/template.png --output outputs/template_out.jpg
```


-- Training (quick PoC)

1. Create dataset directories and copy or add images to `data/dataset/images/train` and `data/dataset/images/val`.
2. Auto-annotate images using the pretrained model (creates YOLO `.txt` label files):
```powershell
python src\auto_annotate.py --images data/dataset/images/train --labels data/dataset/labels/train
python src\auto_annotate.py --images data/dataset/images/val --labels data/dataset/labels/val
```
4. Optionally augment the train set (horizontal flip example), then copy augmented images into the train folder or update `dataset.yaml` to include them:
```powershell
python src\augment_flip.py --src data/dataset/images/train --labels data/dataset/labels/train
# this creates data/dataset/images/train_flip and data/dataset/labels/train_flip
# copy augmented files into the train folder if desired
copy data\dataset\images\train_flip\* data\dataset\images\train\
copy data\dataset\labels\train_flip\* data\dataset\labels\train\
```
5. Edit `data/dataset/dataset.yaml` if needed (it defaults to the sample paths already present).
6. Run a longer training job (example: 3 epochs on CPU; use `--name` to identify run):
```powershell
python src\train.py --data data/dataset/dataset.yaml --epochs 3 --device cpu --name train3
```
7. Evaluate the trained model using a simple TP/FP/FN script (saves `outputs/eval.csv`):
```powershell
python src\evaluate.py --model runs/detect/train3/weights/best.pt --images data/dataset/images/val --labels data/dataset/labels/val --out outputs/eval_train3.csv
```

Notes:
- For a real dataset, annotate images carefully (tools: Roboflow, LabelImg, makeSense.ai). Replace `.txt` labels following YOLO format.
- After training, check `runs/detect/` for generated training runs and exported models.

## Files
- `src/detect.py` — runs YOLOv8 detection and saves a plotted/annotated image.
- `src/template_match.py` — simple OpenCV template matching demo and draws rectangle for best match.
- `setup.ps1` — creates venv and installs dependencies and downloads sample images.

## Notes
- `ultralytics` will download a pre-trained `yolov8n` model the first time it runs.
- For production or edge deployment, replace with optimized builds (ONNX/TensorRT/OpenVINO) and use a curated dataset.

## Release & Docker image
This repository includes a workflow that builds and publishes a Docker image when you push a semantic tag (for example `v0.1.0`). The workflow is located at `.github/workflows/release-and-docker.yml` and will:

- Build the Docker image with Buildx
- Push the image to Docker Hub at `docker.io/<DOCKERHUB_USERNAME>/patterndetect_poc:<tag>` and also tag `latest`
- Create a GitHub Release for the tag

Before pushing a tag, add the following repository secrets (Settings → Secrets → Actions):
- `DOCKERHUB_USERNAME`: your Docker Hub username
- `DOCKERHUB_TOKEN`: a Docker Hub access token (or password)

To create a release and trigger the workflow:
```bash
# create and push a tag
git tag v0.1.0
git push origin v0.1.0
```

