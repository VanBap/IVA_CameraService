import os
from utils.video_utils import extract_thumbnail

def capture_camera_snapshot(camera_id, url):
    snapshot_dir = '/home/vbd-vanhk-l1-ubuntu/work/'
    os.makedirs(snapshot_dir, exist_ok=True)
    snapshot_path = os.path.join(snapshot_dir, f'camera_{camera_id}_snapshot.jpg')

    # Store the simulating snapshot image
    extract_thumbnail(url, snapshot_path)
    return snapshot_path
