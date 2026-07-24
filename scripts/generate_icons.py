import struct
import zlib
import os
import math

def create_png(width, height, pixels_func):
    def make_chunk(chunk_type, data):
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xffffffff
        return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)

    # Build raw IDAT rows
    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter byte
        for x in range(width):
            r, g, b, a = pixels_func(x, y, width, height)
            raw += struct.pack('BBBB', r, g, b, a)

    compressed = zlib.compress(raw)

    png = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png += make_chunk(b'IHDR', ihdr)
    png += make_chunk(b'IDAT', compressed)
    png += make_chunk(b'IEND', b'')
    return png


def generate_launcher_icon(size):
    cx = cy = (size - 1) / 2.0
    radius = (size // 2) - 1

    def pixel(x, y, w, h):
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > radius:
            return (0, 0, 0, 0)
        return (33, 150, 243, 255)

    return create_png(size, size, pixel)


def generate_circle_with_jc(size):
    cx = cy = (size - 1) / 2.0
    radius = size // 2 - 2
    inner_radius = size // 2 - 4

    # Simple JC rendering as pixel blocks
    # For small sizes, just draw the circle
    def pixel(x, y, w, h):
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > radius:
            return (0, 0, 0, 0)
        if dist > inner_radius:
            return (33, 150, 243, 255)

        # Draw "JC" as simple block letters using pixel regions
        third = size / 3
        half = size / 2

        # J region: left third, bottom half
        if x < third and y > half:
            return (255, 255, 255, 255)

        # C region: right two-thirds, centered
        if x > third and abs(y - half) < size / 6:
            return (255, 255, 255, 255)

        return (33, 150, 243, 255)

    return create_png(size, size, pixel)


if __name__ == '__main__':
    sizes = {
        'mdpi': 48,
        'hdpi': 72,
        'xhdpi': 96,
        'xxhdpi': 144,
        'xxxhdpi': 192,
    }
    base = r'C:\Users\sachi\Music\prakash sir\JOBCARE\jobcare_voice\frontend_mobile\android\app\src\main\res'
    for density, size in sizes.items():
        png_data = generate_circle_with_jc(size)
        path = os.path.join(base, f'mipmap-{density}', 'ic_launcher.png')
        with open(path, 'wb') as f:
            f.write(png_data)
        print(f'Created {path}')
        round_path = os.path.join(base, f'mipmap-{density}', 'ic_launcher_round.png')
        with open(round_path, 'wb') as f:
            f.write(png_data)
        print(f'Created {round_path}')
