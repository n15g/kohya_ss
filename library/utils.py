import math
import threading


def fire_in_thread(f, *args, **kwargs):
    threading.Thread(target=f, args=args, kwargs=kwargs).start()


def calculate_aspect_ratio(x: int, y: int) -> (int, int):
    """
    Calculate the aspect ratio for a given width and height
    https://gist.github.com/Integralist/4ca9ff94ea82b0e407f540540f1d8c6c?permalink_comment_id=3879989#gistcomment-3879989
    """
    r = math.gcd(x, y)
    x = int(x / r)
    y = int(y / r)
    return x, y
