import pygame
import pygame.gfxdraw
import sys
import math
import random
from collections import deque

# --- Constants ---
WIDTH, HEIGHT = 1000, 800 # Increased size slightly
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)

# Gravitational constant (scaled for simulation)
G = 5

"""
Time step for integration (change for faster/slower simulation)
Using a smaller time step for smoother simulation
Note: This is a trade-off between performance and accuracy
A smaller time step will yield more accurate results but at a performance cost
A larger time step will be less accurate but faster
Adjust this based on your needs
"""

DT = 1

# Small value to prevent division by zero
EPSILON = 1e-1

# Trail length
TRAIL_LENGTH = 150 

# Starfield settings
NUM_STARS = 100

# Glow settings
GLOW_LAYERS = 5
GLOW_ALPHA_START = 80 # Max alpha for the outermost glow layer

# Trail settings
TRAIL_DOT_MIN_ALPHA = 10
TRAIL_DOT_MAX_ALPHA = 180
TRAIL_DOT_MIN_RADIUS = 1
TRAIL_DOT_MAX_RADIUS = 2

def generate_stars(num_stars, width, height):
    """Generates a list of stars with random positions and brightness."""
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, width)
        y = random.randint(0, height)
        # Brightness affects color (grayscale) and maybe size slightly
        brightness = random.randint(50, 150)
        stars.append(((x, y), (brightness, brightness, brightness)))
    return stars

class Body:
    def __init__(self, mass, pos_x, pos_y, vel_x, vel_y, color, name="Body"):
        self.mass = mass
        self.position = pygame.math.Vector2(pos_x, pos_y)
        self.velocity = pygame.math.Vector2(vel_x, vel_y)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.color = color
        # Radius more sensitive to mass for visual difference
        self.radius = max(2, int(math.pow(mass, 1/3.5) * 1.8))
        self.name = name
        self.trail = deque(maxlen=TRAIL_LENGTH)

    def apply_force(self, force):
        self.acceleration += force / self.mass

    def update(self, dt):
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.trail.append(self.position.copy()) # Store a copy!
        self.acceleration = pygame.math.Vector2(0, 0)

    def draw(self, screen, offset_x, offset_y):
        # Calculate screen position with offset
        screen_x = int(self.position.x + offset_x)
        screen_y = int(self.position.y + offset_y)

        # --- Draw Fading Trail ---
        if len(self.trail) > 1:
            for i, pos in enumerate(reversed(self.trail)): # Iterate oldest to newest is easier here
                # Calculate alpha based on position in trail (age)
                alpha = int(TRAIL_DOT_MIN_ALPHA + (TRAIL_DOT_MAX_ALPHA - TRAIL_DOT_MIN_ALPHA) * (i / TRAIL_LENGTH))
                # Calculate size based on position in trail (age) - smaller further back
                radius = int(TRAIL_DOT_MIN_RADIUS + (TRAIL_DOT_MAX_RADIUS - TRAIL_DOT_MIN_RADIUS) * (i / TRAIL_LENGTH))
                radius = max(1, radius) # Ensure minimum radius of 1

                trail_color = (*self.color, alpha) # RGBA color
                trail_screen_x = int(pos.x + offset_x)
                trail_screen_y = int(pos.y + offset_y)

                # Draw small, fading, anti-aliased circles for the trail
                # Need a surface with per-pixel alpha for this to blend well
                temp_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, trail_color, (radius, radius), radius)
                screen.blit(temp_surface, (trail_screen_x - radius, trail_screen_y - radius))

        # Glow size slightly influenced by mass/radius but mostly fixed layers
        base_glow_radius = self.radius
        for i in range(GLOW_LAYERS, 0, -1):
            # Alpha decreases from outer layer inwards towards the body
            glow_alpha = int(GLOW_ALPHA_START * (i / GLOW_LAYERS)**1.5) # Exponential falloff
            glow_alpha = max(0, min(255, glow_alpha)) # Clamp alpha
            # Radius increases for outer layers
            glow_radius = int(base_glow_radius + (base_glow_radius * 0.8 * (GLOW_LAYERS - i + 1)))
            glow_color = (*self.color, glow_alpha) # RGBA

            # Draw anti-aliased glow circles using a temporary surface for alpha blending
            temp_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(temp_surface, (screen_x - glow_radius, screen_y - glow_radius))

        # Draw the anti-aliased outline
        pygame.gfxdraw.aacircle(screen, screen_x, screen_y, self.radius, self.color)
        # Draw the filled circle
        pygame.gfxdraw.filled_circle(screen, screen_x, screen_y, self.radius, self.color)


    def __repr__(self):
        return f"{self.name}(m={self.mass}, pos={self.position}, vel={self.velocity})"

def calculate_gravitational_force(body1, body2):
    r_vector = body2.position - body1.position
    dist_sq = r_vector.magnitude_squared()
    if dist_sq < EPSILON**2:
        return pygame.math.Vector2(0, 0)
    dist = math.sqrt(dist_sq)
    force_magnitude = (G * body1.mass * body2.mass) / dist_sq
    force_vector = force_magnitude * r_vector.normalize()
    return force_vector

def calculate_center_of_mass(bodies):
    total_mass = sum(b.mass for b in bodies)
    if total_mass == 0:
        return pygame.math.Vector2(WIDTH / 2, HEIGHT / 2) # Default center if no mass

    weighted_sum_pos = pygame.math.Vector2(0, 0)
    for body in bodies:
        weighted_sum_pos += body.mass * body.position

    return weighted_sum_pos / total_mass


# --- Main Function ---
def main():
    pygame.init()
    # Use SRCALPHA flag for the screen to better handle transparency
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.display.set_caption("3-Body Problem Simulation (Enhanced Visuals)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28) # Slightly larger font

    # --- Generate Starfield ---
    stars = generate_stars(NUM_STARS, WIDTH, HEIGHT)

    # --- Initial Conditions --- (Using Example 2 as default)
    body1 = Body(mass=500, pos_x=-150, pos_y=0, vel_x=1, vel_y=1.5, color=RED, name="Body A")
    body2 = Body(mass=600, pos_x=150, pos_y=50, vel_x=-1, vel_y=-1, color=GREEN, name="Body B")
    body3 = Body(mass=400, pos_x=0, pos_y=-200, vel_x=0.5, vel_y=-0.5, color=BLUE, name="Body C")
    bodies = [body1, body2, body3]

    running = True
    paused = False
    show_info = True
    follow_center_of_mass = True

    # Store initial state for reset
    initial_state = [(b.mass, b.position.x, b.position.y, b.velocity.x, b.velocity.y, b.color, b.name) for b in bodies]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_i:
                    show_info = not show_info
                if event.key == pygame.K_c:
                    follow_center_of_mass = not follow_center_of_mass
                if event.key == pygame.K_r: # Reset to initial conditions
                    bodies = []
                    for mass, px, py, vx, vy, col, name in initial_state:
                         body = Body(mass, px, py, vx, vy, col, name)
                         bodies.append(body)
                    paused = False # Ensure simulation runs after reset

        if not paused:
            # --- Physics Calculation ---
            forces = {body: pygame.math.Vector2(0, 0) for body in bodies}
            for i in range(len(bodies)):
                for j in range(i + 1, len(bodies)):
                    body_i = bodies[i]
                    body_j = bodies[j]
                    force_ij = calculate_gravitational_force(body_i, body_j)
                    forces[body_i] += force_ij
                    forces[body_j] -= force_ij

            # Apply forces and update bodies
            for body in bodies:
                body.apply_force(forces[body])
                body.update(DT)

        # --- Drawing ---
        screen.fill(BLACK) # Fill background first

        # Calculate offset
        offset_x = WIDTH / 2
        offset_y = HEIGHT / 2
        if follow_center_of_mass:
            com = calculate_center_of_mass(bodies)
            offset_x -= com.x
            offset_y -= com.y

        # --- Draw Starfield ---
        # Adjust star positions based on offset for a parallax effect (optional, simpler: draw fixed)
        # Simple fixed stars:
        for pos, color in stars:
             # Draw small anti-aliased circles for stars
             pygame.gfxdraw.aacircle(screen, pos[0], pos[1], 1, color)
             pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], 1, color)

        # --- Draw Bodies (with trails and glow) ---
        for body in bodies:
            body.draw(screen, offset_x, offset_y)

        # --- Draw Info Text ---
        if show_info:
            # Use a semi-transparent background for info text readability
            info_panel_height = 130
            info_surface = pygame.Surface((250, info_panel_height), pygame.SRCALPHA)
            info_surface.fill((20, 20, 20, 180)) # Dark semi-transparent background

            info_text = [
                f"Bodies: {len(bodies)} | FPS: {clock.get_fps():.1f}",
                f"G: {G:.1f} | dt: {DT:.4f}",
                f"Paused: {'Yes' if paused else 'No'} [SPACE]",
                f"Center: {'CoM' if follow_center_of_mass else 'Origin'} [C]",
                f"Info: {'On' if show_info else 'Off'} [I]",
                f"Reset: [R]"
            ]
            for i, line in enumerate(info_text):
                text_surface = font.render(line, True, YELLOW)
                info_surface.blit(text_surface, (10, 10 + i * 20))

            screen.blit(info_surface, (5, 5)) # Position info panel top-left


        pygame.display.flip()
        clock.tick(60) # Maintain target FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()