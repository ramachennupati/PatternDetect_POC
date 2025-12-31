import urllib.request
import os
os.makedirs('data', exist_ok=True)

urls = [
    ('https://ultralytics.com/images/zidane.jpg', 'data/sample1.jpg'),
    ('https://raw.githubusercontent.com/opencv/opencv/master/samples/data/opencv-logo.png', 'data/template.png')
]
for url, out in urls:
    print('Downloading', url)
    urllib.request.urlretrieve(url, out)
print('Done')
