# 🌌 Three-Body Simulation

A high-resolution, real-time simulation of gravitational systems — visualizing the raw mechanics of Newtonian gravity in action. Watch as celestial bodies interact, orbit, collide, and form emergent patterns governed purely by mass and motion.

This project models **pairwise gravitational attraction (O(n²))** with visual fidelity, simulating the unpredictable beauty of many-body dynamics. Built for those who enjoy watching physics unfold — one timestep at a time.

---

## 🧠 Under the Hood

Every body in the system is affected by every other, using:

$\[
F = G \cdot \frac{m_1 \cdot m_2}{r^2}
]\$

Velocities and positions are updated per timestep with numerical integration. Bodies leave trails to visualize velocity, orbital decay, and past paths — producing hypnotic, often chaotic motion.

---

## 📸 Preview



---

## 🛠️ Getting Started

Clone the repository and run the simulation:

```bash
git clone https://github.com/yourusername/n-body-simulation.git
cd n-body-simulation
python simulation.py
```

> Requires Python 3 and a standard graphics-capable environment.

---

## 🎮 Controls

| Key        | Action                              |
|------------|-------------------------------------|
| `Space`    | Pause / Resume simulation           |
| `R`        | Reset system to initial state       |
| `C`        | Toggle center-of-mass camera        |
| `I`        | Show/hide simulation stats          |
| `Esc`      | Exit                                |

---

## 🧭 Tweak It

Initial conditions are easy to modify:
- Change the number of bodies
- Adjust mass, velocity, and position
- Experiment with orbital setups, perturbations, and collisions

Want to model a binary star system? A stable Lagrange configuration? Total gravitational chaos? You can.
