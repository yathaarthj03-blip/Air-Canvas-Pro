# 🖌️ Air Canvas Pro ~ By Yathaarth Jaju

> *Draw in the air. Paint with your hands.*

---

## 👋 About Me

Hey, I'm **Yathaarth Jaju** — I started my journey in tech about **8 months ago** with web development, and since then I've gone way deeper than I expected. What began as learning HTML and CSS quickly grew into exploring professional and realistic tech stacks, picking up vibe coding, and diving into **AI engineering**. I love building things that feel like they shouldn't work — but do.

---

## 🎯 Purpose of This Project

Iron Canvas Pro is a **fun, gesture-driven drawing application** built entirely in Python using a webcam. The idea was simple: what if you could paint on a digital canvas without ever touching a keyboard or mouse — just your hands in the air?

This was never meant to be a serious productivity tool. It was built out of **pure curiosity** — to see how far hand-tracking and computer vision could go in a casual, creative context. The result is a real-time canvas that responds to your pinch gestures, lets you pick colors by pointing at them, and glows with a neon effect as you draw.

---

## ⚙️ Core Functions

### 🖥️ What Happens on Screen

| Feature | Description |
|---|---|
| Live camera feed | Your webcam feed serves as the canvas background |
| Drawing canvas | A transparent layer sits on top where your strokes are rendered |
| Neon glow effect | Every stroke gets a blur-based glow for a neon light aesthetic |
| Sci-fi HUD | Your hand is tracked with a glowing skeleton overlay in real time |

---

### ✋ Hand Gesture Guide

Iron Canvas Pro uses **MediaPipe** to track 21 hand landmarks. Everything is controlled by your **index finger** and **thumb**.

#### Pinch to Draw
Bring your **index fingertip (tip of pointer finger)** and **thumb tip** close together — within ~40 pixels of each other. While pinching and moving your hand below the color palette row, strokes are drawn onto the canvas in your selected color.

```
Index Tip ──┐
             ├── Pinch (distance < 40px) → Drawing ON
Thumb Tip ──┘
```

> 💡 **Tip:** The HUD shows a small `ON` label and a green fill bar next to your finger when the pinch is active.

#### Point to Select a Color
Move your index finger up to the **color palette strip** at the top center of the screen. Hover over a swatch — its name will appear below it. **Pinch while hovering** to select that color. The selected swatch gets a white border and a small dot below it.

#### Pinch Indicator Bar
A small bar appears next to your index fingertip at all times:
- **Red fill** = not pinching (drawing OFF)
- **Green fill + "ON" label** = pinching (drawing ON)

---

### 🎨 Color Palette

The palette is a horizontal strip of **7 color swatches** centered at the top of the screen:

| Color | Description |
|---|---|
| 🔴 RED | Classic red |
| 🟠 ORANGE | Warm orange |
| 🟡 YELLOW | Bright yellow |
| 🟢 GREEN | Vivid green |
| 🩵 CYAN | Default selected color |
| 🟣 PURPLE | Deep magenta-purple |
| ⬜ WHITE | White strokes |

---

### ⌨️ Keyboard Controls

| Key | Action |
|---|---|
| `X` | **Clear the canvas** — wipes all strokes. A "CANVAS CLEARED" message flashes on screen for ~2 seconds to confirm. |
| `Q` | **Quit** the application |

---

### 🔊 Sound Engine *(Windows only)*

On Windows, the app generates a **live beep tone** while you're drawing. The pitch of the beep changes based on how fast you're moving your hand — slower movement = lower pitch, faster movement = higher pitch. This feature uses `winsound` and is silently skipped on macOS/Linux.

---

## 🛠️ Tech Stack

| Library | Role |
|---|---|
| `opencv-python` | Camera capture, rendering, drawing |
| `mediapipe` | Real-time hand landmark detection |
| `numpy` | Canvas array operations and glow effect |
| `winsound` *(optional)* | Gesture-responsive audio feedback |

---

## 🚀 Getting Started

```bash
# Install dependencies
pip install opencv-python mediapipe numpy

# Run the app
python air_canvas.py
```

> Make sure your webcam is connected and accessible. The app opens at **1280×720** by default.

---

## 🎬 Outro

This project was a blast to build. It sits at that sweet spot between something technically interesting and something you can just show someone and watch their face light up. If you're exploring computer vision, hand tracking, or just want to build something that feels like magic — I hope this gives you a head start or at least some inspiration.

Feel free to fork it, extend it, or break it entirely. That's how the best projects start.

— **Yathaarth Jaju** 🙌
> *Air Canvas Pro — because the best canvas is the air in front of you.*

