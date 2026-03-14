import cv2
import numpy as np
import mediapipe as mp
import math
import time
import threading

# Try to import Windows sound library (optional feature)
try:
    import winsound
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


# ------------------------------
# Configuration settings
# ------------------------------
class Config:
    WIDTH, HEIGHT = 1280, 720

    # Sensitivity settings
    PINCH_THRESHOLD = 40       # Distance required to start drawing
    SMOOTHING = 0.6            # Lower = smoother but laggy, Higher = faster but jittery

    # Visual settings
    BRUSH_SIZE = 8
    NEON_GLOW = True
    HUD_COLOR = (255, 255, 0)  # Cyan color for HUD elements

    # Square palette settings
    SWATCH_SIZE = 60           # Width and height of each color swatch
    SWATCH_GAP = 8             # Gap between swatches
    PALETTE_NUM = 7            # Number of swatches (must match SquarePalette.colors)
    # Compute centered start X so the strip is horizontally centered on screen
    PALETTE_START_X = (WIDTH - PALETTE_NUM * (SWATCH_SIZE + SWATCH_GAP) + SWATCH_GAP) // 2
    PALETTE_START_Y = 20       # Top edge of the palette strip


# ------------------------------
# Sound engine (runs in a thread)
# ------------------------------
class SoundEngine:
    def __init__(self):
        self.active = False
        self.velocity = 0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()

    # Update drawing state and movement speed
    def set_drawing(self, is_drawing, velocity):
        self.active = is_drawing
        self.velocity = velocity

    # Background loop that generates sound while drawing
    def _loop(self):
        while not self.stop_event.is_set():
            if AUDIO_AVAILABLE and self.active:
                try:
                    # Sound pitch changes based on movement speed
                    freq = int(200 + (self.velocity * 5))
                    freq = max(100, min(freq, 800))  # Clamp frequency range
                    winsound.Beep(freq, 40)
                except Exception:
                    pass
            else:
                time.sleep(0.05)


# ------------------------------
# Hand tracking and HUD drawing
# ------------------------------
class HandSystem:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_pos = (0, 0)

    # Process camera frame and extract hand landmark points
    def process(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            h, w, c = img.shape

            points = []
            for lm in landmarks:
                points.append((int(lm.x * w), int(lm.y * h)))
            return points
        return None

    # Draw a sci-fi styled HUD overlay on the hand
    def draw_sci_fi_hud(self, img, points, pinch_dist):
        if not points:
            return img

        overlay = img.copy()

        # Hand skeleton connections
        connections = [
            [0,1],[1,2],[2,3],[3,4],        # Thumb
            [0,5],[5,6],[6,7],[7,8],        # Index
            [0,9],[9,10],[10,11],[11,12],   # Middle
            [0,13],[13,14],[14,15],[15,16], # Ring
            [0,17],[17,18],[18,19],[19,20]  # Pinky
        ]

        for p1, p2 in connections:
            cv2.line(overlay, points[p1], points[p2], (0, 255, 255), 1, cv2.LINE_AA)

        for pt in points:
            cv2.circle(overlay, pt, 3, (0, 165, 255), -1)
            cv2.circle(overlay, pt, 6, (0, 255, 255), 1)

        # Target circle on index finger tip
        idx_x, idx_y = points[8]
        cv2.circle(overlay, (idx_x, idx_y), 10, (255, 255, 255), 1)

        # Pinch indicator bar
        bar_len = 40
        bar_height = 6
        fill = max(0.0, min(1.0, (100 - pinch_dist) / 60))

        bar_color = (0, 0, 255)
        if pinch_dist < Config.PINCH_THRESHOLD:
            bar_color = (0, 255, 0)
            cv2.putText(overlay, "ON", (idx_x + 20, idx_y - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, bar_color, 2)

        cv2.rectangle(overlay,
                      (idx_x + 15, idx_y),
                      (idx_x + 15 + bar_len, idx_y + bar_height),
                      (50, 50, 50), -1)
        cv2.rectangle(overlay,
                      (idx_x + 15, idx_y),
                      (idx_x + 15 + int(bar_len * fill), idx_y + bar_height),
                      bar_color, -1)

        return cv2.addWeighted(overlay, 0.7, img, 0.3, 0)


# ------------------------------
# Square grid color palette UI
# ------------------------------
class SquarePalette:
    def __init__(self):
        # CLEAR removed — press X on keyboard to clear canvas
        self.colors = [
            ((0, 0, 255),     "RED"),
            ((0, 165, 255),   "ORANGE"),
            ((0, 255, 255),   "YELLOW"),
            ((0, 255, 0),     "GREEN"),
            ((255, 255, 0),   "CYAN"),
            ((255, 0, 255),   "PURPLE"),
            ((255, 255, 255), "WHITE"),
        ]
        self.selected_index = 4  # Default: CYAN

    # Returns the top-left pixel origin of swatch i
    def _swatch_origin(self, i):
        x = Config.PALETTE_START_X + i * (Config.SWATCH_SIZE + Config.SWATCH_GAP)
        y = Config.PALETTE_START_Y
        return x, y

    # Draw the palette strip and return (updated_img, hover_index)
    def draw(self, img, hover_pt):
        size = Config.SWATCH_SIZE
        num = len(self.colors)
        hover_index = -1

        # Detect which swatch the cursor is over
        if hover_pt:
            hx, hy = hover_pt
            for i in range(num):
                sx, sy = self._swatch_origin(i)
                if sx <= hx <= sx + size and sy <= hy <= sy + size:
                    hover_index = i
                    break

        # Semi-transparent dark panel behind swatches
        panel_w = num * (size + Config.SWATCH_GAP) - Config.SWATCH_GAP + 16
        panel_h = size + 34   # extra room below for hover label
        overlay = img.copy()
        cv2.rectangle(overlay,
                      (Config.PALETTE_START_X - 8, Config.PALETTE_START_Y - 8),
                      (Config.PALETTE_START_X - 8 + panel_w,
                       Config.PALETTE_START_Y - 8 + panel_h),
                      (15, 15, 15), -1)
        img = cv2.addWeighted(overlay, 0.55, img, 0.45, 0)

        # Draw each swatch
        for i, (color, name) in enumerate(self.colors):
            sx, sy = self._swatch_origin(i)

            # White selection border around the active swatch
            if i == self.selected_index:
                cv2.rectangle(img,
                              (sx - 4, sy - 4),
                              (sx + size + 4, sy + size + 4),
                              (255, 255, 255), 2)
                # Small dot indicator below the selected swatch
                cv2.circle(img, (sx + size // 2, sy + size + 12), 3,
                           (255, 255, 255), -1)

            # Hover: subtle lighter border + name label below
            if i == hover_index:
                cv2.rectangle(img,
                              (sx - 2, sy - 2),
                              (sx + size + 2, sy + size + 2),
                              (200, 200, 200), 1)
                cv2.putText(img, name,
                            (sx, sy + size + 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

            # Filled color swatch
            cv2.rectangle(img, (sx, sy), (sx + size, sy + size), color, -1)

            # Thin dark border for contrast (especially on white)
            cv2.rectangle(img, (sx, sy), (sx + size, sy + size), (40, 40, 40), 1)

        return img, hover_index


# ------------------------------
# Main application loop
# ------------------------------
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, Config.WIDTH)
    cap.set(4, Config.HEIGHT)

    hand_sys = HandSystem()
    palette = SquarePalette()
    sound = SoundEngine()

    # Drawing canvas (black, same resolution as the frame)
    canvas = np.zeros((Config.HEIGHT, Config.WIDTH, 3), dtype=np.uint8)

    # State variables
    smooth_x, smooth_y = 0, 0
    current_color = (255, 255, 0)   # Default: CYAN

    # Flash message timer for clear confirmation (~60 frames ≈ 2 sec)
    clear_msg_timer = 0

    # Fingers must be below this Y to trigger drawing (avoids palette overlap)
    palette_zone_bottom = Config.PALETTE_START_Y + Config.SWATCH_SIZE + 40

    print("AIR CANVAS ACTIVATED ~ Yathaarth Jaju")
    print("Controls: [Q] Quit   [X] Clear Canvas")

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        points = hand_sys.process(img)

        is_drawing = False
        velocity = 0

        if points:
            idx_tip = points[8]   # Index finger tip
            thm_tip = points[4]   # Thumb tip

            # Smooth the cursor position
            cx, cy = idx_tip
            if smooth_x == 0:
                smooth_x, smooth_y = cx, cy

            smooth_x = int(smooth_x * (1 - Config.SMOOTHING) + cx * Config.SMOOTHING)
            smooth_y = int(smooth_y * (1 - Config.SMOOTHING) + cy * Config.SMOOTHING)

            # Pinch distance
            dist = math.hypot(idx_tip[0] - thm_tip[0], idx_tip[1] - thm_tip[1])

            # Draw HUD
            img = hand_sys.draw_sci_fi_hud(img, points, dist)

            # Draw palette and get hover result
            img, hover_idx = palette.draw(img, (smooth_x, smooth_y))

            if hover_idx != -1 and dist < Config.PINCH_THRESHOLD:
                # Pinching inside palette → select color
                palette.selected_index = hover_idx
                current_color = palette.colors[hover_idx][0]

            elif dist < Config.PINCH_THRESHOLD and smooth_y > palette_zone_bottom:
                # Pinching below palette → draw on canvas
                is_drawing = True
                velocity = math.hypot(smooth_x - cx, smooth_y - cy)
                cv2.line(canvas, (smooth_x, smooth_y), (cx, cy),
                         current_color, Config.BRUSH_SIZE)
                cv2.circle(canvas, (cx, cy),
                           Config.BRUSH_SIZE // 2, current_color, -1)

            smooth_x, smooth_y = cx, cy

        else:
            # No hand detected — still render palette
            img, _ = palette.draw(img, None)

        # Update sound engine
        sound.set_drawing(is_drawing, velocity)

        # --- Neon glow effect ---
        canvas_small = cv2.resize(canvas, (0, 0), fx=0.2, fy=0.2)
        blur = cv2.GaussianBlur(canvas_small, (15, 15), 0)
        blur_up = cv2.resize(blur, (Config.WIDTH, Config.HEIGHT))
        final_canvas = cv2.addWeighted(canvas, 1.0, blur_up, 1.5, 0)

        # --- Merge canvas with camera feed ---
        gray = cv2.cvtColor(final_canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        img_bg = cv2.bitwise_and(img, img, mask=mask_inv)
        img = cv2.add(img_bg, final_canvas)

        # --- Canvas cleared flash message ---
        if clear_msg_timer > 0:
            cv2.putText(img, "CANVAS CLEARED",
                        (Config.WIDTH // 2 - 160, Config.HEIGHT // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            clear_msg_timer -= 1

        # --- Keyboard hint at bottom ---
        cv2.putText(img, "Press X to clear | Q to quit",
                    (20, Config.HEIGHT - 20),
                    cv2.FONT_HERSHEY_PLAIN, 1.4, (180, 180, 180), 1)

        cv2.imshow("Iron Canvas Pro", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('x'):
            canvas[:] = 0
            clear_msg_timer = 60

    sound.stop_event.set()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()