from PIL import Image, ImageDraw, ImageFilter
import math
import os

SIZE = 1024
SCALE = 4  # supersample for smooth edges, then downscale

S = SIZE * SCALE
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

center = S / 2
corner_radius = S * 0.22

# --- Background: radial-ish gradient via concentric rounded squares ---
import numpy as np

# --- Background: smooth radial gradient, light source upper-left ---
light_color = np.array([42, 36, 52])    # lighter aubergine highlight
dark_color = np.array([14, 12, 18])     # deep aubergine shadow

yy, xx = np.mgrid[0:S, 0:S]
light_x, light_y = S * 0.32, S * 0.28  # light source position
dist = np.sqrt((xx - light_x) ** 2 + (yy - light_y) ** 2)
max_dist = np.sqrt(S ** 2 + S ** 2) * 0.62
t = np.clip(dist / max_dist, 0, 1)[..., None]  # 0 near light, 1 far away

gradient = (light_color * (1 - t) + dark_color * t).astype(np.uint8)
alpha = np.full((S, S, 1), 255, dtype=np.uint8)
gradient_rgba = np.concatenate([gradient, alpha], axis=-1)

bg = Image.fromarray(gradient_rgba, mode="RGBA")

# Clip to rounded square
mask = Image.new("L", (S, S), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([(0, 0), (S, S)], radius=corner_radius, fill=255)
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
img.paste(bg, (0, 0), mask)
draw = ImageDraw.Draw(img)

# --- Soft inner glow behind the ring (depth) ---
glow_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow_layer)
glow_r = S * 0.30
glow_draw.ellipse(
    [center - glow_r, center - glow_r, center + glow_r, center + glow_r],
    fill=(232, 163, 61, 90)
)
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(S * 0.04))
img = Image.alpha_composite(img, glow_layer)
draw = ImageDraw.Draw(img)

# --- Ring track (dim) ---
ring_r = S * 0.27
ring_stroke = int(S * 0.045)
draw.arc(
    [center - ring_r, center - ring_r, center + ring_r, center + ring_r],
    0, 360, fill=(60, 54, 72, 255), width=ring_stroke
)

# --- Ring fill (amber, ~70% progress, rounded caps via overlaid circles) ---
progress_degrees = 252  # 70% of 360
start_angle = -90
end_angle = start_angle + progress_degrees

amber = (232, 163, 61, 255)
amber_light = (245, 200, 130, 255)

# Draw the arc in amber
draw.arc(
    [center - ring_r, center - ring_r, center + ring_r, center + ring_r],
    start_angle, end_angle, fill=amber, width=ring_stroke
)

# Rounded cap at the start of the arc
cap_r = ring_stroke / 2
start_rad = math.radians(start_angle)
cap_x = center + ring_r * math.cos(start_rad)
cap_y = center + ring_r * math.sin(start_rad)
draw.ellipse(
    [cap_x - cap_r, cap_y - cap_r, cap_x + cap_r, cap_y + cap_r], fill=amber
)

# Rounded cap (bright) at the end of the arc — the "current moment"
end_rad = math.radians(end_angle)
cap_x = center + ring_r * math.cos(end_rad)
cap_y = center + ring_r * math.sin(end_rad)
draw.ellipse(
    [cap_x - cap_r * 1.3, cap_y - cap_r * 1.3, cap_x + cap_r * 1.3, cap_y + cap_r * 1.3],
    fill=amber_light
)

# --- Clock hands in the center (small, minimal) ---
hand_color = (242, 239, 233, 255)  # off-white
hour_angle = math.radians(60 - 90)
hour_len = ring_r * 0.42
draw.line(
    [center, center,
     center + hour_len * math.cos(hour_angle),
     center + hour_len * math.sin(hour_angle)],
    fill=hand_color, width=int(S * 0.018)
)

minute_angle = math.radians(-90)
minute_len = ring_r * 0.62
draw.line(
    [center, center,
     center + minute_len * math.cos(minute_angle),
     center + minute_len * math.sin(minute_angle)],
    fill=hand_color, width=int(S * 0.018)
)

center_dot_r = S * 0.016
draw.ellipse(
    [center - center_dot_r, center - center_dot_r,
     center + center_dot_r, center + center_dot_r],
    fill=hand_color
)

# --- Downscale for clean anti-aliasing ---
img = img.resize((SIZE, SIZE), Image.LANCZOS)

os.makedirs("assets", exist_ok=True)
img.save("assets/icon_1024.png")
print("Saved assets/icon_1024.png")