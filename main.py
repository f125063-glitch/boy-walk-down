import pygame
import random
import sys
import math
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# --- Sound Synthesis ---
SAMPLE_RATE = 44100

def make_sound(samples):
    samples = np.clip(samples, -32767, 32767).astype(np.int16)
    stereo = np.column_stack((samples, samples))  # duplicate to stereo
    sound = pygame.sndarray.make_sound(stereo)
    return sound

def gen_coin_sfx():
    """Short rising chirp (coin-like)"""
    t = np.linspace(0, 0.12, int(SAMPLE_RATE * 0.12), endpoint=False)
    freq = np.linspace(880, 1760, len(t))
    wave = (np.sin(2 * np.pi * freq * t / SAMPLE_RATE * np.cumsum(np.ones(len(t)))) * 20000).astype(np.float32)
    env = np.exp(-t * 20)
    # simpler direct approach
    samples = np.zeros(len(t), dtype=np.float32)
    phase = 0.0
    for i in range(len(t)):
        f = 880 + (880 * i / len(t))
        phase += 2 * math.pi * f / SAMPLE_RATE
        samples[i] = math.sin(phase) * 28000 * math.exp(-t[i] * 18)
    return make_sound(samples)

def gen_yoshi_sfx():
    """Two-tone bounce sound"""
    duration = 0.18
    n = int(SAMPLE_RATE * duration)
    samples = np.zeros(n, dtype=np.float32)
    phase = 0.0
    for i in range(n):
        tt = i / SAMPLE_RATE
        f = 523 if tt < 0.09 else 784
        phase += 2 * math.pi * f / SAMPLE_RATE
        env = math.exp(-tt * 12)
        samples[i] = math.sin(phase) * 26000 * env
    return make_sound(samples)

def gen_damage_sfx():
    """Low-freq thud + noise burst"""
    duration = 0.22
    n = int(SAMPLE_RATE * duration)
    samples = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(42)
    noise = rng.uniform(-1, 1, n).astype(np.float32)
    phase = 0.0
    for i in range(n):
        tt = i / SAMPLE_RATE
        phase += 2 * math.pi * 110 / SAMPLE_RATE
        env = math.exp(-tt * 14)
        samples[i] = (math.sin(phase) * 0.5 + noise[i] * 0.5) * 28000 * env
    return make_sound(samples)

def gen_heal_sfx():
    """Rising arpeggio chord"""
    freqs = [261, 329, 392, 523]
    duration = 0.55
    n = int(SAMPLE_RATE * duration)
    samples = np.zeros(n, dtype=np.float32)
    note_len = n // len(freqs)
    for fi, freq in enumerate(freqs):
        phase = 0.0
        start = fi * note_len
        end = min(start + note_len, n)
        for i in range(start, end):
            tt = (i - start) / SAMPLE_RATE
            phase += 2 * math.pi * freq / SAMPLE_RATE
            env = math.exp(-tt * 8)
            samples[i] = math.sin(phase) * 24000 * env
    return make_sound(samples)

def gen_gameover_sfx():
    """Slow descending melody"""
    freqs = [392, 349, 330, 294, 262]
    note_dur = 0.35
    total = int(SAMPLE_RATE * note_dur * len(freqs))
    samples = np.zeros(total, dtype=np.float32)
    note_n = int(SAMPLE_RATE * note_dur)
    for fi, freq in enumerate(freqs):
        phase = 0.0
        start = fi * note_n
        end = min(start + note_n, total)
        for i in range(start, end):
            tt = (i - start) / SAMPLE_RATE
            phase += 2 * math.pi * freq / SAMPLE_RATE
            env = math.exp(-tt * 4)
            samples[i] = math.sin(phase) * 22000 * env
    return make_sound(samples)

def gen_fly_sfx():
    """Short cheerful rising whistle/whoosh for flying"""
    duration = 0.15
    n = int(SAMPLE_RATE * duration)
    samples = np.zeros(n, dtype=np.float32)
    phase = 0.0
    for i in range(n):
        tt = i / SAMPLE_RATE
        f = 600 + 900 * (tt / duration)
        phase += 2 * math.pi * f / SAMPLE_RATE
        env = math.exp(-tt * 10)
        samples[i] = math.sin(phase) * 24000 * env
    return make_sound(samples)

# Build all sounds
sfx_coin = gen_coin_sfx()
sfx_yoshi = gen_yoshi_sfx()
sfx_damage = gen_damage_sfx()
sfx_heal = gen_heal_sfx()
sfx_gameover = gen_gameover_sfx()
sfx_fly = gen_fly_sfx()

# Game Constants
WIDTH, HEIGHT = 480, 640
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 5
MAX_FALL_SPEED = 10
PLATFORM_SPEED = 2
PLATFORM_SPAWN_RATE = 60  # frames

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 150, 250)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
DARK_PURPLE = (128, 0, 128)
DARK_GREEN = (0, 100, 0)
LIGHT_ORANGE = (255, 200, 150)
LIGHT_GREEN_FLASH = (144, 238, 144)
ORANGE = (255, 165, 0)
DARK_BLUE = (0, 50, 160)
LIGHT_GRAY = (211, 211, 211)
GOLDEN = (255, 200, 0)  # Golden staircase color (extra-bonus mode only)

# Children Cheerful Theme Colors
KIDS_YELLOW = (255, 200, 0)
KIDS_ORANGE = (255, 120, 0)
KIDS_GREEN = (50, 210, 80)
KIDS_BLUE = (0, 180, 255)
KIDS_PINK = (255, 105, 180)
KIDS_PURPLE = (160, 80, 220)
KIDS_LIGHT_YELLOW = (255, 235, 150)
KIDS_LIGHT_BLUE = (180, 230, 255)
KIDS_LIGHT_GREEN = (180, 250, 190)
KIDS_LIGHT_PINK = (255, 200, 220)
KIDS_DISABLED = (230, 230, 230)

NORMAL_OUTLINE_OFFSETS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if 0 < dx*dx + dy*dy <= 5]
RAINBOW_OUTLINE_OFFSETS = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5) if 0 < dx*dx + dy*dy <= 20]
SCORE_L1_OFFSETS = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5) if 0 < dx*dx + dy*dy <= 20]
SCORE_L2_OFFSETS = [(dx, dy) for dx in range(-7, 8) for dy in range(-7, 8) if 0 < dx*dx + dy*dy <= 55]
SCORE_L3_OFFSETS = [(dx, dy) for dx in range(-11, 12) for dy in range(-11, 12) if 0 < dx*dx + dy*dy <= 125]
HALF_SCORE_L1_OFFSETS = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if 0 < dx*dx + dy*dy <= 5]
HALF_SCORE_L2_OFFSETS = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5) if 0 < dx*dx + dy*dy <= 14]

# Score text piano lacquer outline layers:
# Normal mode  — L1 white ~2px, L2 black ~4px (2× L1)
SCORE_NORMAL_L1 = NORMAL_OUTLINE_OFFSETS
SCORE_NORMAL_L2 = RAINBOW_OUTLINE_OFFSETS
# Rainbow mode — L1 white ~3px, L2 black ~6px (2× L1)
SCORE_RAINBOW_L1 = [(dx, dy) for dx in range(-3, 4) for dy in range(-3, 4) if 0 < dx*dx + dy*dy <= 10]
SCORE_RAINBOW_L2 = [(dx, dy) for dx in range(-6, 7) for dy in range(-6, 7) if 0 < dx*dx + dy*dy <= 45]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("球球大冒險")

# Load background image
try:
    import os, sys
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    bg_raw = pygame.image.load(os.path.join(base_path, "background_rainbow2.jpg")).convert()
    bg_image = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
    # Precompute grayscale background
    try:
        if hasattr(pygame.transform, 'grayscale'):
            bg_image_inverted = pygame.transform.grayscale(bg_image)
        else:
            bg_image_inverted = bg_image.copy()
            arr = pygame.surfarray.pixels3d(bg_image_inverted)
            gray = np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
            arr[..., 0] = gray
            arr[..., 1] = gray
            arr[..., 2] = gray
            del arr
    except Exception:
        bg_image_inverted = bg_image.copy()
    # Load rainbow9 background for extra-bonus/grayscale mode
    try:
        bg_raw9 = pygame.image.load(os.path.join(base_path, "GPT_background_rainbow9.png")).convert()
        bg_image_rainbow9 = pygame.transform.scale(bg_raw9, (WIDTH, HEIGHT))
    except Exception:
        bg_image_rainbow9 = bg_image_inverted
except Exception as e:
    bg_image = None
    bg_image_inverted = None
    bg_image_rainbow9 = None

# Try to load a font that supports Chinese characters, fallback to default
try:
    font_large = pygame.font.SysFont('microsoftjhenghei', 48)
    font_large_bold = pygame.font.SysFont('microsoftjhenghei', 48, bold=True)
    font_half_large_bold = pygame.font.SysFont('microsoftjhenghei', 24, bold=True)
    font_medium = pygame.font.SysFont('microsoftjhenghei', 32)
    font_medium_bold = pygame.font.SysFont('microsoftjhenghei', 32, bold=True)
    font_small = pygame.font.SysFont('microsoftjhenghei', 20)
    font_small_rainbow = pygame.font.SysFont('microsoftjhenghei', 30, bold=True)  # 1.5x size, bold for rainbow mode
except:
    font_large = pygame.font.Font(None, 64)
    font_large_bold = pygame.font.Font(None, 64)
    font_large_bold.set_bold(True)
    font_half_large_bold = pygame.font.Font(None, 32)
    font_half_large_bold.set_bold(True)
    font_medium = pygame.font.Font(None, 48)
    font_medium_bold = pygame.font.Font(None, 48)
    font_medium_bold.set_bold(True)
    font_small = pygame.font.Font(None, 24)
    font_small_rainbow = pygame.font.Font(None, 36)  # 1.5x fallback
    font_small_rainbow.set_bold(True)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, 100, 30, 30)
        self.vel_y = 0
        self.max_health = 20
        self.health = 10
        self.display_health = 10.0
        self.score = 0
        self.is_fly_mode = False
        self.fly_up_count = 0
        self.flash_timer = 0
        self.flash_type = ""
        self.history = []
        self.was_moving = False
        self.heal_land_counter = 0
        self.normal_land_counter = 0
        self.combo_green_blue = 0  # consecutive green+blue stair landings
        self.rainbow_mode = False
        self.rainbow_timer = 0.0  # for rainbow color cycling
        self.rainbow_outline_timer = 0.0  # for white outline fade-in
        self.score_multiplier = 1
        self.extra_score_timer = 999.0
        self.hit_top_spike = False   # currently touching top spikes
        self.on_spike_platform = False  # currently standing on red spike platform
        self.last_landed_platform = None  # track last platform to avoid repeated counting
        self.down_press_count = 0
        self.down_last_press_time = 0.0
        self.up_key_timer = 0.0        # tracks how long up is held
        self.up_key_was_pressed = False # tracks previous frame state
        self.up_boosting = False       # True while ball is actively rising from boost
        self.up_history = []           # afterimage positions during up-boost
        self.up_used_this_fall = True  # must land on a platform before first use
        self.current_platform = None
        self.heal_suppressed = False  # 飛高高吧模式：血量達200%後壓制回血效果
        self.rainbow_safe_combo = 0   # consecutive non-damaging landings while in rainbow mode (normal game mode)
        self.invert_timer = 0.0
        self.speed_timer = 0.0
        self.has_achieved_since_damage = False

    def trigger_extra_bonus(self):
        if self.invert_timer <= 0:
            self.invert_timer = 10.0
            if not self.has_achieved_since_damage:
                self.speed_timer = 10.0
                self.has_achieved_since_damage = True

    def modify_health(self, amount):
        self.health += amount
        if self.health > self.max_health: self.health = self.max_health
        if self.health < 0: self.health = 0
        
        if amount < 0:
            self.has_achieved_since_damage = False
            self.heal_suppressed = False  # 受傷後重新啟用回血效果
            self.flash_timer = 30
            self.flash_type = "DECREASE"
            sfx_damage.play()
            self.fly_up_count = 0
            # Damage breaks rainbow mode and bonus effects
            if self.rainbow_mode and not self.is_fly_mode:
                self.rainbow_mode = False
                self.combo_green_blue = 0
                self.score_multiplier = 1
                self.rainbow_outline_timer = 0.0
            self.invert_timer = 0.0
            self.speed_timer = 0.0
            self.rainbow_safe_combo = 0  # damage resets the rainbow safe combo
        elif amount > 0:
            # 飛高高吧：血量達 max_health（200%）後壓制回血音效與外框閃爍
            if self.is_fly_mode and self.health >= self.max_health:
                self.heal_suppressed = True
            if not self.heal_suppressed:
                self.flash_timer = 30
                self.flash_type = "INCREASE"
                sfx_heal.play()
    
    def move(self, keys):
        moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        
        self.was_moving = moving
        
        # Screen wrapping
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0

    def update(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Up-boost ends automatically when ball stops rising
        if self.vel_y >= 0:
            self.up_boosting = False

        self.history.insert(0, (self.rect.x, self.rect.y))
        if len(self.history) > 10:
            self.history.pop()

        # Track up-boost afterimage positions
        if self.up_boosting:
            self.up_history.insert(0, (self.rect.x, self.rect.y))
            if len(self.up_history) > 10:
                self.up_history.pop()
        else:
            self.up_history.clear()

        was_extra = (self.rect.width > 30)

        if self.invert_timer > 0:
            self.invert_timer = max(0.0, self.invert_timer - 1.0 / 60.0)
        if self.speed_timer > 0:
            self.speed_timer = max(0.0, self.speed_timer - 1.0 / 60.0)

        is_extra = (self.invert_timer > 0)
        if is_extra and not was_extra:
            c = self.rect.center
            self.rect.width = 48
            self.rect.height = 48
            self.rect.center = c
        elif not is_extra and was_extra:
            c = self.rect.center
            self.rect.width = 30
            self.rect.height = 30
            self.rect.center = c

        self.rect.y += self.vel_y

    def draw(self, surface):
        radius = self.rect.width // 2

        # --- Up-boost afterimages (blue-tone gradient, drawn first = below ball) ---
        if self.up_boosting and len(self.up_history) > 0:
            for i in range(len(self.up_history) - 1, -1, -1):
                hx, hy = self.up_history[i]
                fraction = i / 10.0
                # Blue-tone gradient: from vivid sky-blue (0,160,255) → deep navy (0,30,120)
                r = int(0)
                g = int(160 - 130 * fraction)   # 160 → 30
                b = int(255 - 135 * fraction)   # 255 → 120
                alpha = int(190 - 170 * fraction)  # 190 → 20
                ghost_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.circle(ghost_surf, (r, g, b, alpha), (radius, radius), radius)
                pygame.draw.circle(ghost_surf, (0, 0, 80, alpha), (radius, radius), radius, 2)
                # Glossy highlight
                pygame.draw.circle(ghost_surf, (180, 220, 255, int(120 * (1 - fraction))),
                                   (int(radius * 0.7), int(radius * 0.7)), int(radius * 0.4))
                hx = hx % WIDTH
                surface.blit(ghost_surf, (hx, hy))

        # --- Falling afterimages (black, existing behaviour) ---
        if self.vel_y > 0 and len(self.history) > 0:
            # Draw ghosts from oldest to newest
            for i in range(len(self.history) - 1, -1, -1):
                hx, hy = self.history[i]
                fraction = i / 10.0
                
                # Fading alpha from 180 to 20
                alpha = int(180 - 160 * fraction)
                
                # Render onto alpha-enabled surface
                ghost_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                
                # 殘影固定為黑色（彩虹模式與一般模式相同）
                ghost_color = (0, 0, 0)
                
                # Draw the ghost circle; outline shares the same alpha as the body
                pygame.draw.circle(ghost_surf, (*ghost_color, alpha), (radius, radius), radius)
                pygame.draw.circle(ghost_surf, (0, 0, 0, alpha), (radius, radius), radius, 2)
                
                # Glossy highlight with fading alpha
                pygame.draw.circle(ghost_surf, (255, 255, 255, int(100 * (1 - fraction))), (int(radius * 0.7), int(radius * 0.7)), int(radius * 0.4))
                
                # Screen wrap boundary check
                hx = hx % WIDTH
                
                surface.blit(ghost_surf, (hx, hy))

        if self.rainbow_mode:
            self.rainbow_timer += 1.0 / 60.0
            hue = (self.rainbow_timer * 180) % 360
            rc = pygame.Color(0)
            rc.hsla = (hue, 100, 55, 100)
            body_color = (rc.r, rc.g, rc.b)
        else:
            body_color = BLUE

        radius = self.rect.width // 2

        # --- Rainbow glow: flickering white halo around the ball ---
        if self.rainbow_mode:
            glow_max = radius  # max glow width = ball radius
            # Oscillate between 0.3 and 1.0 using sin for flicker
            flicker = 0.3 + 0.7 * ((math.sin(self.rainbow_timer * 10) + 1) / 2)
            glow_width = max(1, int(glow_max * flicker))
            glow_area = radius + glow_width + 2
            glow_surf = pygame.Surface((glow_area * 2, glow_area * 2), pygame.SRCALPHA)
            gc = (glow_area, glow_area)
            # Gradient rings: innermost = most opaque, outermost = transparent
            for s in range(glow_width, 0, -1):
                frac = s / glow_width  # 1.0 at outer, 0.0 at inner
                alpha = int(210 * (1.0 - frac))
                pygame.draw.circle(glow_surf, (255, 255, 255, alpha), gc, radius + s, 1)
            surface.blit(glow_surf, (self.rect.centerx - glow_area, self.rect.centery - glow_area))

        if self.hit_top_spike:
            # Top half dark purple, bottom half transparent
            pygame.draw.rect(surface, DARK_PURPLE, (self.rect.x, self.rect.y, self.rect.width, radius), border_top_left_radius=radius, border_top_right_radius=radius)
            s = pygame.Surface((self.rect.width, radius), pygame.SRCALPHA)
            pygame.draw.rect(s, (*body_color, 128), (0, 0, self.rect.width, radius), border_bottom_left_radius=radius, border_bottom_right_radius=radius)
            surface.blit(s, (self.rect.x, self.rect.y + radius))
        elif self.on_spike_platform:
            # Bottom half dark purple, top half transparent
            s = pygame.Surface((self.rect.width, radius), pygame.SRCALPHA)
            pygame.draw.rect(s, (*body_color, 128), (0, 0, self.rect.width, radius), border_top_left_radius=radius, border_top_right_radius=radius)
            surface.blit(s, (self.rect.x, self.rect.y))
            pygame.draw.rect(surface, DARK_PURPLE, (self.rect.x, self.rect.y + radius, self.rect.width, radius), border_bottom_left_radius=radius, border_bottom_right_radius=radius)
        else:
            pygame.draw.circle(surface, body_color, self.rect.center, radius)
            
        # Add a glossy highlight to make it look like a sphere
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 100), (int(radius * 0.7), int(radius * 0.7)), int(radius * 0.4))
        surface.blit(s, self.rect.topleft)

        pygame.draw.circle(surface, BLACK, self.rect.center, radius, 2)

class Platform:
    def __init__(self, x, y, p_type="normal"):
        self.rect = pygame.Rect(x, y, 100, 15)
        self.type = p_type
        self.healed_amount = 0   # HP healed on this platform (for blue stairs max 3, green max 1)
        self.fading = False      # for fade platforms
        self.fade_timer = 0.0    # elapsed fade time in seconds
        self.fade_duration = 0.5 # total fade time before disappearing
        self.triggered = False   # for purple platforms
        self.trigger_timer = 0.0 # for purple platforms
        self.history = []
        self.stepped_on = False
        self.flash_timer = 0.0
        self.is_invert_mode = False  # True when spawned in extra-bonus/grayscale mode
        
    def get_speed(self):
        if self.type == "purple" and self.triggered:
            return PLATFORM_SPEED * 2.5
        return PLATFORM_SPEED

    def update(self):
        self.rect.y -= self.get_speed()
        if self.fading:
            self.fade_timer += 1.0 / 60.0
        if self.type == "purple" and self.triggered:
            self.trigger_timer += 1.0 / 60.0
            self.history.insert(0, (self.rect.x, self.rect.y))
            if len(self.history) > 10:
                self.history.pop()
        if self.flash_timer > 0.0:
            self.flash_timer -= 1.0 / 60.0
            if self.flash_timer < 0.0:
                self.flash_timer = 0.0
        
    def draw(self, surface):
        if self.type == "purple" and self.triggered:
            # Draw up to 10 overlapping gradient purple afterimages below the main body
            for i in range(len(self.history) - 1, -1, -1):
                hx, hy = self.history[i]
                fraction = i / 10.0
                # Interpolate color from bright lilac (230, 80, 250) to deep violet (80, 0, 80)
                r = int(230 - 150 * fraction)
                g = int(80 - 80 * fraction)
                b = int(250 - 170 * fraction)
                alpha = int(180 - 160 * fraction)
                
                # Render onto alpha-enabled surface
                ghost_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.rect(ghost_surf, (r, g, b, alpha), (0, 0, self.rect.width, self.rect.height))
                pygame.draw.rect(ghost_surf, (0, 0, 0, alpha), (0, 0, self.rect.width, self.rect.height), 2)
                
                # Add gloss reflection
                highlight_rect = pygame.Rect(2, 2, self.rect.width - 4, self.rect.height // 3)
                pygame.draw.rect(ghost_surf, (255, 255, 255, int(60 * (1 - fraction))), highlight_rect)
                
                surface.blit(ghost_surf, (hx, hy))

        color = DARK_GRAY
        if self.type == "spike":
            color = RED
        elif self.type == "heal":
            color = GREEN
        elif self.type == "purple":
            color = DARK_PURPLE
        elif self.type == "fade":
            progress = min(self.fade_timer / self.fade_duration, 1.0) if self.fading else 0.0
            r = int(LIGHT_GRAY[0] + (255 - LIGHT_GRAY[0]) * progress)
            g = int(LIGHT_GRAY[1] + (255 - LIGHT_GRAY[1]) * progress)
            b = int(LIGHT_GRAY[2] + (255 - LIGHT_GRAY[2]) * progress)
            color = (r, g, b)
        elif self.type == "golden":
            color = GOLDEN
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 150.0)
            glow_surf = pygame.Surface((self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA)
            for i in range(1, 5):
                alpha = int(255 * (0.8 - i * 0.15) * pulse)
                if alpha > 0:
                    pygame.draw.rect(glow_surf, (255, 255, 255, alpha), 
                                     (8 - i*2, 8 - i*2, self.rect.width + i*4, self.rect.height + i*4), 2)
            surface.blit(glow_surf, (self.rect.x - 8, self.rect.y - 8))
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Piano black glossy reflection (applied to all platforms)
        highlight_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height // 3)
        s = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 60))
        surface.blit(s, (highlight_rect.x, highlight_rect.y))

        # White flash overlay (first step)
        if self.flash_timer > 0.0:
            flash_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            alpha = int(255 * (self.flash_timer / 0.25))
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, self.rect.topleft)

def draw_top_spikes(surface, spike_flash_alpha=0):
    # Draw the top bar in coffee brown with piano lacquer gloss
    top_spikes_surf = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
    # Coffee brown base
    COFFEE = (105, 62, 18)
    pygame.draw.rect(top_spikes_surf, COFFEE, (0, 0, WIDTH, 50))
    # Piano lacquer: dark shadow at very bottom edge of bar for depth
    pygame.draw.rect(top_spikes_surf, (55, 28, 5), (0, 44, WIDTH, 6))
    # Piano lacquer: bright gloss highlight strip near top
    gloss1 = pygame.Surface((WIDTH - 6, 10), pygame.SRCALPHA)
    gloss1.fill((255, 220, 160, 90))
    top_spikes_surf.blit(gloss1, (3, 4))
    # Secondary softer sheen below the main highlight
    gloss2 = pygame.Surface((WIDTH - 6, 6), pygame.SRCALPHA)
    gloss2.fill((255, 200, 120, 40))
    top_spikes_surf.blit(gloss2, (3, 16))

    # Triangles (single dark red, no border, no gloss highlight)
    for i in range(0, WIDTH, 20):
        pygame.draw.polygon(top_spikes_surf, (150, 0, 0), [(i, 50), (i+10, 70), (i+20, 50)])

    # White flash overlay for top spikes on collision
    if spike_flash_alpha > 0:
        for i in range(0, WIDTH, 20):
            pygame.draw.polygon(top_spikes_surf, (255, 255, 255, spike_flash_alpha), [(i, 50), (i+10, 70), (i+20, 50)])

    surface.blit(top_spikes_surf, (0, 0))

def draw_3d_button(surface, rect, base_color, text, font, text_color=BLACK,
                   border_radius=8, pressed=False, disabled=False):
    """Draw a 3D-style button with highlight and shadow layers."""
    shadow_offset = 0 if pressed else 4
    highlight_offset = 0 if pressed else 2

    is_grad = isinstance(base_color, (list, tuple)) and len(base_color) > 1 and isinstance(base_color[0], (list, tuple))
    primary_color = base_color[0] if is_grad else base_color

    # Shadow layer (darker tone, offset down-right)
    shadow_color = tuple(max(0, c - 60) for c in (base_color[-1] if is_grad else base_color))
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=border_radius)

    # Main face
    face_rect = rect.move(0, 0) if pressed else rect.inflate(0, 0)
    if pressed:
        face_rect = rect.move(2, 2)
        
    if is_grad:
        grad_surf = pygame.Surface((face_rect.width, face_rect.height), pygame.SRCALPHA)
        num_colors = len(base_color)
        for y in range(face_rect.height):
            ratio = y / max(1, face_rect.height - 1)
            segment = int(ratio * (num_colors - 1))
            if segment >= num_colors - 1:
                segment = num_colors - 2
                segment_ratio = 1.0
            else:
                segment_ratio = (ratio - segment / (num_colors - 1)) * (num_colors - 1)
            c1 = base_color[segment]
            c2 = base_color[segment + 1]
            r = int(c1[0] * (1 - segment_ratio) + c2[0] * segment_ratio)
            g = int(c1[1] * (1 - segment_ratio) + c2[1] * segment_ratio)
            b = int(c1[2] * (1 - segment_ratio) + c2[2] * segment_ratio)
            pygame.draw.line(grad_surf, (r, g, b), (0, y), (face_rect.width, y))
        mask_surf = pygame.Surface((face_rect.width, face_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), mask_surf.get_rect(), border_radius=border_radius)
        grad_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(grad_surf, face_rect)
    else:
        pygame.draw.rect(surface, base_color, face_rect, border_radius=border_radius)

    # Highlight (top-left brighter strip)
    highlight_color = tuple(min(255, c + 60) for c in primary_color)
    hl_rect = pygame.Rect(face_rect.x + 3, face_rect.y + 3, face_rect.width - 6, max(1, face_rect.height // 3))
    hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
    hl_surf.fill((*highlight_color, 130))
    surface.blit(hl_surf, hl_rect.topleft)

    # Black outline
    pygame.draw.rect(surface, BLACK, face_rect, width=2, border_radius=border_radius)

    # Centered text
    text_surf = font.render(text, True, text_color)
    tr = text_surf.get_rect(center=face_rect.center)
    # Clip text if too wide
    if text_surf.get_width() > face_rect.width - 6:
        scale = (face_rect.width - 6) / text_surf.get_width()
        new_w = int(text_surf.get_width() * scale)
        new_h = int(text_surf.get_height() * scale)
        text_surf = pygame.transform.smoothscale(text_surf, (new_w, new_h))
        tr = text_surf.get_rect(center=face_rect.center)
    surface.blit(text_surf, tr)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_outlined_text(text, font, body_color, surface, center_x, center_y, l1_offsets, l2_offsets, outline_color1=WHITE, outline_color2=BLACK, body_alpha=255, outline_alpha=255, l3_offsets=None, outline_color3=BLACK, align="center"):
    c1_surf = font.render(text, True, outline_color1)
    c2_surf = font.render(text, True, outline_color2)
    if l3_offsets:
        c3_surf = font.render(text, True, outline_color3)
    
    if isinstance(body_color, (list, tuple)) and len(body_color) > 1 and isinstance(body_color[0], (list, tuple)):
        num_colors = len(body_color)
        temp_surf = font.render(text, True, WHITE)
        width, height = temp_surf.get_size()
        grad_surf = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / max(1, height - 1)
            segment = int(ratio * (num_colors - 1))
            if segment >= num_colors - 1:
                segment = num_colors - 2
                segment_ratio = 1.0
            else:
                segment_ratio = (ratio - segment / (num_colors - 1)) * (num_colors - 1)
            c1 = body_color[segment]
            c2 = body_color[segment + 1]
            r = int(c1[0] * (1 - segment_ratio) + c2[0] * segment_ratio)
            g = int(c1[1] * (1 - segment_ratio) + c2[1] * segment_ratio)
            b = int(c1[2] * (1 - segment_ratio) + c2[2] * segment_ratio)
            pygame.draw.line(grad_surf, (r, g, b), (0, y), (width, y))
        temp_surf.blit(grad_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        body_surf = temp_surf
    else:
        body_surf = font.render(text, True, body_color)
        
    # Apply alpha to body if needed
    if body_alpha < 255:
        body_surf.set_alpha(body_alpha)

    if align == "center":
        text_rect = body_surf.get_rect(center=(center_x, center_y))
    elif align == "right":
        text_rect = body_surf.get_rect(midright=(center_x, center_y))
    elif align == "left":
        text_rect = body_surf.get_rect(midleft=(center_x, center_y))

    # Apply outline_alpha to outline layers
    if outline_alpha < 255:
        if l3_offsets:
            c3_fade = c3_surf.copy()
            c3_fade.set_alpha(outline_alpha)
            for dx, dy in l3_offsets:
                surface.blit(c3_fade, (text_rect.x + dx, text_rect.y + dy))
        c2_fade = c2_surf.copy()
        c2_fade.set_alpha(outline_alpha)
        c1_fade = c1_surf.copy()
        c1_fade.set_alpha(outline_alpha)
        for dx, dy in l2_offsets:
            surface.blit(c2_fade, (text_rect.x + dx, text_rect.y + dy))
        for dx, dy in l1_offsets:
            surface.blit(c1_fade, (text_rect.x + dx, text_rect.y + dy))
    else:
        if l3_offsets:
            for dx, dy in l3_offsets:
                surface.blit(c3_surf, (text_rect.x + dx, text_rect.y + dy))
        for dx, dy in l2_offsets:
            surface.blit(c2_surf, (text_rect.x + dx, text_rect.y + dy))
        for dx, dy in l1_offsets:
            surface.blit(c1_surf, (text_rect.x + dx, text_rect.y + dy))

    surface.blit(body_surf, text_rect)

def draw_piano_score(surface, score_font, score_text, center_x, center_y,
                     l1_offsets, l2_offsets, outline_alpha=255, is_fly_mode=False, body_alpha=255):
    """Draw score text with piano lacquer style.

    Layering order (back → front):
      1. Black outline (L2, 2× width of L1)  — outermost
      2. White outline (L1)
      3. Deep-red body text                   — innermost
      4. Light-red gloss highlight (piano lacquer sheen)

    outline_alpha: 0-255 fade-in alpha applied to both outline layers.
    """
    SCORE_RED   = DARK_GREEN if is_fly_mode else (210, 20, 20)     # deep red or green body
    SCORE_GLOSS = (140, 255, 140) if is_fly_mode else (255, 140, 140)   # green or pink-red gloss highlight

    body_surf  = score_font.render(score_text, True, SCORE_RED)
    white_surf = score_font.render(score_text, True, WHITE)
    black_surf = score_font.render(score_text, True, BLACK)
    gloss_surf = score_font.render(score_text, True, SCORE_GLOSS)

    text_rect = body_surf.get_rect(center=(center_x, center_y))

    if outline_alpha >= 255:
        # Full-opacity outlines
        for dx, dy in l2_offsets:
            surface.blit(black_surf, (text_rect.x + dx, text_rect.y + dy))
        for dx, dy in l1_offsets:
            surface.blit(white_surf, (text_rect.x + dx, text_rect.y + dy))
    else:
        # Fading outlines (rainbow mode fade-in)
        black_fade = black_surf.copy()
        black_fade.set_alpha(outline_alpha)
        white_fade = white_surf.copy()
        white_fade.set_alpha(outline_alpha)
        for dx, dy in l2_offsets:
            surface.blit(black_fade, (text_rect.x + dx, text_rect.y + dy))
        for dx, dy in l1_offsets:
            surface.blit(white_fade, (text_rect.x + dx, text_rect.y + dy))

    # Red body
    if body_alpha < 255:
        body_surf.set_alpha(body_alpha)
    surface.blit(body_surf, text_rect)

    # Piano lacquer gloss: translucent bright highlight shifted 1px up
    gloss_copy = gloss_surf.copy()
    gloss_copy.set_alpha(int(90 * (body_alpha / 255.0)))
    surface.blit(gloss_copy, (text_rect.x, text_rect.y - 1))

def reset_game(game_mode="normal"):
    player = Player()
    if game_mode == "fly":
        player.is_fly_mode = True
        player.rainbow_mode = True
        player.health = 20
        player.display_health = 20.0
    
    p = Platform(WIDTH // 2 - 50, HEIGHT - 100, "normal")
    p.stepped_on = True
    platforms = [p]
    
    player.rect.bottom = p.rect.top
    player.rect.centerx = p.rect.centerx
    player.vel_y = 0
    player.current_platform = p
    player.last_landed_platform = p
    return player, platforms

def main():
    clock = pygame.time.Clock()
    state = "START"
    
    player, platforms = reset_game("normal")
    frame_count = 0
    speed_multiplier = 1.0
    starting_speed_multiplier = 1.0
    bg_x = 0
    bg_alpha_time = 0.0
    BG_SCROLL_SPEED = 0.5  # pixels per frame (slow scroll)
    BG_ALPHA_SPEED = 0.008  # oscillation speed (slower for gentle breathing)
    spike_flash_timer = 0.0  # timer for spikes white flash effect
    game_mode = "normal"  # "normal" = standard rules, "fly" = 飛高高吧 (unlimited up, no HP cost)
    selected_menu_index = 0
    up_key_escape_count = 0  # counter for 5x consecutive up key to return to START
    score_style_alt = False  # True when any speed button pressed during GAME_OVER
    game_start_time = None   # pygame.time.get_ticks() when PLAYING begins
    total_stairs_stepped = 0  # number of distinct stair landings in current game
    game_rating = "新手上路"    # final rating shown on GAME_OVER screen

    # UI Buttons
    btn_start = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 30, 160, 60)
    btn_fly   = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 50, 160, 60)  # 飛高高吧
    btn_pause = pygame.Rect(10, 10, 62, 30)
    btn_stop  = pygame.Rect(80, 10, 52, 30)
    btn_speed_050 = pygame.Rect(140, 10, 52, 30)
    btn_speed_100 = pygame.Rect(200, 10, 52, 30)
    btn_speed_150 = pygame.Rect(260, 10, 52, 30)
    
    ctrl_pressed_last_frame = False
    running = True
    while running:
        player.score = min(99999, player.score)
        auto_speed_mult = 1.0
        if player.score >= 701: auto_speed_mult = 1.5
        elif player.score >= 501: auto_speed_mult = 1.4
        elif player.score >= 301: auto_speed_mult = 1.3
        elif player.score >= 201: auto_speed_mult = 1.2
        elif player.score >= 101: auto_speed_mult = 1.1

        base_speed = speed_multiplier * auto_speed_mult
        if player.speed_timer > 0:
            current_speed = 0.5 if base_speed < 1.0 else 1.0
        else:
            current_speed = base_speed
        clock.tick(int(FPS * current_speed))
        if player.invert_timer > 0:
            screen.fill(WHITE)
            # Use rainbow9 background during extra-bonus mode
            _invert_bg = bg_image_rainbow9 if bg_image_rainbow9 else bg_image
            if _invert_bg:
                bg_alpha = 204
                if player.score >= 701: bg_alpha = 255
                elif player.score >= 501: bg_alpha = 255
                elif player.score >= 301: bg_alpha = 242
                elif player.score >= 201: bg_alpha = 229
                elif player.score >= 101: bg_alpha = 216
                _invert_bg.set_alpha(bg_alpha)
                if state in ["START", "GAME_OVER"]:
                    bg_x = (bg_x - BG_SCROLL_SPEED) % WIDTH
                blit_x = int(bg_x)
                screen.blit(_invert_bg, (blit_x, 0))
                screen.blit(_invert_bg, (blit_x - WIDTH, 0))
        else:
            screen.fill(WHITE)
            if bg_image:
                bg_alpha = 204
                if player.score >= 701: bg_alpha = 255
                elif player.score >= 501: bg_alpha = 255
                elif player.score >= 301: bg_alpha = 242
                elif player.score >= 201: bg_alpha = 229
                elif player.score >= 101: bg_alpha = 216
                bg_image.set_alpha(bg_alpha)
                # Scroll background only on menu screens; freeze during gameplay
                if state in ["START", "GAME_OVER"]:
                    bg_x = (bg_x - BG_SCROLL_SPEED) % WIDTH
                blit_x = int(bg_x)
                screen.blit(bg_image, (blit_x, 0))
                screen.blit(bg_image, (blit_x - WIDTH, 0))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if state in ["START", "GAME_OVER"]:
                        selected_menu_index = (selected_menu_index + 1) % 2
                    elif state in ["PLAYING", "PAUSED"]:
                        if up_key_escape_count == 5:
                            up_key_escape_count = 0
                            state = "START"
                            speed_multiplier = 1.0
                            selected_menu_index = 0
                        else:
                            up_key_escape_count = 0
                            if state == "PLAYING" and player.current_platform and player.current_platform.type in ["normal", "heal", "golden"]:
                                current_time = pygame.time.get_ticks() / 1000.0
                                if current_time - player.down_last_press_time < 0.4:
                                    player.down_press_count += 1
                                else:
                                    player.down_press_count = 1
                                player.down_last_press_time = current_time
                                
                                if player.down_press_count >= 2:
                                    # Penetrate!
                                    player.rect.y += 25
                                    if player.invert_timer <= 0 and player.current_platform.type == "normal":
                                        player.modify_health(-1)
                                    player.down_press_count = 0
                                    player.current_platform = None
                elif event.key == pygame.K_UP:
                    if state in ["START", "GAME_OVER"]:
                        selected_menu_index = (selected_menu_index - 1) % 2
                    if state in ["PLAYING", "PAUSED"]:
                        if up_key_escape_count < 5:
                            up_key_escape_count += 1
                        else:
                            up_key_escape_count = 1
                elif event.key == pygame.K_LEFT:
                    if state in ["PLAYING", "PAUSED"]:
                        up_key_escape_count = 0
                    if state in ["START", "GAME_OVER", "PAUSED"]:
                        speeds = [0.5, 1.0, 1.5]
                        try:
                            idx = speeds.index(speed_multiplier)
                        except ValueError:
                            idx = 1
                        idx = max(0, idx - 1)
                        speed_multiplier = speeds[idx]
                        if state == "GAME_OVER":
                            score_style_alt = True
                elif event.key == pygame.K_RIGHT:
                    if state in ["PLAYING", "PAUSED"]:
                        up_key_escape_count = 0
                    if state in ["START", "GAME_OVER", "PAUSED"]:
                        speeds = [0.5, 1.0, 1.5]
                        try:
                            idx = speeds.index(speed_multiplier)
                        except ValueError:
                            idx = 1
                        idx = min(len(speeds) - 1, idx + 1)
                        speed_multiplier = speeds[idx]
                        if state == "GAME_OVER":
                            score_style_alt = True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if state == "START":
                        state = "PLAYING"
                        starting_speed_multiplier = speed_multiplier
                        game_mode = "normal" if selected_menu_index == 0 else "fly"
                        player, platforms = reset_game(game_mode)
                        score_style_alt = False
                        game_start_time = pygame.time.get_ticks()
                        total_stairs_stepped = 0
                        btn_start.y = HEIGHT // 2 - 30
                        btn_fly.y = HEIGHT // 2 + 50
                    elif state == "GAME_OVER":
                        if selected_menu_index == 0:
                            state = "PLAYING"
                            starting_speed_multiplier = speed_multiplier
                            player, platforms = reset_game(game_mode)
                            score_style_alt = False
                            game_start_time = pygame.time.get_ticks()
                            total_stairs_stepped = 0
                            btn_start.y = HEIGHT // 2 - 30
                            btn_fly.y = HEIGHT // 2 + 50
                        else:
                            state = "START"
                            speed_multiplier = 1.0
                            selected_menu_index = 0

        keys = pygame.key.get_pressed()
        ctrl_pressed = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        
        if ctrl_pressed and not ctrl_pressed_last_frame:
            if state == "PLAYING":
                state = "PAUSED"
            elif state == "PAUSED":
                state = "PLAYING"
        ctrl_pressed_last_frame = ctrl_pressed

        if state == "START":
            if btn_start.collidepoint(mouse_pos):
                selected_menu_index = 0
            elif btn_fly.collidepoint(mouse_pos):
                selected_menu_index = 1

            draw_top_spikes(screen, 0)
            # 字本體與外框同步，透明度從 0% 到 95%（alpha 0→242），每 2 秒循環一次；第二層外框為黑色
            title_alpha = int((pygame.time.get_ticks() % 2000) / 2000 * 242)
            draw_outlined_text("球球大冒險", font_large_bold, BLACK, screen, WIDTH // 2, HEIGHT // 3, NORMAL_OUTLINE_OFFSETS, RAINBOW_OUTLINE_OFFSETS, outline_color2=BLACK, body_alpha=title_alpha, outline_alpha=title_alpha)

            # Start Button (3D) — normal mode
            pressed = btn_start.collidepoint(mouse_pos) and mouse_clicked
            color = KIDS_ORANGE
            current_font = font_medium_bold if selected_menu_index == 0 else font_medium
            draw_3d_button(screen, btn_start, color, "開始遊戲", current_font, WHITE,
                           border_radius=15, pressed=pressed)
            if mouse_clicked and btn_start.collidepoint(mouse_pos):
                state = "PLAYING"
                starting_speed_multiplier = speed_multiplier
                game_mode = "normal"
                player, platforms = reset_game("normal")
                game_start_time = pygame.time.get_ticks()
                total_stairs_stepped = 0

            # Fly Button (3D) — unlimited up-boost, no HP cost
            fly_pressed = btn_fly.collidepoint(mouse_pos) and mouse_clicked
            fly_color = KIDS_PINK
            current_font_fly = font_medium_bold if selected_menu_index == 1 else font_medium
            draw_3d_button(screen, btn_fly, fly_color, "飛高高吧", current_font_fly, WHITE,
                           border_radius=15, pressed=fly_pressed)
            if mouse_clicked and btn_fly.collidepoint(mouse_pos):
                state = "PLAYING"
                starting_speed_multiplier = speed_multiplier
                game_mode = "fly"
                player, platforms = reset_game("fly")
                game_start_time = pygame.time.get_ticks()
                total_stairs_stepped = 0

        elif state == "PLAYING" or state == "PAUSED":
            if state == "PLAYING":
                player.move(keys)
                player.update()
                
                # Platform generation
                frame_count += 1
                if frame_count >= PLATFORM_SPAWN_RATE:
                    frame_count = 0
                    p_x = random.randint(0, WIDTH - 100)
                    r = random.random()
                    if player.invert_timer > 0:
                        p_type = "golden"
                    else:
                        if r < 0.60:
                            p_type = "normal"
                        elif r < 0.80:
                            p_type = "spike"
                        elif r < 0.85:
                            p_type = "heal"
                        elif r < 0.90:
                            p_type = "fade"
                        else:
                            p_type = "purple"
                    new_p = Platform(p_x, HEIGHT + 20, p_type)
                    new_p.is_invert_mode = (player.invert_timer > 0)
                    platforms.append(new_p)
                    # 分數只在踩到深灰色/綠色階梯時計算，不再依時間增加

                # Update platforms
                for p in platforms:
                    p.update()

                # Clean up platforms (off-screen or fully faded)
                platforms = [p for p in platforms if p.rect.bottom > 0 and not (p.type == "fade" and p.fading and p.fade_timer >= p.fade_duration) and not (p.type == "purple" and p.triggered and p.trigger_timer >= 0.5)]
                
                # Collision detection
                on_platform = False
                player.on_spike_platform = False  # reset each frame
                player.current_platform = None
                for p in platforms:
                    # Check if player is falling and hits the top of a platform
                    # Spikes use original > 0 check to restore original bounce and damage rate
                    p_speed = p.get_speed()
                    if (player.vel_y > 0 if p.type == "spike" else player.vel_y >= -p_speed) and p.rect.top <= player.rect.bottom <= p.rect.top + 20 and \
                       player.rect.right > p.rect.left and player.rect.left < p.rect.right:
                        player.rect.bottom = p.rect.top
                        player.vel_y = -p_speed # move up with platform
                        on_platform = True
                        player.current_platform = p
                        if not p.stepped_on:
                            p.stepped_on = True
                            p.flash_timer = 0.25
                            sfx_coin.play()
                        is_new_landing = (p is not player.last_landed_platform)
                        player.last_landed_platform = p
                        if is_new_landing:
                            total_stairs_stepped += 1
                            player.up_used_this_fall = False  # restore 1 up-boost for next fall
                            player.fly_up_count = 0
                        eff_type = p.type
                        if eff_type == "spike":
                            player.modify_health(-1)
                            if is_new_landing:
                                player.combo_green_blue = 0
                            player.on_spike_platform = True
                        elif eff_type in ("heal", "golden"):
                            if is_new_landing:
                                player.combo_green_blue += 1
                                player.heal_land_counter = 0
                                player.score += 2 * player.score_multiplier
                                if player.rainbow_mode and not player.is_fly_mode:
                                    player.rainbow_safe_combo += 1
                                    if player.rainbow_safe_combo >= 6:
                                        player.score += 18
                                        player.rainbow_safe_combo = 0
                                        player.extra_score_timer = 0.0
                                        player.trigger_extra_bonus()
                            if player.health < player.max_health and p.healed_amount < 3:
                                player.heal_land_counter += 1
                                if player.heal_land_counter >= 45:
                                    player.heal_land_counter = 0
                                    player.modify_health(1)
                                    p.healed_amount += 1
                        elif eff_type == "fade":
                            if is_new_landing:
                                if player.invert_timer <= 0:
                                    player.modify_health(-1)
                                if player.rainbow_mode and not player.is_fly_mode:
                                    player.rainbow_mode = False
                                    player.score_multiplier = 1
                                    player.rainbow_outline_timer = 0.0
                                player.combo_green_blue = 0
                                player.rainbow_safe_combo = 0
                            p.fading = True
                        elif eff_type == "purple":
                            if is_new_landing:
                                if player.invert_timer <= 0:
                                    if player.rainbow_mode and not player.is_fly_mode:
                                        player.rainbow_mode = False
                                        player.score_multiplier = 1
                                        player.rainbow_outline_timer = 0.0
                                    player.combo_green_blue = 0
                                    player.rainbow_safe_combo = 0
                                    player.invert_timer = 0.0
                                    player.speed_timer = 0.0
                            if not p.triggered:
                                p.triggered = True
                                p.trigger_timer = 0.0
                        elif eff_type == "normal":
                            if is_new_landing:
                                player.combo_green_blue += 1
                                player.normal_land_counter = 0
                                player.score += 1 * player.score_multiplier
                                if player.rainbow_mode and not player.is_fly_mode:
                                    player.rainbow_safe_combo += 1
                                    if player.rainbow_safe_combo >= 6:
                                        player.score += 18
                                        player.rainbow_safe_combo = 0
                                        player.extra_score_timer = 0.0
                                        player.trigger_extra_bonus()
                            if player.health < player.max_health and p.healed_amount < 1:
                                player.normal_land_counter += 1
                                if player.normal_land_counter >= 60:
                                    player.normal_land_counter = 0
                                    player.modify_health(1)
                                    p.healed_amount += 1
                        
                        # Check rainbow activation (5+ consecutive green/blue)
                        if player.combo_green_blue >= 5 and not player.rainbow_mode:
                            player.rainbow_mode = True
                            player.score_multiplier = 2
                            player.rainbow_outline_timer = 0.0
                        break

                if on_platform:
                    player.history.clear()

                # Penetration logic is now handled in the KEYDOWN event loop

                # Up-key boost logic
                if keys[pygame.K_UP]:
                    if player.current_platform is None:
                        if not player.up_key_was_pressed:
                            can_start_boost = (game_mode == "fly") or (not player.up_used_this_fall)
                            if can_start_boost:
                                player.up_boosting = True
                                if game_mode == "normal":
                                    if player.invert_timer > 0:
                                        sfx_fly.play()
                                    elif player.health <= 5:
                                        sfx_fly.play()
                                    else:
                                        player.modify_health(-2)
                                    player.up_used_this_fall = True
                                elif game_mode == "fly":
                                    player.score += 3
                                    player.fly_up_count += 1
                                    if player.fly_up_count >= 3:
                                        player.modify_health(1)
                                        player.fly_up_count = 0
                                    sfx_fly.play()
                        
                        if player.up_boosting:
                            player.up_key_timer += 1.0 / 60.0
                            if player.up_key_timer <= 0.2:
                                player.vel_y = -(PLATFORM_SPEED * 3.0)
                            else:
                                player.up_boosting = False
                    else:
                        player.up_key_timer = 0.0
                        player.up_boosting = False
                else:
                    player.up_key_timer = 0.0
                    player.up_boosting = False
                
                player.up_key_was_pressed = keys[pygame.K_UP]

                # Top spike damage
                if player.rect.top <= 70:
                    if not player.hit_top_spike:
                        spike_flash_timer = 0.001
                    player.modify_health(-7)
                    player.rect.y += 20
                    player.vel_y = 0
                    player.hit_top_spike = True
                else:
                    player.hit_top_spike = False

                # Death condition
                if player.rect.top > HEIGHT or player.health <= 0:
                    # --- Compute final rating ---
                    # Composite score: score(50) + stairs(30) + speed(20) = 100 max
                    speed_factor = (speed_multiplier - 0.5) / 1.5         # proportional
                    composite = (player.score / 400.0) * 50.0 \
                               + (total_stairs_stepped / 100.0) * 30.0 \
                               + speed_factor * 20.0
                    if starting_speed_multiplier in [1.0, 1.5]:
                        composite = composite / 1.5625
                    composite = max(0.0, min(composite, 100.0))
                    
                    rating_tier = 1
                    if composite >= 80:
                        rating_tier = 5
                    elif composite >= 60:
                        rating_tier = 4
                    elif composite >= 40:
                        rating_tier = 3
                    elif composite >= 20:
                        rating_tier = 2

                    if rating_tier == 5 and player.score < 999:
                        rating_tier = 4
                    if rating_tier == 4 and player.score < 777:
                        rating_tier = 3

                    if rating_tier == 5:
                        game_rating = "★★★★★ 最優秀"
                    elif rating_tier == 4:
                        game_rating = "★★★★ 非常棒"
                    elif rating_tier == 3:
                        game_rating = "★★★ 很優秀"
                    elif rating_tier == 2:
                        game_rating = "★★ 比個讚"
                    else:
                        game_rating = "★ 有進步"
                        
                    if player.score == 0:
                        game_rating = "放鬆一下,再試一次"
                    state = "GAME_OVER"
                    selected_menu_index = 0
                    sfx_gameover.play()

                # Update spike flash timer (only top spikes flash, duration 0.2s)
                if spike_flash_timer > 0.0:
                    spike_flash_timer += 1.0 / 60.0
                    if spike_flash_timer >= 0.2:
                        spike_flash_timer = 0.0

            # Calculate flash opacity
            spike_flash_alpha = 0
            if spike_flash_timer > 0.0:
                spike_flash_alpha = int((spike_flash_timer / 0.2) * 255)
                spike_flash_alpha = max(0, min(255, spike_flash_alpha))

            # Draw Game Elements
            for p in platforms:
                p.draw(screen)
            player.draw(screen)
            
            # Draw top spikes on top of platforms and player
            draw_top_spikes(screen, spike_flash_alpha=spike_flash_alpha)
            
            # Draw UI
            # Health and Score
            if player.display_health < player.health:
                player.display_health += 0.2
                if player.display_health > player.health:
                    player.display_health = player.health
            elif player.display_health > player.health:
                player.display_health -= 0.5
                if player.display_health < player.health:
                    player.display_health = player.health

            if player.flash_timer > 0:
                player.flash_timer -= 1

            pct = player.display_health / player.max_health
            if player.display_health > 10.0:
                health_bar_color = BLUE
            elif player.display_health / 10.0 < 0.30:
                health_bar_color = RED
            elif player.display_health / 10.0 < 0.75:
                health_bar_color = ORANGE
            else:
                health_bar_color = GREEN

            health_bar_alpha = 255
            border_color = BLACK
            border_rect = pygame.Rect(WIDTH - 160, 10, 150, 30)
            
            if player.flash_timer > 0:
                if player.flash_type == "DECREASE":
                    if (player.flash_timer // 8) % 2 == 0:
                        health_bar_color = DARK_PURPLE
                    if (player.flash_timer // 4) % 2 == 0:
                        border_color = DARK_PURPLE
                        border_rect.inflate_ip(8, 8)
                elif player.flash_type == "INCREASE":
                    health_bar_alpha = int(255 - 127 * (player.flash_timer / 30.0))
                    if (player.flash_timer // 4) % 2 == 0:
                        border_color = DARK_GREEN
                        border_rect.inflate_ip(8, 8)

            pygame.draw.rect(screen, border_color, border_rect)
            pygame.draw.rect(screen, BLACK, (WIDTH - 158, 12, 146, 26))
            
            health_width = max(0, int((146 * player.display_health) / player.max_health))
            if health_width > 0:
                if health_bar_alpha < 255:
                    s = pygame.Surface((health_width, 26), pygame.SRCALPHA)
                    s.fill((*health_bar_color, health_bar_alpha))
                    screen.blit(s, (WIDTH - 158, 12))
                else:
                    pygame.draw.rect(screen, health_bar_color, (WIDTH - 158, 12, health_width, 26))
                # Piano gloss highlight on health bar
                gloss_h = max(1, 26 // 3)
                gloss_surf = pygame.Surface((health_width - 2, gloss_h), pygame.SRCALPHA)
                gloss_surf.fill((255, 255, 255, 60))
                screen.blit(gloss_surf, (WIDTH - 158 + 1, 12 + 2))
            if player.extra_score_timer < 0.5:
                player.extra_score_timer += 1.0 / 60.0
                progress = min(1.0, player.extra_score_timer / 0.5)
                current_alpha = int(progress * 255 * 0.95)
            else:
                current_alpha = 255

            score_font = font_small_rainbow if player.rainbow_mode else font_small
            score_text = f"分數: {player.score}"
            timer_sec = int(player.invert_timer)
            timer_ms = int((player.invert_timer - timer_sec) * 1000)
            timer_text = f"{timer_sec:02d}秒{timer_ms:03d}"
            timer_y = 105 if player.rainbow_mode else 90
            
            if player.rainbow_mode:
                # 彩虹模式：同預設鋼琴烤漆規則，外框淡入後全顯
                player.rainbow_outline_timer += 1.0 / 60.0
                outline_alpha = int(min(player.rainbow_outline_timer / 0.25, 1.0) * current_alpha)
                draw_piano_score(screen, score_font, score_text,
                                 WIDTH - 80, 60,
                                 SCORE_RAINBOW_L1, SCORE_RAINBOW_L2,
                                 outline_alpha, player.is_fly_mode, current_alpha)
                if player.invert_timer > 0:
                    draw_piano_score(screen, score_font, timer_text,
                                     WIDTH - 80, timer_y,
                                     SCORE_RAINBOW_L1, SCORE_RAINBOW_L2,
                                     outline_alpha, player.is_fly_mode, current_alpha)
            else:
                # 預設模式：紅色鋼琴烤漆 + 白色L1外框 + 黑色L2外框（2倍寬）
                draw_piano_score(screen, score_font, score_text,
                                 WIDTH - 80, 60,
                                 SCORE_NORMAL_L1, SCORE_NORMAL_L2,
                                 current_alpha, player.is_fly_mode, current_alpha)
                if player.invert_timer > 0:
                    draw_piano_score(screen, score_font, timer_text,
                                     WIDTH - 80, timer_y,
                                     SCORE_NORMAL_L1, SCORE_NORMAL_L2,
                                     current_alpha, player.is_fly_mode, current_alpha)

            if state == "PAUSED":
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 128))
                screen.blit(s, (0, 0))
                draw_text("遊戲暫停", font_large, WHITE, screen, WIDTH // 2, HEIGHT // 2)

        elif state == "GAME_OVER":
            btn_start.y = HEIGHT // 2 + 102
            btn_fly.y = HEIGHT // 2 + 182

            if btn_start.collidepoint(mouse_pos):
                selected_menu_index = 0
            elif btn_fly.collidepoint(mouse_pos):
                selected_menu_index = 1

            draw_top_spikes(screen, 0)
            draw_outlined_text("遊戲結束", font_large_bold, ((0, 0, 139), (221, 160, 221)), screen, WIDTH // 2, HEIGHT // 3, NORMAL_OUTLINE_OFFSETS, RAINBOW_OUTLINE_OFFSETS, outline_color2=(128, 0, 128))
            if game_mode == 'fly':
                score_body = ((0, 100, 0), (144, 238, 144))
                score_out1 = WHITE
                score_out2 = (0, 100, 0)
            else:
                score_body = ((139, 0, 0), (255, 128, 128))
                score_out1 = WHITE
                score_out2 = (139, 0, 0)
            speed_changed = speed_multiplier != starting_speed_multiplier
            display_score = "---" if speed_changed else player.score
            display_rating = "---" if speed_changed else game_rating
            draw_outlined_text("獲得分數: ", font_large_bold, score_body, screen, WIDTH // 2 + 90, HEIGHT // 2, SCORE_L1_OFFSETS, SCORE_L2_OFFSETS, outline_color1=score_out1, outline_color2=score_out2, align="right")
            draw_outlined_text(f"{display_score}", font_large_bold, score_body, screen, WIDTH // 2 + 90, HEIGHT // 2, SCORE_L1_OFFSETS, SCORE_L2_OFFSETS, outline_color1=score_out1, outline_color2=score_out2, align="left")
            draw_outlined_text("獲得評等: ", font_half_large_bold, score_body, screen, WIDTH // 2 + 20, HEIGHT // 2 + 45, HALF_SCORE_L1_OFFSETS, HALF_SCORE_L2_OFFSETS, outline_color1=score_out1, outline_color2=score_out2, align="right")
            draw_outlined_text(f"{display_rating}", font_half_large_bold, score_body, screen, WIDTH // 2 + 20, HEIGHT // 2 + 45, HALF_SCORE_L1_OFFSETS, HALF_SCORE_L2_OFFSETS, outline_color1=score_out1, outline_color2=score_out2, align="left")

            pressed = btn_start.collidepoint(mouse_pos) and mouse_clicked
            is_hover_start = btn_start.collidepoint(mouse_pos) or selected_menu_index == 0
            color = ((0, 0, 255), (128, 0, 255)) if is_hover_start else ((0, 0, 139), (128, 0, 128))
            current_font = font_medium_bold if selected_menu_index == 0 else font_medium
            draw_3d_button(screen, btn_start, color, "繼續挑戰", current_font, WHITE,
                           border_radius=15, pressed=pressed)
            
            if mouse_clicked and btn_start.collidepoint(mouse_pos):
                state = "PLAYING"
                starting_speed_multiplier = speed_multiplier
                player, platforms = reset_game(game_mode)
                score_style_alt = False
                game_start_time = pygame.time.get_ticks()
                total_stairs_stepped = 0
                btn_start.y = HEIGHT // 2 - 30
                btn_fly.y = HEIGHT // 2 + 50
                mouse_clicked = False  # consume click
                
            fly_pressed = btn_fly.collidepoint(mouse_pos) and mouse_clicked
            is_hover_fly = btn_fly.collidepoint(mouse_pos) or selected_menu_index == 1
            fly_color = ((0, 0, 255), (128, 0, 255)) if is_hover_fly else ((0, 0, 139), (128, 0, 128))
            current_font_fly = font_medium_bold if selected_menu_index == 1 else font_medium
            draw_3d_button(screen, btn_fly, fly_color, "回到首頁", current_font_fly, WHITE,
                           border_radius=15, pressed=fly_pressed)
            
            if mouse_clicked and btn_fly.collidepoint(mouse_pos):
                state = "START"
                speed_multiplier = 1.0
                selected_menu_index = 0
                mouse_clicked = False  # consume click
 
        # ---- Top Bar UI (Always visible) ----
        # Pause Button
        p_clickable = (state in ["PLAYING", "PAUSED"])
        p_pressed = p_clickable and btn_pause.collidepoint(mouse_pos) and mouse_clicked
        if not p_clickable:
            p_color = DARK_GRAY
        elif btn_pause.collidepoint(mouse_pos):
            p_color = KIDS_GREEN
        else:
            p_color = KIDS_LIGHT_GREEN
        p_text = "繼續" if state == "PAUSED" else "暫停"
        draw_3d_button(screen, btn_pause, p_color, p_text, font_small, BLACK,
                       border_radius=8, pressed=p_pressed, disabled=not p_clickable)
        if p_clickable and mouse_clicked and btn_pause.collidepoint(mouse_pos):
            state = "PLAYING" if state == "PAUSED" else "PAUSED"
 
        # Stop Button
        s_clickable = (state in ["PLAYING", "PAUSED"])
        s_pressed = s_clickable and btn_stop.collidepoint(mouse_pos) and mouse_clicked
        if not s_clickable:
            s_color = DARK_GRAY
        elif btn_stop.collidepoint(mouse_pos):
            s_color = KIDS_PINK
        else:
            s_color = KIDS_LIGHT_PINK
        draw_3d_button(screen, btn_stop, s_color, "停止", font_small, BLACK,
                       border_radius=8, pressed=s_pressed, disabled=not s_clickable)
        if s_clickable and mouse_clicked and btn_stop.collidepoint(mouse_pos):
            state = "START"
            speed_multiplier = 1.0
 
        # Speed Buttons — only available in START, GAME_OVER
        if state in ["START", "GAME_OVER"]:
            for btn, mult, text in [(btn_speed_050, 0.5, "0.5倍"), (btn_speed_100, 1.0, "1.0倍"), (btn_speed_150, 1.5, "1.5倍")]:
                is_selected = (speed_multiplier == mult)
                sp_pressed = btn.collidepoint(mouse_pos) and mouse_clicked
                
                if is_selected:
                    sp_color = KIDS_YELLOW
                elif btn.collidepoint(mouse_pos):
                    sp_color = KIDS_BLUE
                else:
                    sp_color = KIDS_LIGHT_BLUE
                
                draw_3d_button(screen, btn, sp_color, text, font_small, BLACK,
                               border_radius=8, pressed=sp_pressed, disabled=False)
                
                if mouse_clicked and btn.collidepoint(mouse_pos):
                    speed_multiplier = mult
                    if state == "GAME_OVER":
                        score_style_alt = True
        elif state in ["PLAYING", "PAUSED"]:
            font_bold_small = pygame.font.SysFont("microsoftjhenghei", 16, bold=True)
            try:
                actual_speed_val = current_speed
            except NameError:
                actual_speed_val = speed_multiplier
            speed_text = f"實際倍速: {actual_speed_val:.2f}"
            draw_outlined_text(speed_text, font_bold_small, WHITE, screen, 140, 15 + font_bold_small.get_height() // 2, SCORE_L1_OFFSETS, SCORE_L2_OFFSETS, outline_color1=BLACK, outline_color2=WHITE, align="left")

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
