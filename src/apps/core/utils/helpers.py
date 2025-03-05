import datetime


def get_trajectory_points(trajectory):
    if not trajectory:
        return []

    points = []
    for entry in trajectory:
        box = entry['box']
        x = box['x']
        y = box['y']
        w = box.get('w') or box.get('width')
        h = box.get('h') or box.get('height')
        points.append([x + w / 2, y + h])
    return points


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)
