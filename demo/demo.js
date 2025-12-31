async function postDetect(formData, base, endpoint, conf) {
  const url = base + (endpoint === 'detect' ? '/detect' : '/detect/image') + `?conf=${encodeURIComponent(conf)}`;
  const resp = await fetch(url, { method: 'POST', body: formData });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
  }
  return resp;
}

function b64ToBlob(b64, mime) {
  const byteChars = atob(b64);
  const byteNumbers = new Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) {
    byteNumbers[i] = byteChars.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mime });
}

document.getElementById('run').addEventListener('click', async () => {
  const base = document.getElementById('baseUrl').value.replace(/\/$/, '');
  const fileEl = document.getElementById('file');
  const endpoint = document.getElementById('endpoint').value;
  const conf = document.getElementById('conf').value;
  const status = document.getElementById('status');
  const jsonOut = document.getElementById('jsonOut');
  const imgOut = document.getElementById('imgOut');

  status.textContent = '';
  jsonOut.textContent = '';
  imgOut.innerHTML = '';

  if (!fileEl.files || fileEl.files.length === 0) {
    status.textContent = 'Please choose an image file.';
    return;
  }

  const file = fileEl.files[0];
  const fd = new FormData();
  fd.append('file', file, file.name);

  try {
    status.textContent = 'Calling API...';
    const resp = await postDetect(fd, base, endpoint, conf);

    if (endpoint === 'detect') {
      const data = await resp.json();
      jsonOut.textContent = JSON.stringify(data.detections || data, null, 2);
      if (data.annotated_image_base64) {
        const blob = b64ToBlob(data.annotated_image_base64, 'image/jpeg');
        const url = URL.createObjectURL(blob);
        const img = document.createElement('img');
        img.src = url;
        img.alt = 'Annotated';
        img.style.maxWidth = '600px';
        imgOut.appendChild(img);
      }
      status.textContent = 'Done.';
    } else {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const img = document.createElement('img');
      img.src = url;
      img.alt = 'Annotated';
      img.style.maxWidth = '600px';
      imgOut.appendChild(img);
      status.textContent = 'Done.';
    }
  } catch (err) {
    status.textContent = 'Error: ' + err.message;
    console.error(err);
  }
});