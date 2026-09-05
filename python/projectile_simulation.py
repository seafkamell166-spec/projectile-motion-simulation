"""
Projectile motion simulation for a Classical Mechanics project.

The program models two-dimensional projectile motion with constant
gravitational acceleration.  It compares several launch angles, saves a
results table, and creates simple PNG visualizations using Pillow.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


G = 9.80  # gravitational acceleration in m/s^2
INITIAL_SPEED = 30.0  # m/s
ANGLES_DEGREES = [20, 30, 45, 60, 70]
TIME_STEP = 0.02  # seconds
OUTPUT_DIR = Path(__file__).resolve().parent / "projectile_outputs"


@dataclass
class Trajectory:
    """Stores the simulated motion for one launch angle."""

    angle_deg: float
    time: list[float]
    x: list[float]
    y: list[float]
    vx: list[float]
    vy: list[float]

    @property
    def flight_time(self) -> float:
        return self.time[-1]

    @property
    def range_m(self) -> float:
        return self.x[-1]

    @property
    def max_height_m(self) -> float:
        return max(self.y)


def simulate_projectile(speed: float, angle_deg: float, dt: float = TIME_STEP) -> Trajectory:
    """
    Simulate projectile motion until the projectile returns to ground level.

    The horizontal acceleration is zero, while the vertical acceleration is -g.
    Euler stepping is used with a small time interval, then the final point is
    linearly interpolated so that the impact point lies on y = 0.
    """

    angle_rad = math.radians(angle_deg)
    vx0 = speed * math.cos(angle_rad)
    vy0 = speed * math.sin(angle_rad)

    time = [0.0]
    x = [0.0]
    y = [0.0]
    vx = [vx0]
    vy = [vy0]

    t = 0.0
    while True:
        t += dt
        new_x = vx0 * t
        new_y = vy0 * t - 0.5 * G * t * t
        new_vy = vy0 - G * t

        if new_y < 0:
            # Interpolate between the last positive point and this below-ground
            # point to estimate the exact landing point at y = 0.
            fraction = y[-1] / (y[-1] - new_y)
            impact_t = time[-1] + fraction * (t - time[-1])
            impact_x = x[-1] + fraction * (new_x - x[-1])
            impact_vy = vy[-1] + fraction * (new_vy - vy[-1])
            time.append(impact_t)
            x.append(impact_x)
            y.append(0.0)
            vx.append(vx0)
            vy.append(impact_vy)
            break

        time.append(t)
        x.append(new_x)
        y.append(new_y)
        vx.append(vx0)
        vy.append(new_vy)

    return Trajectory(angle_deg, time, x, y, vx, vy)


def theoretical_values(speed: float, angle_deg: float) -> tuple[float, float, float]:
    """Return theoretical range, maximum height, and flight time."""

    angle_rad = math.radians(angle_deg)
    range_m = speed * speed * math.sin(2 * angle_rad) / G
    max_height_m = speed * speed * math.sin(angle_rad) ** 2 / (2 * G)
    flight_time = 2 * speed * math.sin(angle_rad) / G
    return range_m, max_height_m, flight_time


def save_results_csv(trajectories: list[Trajectory], path: Path) -> None:
    """Save simulation results and theoretical comparisons to a CSV file."""

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Angle (degrees)",
                "Simulated range (m)",
                "Theoretical range (m)",
                "Maximum height (m)",
                "Flight time (s)",
            ]
        )
        for tr in trajectories:
            theory_range, _, _ = theoretical_values(INITIAL_SPEED, tr.angle_deg)
            writer.writerow(
                [
                    f"{tr.angle_deg:.0f}",
                    f"{tr.range_m:.2f}",
                    f"{theory_range:.2f}",
                    f"{tr.max_height_m:.2f}",
                    f"{tr.flight_time:.2f}",
                ]
            )


def make_canvas(title: str, width: int = 1200, height: int = 760) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create a white plotting canvas with a title."""

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_title = ImageFont.truetype("arial.ttf", 34)
    draw.text((60, 28), title, fill=(20, 28, 40), font=font_title)
    return image, draw


def draw_trajectory_plot(trajectories: list[Trajectory], path: Path) -> None:
    """Draw x-y paths for all launch angles."""

    image, draw = make_canvas("Projectile trajectories for different launch angles")
    width, height = image.size
    left, top, right, bottom = 90, 100, width - 60, height - 95

    max_x = max(tr.range_m for tr in trajectories) * 1.08
    max_y = max(tr.max_height_m for tr in trajectories) * 1.18

    def sx(value: float) -> float:
        return left + value / max_x * (right - left)

    def sy(value: float) -> float:
        return bottom - value / max_y * (bottom - top)

    axis_color = (80, 88, 100)
    grid_color = (224, 228, 235)
    draw.line((left, bottom, right, bottom), fill=axis_color, width=2)
    draw.line((left, bottom, left, top), fill=axis_color, width=2)

    font = ImageFont.truetype("arial.ttf", 18)
    small_font = ImageFont.truetype("arial.ttf", 16)

    for i in range(6):
        x_value = max_x * i / 5
        x_pos = sx(x_value)
        draw.line((x_pos, top, x_pos, bottom), fill=grid_color, width=1)
        draw.text((x_pos - 20, bottom + 14), f"{x_value:.0f}", fill=axis_color, font=small_font)

        y_value = max_y * i / 5
        y_pos = sy(y_value)
        draw.line((left, y_pos, right, y_pos), fill=grid_color, width=1)
        draw.text((20, y_pos - 10), f"{y_value:.0f}", fill=axis_color, font=small_font)

    colors = [(21, 101, 192), (0, 137, 123), (245, 124, 0), (126, 87, 194), (198, 40, 40)]
    for tr, color in zip(trajectories, colors):
        points = [(sx(px), sy(py)) for px, py in zip(tr.x, tr.y)]
        draw.line(points, fill=color, width=4)
        end_x, end_y = points[min(len(points) - 1, int(len(points) * 0.55))]
        draw.text((end_x + 5, end_y - 20), f"{tr.angle_deg:.0f} deg", fill=color, font=font)

    draw.text(((left + right) // 2 - 90, height - 45), "Horizontal distance x (m)", fill=axis_color, font=font)
    draw.text((18, 70), "Height y (m)", fill=axis_color, font=font)
    image.save(path)


def draw_energy_plot(trajectory: Trajectory, path: Path) -> None:
    """Draw kinetic, potential, and total energy for a 1 kg projectile."""

    image, draw = make_canvas("Energy check for the 45 degree launch")
    width, height = image.size
    left, top, right, bottom = 90, 100, width - 60, height - 95

    mass = 1.0
    kinetic = [0.5 * mass * (vx * vx + vy * vy) for vx, vy in zip(trajectory.vx, trajectory.vy)]
    potential = [mass * G * y for y in trajectory.y]
    total = [ke + pe for ke, pe in zip(kinetic, potential)]
    max_energy = max(max(kinetic), max(potential), max(total)) * 1.08
    max_time = trajectory.flight_time

    def sx(value: float) -> float:
        return left + value / max_time * (right - left)

    def sy(value: float) -> float:
        return bottom - value / max_energy * (bottom - top)

    axis_color = (80, 88, 100)
    grid_color = (224, 228, 235)
    draw.line((left, bottom, right, bottom), fill=axis_color, width=2)
    draw.line((left, bottom, left, top), fill=axis_color, width=2)

    font = ImageFont.truetype("arial.ttf", 18)
    small_font = ImageFont.truetype("arial.ttf", 16)

    for i in range(6):
        t_value = max_time * i / 5
        x_pos = sx(t_value)
        draw.line((x_pos, top, x_pos, bottom), fill=grid_color, width=1)
        draw.text((x_pos - 18, bottom + 14), f"{t_value:.1f}", fill=axis_color, font=small_font)

        e_value = max_energy * i / 5
        y_pos = sy(e_value)
        draw.line((left, y_pos, right, y_pos), fill=grid_color, width=1)
        draw.text((18, y_pos - 10), f"{e_value:.0f}", fill=axis_color, font=small_font)

    series = [
        ("Kinetic", kinetic, (21, 101, 192)),
        ("Potential", potential, (0, 137, 123)),
        ("Total", total, (198, 40, 40)),
    ]
    for name, values, color in series:
        points = [(sx(t), sy(e)) for t, e in zip(trajectory.time, values)]
        draw.line(points, fill=color, width=4)

    legend_x = right - 230
    for i, (name, _, color) in enumerate(series):
        y = top + 22 + 32 * i
        draw.line((legend_x, y + 10, legend_x + 38, y + 10), fill=color, width=5)
        draw.text((legend_x + 48, y), name, fill=(30, 36, 48), font=font)

    draw.text(((left + right) // 2 - 55, height - 45), "Time (s)", fill=axis_color, font=font)
    draw.text((18, 70), "Energy (J)", fill=axis_color, font=font)
    image.save(path)


def main() -> None:
    """Run the simulation and create all project outputs."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    trajectories = [simulate_projectile(INITIAL_SPEED, angle) for angle in ANGLES_DEGREES]

    save_results_csv(trajectories, OUTPUT_DIR / "projectile_results.csv")
    draw_trajectory_plot(trajectories, OUTPUT_DIR / "trajectory_comparison.png")

    trajectory_45 = next(tr for tr in trajectories if tr.angle_deg == 45)
    draw_energy_plot(trajectory_45, OUTPUT_DIR / "energy_conservation.png")

    print("Projectile Motion Simulation Results")
    print(f"Initial speed: {INITIAL_SPEED:.1f} m/s")
    print(f"Gravity: {G:.2f} m/s^2")
    for tr in trajectories:
        theory_range, theory_height, theory_time = theoretical_values(INITIAL_SPEED, tr.angle_deg)
        print(
            f"{tr.angle_deg:>2.0f} deg | "
            f"range {tr.range_m:6.2f} m (theory {theory_range:6.2f}) | "
            f"height {tr.max_height_m:6.2f} m (theory {theory_height:6.2f}) | "
            f"time {tr.flight_time:5.2f} s (theory {theory_time:5.2f})"
        )


if __name__ == "__main__":
    main()
