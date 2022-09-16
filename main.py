from math import cos, sin, radians, ceil, floor
import assets.audio_loader as sounds
import assets.image_loader as assets
import assets.font_loader as fonts
import assets.path_loader as paths
import assets.map_loader as maps
from threading import Thread
from random import randint
from time import sleep
import json
try:
    import pygame
except ImportError:  # Attempt to install pygame if it doesn't exist with tkinter UI
    from tkinter import messagebox, Toplevel, Message
    import subprocess
    import sys
    loop = True

    while loop:
        user = messagebox.askyesno('Install Pygame?', 'Pygame is required for this game.\n'
                                                      'Would you like to install Pygame?')
        if user:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
                import pygame
                messagebox.showinfo('Success', 'Pygame was successfully installed.')
                loop = None
                user = None
            except subprocess.CalledProcessError or ModuleNotFoundError as error:
                user = messagebox.askretrycancel('Could not Install', 'There was an error installing pygame.\n'
                                                                      'If the problem persists, you may have to'
                                                                      ' manually install it.\n\n'
                                                                      'Would you like to retry?', icon='error')
                if not user:
                    quit()
        else:
            confirm = messagebox.askyesno('Are you sure?', 'If you do not install pygame,\n'
                                                           'you will not be able to play this game!',
                                          icon='warning', default=messagebox.NO)
            if confirm:
                quit()

pygame.init()  # Initialise all libraries for pygame
pygame.joystick.init()
pygame.mixer.init()

# -------- GLOBAL VARIABLES -------- #
# Menu colour constants
RED = 255, 0, 0
WHITE = 255, 255, 255
V_LIGHT_GREY = 200, 200, 200
LIGHT_GREY = 170, 170, 170
GREY = 100, 100, 100
BLACK = 0, 0, 0
# Car colour constants
RED_CAR = 232, 106, 23
YELLOW_CAR = 255, 204, 0
GREEN_CAR = 57, 194, 114
BLUE_CAR = 47, 149, 208
BLACK_CAR = 93, 91, 91
# Other variables
Debug = False  # Enables Debug mode for detecting issues. (Changes various things other than visual changes)
Force_resolution = []  # Manual window size ([] = Automatic, [width, height] = Forced)
Screen = 0  # If the user has multiple monitors, sets which monitor to use (starts at 0)
Menu_animation = False  # Enables animations on the main menu
Mute_volume = False  # Set default muted state
Music_volume = 0.5  # Set default Volume level for music
Sfx_volume = 0.5  # Set default Volume level for all sounds effects
FPS = 60  # Controls the speed of the game ***changing from 60 will break EVERYTHING!***
Intro_screen = False  # Enables the intro screen on game boot
Countdown = False  # Enables the traffic light countdown on game start
Load_settings = True  # Enables setting loading + saving
Game_end = False  # Lets the game know if the game finished or if the player quit


# -------- SETTINGS FUNCTIONS -------- #
def save_settings():
    if Load_settings:
        with open('settings.json', 'r+') as file:
            data = json.load(file)
            data['Debug'] = Debug
            if Display_resolution == Desktop_info[Screen]:  # If resolution is automatic
                data['Resolution'] = 0
            else:  # If resolution is forced...
                data['Resolution'] = Display_resolution
            data['Screen'] = Screen
            data['Menu animations'] = Menu_animation
            data['Mute volume'] = Mute_volume
            data['Music volume'] = Music_volume
            data['Sfx volume'] = Sfx_volume
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()


def load_settings():
    if Load_settings:
        global Debug, Force_resolution, Screen, Menu_animation, Mute_volume, Music_volume, Sfx_volume
        with open('settings.json') as file:
            file = json.load(file)
            Debug = file['Debug']
            Force_resolution = file['Resolution']
            Screen = file['Screen']
            Menu_animation = file['Menu animations']
            Mute_volume = file['Mute volume']
            Music_volume = file['Music volume']
            Sfx_volume = file['Sfx volume']
            print('Successfully loaded settings from file.')


if Load_settings:
    try:
        load_settings()
    except FileNotFoundError:
        with open('settings.json', 'w') as settings:
            default_settings = {'Debug': False,
                                'Resolution': 0,
                                'Screen': 0,
                                'Menu animations': True,
                                'Mute volume': False,
                                'Music volume': 0.5,
                                'Sfx volume': 0.5}
            json.dump(default_settings, settings, indent=2)

Desktop_info = pygame.display.get_desktop_sizes()
if not Force_resolution:  # Automatically detect screen resolution and set display size
    if len(Desktop_info) < Screen + 1:  # Always default to 1st screen if previously set to other and only have one
        Screen = 0
    Display_resolution = Desktop_info[Screen]
else:
    if len(Desktop_info) < Screen + 1:  # Always default to 1st screen if previously set to second and only have one
        Screen = 0
        save_settings()
    Display_resolution = Force_resolution

if Desktop_info[Screen] != Display_resolution:
    Display = pygame.display.set_mode(Display_resolution, display=Screen)
else:
    Display = pygame.display.set_mode(Display_resolution, display=Screen, flags=pygame.FULLSCREEN)

print('Running at ' + str(Display_resolution[0]) + ' x ' + str(Display_resolution[1]))
pygame.display.set_caption('Retro Rampage')  # Set display name
try:
    pygame.display.set_icon(pygame.image.load(assets.icon()))  # Set display icon
except FileNotFoundError:
    Display.fill(BLACK)
    try:
        Display.blit(pygame.font.Font(fonts.load(), 50).render("ERR: 'icon.ico' not found in files",
                                                               True, WHITE), (0, 0))
    except FileNotFoundError:
        Display.blit(pygame.font.Font(None, 50).render("ERR: 'icon.ico' not found in files", True, WHITE), (0, 0))
    pygame.time.wait(3000)
    pygame.quit()
    quit()

'''
Create virtual window at 1080p that game writes to, then when screen is updated scale the window 
to the size of the screen and write to screen, also scale mouse positions and screen updates 
between window and screen. This means that the game will always render at 1080p, however can output 
any resolution by scaling. There is also a secondary window for fade effects and visual animations that works the same.

Note: any scaling between any window and the screen (apart from writing directly to it, which this game doesn't do)
      is not 100% exact due to rounding! Rounding will always round UP to avoid artifacts, but could overlap pixels 
      in the process. This usually results in thin lines not showing up or being thinner than they are supposed to.
'''
WIDTH, HEIGHT = 1920, 1080  # System default resolution that will scale to display *MUST BE 1080p!*
CENTRE = WIDTH // 2, HEIGHT // 2  # Calculate centre pixel for reference
Window = pygame.Surface((WIDTH, HEIGHT))
Window_resolution = Window.get_size()
Window_screenshot = Window.copy()
Window_sleep = False  # Slow down screen updates when not focused
Secondary_window = pygame.Surface((WIDTH, HEIGHT))
current_window = ''
if Display_resolution != Window_resolution:
    Display_scaling = True
else:
    Display_scaling = False
Players = []
Selected_player = []
Player_amount = 0
Npc_amount = 3
Map = 'snake'
Total_laps = 3
Current_lap = 0
Race_time = 0
Music_loop = True
Player_positions = []
Npc_names = [['John', False], ['Mark', False], ['Lilly', False], ['Jessica', False], ['Matthew', False],
             ['James', False], ['Jack', False], ['Holly', False], ['Aimee', False], ['Harrison', False],
             ['Emily', False], ['Ben', False], ['Tom', False], ['Anthony', False], ['Michael', False],
             ['Noah', False], ['Oliver', False], ['Jake', False], ['Olivia', False], ['Teddy', False],
             ['Tyler', False], ['Carmel', False], ['Jeremy', False], ['Joe', False], ['Steven', False],
             ['Scott', False], ['Keith', False]]
controllers = []
controls = []
controller_prompts = []
Npc_force_veh = 0
Npc_force_colour = None
lightning_frames = []
for frame in range(0, 15):
    lightning_frames.append(pygame.transform.scale(pygame.image.load(assets.animation('lightning', frame)), (128, 128)))
smoke_frames = []
for frame in range(0, 7):
    smoke_frames.append(pygame.transform.scale(pygame.image.load(assets.animation('smoke', frame)), (64, 64)))
repair_frames = []
for frame in range(0, 11):
    repair_frames.append(pygame.transform.scale(pygame.image.load(assets.animation('repair', frame)), (128, 128)))
# Define tile and menu variables
map_preview_size = 974, 600
map_preview_pos = CENTRE[0] - map_preview_size[0] // 2, CENTRE[1] - map_preview_size[1] // 2
map_preview = '', pygame.surface.Surface(map_preview_size)
tile_scale = ceil(WIDTH / 15), ceil(HEIGHT / 10)
menu_scroll_speed = 70  # Default = 20
menu_car_speed = 10  # Default = 6
button_trigger = False  # only press single button with single click
selected_text_entry = 0
current_song = ''
clock = pygame.time.Clock()  # Used for timing display updates and keeping constant FPS
music_thread = Thread()

# Define game variables
powerups = True
Game_paused = False
global_car_rotation_speed = 1
global_car_move_speed = 4

# Define updating and loaded asset lists
screen_updates = []
loaded_assets = []
loaded_sounds = []
recorded_keys = []  # Empty list for creating NPC paths


# -------- CLASSES -------- #
class Player:
    def __init__(self, player: int):
        self.id = player
        if 0 > self.id or 5 < self.id:
            raise ValueError('Player | self._id can only be between 0 and 5 not ' + str(self.id))
        self.name = None
        self.veh_name = None
        self.veh_image = None
        self.veh_colour = None
        self.start_pos = None
        self.controls = None
        self.default_controls = None
        self.load_defaults()

    def load_defaults(self):
        if self.id == 0:
            self.veh_name = 'Family Car'
            self.veh_colour = RED_CAR
            if 'wasd' not in controls:
                self.controls = 'wasd'
            elif 'arrows' not in controls:
                self.controls = 'arrows'
        elif self.id == 1:
            self.name = ''
            self.veh_name = 'Sports Car'
            self.veh_colour = YELLOW_CAR
            if 'wasd' not in controls:
                self.controls = 'wasd'
            elif 'arrows' not in controls:
                self.controls = 'arrows'
        elif self.id == 2:
            self.veh_name = 'Luxury Car'
            self.veh_colour = GREEN_CAR
            if 'wasd' not in controls:
                self.controls = 'wasd'
            elif 'arrows' not in controls:
                self.controls = 'arrows'
        elif self.id == 3:
            self.veh_name = 'Truck'
            self.veh_colour = BLUE_CAR
            if 'wasd' not in controls:
                self.controls = 'wasd'
            elif 'arrows' not in controls:
                self.controls = 'arrows'
        elif self.id == 4:
            self.veh_name = 'Race Car'
            self.veh_colour = BLACK_CAR
            if 'wasd' not in controls:
                self.controls = 'wasd'
            elif 'arrows' not in controls:
                self.controls = 'arrows'
        elif self.id == 5:
            self.veh_name = 'Family Car'
            self.veh_colour = RED_CAR
            if 'wasd' not in controls:
                self.controls = 'wasd'
            elif 'arrows' not in controls:
                self.controls = 'arrows'

        if self.controls:
            controls.append(self.controls)
        else:
            self.controls = 'controller'
        self.name = ''
        self.veh_image = pygame.transform.scale(pygame.image.load(assets.car(self.veh_colour, self.veh_name)),
                                                (175, 300))
        self.start_pos = 6 - self.id
        self.default_controls = self.controls

    def update_image(self):
        self.veh_image = pygame.transform.scale(pygame.image.load(assets.car(self.veh_colour, self.veh_name)),
                                                (175, 300))


class MenuCar:  # Create car sprite
    def __init__(self):
        self.scale = 71, 131
        self.pos_x = CENTRE[0]
        self.pos_y = CENTRE[1]
        self.rotation = 0  # Default rotation
        self.image = pygame.transform.scale(pygame.image.load(assets.car('red', 'family car')).convert(), self.scale)
        self.image.set_colorkey(BLACK)  # Remove background from image
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()  # Set surface size to image size
        self.scaled_rect = None
        self.prev_rect = self.rect
        if Debug:
            pygame.draw.rect(self.image, WHITE, self.rect, 1)  # Draw outline of sprite (debugging)
        self.rect.center = self.pos_x, self.pos_y  # Centre car on screen
        self.speed = menu_car_speed

    def rotate(self, degree):  # Func to rotate car
        if self.rotation != degree:  # Only change rotation if it is different from current rotation for efficiency
            self.prev_rect = pygame.rect.Rect(self.rect)  # Remember previous position as clear rect
            self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                assets.car('red', 'family car')).convert(), self.scale), degree)  # Rotate image
            self.image.set_colorkey(BLACK)  # Remove bg from rotated image
            self.rotation = degree  # Set current rotation as rotation
            self.rect = self.image.get_rect()  # Set surface size to image size
            if Debug:
                pygame.draw.rect(self.image, WHITE, self.rect, 1)  # Draw outline of sprite (debugging)
            self.rect.center = self.pos_x, self.pos_y
            self.size = self.image.get_size()

    def move(self, x, y):
        self.prev_rect = pygame.rect.Rect(self.rect)  # Remember previous position as clear rect
        screen_updates.append(self.prev_rect)  # Add clear rectangle to update list to clear previous pos
        self.pos_x = x
        self.pos_y = y
        self.rect.center = x, y

    def draw(self, update=False):
        Window.blit(self.image, (self.rect.left, self.rect.top))  # Draw new car on screen
        if update:
            if Display_scaling:
                self.scaled_rect = [self.rect[0], self.rect[1], self.rect[2], self.rect[3]]
                update_screen(scale_rect(self.scaled_rect))
                self.scaled_rect = [self.prev_rect[0], self.prev_rect[1], self.prev_rect[2], self.prev_rect[3]]
                update_screen(scale_rect(self.scaled_rect))
            else:
                update_screen(rect=self.prev_rect)
                update_screen(rect=self.rect)
        else:
            if Display_scaling:
                self.scaled_rect = [self.rect[0], self.rect[1], self.rect[2], self.rect[3]]  # Get rect size and pos
                screen_updates.append(scale_rect(self.scaled_rect))  # Scale and update to screen
                self.scaled_rect = [self.prev_rect[0], self.prev_rect[1], self.prev_rect[2], self.prev_rect[3]]
                screen_updates.append(scale_rect(self.scaled_rect))
            else:
                screen_updates.append(self.prev_rect)
                screen_updates.append(self.rect)

    def animate(self, direction: str, bg: any):
        if direction == 'up':
            if self.rotation != 0:
                if self.rotation < 180:
                    for rotation in reversed(range(0, self.rotation, self.speed)):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)
                else:
                    for rotation in range(self.rotation, 360 + 1, self.speed):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)
                    self.rotation = 0

        elif direction == 'down':
            if self.rotation != 180:
                if self.rotation < 180:
                    for rotation in range(self.rotation, 180 + 1, self.speed):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))  # Draw background and assets to remove old car frame
                        self.rotate(rotation)  # Rotate car by set degree
                        self.draw(update=True)  # Only update area around car

                else:
                    for rotation in reversed(range(180, self.rotation, self.speed)):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))  # Draw background and assets to remove old car frame
                        self.rotate(rotation)  # Rotate car by set degree
                        self.draw(update=True)  # Only update area around car

        elif direction == 'left':
            if self.rotation != 90:
                if self.rotation > 90:
                    for rotation in reversed(range(90, self.rotation, self.speed)):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)
                else:
                    for rotation in range(self.rotation, 90 + 1, self.speed):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)

        elif direction == 'right':
            if self.rotation != 270:
                if self.rotation > 270:
                    for rotation in reversed(range(270, self.rotation, menu_car_speed)):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)
                elif self.rotation < 90:
                    for rotation in reversed(range(-90, self.rotation, menu_car_speed)):
                        clock.tick(FPS)
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)
                    self.rotation = 270
                else:
                    for rotation in range(self.rotation, 270 + 1, menu_car_speed):
                        clock.tick(FPS)  # Ensure constant FPS between animations
                        Window.blit(bg, (0, 0))
                        self.rotate(rotation)
                        self.draw(update=True)


class Car(pygame.sprite.Sprite):
    def __init__(self, player: Player):
        super().__init__()
        self.type = 'Player'
        self.player = player
        if self.player.id > 6 or self.player.id < 0:
            raise ValueError('Car | self._id should only be between 0 and 5, not ' + str(self.player.id))
        # STARTING variables
        self.start_pos = self.player.start_pos
        if Map == 'racetrack':
            self._origin_pos = paths.Racetrack.start_pos(self.start_pos)
        elif Map == 'snake':
            self._origin_pos = paths.Snake.start_pos(self.start_pos)
        elif Map == 'dog bone':
            self._origin_pos = paths.DogBone.start_pos(self.start_pos)
        elif Map == 'hairpin':
            self._origin_pos = paths.Hairpin.start_pos(self.start_pos)
        self._origin_rotation = self._origin_pos[2]  # Original rotation
        self._origin_pos = self._origin_pos[:2]
        self.vehicle = self.player.veh_name
        self._move_speed = global_car_move_speed
        self._rotation_speed = global_car_rotation_speed
        if self.vehicle == 'Family Car':
            self.max_speed = 3
            self.max_rotation_speed = 2
            self.durability = 4
        elif self.vehicle == 'Sports Car':
            self.max_speed = 4
            self.max_rotation_speed = 3
            self.durability = 2
        elif self.vehicle == 'Luxury Car':
            self.max_speed = 3
            self.max_rotation_speed = 3
            self.durability = 3
        elif self.vehicle == 'Truck':
            self.max_speed = 2
            self.max_rotation_speed = 2
            self.durability = 5
        elif self.vehicle == 'Race Car':
            self.max_speed = 5
            self.max_rotation_speed = 3
            self.durability = 1
        self.set_move_speed(self.max_speed)
        self.set_rotation_speed(self.max_rotation_speed)
        # SURFACE variables
        self.colour = self.player.veh_colour
        self.image_dir = assets.car(self.colour, self.vehicle)
        self.image = pygame.transform.scale(pygame.image.load(self.image_dir).convert(), (40, 70))
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)  # Get mask from image
        self._dmg_img = None
        self.damage = 0
        self.size = self.image.get_size()
        # RECT variables
        self.rect = self.image.get_rect()
        self.rect.center = self._origin_pos
        self.pos_x = self.rect.x
        self.pos_y = self.rect.y
        self.rotation = self._origin_rotation
        # COLLISION variables
        self.mask_overlap = None  # Used for checking collision position
        self.mask_area = None  # Used to ensure the player cannot get outside the map
        self.mask_size = None
        self.collision = False
        # MOVEMENT variables
        self._record = False
        if self._record:
            self.keystrokes = []
        self._up = None
        self._down = None
        self._left = None
        self._right = None
        self.input_type = None
        self.controller = None
        self.set_controls(self.player.controls)
        self._allow_forwards = True
        self._allow_reverse = True
        self._pressed_keys = None
        self._boost_timeout = 0
        self.bullet_penalty = 0
        self._bullet_damage = 0
        self._current_speed = 0
        self._boost_frames = []  # Boost animation frames
        self._boost_ani_frame = -1
        for frames in range(0, 4):
            self._boost_frames.append(pygame.transform.scale(pygame.image.load(assets.animation(
                'flame', frames, car_num=self.vehicle)), (self.size[0], self.size[1] + 20)))
        self._smoke_ani_frame = -1
        self._repair_ani_frame = -1
        self._ani_frame = None
        self._ani_frame_rect = None
        # NAME variables
        self.name = self.player.name
        self._name_rect = None
        # LAP variables
        self._lap_halfway = True
        self.laps = 0
        # CHECKPOINT variables
        self.checkpoint_count = -1
        self.checkpoint_time = 0
        # SOUND variables
        self._collision_sound = False
        # Move car to starting position
        self.move(self._origin_pos[0], self._origin_pos[1])
        if self.rotation != 0:  # If start rotation is not 0 then rotate
            self.rotate(self.rotation)

    def set_move_speed(self, speed):
        if speed < 1:
            speed = 1
        if speed != 10:  # Save current speed for boost powerup
            self._current_speed = speed
        self._move_speed = global_car_move_speed + speed

    def set_rotation_speed(self, speed):
        self._rotation_speed = global_car_rotation_speed + speed

    def set_controls(self, control: str or pygame.joystick.Joystick):  # Set controls to appropriate keys
        if control == 'wasd':
            self.input_type = 'keyboard'
            self._up = pygame.K_w
            self._down = pygame.K_s
            self._left = pygame.K_a
            self._right = pygame.K_d
        elif control == 'arrows':
            self.input_type = 'keyboard'
            self._up = pygame.K_UP
            self._down = pygame.K_DOWN
            self._left = pygame.K_LEFT
            self._right = pygame.K_RIGHT
        elif control in controllers:
            self.input_type = 'controller'
            self.controller = control
        else:
            raise ValueError("Car | controls is not == 'wasd' or 'arrows' or controller. : " + str(control))

    def check_checkpoints(self, checkpoint_rectangles):
        for checkpoint in checkpoint_rectangles:
            if checkpoint.colliderect(self.rect) and self.checkpoint_count != checkpoint_rectangles.index(checkpoint):
                self.checkpoint_count = checkpoint_rectangles.index(checkpoint)
                self.checkpoint_time = pygame.time.get_ticks()
                if not self._lap_halfway and self.checkpoint_count == floor(len(checkpoint_rectangles) / 2):
                    self._lap_halfway = True
                if self._lap_halfway and self.checkpoint_count == 0:
                    self._lap_halfway = False
                    self.laps += 1

    def check_track_collisions(self, track_mask):  # Check if there are collisions and take action
        if not self.collision or self.collision == 'track':
            if Debug:  # If debug then outline car mask in red
                for pos in self.mask.outline():
                    pos_x, pos_y = pos
                    pygame.draw.circle(self.image, RED, (pos_x, pos_y), 1)
            self.mask_overlap = self.mask.overlap(track_mask, (-self.rect.left, -self.rect.top))
            if self.mask_overlap:
                self.collision = 'track'
                if not self._collision_sound:
                    play_sound('collision')
                    if self.controller:
                        self.controller.rumble(0, 0.2, 250)
                    self._collision_sound = True
                    if self.damage < self.durability:
                        self.damage += 1
                    if self.damage:
                        self._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                            assets.car_damage(self.vehicle, self.damage)), self.size), self.rotation)
                        self._dmg_img.set_colorkey(WHITE)
                        self.image.blit(self._dmg_img, (0, 0))  # Overlay damage on top of image

                # If there is a collision between masks...
                self.mask_area = self.mask.overlap_area(track_mask, (-self.rect.left, -self.rect.top))
                self.mask_size = self.mask.count()

                if Debug:  # If debug then show collision position via small yellow square
                    pygame.draw.rect(self.image, YELLOW_CAR, (self.mask_overlap[0], self.mask_overlap[1], 5, 5))
                    screen_updates.append((self.mask_overlap[0], self.mask_overlap[1], 5, 5))

                if self.rotation <= 45 or self.rotation >= 315:  # If car is pointing up...
                    # print('pointing up')
                    if self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                elif 45 < self.rotation < 135:  # If the car is pointing left...
                    # print('pointing left')
                    if self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                elif 135 <= self.rotation <= 225:  # If the car is pointing down...
                    # print('pointing down')
                    if self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                elif 225 < self.rotation < 315:  # If the car is pointing right...
                    # print('pointing right')
                    if self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')

                if self.mask_area > self.mask_size // 1.5:  # If over half of the car is colliding with the mask...
                    self.move(self._origin_pos[0], self._origin_pos[1])  # Reset the car to starting position + rotation
                    self.rotate(self._origin_rotation)
                    # print('reset to origin')

            else:  # If there are no collisions with the track
                self.collision = False
                self._collision_sound = False
                if not self._allow_forwards:  # Ensure that the player can move forwards and backwards
                    self._allow_forwards = True
                if not self._allow_reverse:
                    self._allow_reverse = True

    def check_car_collision(self, sprite):
        if not self.collision or self.collision == sprite:
            self.mask_overlap = pygame.sprite.collide_mask(self, sprite)
            if self.mask_overlap:
                self.collision = sprite
                if not self._collision_sound:
                    play_sound('collision')
                    if self.controller:
                        self.controller.rumble(0, 0.2, 250)
                    self._collision_sound = True
                    if self.damage < self.durability:
                        self.damage += 1
                    if self.damage:
                        self._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                            assets.car_damage(self.vehicle, self.damage)), self.size), self.rotation)
                        self._dmg_img.set_colorkey(WHITE)
                        self.image.blit(self._dmg_img, (0, 0))  # Overlay damage on top of image
                # If there is a collision between masks...
                self.mask_area = self.mask.overlap_area(sprite.mask, (-self.rect.left, -self.rect.top))
                self.mask_size = self.mask.count()

                if Debug:  # If debug then show collision position via small yellow square
                    pygame.draw.rect(self.image, YELLOW_CAR, (self.mask_overlap[0], self.mask_overlap[1], 5, 5))
                    screen_updates.append((self.mask_overlap[0], self.mask_overlap[1], 5, 5))

                if self.rotation <= 45 or self.rotation >= 315:  # If car is pointing up...
                    # print('pointing up')
                    if self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                elif 45 < self.rotation < 135:  # If the car is pointing left...
                    # print('pointing left')
                    if self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                elif 135 <= self.rotation <= 225:  # If the car is pointing down...
                    # print('pointing down')
                    if self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                elif 225 < self.rotation < 315:  # If the car is pointing right...
                    # print('pointing right')
                    if self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self._allow_forwards = False  # Do not allow forwards
                        self._allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self._allow_forwards = True  # Do not allow reverse
                        self._allow_reverse = False
                        # print('do not allow reverse')

                if self.mask_area > self.mask_size // 1.5:  # If over half of the car is colliding with the mask...
                    self.move(self._origin_pos[0], self._origin_pos[1])  # Reset the car to starting position + rotation
                    self.rotate(self._origin_rotation)
                    # print('reset to origin')

            else:  # If there are no collisions with the track
                self.collision = False
                self._collision_sound = False
                if not self._allow_forwards:  # Ensure that the player can move forwards and backwards
                    self._allow_forwards = True
                if not self._allow_reverse:
                    self._allow_reverse = True

    def move(self, x, y):  # Move car to new position
        self.pos_x = x
        self.pos_y = y
        self.rect.center = x, y

    def rotate(self, degree):  # Rotate car to new angle
        self.rotation = degree  # Set current rotation as rotation
        if global_car_rotation_speed + 1 >= self.rotation:  # Create snapping points to drive in straight lines
            self.rotation = 360
        elif self.rotation >= 360 - (global_car_rotation_speed + 1):
            self.rotation = 0
        elif 90 - (global_car_rotation_speed + 1) <= self.rotation <= 90 + (global_car_rotation_speed + 1):
            self.rotation = 90
        elif 180 - (global_car_rotation_speed + 1) <= self.rotation <= 180 + (global_car_rotation_speed + 1):
            self.rotation = 180
        elif 270 - (global_car_rotation_speed + 1) <= self.rotation <= 270 + (global_car_rotation_speed + 1):
            self.rotation = 270
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
            self.image_dir).convert(), self.size), self.rotation)  # Rotate image
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)  # Update mask to new rotation
        if 0 < self.damage <= self.durability:
            self._dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                assets.car_damage(self.vehicle, self.damage)), self.size), self.rotation)  # Load and rotate damage
            self._dmg_img.set_colorkey(WHITE)
            self.image.blit(self._dmg_img, (0, 0))  # Overlay damage on top of image
        self.rect = self.image.get_rect()  # Set surface size to image size
        if Debug:
            pygame.draw.rect(self.image, WHITE, self.rect, 1)  # Draw outline of sprite (debugging)
        self.rect.center = self.pos_x, self.pos_y

    def power_up(self, ver):
        if ver == 'repair':
            play_sound('repair')
            if self.controller:
                self.controller.rumble(0, 0.7, 200)
            self.damage = 0
            self._repair_ani_frame = 0
        elif ver == 'boost':
            play_sound('boost')
            if not self._boost_timeout:
                self._boost_timeout = pygame.time.get_ticks() + 2000 + (5000 - self._current_speed * 1000)
                self.set_move_speed(10)
                self.set_rotation_speed(5)
                self._boost_ani_frame = 0
            else:
                self._boost_timeout += 2000 + (5000 - self._current_speed * 1000)

            if self.controller:
                self.controller.rumble(0, 0.2, self._boost_timeout - pygame.time.get_ticks())
        elif ver == 'bullet':
            if self._boost_timeout:
                self._boost_timeout = 0
                self._boost_ani_frame = -1
            play_sound('bullet')
            if self.controller:
                self.controller.rumble(1, 1, 500)
            self._bullet_damage = self.damage
            self.bullet_penalty = pygame.time.get_ticks() + 2000 + (5000 - self._current_speed * 1000)
            self._smoke_ani_frame = 0
            self.damage = self.durability
            self.rotate(self.rotation + 1)
            self.rotate(self.rotation - 1)
        elif ver == 'lightning':
            if self.controller:
                self.controller.rumble(0.3, 0.5, 700)

    def check_inputs(self):  # Check all inputs and take action
        if self.input_type == 'keyboard':
            self._pressed_keys = pygame.key.get_pressed()  # Get all pressed keys on keyboard

            if self._pressed_keys[self._up] and self._pressed_keys[self._down]:  # If up and down pressed at same time
                return  # Do not move the car

            if self._pressed_keys[self._up] and self._allow_forwards:  # If up key is pressed
                if self._record:
                    self.keystrokes.append(0)
                self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self._move_speed),
                          self.pos_y + round(sin(radians(self.rotation - 90)) * self._move_speed))
                # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))

                if self._pressed_keys[self._left]:  # If left key is pressed
                    if self._record:
                        self.keystrokes.append(2)
                    self.rotate(self.rotation + self._rotation_speed)  # Rotate car to new position
                    # print(self.rotation)

                elif self._pressed_keys[self._right]:  # If right key is pressed
                    if self._record:
                        self.keystrokes.append(3)
                    self.rotate(self.rotation - self._rotation_speed)
                    # print(self.rotation)
                if self._record:
                    recorded_keys.append(self.keystrokes)
                    self.keystrokes = []

            elif self._pressed_keys[self._down] and self._allow_reverse:  # If down key is pressed
                if self._record:
                    self.keystrokes.append(1)
                self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self._move_speed),  # Always move back
                          self.pos_y - round(sin(radians(self.rotation - 90)) * self._move_speed))  # Despite rotation
                # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))

                if self._pressed_keys[self._left]:  # If left key is pressed
                    if self._record:
                        self.keystrokes.append(2)
                    self.rotate(self.rotation - self._rotation_speed)  # Rotate car to new position
                    # print(self.rotation)

                elif self._pressed_keys[self._right]:  # If right key is pressed
                    if self._record:
                        self.keystrokes.append(3)
                    self.rotate(self.rotation + self._rotation_speed)
                    # print(self.rotation)
                if self._record:
                    recorded_keys.append(self.keystrokes)
                    self.keystrokes = []

        elif self.input_type == 'controller':
            if self.controller.get_axis(5) > 0.6 and self.controller.get_axis(4) > 0.6:
                return  # Do not move the car

            if self.controller.get_axis(5) > 0.6 and self._allow_forwards:
                if self._record:
                    self.keystrokes.append(0)
                self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self._move_speed),
                          self.pos_y + round(sin(radians(self.rotation - 90)) * self._move_speed))

                if self.controller.get_axis(0) < -0.6:  # If left key is pressed
                    if self._record:
                        self.keystrokes.append(2)
                    self.rotate(self.rotation + self._rotation_speed)  # Rotate car to new position

                elif self.controller.get_axis(0) > 0.6:  # If right key is pressed
                    if self._record:
                        self.keystrokes.append(3)
                    self.rotate(self.rotation - self._rotation_speed)

                if self._record:
                    recorded_keys.append(self.keystrokes)
                    self.keystrokes = []

            elif self.controller.get_axis(4) > 0.6 and self._allow_reverse:  # If down key is pressed
                if self._record:
                    self.keystrokes.append(1)
                self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self._move_speed),  # Always move back
                          self.pos_y - round(sin(radians(self.rotation - 90)) * self._move_speed))  # Despite rotation

                if self.controller.get_axis(0) < -0.6:  # If left key is pressed
                    if self._record:
                        self.keystrokes.append(2)
                    self.rotate(self.rotation - self._rotation_speed)  # Rotate car to new position

                elif self.controller.get_axis(0) > 0.6:  # If right key is pressed
                    if self._record:
                        self.keystrokes.append(3)
                    self.rotate(self.rotation + self._rotation_speed)

                if self._record:
                    recorded_keys.append(self.keystrokes)
                    self.keystrokes = []

    def draw(self, surf=Window):
        surf.blit(self.image, (self.rect.left, self.rect.top))  # Car image

        draw_triangle((self.rect.centerx, self.rect.top - 14), 'down',  # Name
                      width=10, height=10, border=self.colour, border_width=3, surface=surf)
        self._name_rect = draw_text(self.rect.centerx, self.rect.top - 35, self.name, WHITE, 12, surf=surf)

        if self._boost_ani_frame == 4 and self._boost_timeout:  # If boost animation finished
            self._boost_ani_frame = 0  # Replay animation
        elif not self._boost_timeout and self._boost_ani_frame != -1:  # If boost timeout finished
            self._boost_ani_frame = -1  # Reset animation
        if self._boost_timeout and self._boost_ani_frame >= 0:  # If boost animation playing
            self._ani_frame = pygame.transform.rotate(self._boost_frames[self._boost_ani_frame], self.rotation)
            self._ani_frame_rect = self._ani_frame.get_rect()
            self._ani_frame_rect.center = self.rect.center
            surf.blit(self._ani_frame, (self._ani_frame_rect.left, self._ani_frame_rect.top))
            self._boost_ani_frame += 1  # Increase animation to next frame

        if self._smoke_ani_frame >= 14 and self.bullet_penalty:  # If smoke animation finished
            self._smoke_ani_frame = 0  # Replay animation
        elif not self.bullet_penalty and self._smoke_ani_frame >= 14:  # If smoke timeout finished
            self._smoke_ani_frame = -1  # Reset animation at end of loop
        if self._smoke_ani_frame >= 0:  # If smoke animation playing
            self._ani_frame = smoke_frames[floor(self._smoke_ani_frame/2)]
            self._ani_frame_rect = self._ani_frame.get_rect()
            self._ani_frame_rect.centerx = self.rect.centerx
            self._ani_frame_rect.bottom = self.rect.centery
            surf.blit(self._ani_frame, (self._ani_frame_rect.left, self._ani_frame_rect.top))
            self._smoke_ani_frame += 1  # Increase animation to next frame

        if self._repair_ani_frame >= 22:  # If repair animation finished...
            self._repair_ani_frame = -1  # Reset animation
        if self._repair_ani_frame >= 0:
            self._ani_frame = repair_frames[floor(self._repair_ani_frame/2)]
            self._ani_frame_rect = self._ani_frame.get_rect()
            self._ani_frame_rect.center = self.rect.center
            surf.blit(self._ani_frame, (self._ani_frame_rect.left, self._ani_frame_rect.top))
            self._repair_ani_frame += 1  # Increase animation to next frame

    def update(self):  # Called each loop and checks if anything has changed
        if self._boost_timeout and self._boost_timeout < pygame.time.get_ticks():  # If boost timeout has expired
            self._boost_timeout = 0  # Reset current speed to previous state
            self.set_move_speed(self._current_speed)
            self.set_rotation_speed(self.max_rotation_speed)
        elif self.bullet_penalty and self.bullet_penalty < pygame.time.get_ticks():
            self.bullet_penalty = 0
            self.damage = self._bullet_damage
            self.rotate(self.rotation + 1)
            self.rotate(self.rotation - 1)
        elif not self._boost_timeout:
            if self.damage:  # Change player speed based on damage and durability
                self.set_move_speed(round(self.max_speed - (self.max_speed / (self.durability / self.damage))))
                self.set_rotation_speed(self.max_rotation_speed)
            elif self._move_speed != self.max_speed or self._rotation_speed != self.max_rotation_speed:
                self.set_move_speed(self.max_speed)
                self.set_rotation_speed(self.max_rotation_speed)
        if not self.bullet_penalty:
            self.check_inputs()


class NpcCar(pygame.sprite.Sprite):
    def __init__(self, vehicle: str or int, colour: tuple[int, int, int], size: tuple[int, int],
                 name: str, track: str, start_position: int):
        super().__init__()
        self.type = 'NPC'
        self.start_position = start_position
        if track == 'racetrack':
            self.paths = paths.Racetrack()
        elif track == 'snake':
            self.paths = paths.Snake()
        elif track == 'dog bone':
            self.paths = paths.DogBone()
        elif track == 'hairpin':
            self.paths = paths.Hairpin()
        self.vehicle = vehicle.lower() if type(vehicle) == str else vehicle
        self.move_speed = global_car_move_speed
        self.rotation_speed = global_car_rotation_speed
        if type(self.vehicle) == str:
            self.vehicle = self.vehicle.lower()
        if self.vehicle == 'family car' or self.vehicle == 1:
            self.vehicle = 'Family Car'
            self.set_move_speed(3)
            self.set_rotation_speed(2)
        elif self.vehicle == 'sports car' or self.vehicle == 2:
            self.vehicle = 'Sports Car'
            self.set_move_speed(4)
            self.set_rotation_speed(3)
        elif self.vehicle == 'luxury car' or self.vehicle == 3:
            self.vehicle = 'Luxury Car'
            self.set_move_speed(3)
            self.set_rotation_speed(3)
        elif self.vehicle == 'truck' or self.vehicle == 4:
            self.vehicle = 'Truck'
            self.set_move_speed(2)
            self.set_rotation_speed(2)
        elif self.vehicle == 'race car' or self.vehicle == 5:
            self.vehicle = 'Race Car'
            self.set_move_speed(5)
            self.set_rotation_speed(3)
        else:
            raise ValueError('NpcCar | __init__ | self.vehicle incorrect value -> ' + str(self.vehicle))
        # STARTING variables
        self.origin_pos = self.paths.start_pos(start_position)[0:2]  # Original position
        self.origin_rotation = self.paths.start_pos(start_position)[2]
        # SURFACE variables
        self.colour = colour
        self.image_dir = assets.car(self.colour, self.vehicle)
        self.image = pygame.transform.scale(pygame.image.load(self.image_dir).convert(), size)
        self.image.set_colorkey(BLACK)
        self.dmg_img = None
        self.size = self.image.get_size()
        # RECT variables
        self.rect = self.image.get_rect()
        self.rect.center = self.origin_pos
        self.pos_x = self.rect.x
        self.pos_y = self.rect.y
        self.rotation = self.origin_rotation
        self.move(self.origin_pos[0], self.origin_pos[1])
        if self.origin_rotation != 0:  # If start rotation is not 0 then rotate
            self.rotate(self.rotation)
        # COLLISION variables
        self.mask = pygame.mask.from_surface(self.image)  # Get mask from image
        self.mask_overlap = None  # Used for checking collision position
        self.mask_area = None  # Used to ensure the player cannot get outside the map
        self.mask_size = None
        self.collision = False
        self.collision_time = 0
        self.lightning_animation = False
        self._lightning_frame = None
        # MOVEMENT variables
        self.allow_forwards = True
        self.allow_reverse = True
        self.pressed_keys = None
        self.path = self.get_path()
        self.penalty_time = 0
        # NAME variables
        self.name = name
        self.name_rect = None
        # LAP variables
        self.lap_halfway = True
        self.laps = 0
        # CHECKPOINT variables
        self.checkpoint_count = -1
        self.checkpoint_time = 0
        self.prev_checkpoint_position = self.origin_pos
        self.prev_checkpoint_rotation = self.origin_rotation
        self.prev_checkpoint_path_position = 0
        # PATH variables
        self.path_position = 0
        self.diversion = False
        self.diversion_path = paths.diversion(0)
        self.diversion_position = 0
        self.diversion_delay = 0
        # SOUND variables
        self.collision_sound = False

    def set_move_speed(self, speed):
        self.move_speed = global_car_move_speed + speed

    def set_rotation_speed(self, speed):
        self.rotation_speed = global_car_rotation_speed + speed

    def check_checkpoints(self, checkpoint_rectangles):
        for checkpoint in checkpoint_rectangles:
            if checkpoint.colliderect(self.rect) and self.checkpoint_count != checkpoint_rectangles.index(checkpoint):
                self.checkpoint_count = checkpoint_rectangles.index(checkpoint)
                self.checkpoint_time = pygame.time.get_ticks()
                if not self.lap_halfway and self.checkpoint_count == floor(len(checkpoint_rectangles) / 2):
                    self.lap_halfway = True
                if self.lap_halfway and self.checkpoint_count == 0:
                    self.lap_halfway = False
                    self.laps += 1

    def get_path(self):  # Randomise path according to start position
        return self.paths.path(self.rotation_speed - global_car_rotation_speed, self.start_position,
                               self.move_speed - global_car_move_speed, randint(1, 3))

    def check_track_collisions(self, track_mask):  # Check if there are collisions and take action
        if not self.collision or self.collision == 'track':
            if Debug:  # If debug then outline car mask in red
                for pos in self.mask.outline():
                    pos_x, pos_y = pos
                    pygame.draw.circle(self.image, RED, (pos_x, pos_y), 1)
            self.mask_overlap = self.mask.overlap(track_mask, (-self.rect.left, -self.rect.top))
            if self.mask_overlap:
                self.collision = 'track'
                if not self.collision_sound:
                    play_sound('collision')
                    self.penalty_time = pygame.time.get_ticks() + 3000 + \
                        ((self.move_speed - global_car_move_speed) * 1000)
                    self.collision_sound = True
                if self.collision_time == 0:
                    self.collision_time = pygame.time.get_ticks()

                # If there is a collision between masks...
                self.mask_area = self.mask.overlap_area(track_mask, (-self.rect.left, -self.rect.top))
                self.mask_size = self.mask.count()

                if Debug:  # If debug then show collision position via small yellow square
                    pygame.draw.rect(self.image, YELLOW_CAR, (self.mask_overlap[0], self.mask_overlap[1], 5, 5))
                    screen_updates.append((self.mask_overlap[0], self.mask_overlap[1], 5, 5))

                if self.rotation <= 45 or self.rotation >= 315:  # If car is pointing up...
                    # print('pointing up')
                    if self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                elif 45 < self.rotation < 135:  # If the car is pointing left...
                    # print('pointing left')
                    if self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                elif 135 <= self.rotation <= 225:  # If the car is pointing down...
                    # print('pointing down')
                    if self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                elif 225 < self.rotation < 315:  # If the car is pointing right...
                    # print('pointing right')
                    if self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                if self.mask_area > self.mask_size // 1.5:  # If over half of the car is colliding with the mask...
                    self.move(self.origin_pos[0], self.origin_pos[1])  # Reset the car to starting position and rotation
                    self.rotate(self.origin_rotation)
                    # print('reset to origin')

            else:  # If there are no collisions with the track
                if self.diversion and self.diversion_delay + 2000 > pygame.time.get_ticks():
                    self.collision_sound = False
                    if not self.allow_forwards:  # Ensure that the player can move forwards and backwards
                        self.allow_forwards = True
                    if not self.allow_reverse:
                        self.allow_reverse = True
                else:
                    self.collision = False
                    self.collision_time = 0
                    self.collision_sound = False
                    if not self.allow_forwards:  # Ensure that the player can move forwards and backwards
                        self.allow_forwards = True
                    if not self.allow_reverse:
                        self.allow_reverse = True

    def check_car_collision(self, sprite):
        if not self.collision or self.collision == sprite:
            self.mask_overlap = pygame.sprite.collide_mask(self, sprite)
            if self.mask_overlap:
                self.collision = sprite
                if not self.collision_sound:
                    play_sound('collision')
                    self.penalty_time = pygame.time.get_ticks() + 3000 + \
                        ((self.move_speed - global_car_move_speed) * 1000)
                    self.collision_sound = True
                if self.collision_time == 0:
                    self.collision_time = pygame.time.get_ticks()
                    # print('set timer')
                # If there is a collision between masks...
                self.mask_area = self.mask.overlap_area(sprite.mask, (-self.rect.left, -self.rect.top))
                self.mask_size = self.mask.count()

                if Debug:  # If debug then show collision position via small yellow square
                    pygame.draw.rect(self.image, YELLOW_CAR, (self.mask_overlap[0], self.mask_overlap[1], 5, 5))
                    screen_updates.append((self.mask_overlap[0], self.mask_overlap[1], 5, 5))

                if self.rotation <= 45 or self.rotation >= 315:  # If car is pointing up...
                    # print('pointing up')
                    if self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                elif 45 < self.rotation < 135:  # If the car is pointing left...
                    # print('pointing left')
                    if self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                elif 135 <= self.rotation <= 225:  # If the car is pointing down...
                    # print('pointing down')
                    if self.image.get_size()[1] // 2 < self.mask_overlap[1]:  # If the collision is on the bottom half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[1] // 2 > self.mask_overlap[1]:  # If the collision is on the top half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                elif 225 < self.rotation < 315:  # If the car is pointing right...
                    # print('pointing right')
                    if self.image.get_size()[0] // 2 < self.mask_overlap[0]:  # If the collision is on the right half
                        self.allow_forwards = False  # Do not allow forwards
                        self.allow_reverse = True
                        # print('do not allow forwards')
                    elif self.image.get_size()[0] // 2 > self.mask_overlap[0]:  # If the collision is on the left half
                        self.allow_forwards = True  # Do not allow reverse
                        self.allow_reverse = False
                        # print('do not allow reverse')

                if self.mask_area > self.mask_size // 1.5:  # If over half of the car is colliding with the mask...
                    self.move(self.origin_pos[0], self.origin_pos[1])  # Reset the car to starting position and rotation
                    self.rotate(self.origin_rotation)
                    # print('reset to origin')

            else:  # If there are no collisions with the track
                if self.diversion and self.diversion_delay + 2000 > pygame.time.get_ticks():
                    self.collision_sound = False
                    self.allow_forwards = True  # Ensure that the player can move forwards and backwards
                    self.allow_reverse = True
                else:
                    self.collision = False
                    self.collision_sound = False
                    self.collision_time = 0
                    self.allow_forwards = True  # Ensure that the player can move forwards and backwards
                    self.allow_reverse = True

    def move(self, x, y):  # Move car to new position
        self.pos_x = x
        self.pos_y = y
        self.rect.center = x, y

    def rotate(self, degree):  # Rotate car to new angle
        self.rotation = degree  # Set current rotation as rotation
        if global_car_rotation_speed + 1 >= self.rotation:  # Create snapping points to drive in straight lines
            self.rotation = 360
        elif self.rotation >= 360 - global_car_rotation_speed + 1:
            self.rotation = 0
        elif 90 - global_car_rotation_speed + 1 <= self.rotation <= 90 + global_car_rotation_speed + 1:
            self.rotation = 90
        elif 180 - global_car_rotation_speed + 1 <= self.rotation <= 180 + global_car_rotation_speed + 1:
            self.rotation = 180
        elif 270 - global_car_rotation_speed + 1 <= self.rotation <= 270 + global_car_rotation_speed + 1:
            self.rotation = 270
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
            self.image_dir).convert(), self.size), self.rotation)  # Rotate image
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)  # Update mask to new rotation
        self.rect = self.image.get_rect()  # Set surface size to image size
        if Debug:
            pygame.draw.rect(self.image, WHITE, self.rect, 1)  # Draw outline of sprite (debugging)
        self.rect.center = self.pos_x, self.pos_y

    def reset_to_checkpoint(self):
        self.collision_time = 0
        self.diversion_delay = 0
        self.allow_forwards = True
        self.allow_reverse = True
        self.collision = False
        self.diversion = False
        self.path_position = self.prev_checkpoint_path_position  # Reset path position to start
        self.move(*self.prev_checkpoint_position)  # Move car to exact start position
        self.rotate(self.prev_checkpoint_rotation)

    def follow_path(self):  # Check all inputs and take action
        if self.allow_forwards:  # Only increment path position if they are allowed to go forwards
            if len(self.path) <= self.path_position:  # If reached the end of path reset to start position and replay
                self.path_position = 0  # Reset path position to start
                self.move(*self.origin_pos)  # Move car to exact start position
                self.rotate(self.origin_rotation)
                self.path = self.get_path()  # Randomise next path

            self.pressed_keys = self.path[self.path_position]
            if len(self.pressed_keys) == 1:
                if self.pressed_keys[0] == 0 and self.allow_forwards:  # UP
                    self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y + round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))

                elif self.pressed_keys[0] == 1 and self.allow_reverse:  # DOWN
                    self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y - round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))

            elif len(self.pressed_keys) == 2:
                if self.pressed_keys[0] == 0 and self.pressed_keys[1] == 2 and self.allow_forwards:  # UP & LEFT
                    self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y + round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                    self.rotate(self.rotation + self.rotation_speed)  # Rotate car to new position
                    # print(self.rotation)

                elif self.pressed_keys[0] == 0 and self.pressed_keys[1] == 3 and self.allow_forwards:  # UP & RIGHT
                    self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y + round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                    self.rotate(self.rotation - self.rotation_speed)
                    # print(self.rotation)

                elif self.pressed_keys[0] == 1 and self.pressed_keys[1] == 2 and self.allow_reverse:  # DOWN & LEFT
                    self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y - round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                    self.rotate(self.rotation + self.rotation_speed)  # Rotate car to new position
                    # print(self.rotation)

                elif self.pressed_keys[0] == 1 and self.pressed_keys[1] == 2 and self.allow_reverse:  # DOWN & RIGHT
                    self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y - round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                    self.rotate(self.rotation - self.rotation_speed)  # Rotate car to new position
                    # print(self.rotation)

            self.path_position += 1

    def follow_diversion(self):
        if len(self.diversion_path) <= self.diversion_position:  # If it is the end of the diversion...
            self.diversion_position = 0  # Reset diversion variables as diversion finished and return
            self.diversion_delay = 0
            self.diversion = False
            return

        self.pressed_keys = self.diversion_path[self.diversion_position]
        if self.allow_reverse and self.diversion_delay:
            # self._pressed_keys == [0] and self._allow_forwards and self.diversion_delay:  # Only move if allowed to

            if len(self.pressed_keys) == 1:
                if self.pressed_keys[0] == 0 and self.allow_forwards:  # UP
                    self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y + round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))

                elif self.pressed_keys[0] == 1 and self.allow_reverse:  # DOWN
                    self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self.move_speed),
                              self.pos_y - round(sin(radians(self.rotation - 90)) * self.move_speed))
                    # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))

            elif len(self.pressed_keys) == 2:
                self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self.move_speed),
                          self.pos_y + round(sin(radians(self.rotation - 90)) * self.move_speed))
                # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                self.rotate(self.rotation + self.rotation_speed)  # Rotate car to new position
                # print(self.rotation)

            elif self.pressed_keys[0] == 0 and self.pressed_keys[1] == 3 and self.allow_forwards:  # UP & RIGHT
                self.move(self.pos_x - round(cos(radians(self.rotation - 90)) * self.move_speed),
                          self.pos_y + round(sin(radians(self.rotation - 90)) * self.move_speed))
                # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                self.rotate(self.rotation - self.rotation_speed)
                # print(self.rotation)

            elif self.pressed_keys[0] == 1 and self.pressed_keys[1] == 2 and self.allow_reverse:  # DOWN & LEFT
                self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self.move_speed),
                          self.pos_y - round(sin(radians(self.rotation - 90)) * self.move_speed))
                # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                self.rotate(self.rotation + self.rotation_speed)  # Rotate car to new position
                # print(self.rotation)

            elif self.pressed_keys[0] == 1 and self.pressed_keys[1] == 2 and self.allow_reverse:  # DOWN & RIGHT
                self.move(self.pos_x + round(cos(radians(self.rotation - 90)) * self.move_speed),
                          self.pos_y - round(sin(radians(self.rotation - 90)) * self.move_speed))
                # print('car move: ' + str(self.pos_x) + ', ' + str(self.pos_y))
                self.rotate(self.rotation - self.rotation_speed)  # Rotate car to new position
                # print(self.rotation)
            self.diversion_position += 1

    def power_up(self, ver):
        if ver == 'lightning' and not self.collision and not self.penalty_time:
            self.lightning_animation = pygame.time.get_ticks() // 70

    def draw(self, surf=Window):
        surf.blit(self.image, (self.rect.left, self.rect.top))  # Car image

        draw_triangle((self.rect.centerx, self.rect.top - 14), 'down',  # Name and arrow
                      width=10, height=10, border=self.colour, border_width=3, surface=surf)
        self.name_rect = draw_text(self.rect.centerx, self.rect.top - 35, self.name, WHITE, 12, surf=surf)

        if self.lightning_animation:  # Lightning animation
            self._lightning_frame = pygame.time.get_ticks() // 70 - self.lightning_animation
            if self._lightning_frame < 15:
                surf.blit(lightning_frames[self._lightning_frame], (self.rect.centerx - 64, self.rect.centery - 128))
                if self._lightning_frame == 2:
                    play_sound('lightning')
                elif self._lightning_frame == 3:
                    self.penalty_time = pygame.time.get_ticks() + 3000 + \
                                        (self.move_speed - global_car_move_speed) * 1000

    def update(self):  # Called each loop and checks if anything has changed
        if self.penalty_time and self.penalty_time > pygame.time.get_ticks():
            self.dmg_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                assets.car_damage(self.vehicle, 5)), self.size), self.rotation)
            self.dmg_img.set_colorkey(WHITE)
            self.image.blit(self.dmg_img, (0, 0))  # Overlay damage on top of image
            return
        elif self.penalty_time and self.penalty_time < pygame.time.get_ticks():
            self.penalty_time = 0
            self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
                self.image_dir).convert(), self.size), self.rotation)  # Load new image to reset damage
            self.image.set_colorkey(BLACK)
            self.mask = pygame.mask.from_surface(self.image)  # Update mask to new rotation
            self.rect = self.image.get_rect()  # Set surface size to image size
            self.rect.center = self.pos_x, self.pos_y
        else:
            if self.collision_time != 0 and self.allow_reverse:
                if pygame.time.get_ticks() >= self.collision_time + 5000:
                    self.reset_to_checkpoint()
                    # print('reset')
                elif pygame.time.get_ticks() >= self.collision_time + 2000:
                    self.diversion = True
                    self.diversion_delay = pygame.time.get_ticks() + (randint(0, 10) * 100)
                    if self.allow_reverse:  # Determine forwards or backwards diversion
                        self.diversion_path = paths.diversion(0)
                    elif self.allow_forwards:
                        self.diversion_path = paths.diversion(1)

            if self.diversion and pygame.time.get_ticks() >= self.diversion_delay and self.allow_reverse:
                self.follow_diversion()
                # print('follow diversion')
            else:
                self.follow_path()
                # print('follow path')


# -------- CAR FUNCTIONS -------- #
def get_car_positions(player_list, npc_list):
    positions = []
    vehicles = player_list + npc_list
    for vehicle in vehicles:
        vehicle = vehicle.laps, vehicle.checkpoint_count, vehicle.checkpoint_time, vehicle
        positions.append(vehicle)  # Cut down vehicle data

    positions = sorted(positions, key=lambda tup: tup[2])  # Sort based on checkpoint times
    positions = sorted(positions, key=lambda tup: tup[1], reverse=True)  # Sort based on checkpoint number
    return sorted(positions, key=lambda tup: tup[0], reverse=True)  # Sort positions based on their lap number


# -------- MAP PREVIEW -------- #
def get_map_preview():
    global map_preview
    if Map == 'racetrack':
        if map_preview[0] != 'racetrack':
            surf = pygame.surface.Surface(map_preview_size)
            surf.blit(pygame.transform.scale(pygame.image.load(maps.racetrack('bg')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.racetrack('obj')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.racetrack('trk')), map_preview_size), (0, 0))
            map_preview = Map, surf
    elif Map == 'snake':
        if map_preview[0] != 'snake':
            surf = pygame.surface.Surface(map_preview_size)
            surf.blit(pygame.transform.scale(pygame.image.load(maps.snake('bg')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.snake('obj')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.snake('trk')), map_preview_size), (0, 0))
            map_preview = Map, surf
    elif Map == 'dog bone':
        if map_preview[0] != 'dog bone':
            surf = pygame.surface.Surface(map_preview_size)
            surf.blit(pygame.transform.scale(pygame.image.load(maps.dog_bone('bg')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.dog_bone('obj')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.dog_bone('trk')), map_preview_size), (0, 0))
            map_preview = Map, surf
    elif Map == 'hairpin':
        if map_preview[0] != 'hairpin':
            surf = pygame.surface.Surface(map_preview_size)
            surf.blit(pygame.transform.scale(pygame.image.load(maps.hairpin('bg')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.hairpin('obj')), map_preview_size), (0, 0))
            surf.blit(pygame.transform.scale(pygame.image.load(maps.hairpin('trk')), map_preview_size), (0, 0))
            map_preview = Map, surf
    else:
        raise ValueError('get_map_preview -> unknown map: ' + str(Map))


# -------- WINDOW FUNCTIONS -------- #
def main_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))  # Display the current bg

    x = pad_x + CENTRE[0]
    y = pad_y + 100
    draw_text(x, y, 'Retro Rampage', WHITE, 100, bold=True, bar=True)  # Title

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Quit button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 98, y + 21, 'Quit', WHITE, 60)

    x = pad_x + 340
    y = pad_y + 324
    tile(x, y, 'dirt road', 76, grid=False)  # Start button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    x = pad_x + 1220
    y = pad_y + 324
    tile(x, y, 'dirt road', 76, grid=False)  # Settings button
    tile(x + 128, y, 'dirt road', 1, grid=False)
    tile(x + 256, y, 'dirt road', 60, grid=False)
    draw_text(x + 190, y + 20, 'Settings', WHITE, 70)

    x = pad_x + 1220
    y = pad_y + 648
    tile(x, y, 'dirt road', 76, grid=False)  # Tutorial button
    tile(x + 128, y, 'dirt road', 1, grid=False)
    tile(x + 256, y, 'dirt road', 60, grid=False)
    draw_text(x + 190, y + 20, 'Tutorial', WHITE, 70)

    x = pad_x + 340
    y = pad_y + 648
    tile(x, y, 'dirt road', 76, grid=False)  # Credits button
    tile(x + 128, y, 'dirt road', 1, grid=False)
    tile(x + 205, y, 'dirt road', 60, grid=False)
    draw_text(x + 163, y + 20, 'Credits', WHITE, 70)


def choose_map_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))  # Display the current bg

    x = pad_x + CENTRE[0]
    y = pad_y + 70
    draw_text(x, y, 'Choose Map', WHITE, 100)  # Title

    x = pad_x + 528
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Back button
    tile(x + 128, y, 'dirt road', 60, grid=False)
    draw_text(x + 130, y + 20, 'Back', WHITE, 70)

    x = pad_x + 1100
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Select button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Select', WHITE, 70)

    # Draw map preview with border
    Window.blit(map_preview[1], (pad_x + map_preview_pos[0], pad_y + map_preview_pos[1]))
    pygame.draw.rect(Window, WHITE, (pad_x + map_preview_pos[0], pad_y + map_preview_pos[1], *map_preview_size), 4)

    x = pad_x + CENTRE[0]
    y = pad_y + (map_preview_pos[1] - 70)
    text = str(maps.map_index.index(Map) + 1) + '. ' + Map
    draw_text(x, y, text, WHITE, 60)  # Title

    draw_triangle((pad_x + (map_preview_pos[0] - 50),  # Map arrows
                   pad_y + (map_preview_pos[1] + map_preview_size[1] // 2)), 'left', width=40, height=80)
    draw_triangle((pad_x + (map_preview_pos[0] + map_preview_size[0] + 50),
                   pad_y + (map_preview_pos[1] + map_preview_size[1] // 2)), 'right', width=40, height=80)


def choose_players_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Choose Players', WHITE, 100)  # Title

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 100, y + 23, 'Back', WHITE, 55)

    if Player_amount == 1:
        player = Players[0]
        # Controls
        x = pad_x + CENTRE[0]
        y = pad_y + 240
        draw_text(x, y, 'P1 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 840, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 1080, pad_y + 380), 'right', width=25, height=50)

        x = pad_x + CENTRE[0]
        y = pad_y + CENTRE[1] + 100
        # P1 name title
        draw_text(x, y, 'P1 Name', WHITE, 50, bar=True)
        # P1 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P1 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P1 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 1:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 1 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

    elif Player_amount >= 2:
        # P1
        player = Players[0]
        # Controls
        x = pad_x + 560
        y = pad_y + 240
        draw_text(x, y, 'P1 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 440, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 680, pad_y + 380), 'right', width=25, height=50)

        y = pad_y + CENTRE[1] + 100
        # P1 name title
        draw_text(x, y, 'P1 Name', WHITE, 50, bar=True)
        # P1 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P1 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P1 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 1:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 1 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

        # P2
        player = Players[1]
        x = pad_x + 1360
        y = pad_y + 240
        # Controls
        draw_text(x, y, 'P2 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 1240, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 1480, pad_y + 380), 'right', width=25, height=50)

        y = pad_y + CENTRE[1] + 100
        # P2 name title
        draw_text(x, y, 'P2 Name', WHITE, 50, bar=True)
        # P2 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P2 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P2 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 2:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 2 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

    for player in Players:
        if player.controls in controllers:
            rect = draw_text(100, HEIGHT-108, 'To unbind a controller, press ',
                             WHITE, 32, center_x=False, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('b')), (34, 34)),
                        (100 + rect.width, HEIGHT-109))

    # START BUTTON
    if Player_amount == 1 and Players[0].name.strip() and Players[0].controls != 'controller' or \
            Player_amount >= 2 and Players[0].name.strip() and Players[0].controls != 'controller' and \
            Players[1].name.strip() and Players[1].controls != 'controller':
        x = pad_x + 800
        y = pad_y + 940
        tile(x, y, 'dirt road', 76, grid=False)  # Start button
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    if len(controllers) >= 1:
        x = pad_x + 93
        y = pad_y + HEIGHT - 255
        tile(x, y, 'dirt road', 76, grid=False)  # 3 player button
        tile(x + 128, y, 'dirt road', 1, grid=False)
        tile(x + 256, y, 'dirt road', 60, grid=False)
        draw_text(x + 190, y + 20, '3 Player', WHITE, 70)
    if len(controllers) >= 2:
        x = pad_x + 492
        y = pad_y + HEIGHT - 255
        tile(x, y, 'dirt road', 76, grid=False)  # 4 player button
        tile(x + 128, y, 'dirt road', 1, grid=False)
        tile(x + 256, y, 'dirt road', 60, grid=False)
        draw_text(x + 190, y + 20, '4 Player', WHITE, 70)
    if len(controllers) >= 3:
        x = pad_x + WIDTH - 876
        y = pad_y + HEIGHT - 255
        tile(x, y, 'dirt road', 76, grid=False)  # 5 player button
        tile(x + 128, y, 'dirt road', 1, grid=False)
        tile(x + 256, y, 'dirt road', 60, grid=False)
        draw_text(x + 190, y + 20, '5 Player', WHITE, 70)
    if len(controllers) >= 4:
        x = pad_x + WIDTH - 477
        y = pad_y + HEIGHT - 255
        tile(x, y, 'dirt road', 76, grid=False)  # 6 player button
        tile(x + 128, y, 'dirt road', 1, grid=False)
        tile(x + 256, y, 'dirt road', 60, grid=False)
        draw_text(x + 190, y + 20, '6 Player', WHITE, 70)

    if Player_amount != 1:
        x = pad_x + 400
        y = pad_y + 476
        tile(x, y, 'dirt road', 76, grid=False)  # Single player button
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        draw_text(x + 160, y + 20, 'Single', WHITE, 70)
    if Player_amount != 2:
        x = pad_x + 1200
        y = pad_y + 476
        tile(x, y, 'dirt road', 76, grid=False)  # Dual player button
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        draw_text(x + 160, y + 20, 'Dual', WHITE, 70)

    if Player_amount == 1:
        x = pad_x + 400
        y = pad_y + 476
        tile(x, y, 'road', 77, grid=False)  # Single Player button
        tile(x + 65, y, 'road', 2, grid=False)
        tile(x + 190, y, 'road', 61, grid=False)
        draw_text(x + 160, y + 20, 'Single', BLACK, 70)
    elif Player_amount == 2:
        x = pad_x + 1200
        y = pad_y + 476
        tile(x, y, 'road', 77, grid=False)  # Dual player button
        tile(x + 65, y, 'road', 2, grid=False)
        tile(x + 190, y, 'road', 61, grid=False)
        draw_text(x + 160, y + 20, 'Dual', BLACK, 70)
    elif Player_amount == 3:
        x = pad_x + 93
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 3 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '3 Player', BLACK, 70)
    elif Player_amount == 4:
        x = pad_x + 492
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 4 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '4 Player', BLACK, 70)
    elif Player_amount == 5:
        x = pad_x + WIDTH - 876
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 5 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '5 Player', BLACK, 70)
    elif Player_amount == 6:
        x = pad_x + WIDTH - 477
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 6 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '6 Player', BLACK, 70)


def choose_players_window_2(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Choose Players', WHITE, 100)  # Title

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 100, y + 23, 'Back', WHITE, 55)

    if Player_amount == 3:
        player = Players[2]
        # Controls
        x = pad_x + CENTRE[0]
        y = pad_y + 240
        draw_text(x, y, 'P3 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 840, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 1080, pad_y + 380), 'right', width=25, height=50)

        x = pad_x + CENTRE[0]
        y = pad_y + CENTRE[1] + 100
        # P1 name title
        draw_text(x, y, 'P3 Name', WHITE, 50, bar=True)
        # P1 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P1 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P1 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 3:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 3 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

    elif Player_amount >= 4:
        # P1
        player = Players[2]
        # Controls
        x = pad_x + 560
        y = pad_y + 240
        draw_text(x, y, 'P3 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 440, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 680, pad_y + 380), 'right', width=25, height=50)

        y = pad_y + CENTRE[1] + 100
        # P1 name title
        draw_text(x, y, 'P3 Name', WHITE, 50, bar=True)
        # P1 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P1 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P1 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 3:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 3 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

        # P2
        player = Players[3]
        x = pad_x + 1360
        y = pad_y + 240
        # Controls
        draw_text(x, y, 'P4 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 1240, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 1480, pad_y + 380), 'right', width=25, height=50)

        y = pad_y + CENTRE[1] + 100
        # P2 name title
        draw_text(x, y, 'P4 Name', WHITE, 50, bar=True)
        # P2 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P2 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P2 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 4:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 4 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

    for player in Players:
        if player.controls in controllers:
            rect = draw_text(100, HEIGHT - 110, 'To unbind a controller, press ',
                             WHITE, 32, center_x=False, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('b')), (34, 34)),
                        (100 + rect.width, HEIGHT - 111))

    # START BUTTON
    if Player_amount == 3 and Players[0].name.strip() and Players[0].controls != 'controller' and \
            Players[1].name.strip() and Players[1].controls != 'controller' and Players[2].name.strip() and \
            Players[2].name.strip() or Player_amount >= 4 and Players[0].name.strip() and \
            Players[0].controls != 'controller' and Players[1].name.strip() and Players[1].controls != 'controller' \
            and Players[2].name.strip() and Players[2].name.strip() and Players[3].name.strip() and \
            Players[3].controls != 'controller':
        x = pad_x + 800
        y = pad_y + 940
        tile(x, y, 'dirt road', 76, grid=False)  # Start button
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    if Player_amount == 3:
        x = pad_x + 93
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 3 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '3 Player', BLACK, 70)
    elif Player_amount == 4:
        x = pad_x + 492
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 4 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '4 Player', BLACK, 70)
    elif Player_amount == 5:
        x = pad_x + WIDTH - 876
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 5 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '5 Player', BLACK, 70)
    elif Player_amount == 6:
        x = pad_x + WIDTH - 477
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 6 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '6 Player', BLACK, 70)


def choose_players_window_3(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Choose Players', WHITE, 100)  # Title

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 100, y + 23, 'Back', WHITE, 55)

    if Player_amount == 5:
        player = Players[4]
        # Controls
        x = pad_x + CENTRE[0]
        y = pad_y + 240
        draw_text(x, y, 'P5 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 840, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 1080, pad_y + 380), 'right', width=25, height=50)

        x = pad_x + CENTRE[0]
        y = pad_y + CENTRE[1] + 100
        # P1 name title
        draw_text(x, y, 'P5 Name', WHITE, 50, bar=True)
        # P1 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P1 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P1 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 5:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 5 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

        x = pad_x + WIDTH - 876
        y = pad_y + HEIGHT - 255
        tile(x, y, 'road', 77, grid=False)  # 5 player button
        tile(x + 128, y, 'road', 2, grid=False)
        tile(x + 256, y, 'road', 61, grid=False)
        draw_text(x + 190, y + 20, '5 Player', BLACK, 70)

    if Player_amount == 6:
        # P1
        player = Players[4]
        # Controls
        x = pad_x + 560
        y = pad_y + 240
        draw_text(x, y, 'P5 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 440, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 680, pad_y + 380), 'right', width=25, height=50)

        y = pad_y + CENTRE[1] + 100
        # P1 name title
        draw_text(x, y, 'P5 Name', WHITE, 50, bar=True)
        # P1 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P1 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P1 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 5:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 5 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

        # P2
        player = Players[5]
        x = pad_x + 1360
        y = pad_y + 240
        # Controls
        draw_text(x, y, 'P6 controls', WHITE, 50, bar=True)
        rect = draw_controls(x, y + 140, player.controls, return_rect=True)
        if player.controls == 'controller':
            rect_2 = draw_text(x - 16, y + rect.height + rect.centerx + 42, 'Press ', WHITE, 32, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('a')), (34, 34)),
                        (x + rect_2.centerx - 16, y + rect.height + rect.centerx + 41))
        elif player.controls in controllers:
            draw_text(x, y + rect.height + rect.centerx + 42,
                      short_controller_name(player.controls.get_name()), WHITE, 32)
        if type(player.controls) == str:
            draw_triangle((pad_x + 1240, pad_y + 380), 'left', width=25, height=50)
            draw_triangle((pad_x + 1480, pad_y + 380), 'right', width=25, height=50)

        y = pad_y + CENTRE[1] + 100
        # P2 name title
        draw_text(x, y, 'P6 Name', WHITE, 50, bar=True)
        # P2 name underline
        pygame.draw.line(Window, WHITE, (x - 200, y + 160), (x + 200, y + 160), 4)
        # P2 name
        rect = draw_text(x, y + 115, player.name, WHITE, 50, return_rect=True)
        # P2 name cursor
        if (pygame.time.get_ticks() // 1060) % 2 and selected_text_entry == 6:
            pygame.draw.line(Window, WHITE, (x + 5 + rect.width // 2, y + 124), (x + 5 + rect.width // 2, y + 152), 3)
        # Enter name prompt
        if selected_text_entry != 6 and not player.name:
            if (pygame.time.get_ticks() // 1060) % 2:
                draw_text(x, y + 115, 'Enter name', V_LIGHT_GREY, 50)
            else:
                draw_text(x, y + 115, 'Enter name', LIGHT_GREY, 50)

    for player in Players:
        if player.controls in controllers:
            rect = draw_text(100, HEIGHT - 110, 'To unbind a controller, press ',
                             WHITE, 32, center_x=False, return_rect=True)
            Window.blit(pygame.transform.scale(pygame.image.load(assets.controller_button('b')), (34, 34)),
                        (100 + rect.width, HEIGHT - 111))

    # START BUTTON
    if Player_amount == 5 and Players[4].name.strip() and Players[4].controls != 'controller' or \
            Player_amount == 6 and Players[4].name.strip() and Players[4].controls != 'controller' and \
            Players[5].name.strip() and Players[5].controls != 'controller':
        x = pad_x + 800
        y = pad_y + 940
        tile(x, y, 'dirt road', 76, grid=False)  # Start button
        tile(x + 65, y, 'dirt road', 1, grid=False)
        tile(x + 190, y, 'dirt road', 60, grid=False)
        draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    x = pad_x + WIDTH - 477
    y = pad_y + HEIGHT - 255
    tile(x, y, 'road', 77, grid=False)  # 6 player button
    tile(x + 128, y, 'road', 2, grid=False)
    tile(x + 256, y, 'road', 61, grid=False)
    draw_text(x + 190, y + 20, '6 Player', BLACK, 70)


def choose_vehicle_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Choose Vehicle', WHITE, 100)  # Title

    x = pad_x + 528
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Back button
    tile(x + 128, y, 'dirt road', 60, grid=False)
    draw_text(x + 130, y + 20, 'Back', WHITE, 70)

    x = pad_x + 1100
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Start button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    if Player_amount == 1:
        player = Players[0]
        draw_text(pad_x + CENTRE[0], pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + CENTRE[0], pad_y + 325, player.veh_name, WHITE, 50)

        p1_veh_rect = player.veh_image.get_rect()
        draw_triangle((pad_x + CENTRE[0] - 170 - p1_veh_rect.width, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + CENTRE[0] - 215 - p1_veh_rect.width // 2,
                                       pad_y + CENTRE[1] - p1_veh_rect.height // 2))
        draw_triangle((pad_x + CENTRE[0] + 170 + p1_veh_rect.width, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'
        draw_text(pad_x + CENTRE[0], pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + CENTRE[0] - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + CENTRE[0] + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + CENTRE[0], pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + CENTRE[0], pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + CENTRE[0], pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)

    elif Player_amount >= 2:
        # 1P VEHICLE
        player = Players[0]
        pos_x = CENTRE[0] // 2 + 10
        draw_text(pad_x + pos_x, pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + pos_x, pad_y + 325, player.veh_name, WHITE, 50)

        draw_triangle((pad_x + pos_x - 345, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + pos_x - 300, pad_y + CENTRE[1] - 150))
        draw_triangle((pad_x + pos_x + 345, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'
        draw_text(pad_x + pos_x, pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + pos_x - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + pos_x + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + pos_x, pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)

        # 2P VEHICLE
        player = Players[1]
        pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
        draw_text(pad_x + pos_x, pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + pos_x, pad_y + 325, player.veh_name, WHITE, 50)

        draw_triangle((pad_x + pos_x - 345, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + pos_x - 300, pad_y + CENTRE[1] - 150))
        draw_triangle((pad_x + pos_x + 345, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'

        draw_text(pad_x + pos_x, pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + pos_x - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + pos_x + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + pos_x, pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)


def choose_vehicle_window_2(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Choose Vehicle', WHITE, 100)  # Title

    x = pad_x + 528
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Back button
    tile(x + 128, y, 'dirt road', 60, grid=False)
    draw_text(x + 130, y + 20, 'Back', WHITE, 70)

    x = pad_x + 1100
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Start button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    if Player_amount == 3:
        player = Players[2]
        draw_text(pad_x + CENTRE[0], pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + CENTRE[0], pad_y + 325, player.veh_name, WHITE, 50)

        p1_veh_rect = player.veh_image.get_rect()
        draw_triangle((pad_x + CENTRE[0] - 170 - p1_veh_rect.width, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + CENTRE[0] - 215 - p1_veh_rect.width // 2,
                                       pad_y + CENTRE[1] - p1_veh_rect.height // 2))
        draw_triangle((pad_x + CENTRE[0] + 170 + p1_veh_rect.width, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'
        draw_text(pad_x + CENTRE[0], pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + CENTRE[0] - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + CENTRE[0] + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + CENTRE[0], pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + CENTRE[0], pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + CENTRE[0], pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)

    elif Player_amount >= 4:
        # 1P VEHICLE
        player = Players[2]
        pos_x = CENTRE[0] // 2 + 10
        draw_text(pad_x + pos_x, pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + pos_x, pad_y + 325, player.veh_name, WHITE, 50)

        draw_triangle((pad_x + pos_x - 345, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + pos_x - 300, pad_y + CENTRE[1] - 150))
        draw_triangle((pad_x + pos_x + 345, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'
        draw_text(pad_x + pos_x, pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + pos_x - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + pos_x + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + pos_x, pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)

        # 2P VEHICLE
        player = Players[3]
        pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
        draw_text(pad_x + pos_x, pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + pos_x, pad_y + 325, player.veh_name, WHITE, 50)

        draw_triangle((pad_x + pos_x - 345, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + pos_x - 300, pad_y + CENTRE[1] - 150))
        draw_triangle((pad_x + pos_x + 345, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'

        draw_text(pad_x + pos_x, pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + pos_x - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + pos_x + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + pos_x, pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)


def choose_vehicle_window_3(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Choose Vehicle', WHITE, 100)  # Title

    x = pad_x + 528
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Back button
    tile(x + 128, y, 'dirt road', 60, grid=False)
    draw_text(x + 130, y + 20, 'Back', WHITE, 70)

    x = pad_x + 1100
    y = pad_y + 890
    tile(x, y, 'dirt road', 76, grid=False)  # Start button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    if Player_amount == 5:
        player = Players[4]
        draw_text(pad_x + CENTRE[0], pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + CENTRE[0], pad_y + 325, player.veh_name, WHITE, 50)

        p1_veh_rect = player.veh_image.get_rect()
        draw_triangle((pad_x + CENTRE[0] - 170 - p1_veh_rect.width, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + CENTRE[0] - 215 - p1_veh_rect.width // 2,
                                       pad_y + CENTRE[1] - p1_veh_rect.height // 2))
        draw_triangle((pad_x + CENTRE[0] + 170 + p1_veh_rect.width, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'
        draw_text(pad_x + CENTRE[0], pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + CENTRE[0] - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + CENTRE[0] + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + CENTRE[0], pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + CENTRE[0], pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + CENTRE[0], pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + CENTRE[0] + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)

    elif Player_amount == 6:
        # 1P VEHICLE
        player = Players[4]
        pos_x = CENTRE[0] // 2 + 10
        draw_text(pad_x + pos_x, pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + pos_x, pad_y + 325, player.veh_name, WHITE, 50)

        draw_triangle((pad_x + pos_x - 345, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + pos_x - 300, pad_y + CENTRE[1] - 150))
        draw_triangle((pad_x + pos_x + 345, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'
        draw_text(pad_x + pos_x, pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + pos_x - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + pos_x + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + pos_x, pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)

        # 2P VEHICLE
        player = Players[5]
        pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
        draw_text(pad_x + pos_x, pad_y + 220, player.name, WHITE, 60, bar=True)
        draw_text(pad_x + pos_x, pad_y + 325, player.veh_name, WHITE, 50)

        draw_triangle((pad_x + pos_x - 345, pad_y + CENTRE[1]), 'left', width=40, height=80)
        Window.blit(player.veh_image, (pad_x + pos_x - 300, pad_y + CENTRE[1] - 150))
        draw_triangle((pad_x + pos_x + 345, pad_y + CENTRE[1]), 'right', width=40, height=80)

        if player.veh_colour == RED_CAR:
            text = 'Red'
        elif player.veh_colour == YELLOW_CAR:
            text = 'Yellow'
        elif player.veh_colour == GREEN_CAR:
            text = 'Green'
        elif player.veh_colour == BLUE_CAR:
            text = 'Blue'
        else:
            text = 'Black'

        draw_text(pad_x + pos_x, pad_y + CENTRE[1] + 160, text, WHITE, 50)
        draw_triangle((pad_x + pos_x - 120, pad_y + CENTRE[1] + 183), 'left', width=25, height=25)
        draw_triangle((pad_x + pos_x + 120, pad_y + CENTRE[1] + 183), 'right', width=25, height=25)

        draw_text(pad_x + pos_x, pad_y + 400, 'Speed', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 520, 'Cornering', WHITE, 40)
        draw_text(pad_x + pos_x, pad_y + 640, 'Durability', WHITE, 40)

        if player.veh_name == 'Family Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Sports Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 4, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Luxury Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 3, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Truck':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
        elif player.veh_name == 'Race Car':
            draw_slider((pad_x + pos_x + 115, pad_y + 408),
                        (200, 22), 5, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 528),
                        (200, 22), 2, 0, 5, center_x=False, fill_color=player.veh_colour)
            draw_slider((pad_x + pos_x + 115, pad_y + 648),
                        (200, 22), 1, 0, 5, center_x=False, fill_color=player.veh_colour)


def race_settings_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Race Settings', WHITE, 100)  # Title

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 100, y + 23, 'Back', WHITE, 55)

    x = pad_x + 800
    y = pad_y + 850
    tile(x, y, 'dirt road', 76, grid=False)  # Start button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Start', WHITE, 70)

    if Player_amount != 6:
        x = pad_x + 511
        y = pad_y + 345
        draw_text(x, y, str(Npc_amount), WHITE, 70)  # NPC Amount option
        draw_text(x, y - 48, 'NPC Amount', WHITE, 30)
        draw_triangle((x - 120, y - 34), 'left', width=25, height=25)
        draw_triangle((x + 120, y - 34), 'right', width=25, height=25)

        x = pad_x + 960
        y = pad_y + 345
        if powerups:
            text = 'On'
        else:
            text = 'Off'
        draw_text(x, y, text, WHITE, 70)  # Powerups option
        draw_text(x, y - 48, 'Powerups', WHITE, 30)
        draw_triangle((x - 100, y - 34), 'left', width=25, height=25)
        draw_triangle((x + 100, y - 34), 'right', width=25, height=25)

        x = pad_x + 1408
        y = pad_y + 345
        draw_text(x, y, str(Total_laps), WHITE, 70)  # Laps option
        draw_text(x, y - 48, 'Laps', WHITE, 30)
        draw_triangle((x - 60, y - 34), 'left', width=25, height=25)
        draw_triangle((x + 60, y - 34), 'right', width=25, height=25)

        if Npc_amount:
            x = pad_x + 511
            y = pad_y + 540
            if Npc_force_veh == 1:
                text = 'family car'
            elif Npc_force_veh == 2:
                text = 'sports car'
            elif Npc_force_veh == 3:
                text = 'luxury car'
            elif Npc_force_veh == 4:
                text = 'truck'
            elif Npc_force_veh == 5:
                text = 'race car'
            else:
                text = 'random'
            draw_text(x, y, str(text), WHITE, 70)  # NPC Vehicle option
            draw_text(x, y - 48, 'NPC Vehicle', WHITE, 30)
            draw_triangle((x - 110, y - 34), 'left', width=25, height=25)
            draw_triangle((x + 110, y - 34), 'right', width=25, height=25)

            x = pad_x + 511
            y = pad_y + 735
            if Npc_force_colour == RED_CAR:
                text = 'red'
            elif Npc_force_colour == YELLOW_CAR:
                text = 'yellow'
            elif Npc_force_colour == GREEN_CAR:
                text = 'green'
            elif Npc_force_colour == BLUE_CAR:
                text = 'blue'
            elif Npc_force_colour == BLACK_CAR:
                text = 'black'
            else:
                text = 'random'
            draw_text(x, y, str(text), WHITE, 70)  # NPC Colour option
            draw_text(x, y - 48, 'NPC Colour', WHITE, 30)
            draw_triangle((x - 110, y - 34), 'left', width=25, height=25)
            draw_triangle((x + 110, y - 34), 'right', width=25, height=25)

        x = pad_x + 1408
        y = pad_y + 540
        draw_text(x, y, str(Players[0].start_pos), WHITE, 70)  # P1 start option
        draw_text(x, y - 48, 'P1 Start', WHITE, 30)
        draw_triangle((x - 90, y - 34), 'left', width=25, height=25)
        draw_triangle((x + 90, y - 34), 'right', width=25, height=25)

        if Player_amount >= 2:
            x = pad_x + 1408
            y = pad_y + 735
            draw_text(x, y, str(Players[1].start_pos), WHITE, 70)  # P2 start option
            draw_text(x, y - 48, 'P2 Start', WHITE, 30)
            draw_triangle((x - 90, y - 34), 'left', width=25, height=25)
            draw_triangle((x + 90, y - 34), 'right', width=25, height=25)

        if Player_amount >= 3:
            x = pad_x + 1408
            y = pad_y + 930
            draw_text(x, y, str(Players[2].start_pos), WHITE, 70)  # P3 start option
            draw_text(x, y - 48, 'P3 Start', WHITE, 30)
            draw_triangle((x - 90, y - 34), 'left', width=25, height=25)
            draw_triangle((x + 90, y - 34), 'right', width=25, height=25)

        if Player_amount >= 4:
            x = pad_x + 1688
            y = pad_y + 540
            draw_text(x, y, str(Players[3].start_pos), WHITE, 70)  # P4 start option
            draw_text(x, y - 48, 'P4 Start', WHITE, 30)
            draw_triangle((x - 90, y - 34), 'left', width=25, height=25)
            draw_triangle((x + 90, y - 34), 'right', width=25, height=25)

        if Player_amount == 5:
            x = pad_x + 1688
            y = pad_y + 735
            draw_text(x, y, str(Players[4].start_pos), WHITE, 70)  # P5 start option
            draw_text(x, y - 48, 'P5 Start', WHITE, 30)
            draw_triangle((x - 90, y - 34), 'left', width=25, height=25)
            draw_triangle((x + 90, y - 34), 'right', width=25, height=25)

    else:
        x = pad_x + 960
        y = pad_y + 345
        draw_text(x, y, str(Total_laps), WHITE, 70)  # Laps option
        draw_text(x, y - 48, 'Laps', WHITE, 30)
        draw_triangle((x - 60, y - 34), 'left', width=25, height=25)
        draw_triangle((x + 60, y - 34), 'right', width=25, height=25)

        x = pad_x + 960
        y = pad_y + 735
        if powerups:
            text = 'On'
        else:
            text = 'Off'
        draw_text(x, y, text, WHITE, 70)  # Powerups option
        draw_text(x, y - 48, 'Powerups', WHITE, 30)
        draw_triangle((x - 100, y - 34), 'left', width=25, height=25)
        draw_triangle((x + 100, y - 34), 'right', width=25, height=25)

        x = pad_x + 511
        y = pad_y + 345
        draw_text(x, y, str(Players[0].start_pos), WHITE, 70)  # P1 start option
        draw_text(x, y - 48, 'P1 Start', WHITE, 30)

        x = pad_x + 511
        y = pad_y + 540
        draw_text(x, y, str(Players[1].start_pos), WHITE, 70)  # P2 start option
        draw_text(x, y - 48, 'P2 Start', WHITE, 30)

        x = pad_x + 511
        y = pad_y + 735
        draw_text(x, y, str(Players[2].start_pos), WHITE, 70)  # P3 start option
        draw_text(x, y - 48, 'P3 Start', WHITE, 30)

        x = pad_x + 1408
        y = pad_y + 345
        draw_text(x, y, str(Players[3].start_pos), WHITE, 70)  # P4 start option
        draw_text(x, y - 48, 'P4 Start', WHITE, 30)

        x = pad_x + 1408
        y = pad_y + 540
        draw_text(x, y, str(Players[4].start_pos), WHITE, 70)  # P5 start option
        draw_text(x, y - 48, 'P5 Start', WHITE, 30)

        x = pad_x + 1408
        y = pad_y + 735
        draw_text(x, y, str(Players[5].start_pos), WHITE, 70)  # P6 start option
        draw_text(x, y - 48, 'P6 Start', WHITE, 30)


def confirm_quit_window(curr_bg, pad_x=0, pad_y=0, surf=Window):
    surf.blit(curr_bg, (pad_x, pad_y))  # Display the current bg

    x = pad_x + CENTRE[0]
    y = pad_y + 128
    draw_text(x, y, 'Are you sure?', WHITE, 100, surf=surf)  # Are you sure? title

    x = pad_x + 347
    y = pad_y + CENTRE[1] - (tile_scale[1] // 2)
    tile(x, y, 'dirt road', 76, grid=False, surf=surf)  # Yes button
    tile(x + 85, y, 'dirt road', 1, grid=False, surf=surf)
    tile(x + 168, y, 'dirt road', 60, grid=False, surf=surf)
    draw_text(x + 153, y + 20, 'Yes', WHITE, 70, surf=surf)

    x = pad_x + CENTRE[0] + 347
    y = pad_y + CENTRE[1] - (tile_scale[1] // 2)
    tile(x, y, 'dirt road', 76, grid=False, surf=surf)  # No button
    tile(x + 85, y, 'dirt road', 1, grid=False, surf=surf)
    tile(x + 168, y, 'dirt road', 60, grid=False, surf=surf)
    draw_text(x + 153, y + 20, 'No', WHITE, 70, surf=surf)


def credits_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Credits', WHITE, 100)  # Title

    y = pad_y + 215
    text = 'Developer - Anthony Guy'
    draw_text(x, y, text, WHITE, 50)  # Credits #1

    y += 70
    text = 'Graphics - Kenney Vleugels'
    draw_text(x, y, text, WHITE, 50)  # Credits #2

    y += 70
    text = 'Menu Music - Trevor Lentz'
    draw_text(x, y, text, WHITE, 50)  # Credits #3

    y += 70
    text = 'Game Music & SFX - Juhani Junkala'
    draw_text(x, y, text, WHITE, 50)  # Credits #4

    y = CENTRE[1] + 80
    text = 'Special Thanks'
    draw_text(x, y, text, WHITE, 50, bar=True)  # Credits #1

    y += 80
    text = 'Keith Brown'
    draw_text(x, y, text, WHITE, 50)  # Credits #2

    y += 70
    text = 'Jonny Farmer'
    draw_text(x, y, text, WHITE, 50)  # Credits #3

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 100, y + 23, 'Back', WHITE, 55)


def tutorial_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Tutorial', WHITE, 100)  # Title

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100))  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100))
    draw_text(x + 100, y + 23, 'Back', WHITE, 55)

    x = pad_x + 535
    y = pad_y + 325
    surf = pygame.transform.scale(pygame.image.load(assets.power_up('boost')), (80, 80))
    surf.set_colorkey(BLACK)
    Window.blit(surf, (x, y))
    draw_text(x + 40, y + 80, 'Boost', WHITE, 60)
    draw_text(x + 40, y + 140, "Temporarily boosts player's", WHITE, 40)
    draw_text(x + 40, y + 180, "speed based on their max speed", WHITE, 40)

    x = pad_x + 535
    y = pad_y + 649
    surf = pygame.transform.scale(pygame.image.load(assets.power_up('repair')), (80, 80))
    surf.set_colorkey(BLACK)
    Window.blit(surf, (x, y))
    draw_text(x + 40, y + 80, 'Repair', WHITE, 60)
    draw_text(x + 40, y + 140, "Repairs player's damage", WHITE, 40)
    draw_text(x + 40, y + 180, "(crashing will cause damage)", WHITE, 40)

    x = pad_x + 1435
    y = pad_y + 325
    surf = pygame.transform.scale(pygame.image.load(assets.power_up('lightning')), (80, 80))
    surf.set_colorkey(BLACK)
    Window.blit(surf, (x, y))
    draw_text(x + 40, y + 80, 'Lightning', WHITE, 60)
    draw_text(x + 40, y + 140, "Randomly causes an", WHITE, 40)
    draw_text(x + 40, y + 180, "NPC to crash", WHITE, 40)

    x = pad_x + 1435
    y = pad_y + 649
    surf = pygame.transform.scale(pygame.image.load(assets.power_up('bullet')), (80, 80))
    surf.set_colorkey(BLACK)
    Window.blit(surf, (x, y))
    draw_text(x + 40, y + 80, 'Bullet', WHITE, 60)
    draw_text(x + 40, y + 140, "Penalises the player", WHITE, 40)
    draw_text(x + 40, y + 180, "by a few seconds", WHITE, 40)

    draw_text(CENTRE[0], 923, 'All penalties are based on car speeds to be fair', WHITE, 40)
    draw_text(CENTRE[0], 963, 'Powerups can only be picked up by players!', WHITE, 40)


def settings_window(curr_bg, pad_x=0, pad_y=0, surf=Window):
    surf.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Settings', WHITE, 100, surf=surf)  # Title

    x = pad_x + CENTRE[0]
    y = pad_y + 220
    draw_text(x, y, 'Make sure you save your changes!', WHITE, 35, surf=surf)  # Tip

    x = pad_x + 210
    y = pad_y + 112
    tile(x, y, 'dirt road', 76, grid=False, scale=(100, 100), surf=surf)  # Back button
    tile(x + 100, y, 'dirt road', 60, grid=False, scale=(100, 100), surf=surf)
    draw_text(x + 100, y + 23, 'Back', WHITE, 55, surf=surf)

    x = pad_x + 800
    y = pad_y + 864
    tile(x, y, 'dirt road', 76, grid=False, surf=surf)  # Save button
    tile(x + 65, y, 'dirt road', 1, grid=False, surf=surf)
    tile(x + 190, y, 'dirt road', 60, grid=False, surf=surf)
    draw_text(x + 160, y + 20, 'Save', WHITE, 70, surf=surf)

    x = pad_x + 514
    y = pad_y + 345
    if Display_resolution == Desktop_info[Screen]:
        text = 'Auto'
    else:
        text = str(Display_resolution[0]) + ' x ' + str(Display_resolution[1])  # Resolution option
    draw_text(x, y, text, WHITE, 70, surf=surf)
    draw_text(x, y - 48, 'Resolution', WHITE, 30, surf=surf)
    draw_triangle((x - 105, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 105, y - 34), 'right', width=25, height=25, surface=surf)

    x = pad_x + 960
    y = pad_y + 345
    text = str(Desktop_info[Screen][0]) + ' x ' + str(Desktop_info[Screen][1])  # Screen option
    draw_text(x, y, str(Screen + 1), WHITE, 70, surf=surf)
    draw_text(x, y - 48, 'Screen', WHITE, 30, surf=surf)
    draw_triangle((x - 75, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 75, y - 34), 'right', width=25, height=25, surface=surf)
    draw_text(x, y + 70, text, WHITE, 30, surf=surf)
    draw_text(x, y + 100, '(Requires restart)', WHITE, 20, surf=surf)

    x = pad_x + 1408
    y = pad_y + 345
    if Menu_animation:
        text = 'On'
    else:
        text = 'Off'
    draw_text(x, y, text, WHITE, 70, surf=surf)  # Animation option
    draw_text(x, y - 48, 'Animations', WHITE, 30, surf=surf)
    draw_triangle((x - 105, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 105, y - 34), 'right', width=25, height=25, surface=surf)

    x = pad_x + 1408
    y = pad_y + 696
    if Mute_volume:
        text = 'On'
    else:
        text = 'Off'
    draw_text(x, y, text, WHITE, 70, surf=surf)  # Mute volume option
    draw_text(x, y - 48, 'Mute volume', WHITE, 30, surf=surf)
    draw_triangle((x - 125, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 125, y - 34), 'right', width=25, height=25, surface=surf)

    x = pad_x + 1408
    y = pad_y + 912
    if Debug:
        text = 'On'
    else:
        text = 'Off'
    draw_text(x, y, text, WHITE, 70, surf=surf)  # Debug option
    draw_text(x, y - 48, 'Debug mode', WHITE, 30, surf=surf)
    draw_triangle((x - 110, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 110, y - 34), 'right', width=25, height=25, surface=surf)

    x = pad_x + 960
    y = pad_y + 696
    draw_slider((x, y + 30), (300, 20), Music_volume, 0, 1, surface=surf)  # Music volume option
    draw_text(x, y - 48, 'Music Volume', WHITE, 30, surf=surf)
    draw_triangle((x - 125, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 125, y - 34), 'right', width=25, height=25, surface=surf)

    x = pad_x + 514
    y = pad_y + 696
    draw_slider((x, y + 30), (300, 20), Sfx_volume, 0, 1, surface=surf)  # Sfx volume option
    draw_text(x, y - 48, 'Sfx Volume', WHITE, 30, surf=surf)
    draw_triangle((x - 110, y - 34), 'left', width=25, height=25, surface=surf)
    draw_triangle((x + 110, y - 34), 'right', width=25, height=25, surface=surf)


def leaderboard_window(curr_bg, pad_x=0, pad_y=0):
    Window.blit(curr_bg, (pad_x, pad_y))

    x = pad_x + CENTRE[0]
    y = pad_y + 115
    draw_text(x, y, 'Leaderboard', WHITE, 100)  # Title

    x = pad_x + 800
    y = pad_y + 764
    tile(x, y, 'dirt road', 76, grid=False)  # Finish button
    tile(x + 65, y, 'dirt road', 1, grid=False)
    tile(x + 190, y, 'dirt road', 60, grid=False)
    draw_text(x + 160, y + 20, 'Finish', WHITE, 70)

    for car_no in range(0, len(Player_positions)):
        rect = draw_text(CENTRE[0], 85 * car_no + 250, str(car_no + 1) + '. ' + Player_positions[car_no][3].name,
                         WHITE, 75, return_rect=True)  # Car position
        Window.blit(pygame.transform.scale(pygame.image.load(Player_positions[car_no][3].image_dir),
                                           (45, 68)), (CENTRE[0] + rect.width // 2 + 15, 85 * car_no + 250))

    # Draw race info at bottom of screen
    text = 'Map: ' + str(Map) + '  |  Laps: ' + str(Total_laps) + '  |  NPCs: ' + str(Npc_amount) + \
           '  |  Players: ' + str(Player_amount) + '  |  Time: ' + str(Race_time)
    draw_text(CENTRE[0], 926, text, WHITE, 50)


def gameplay_gui(player_list, game_countdown_timer, lap_timer):
    if Player_amount >= 1:
        draw_text(CENTRE[0] - 250, 10, 'P1 Lap', WHITE, 40)
        draw_text(CENTRE[0] - 250, 50, str(player_list[0].laps) + '/' + str(Total_laps), WHITE, 30)
        draw_text(CENTRE[0] - 450, 10, 'P1 Damage', WHITE, 40)
        draw_slider((CENTRE[0] - 450, 63), (130, 20), player_list[0].damage, 0,
                    player_list[0].durability, fill_color=player_list[0].colour)
    if Player_amount == 2:
        draw_text(CENTRE[0] + 250, 10, 'P2 Lap', WHITE, 40)
        draw_text(CENTRE[0] + 250, 50, str(player_list[1].laps) + '/' + str(Total_laps), WHITE, 30)
        draw_text(CENTRE[0] + 450, 10, 'P2 Damage', WHITE, 40)
        draw_slider((CENTRE[0] + 450, 63), (130, 20), player_list[1].damage, 0,
                    player_list[1].durability, fill_color=player_list[1].colour)

    draw_text(10, 10, 'Positions', WHITE, 50, center_x=False)  # Leaderboard positions
    for car_no in range(0, len(Player_positions)):
        draw_text(10, 40 * car_no + 60, str(car_no + 1) + '.', WHITE, 40, center_x=False)  # Car position
        Window.blit(pygame.transform.scale(pygame.image.load(Player_positions[car_no][3].image_dir),
                                           (30, 40)), (50, 40 * car_no + 60))  # Small car image
        draw_text(85, 40 * car_no + 60, ' ' + str(Player_positions[car_no][3].laps) + '/' + str(Total_laps) + ' ' +
                  Player_positions[car_no][3].name, WHITE, 40, center_x=False)  # Car name and current lap

    draw_text(1800, 10, 'Total Laps', WHITE, 40)
    if Player_positions:
        draw_text(1850, 50, Player_positions[0][3].name, WHITE, 40)
        if lap_timer > pygame.time.get_ticks():
            draw_text(CENTRE[0], CENTRE[1], 'Lap ' + str(Player_positions[0][3].laps), WHITE, 70, bar=True)
    else:
        draw_text(1850, 50, 0, WHITE, 40)

    if game_countdown_timer:
        draw_text(CENTRE[0], CENTRE[1] - 50, Player_positions[0][3].name + ' has finished!', WHITE, 50)
        draw_text(CENTRE[0], CENTRE[1], 'Game ends in ' + str(game_countdown_timer // 1000), WHITE, 50)


def paused_window():
    Secondary_window.fill(BLACK)
    Secondary_window.blit(Window_screenshot, (0, 0))

    draw_text(CENTRE[0], 115, 'Paused', WHITE, 100, bar=True, surf=Secondary_window)  # Title

    x = CENTRE[0] - 192
    y = CENTRE[1] - 180
    tile(x, y, 'dirt road', 76, grid=False, surf=Secondary_window)  # Resume button
    tile(x + 128, y, 'dirt road', 1, grid=False, surf=Secondary_window)
    tile(x + 256, y, 'dirt road', 60, grid=False, surf=Secondary_window)
    draw_text(x + 193, y + 20, 'Resume', WHITE, 70, surf=Secondary_window)

    x = CENTRE[0] - 192
    y = CENTRE[1] - 30
    tile(x, y, 'dirt road', 76, grid=False, surf=Secondary_window)  # Settings button
    tile(x + 128, y, 'dirt road', 1, grid=False, surf=Secondary_window)
    tile(x + 256, y, 'dirt road', 60, grid=False, surf=Secondary_window)
    draw_text(x + 190, y + 20, 'Settings', WHITE, 70, surf=Secondary_window)

    x = CENTRE[0] - 128
    y = CENTRE[1] + 120
    tile(x, y, 'dirt road', 76, grid=False, surf=Secondary_window)  # Quit button
    tile(x + 128, y, 'dirt road', 60, grid=False, surf=Secondary_window)
    draw_text(x + 130, y + 20, 'Quit', WHITE, 70, surf=Secondary_window)


def menu_background(top=False, right=False, bottom=False, left=False):
    # Function to generate background as single surface
    surf = pygame.surface.Surface((WIDTH, HEIGHT))

    # CORNERS
    tile(0, 0, 'sand', 2, surf=surf, update=False)  # Top left
    tile(14, 0, 'sand', 3, surf=surf, update=False)  # Top right
    tile(0, 9, 'sand', 7, surf=surf, update=False)  # Bottom left
    tile(14, 9, 'sand', 8, surf=surf, update=False)  # Bottom right

    for x in range(1, 14):  # TOP
        tile(x, 0, 'sand', 10, surf=surf, update=False)  # Bottom left
    if top:  # If we want a top entrance...
        tile(6, 0, 'sand', 11, surf=surf, update=False)  # Top left
        tile(7, 0, 'dirt', 5, surf=surf, update=False)  # Top centre
        tile(8, 0, 'sand', 9, surf=surf, update=False)  # Top right

    for y in range(1, 9):  # RIGHT
        tile(14, y, 'sand', 4, surf=surf, update=False)  # Bottom left
    if right:  # If we want a right entrance...
        tile(14, 4, 'sand', 9, surf=surf, update=False)  # Top right
        tile(14, 5, 'sand', 13, surf=surf, update=False)  # Bottom right

    for x in range(1, 14):  # BOTTOM
        tile(x, 9, 'sand', 14, surf=surf, update=False)  # Bottom left
    if bottom:  # If we want a top entrance...
        tile(6, 9, 'sand', 1, surf=surf, update=False)  # Top left
        tile(7, 9, 'dirt', 5, surf=surf, update=False)  # Top centre
        tile(8, 9, 'sand', 13, surf=surf, update=False)  # Top right

    for y in range(1, 9):  # LEFT
        tile(0, y, 'sand', 6, surf=surf, update=False)
    if left:  # If we want a left entrance...
        tile(0, 4, 'sand', 11, surf=surf, update=False)  # Top left
        tile(0, 5, 'sand', 1, surf=surf, update=False)  # Bottom left

    for x in range(1, 14):  # For every row
        for y in range(1, 9):  # For every column
            rand = randint(0, 1)  # Randomize dirt pattern
            if rand == 1:
                ver = 5
            else:
                ver = 12
            tile(x, y, 'dirt', ver, surf=surf, update=False)  # Fill dirt

    return surf  # Return complete image


def animate_window(window, new_window, bg, new_bg, car, direction: str):
    if direction == 'up':
        if new_window == choose_map_window or new_window == choose_vehicle_window:
            for offset_y in range(0, HEIGHT + 1, menu_scroll_speed):  # Animate window transition
                clock.tick(FPS)  # Ensure constant FPS between animations
                window(bg, pad_y=offset_y)
                new_window(new_bg, pad_y=offset_y - HEIGHT)
                if offset_y // 2 + HEIGHT // 2 < 940:
                    car.move(960, offset_y // 2 + HEIGHT // 2)
                else:
                    car.move(960, 940)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)

        elif window == choose_map_window or window == choose_vehicle_window:
            for offset_y in reversed(range(540, 940, menu_scroll_speed)):
                clock.tick(FPS)
                window(bg)
                car.move(960, offset_y)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)
            for offset_y in range(0, HEIGHT + 1, menu_scroll_speed):  # Animate window transition
                clock.tick(FPS)  # Ensure constant FPS between animations
                window(bg, pad_y=offset_y)
                new_window(new_bg, pad_y=offset_y - HEIGHT)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)

        else:
            for offset_y in range(0, HEIGHT + 1, menu_scroll_speed):  # Animate window transition
                clock.tick(FPS)  # Ensure constant FPS between animations
                window(bg, pad_y=offset_y)
                new_window(new_bg, pad_y=offset_y - HEIGHT)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)

    elif direction == 'down':
        if new_window == choose_map_window or new_window == choose_vehicle_window:
            for offset_y in range(540, 940, menu_scroll_speed):
                clock.tick(FPS)
                window(bg)
                car.move(960, offset_y)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)
            for offset_y in reversed(range(0, HEIGHT + 1, menu_scroll_speed)):  # Animate window transition
                clock.tick(FPS)  # Ensure constant frame rate between animations
                window(bg, pad_y=offset_y - HEIGHT)  # Draw main menu screen
                new_window(new_bg, pad_y=offset_y)  # Draw confirm quit screen
                car.draw()
                controller_popup()
                update_screen(full_screen=True)  # Since entire window moves, update entire screen

        elif window == choose_map_window or window == choose_vehicle_window:
            for offset_y in range(940, 1080, menu_scroll_speed):
                clock.tick(FPS)
                window(bg)
                car.move(960, offset_y)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)
            for offset_y in reversed(range(0, HEIGHT + 1, menu_scroll_speed)):  # Animate window transition
                clock.tick(FPS)  # Ensure constant frame rate between animations
                window(bg, pad_y=offset_y - HEIGHT)  # Draw main menu screen
                new_window(new_bg, pad_y=offset_y)  # Draw confirm quit screen
                if offset_y // 2 <= CENTRE[1]:
                    car.move(960, offset_y // 2 + HEIGHT // 2)
                else:
                    car.move(*CENTRE)
                car.draw()
                controller_popup()
                update_screen(full_screen=True)  # Since entire window moves, update entire screen

        else:
            for offset_y in reversed(range(0, HEIGHT + 1, menu_scroll_speed)):  # Animate window transition
                clock.tick(FPS)  # Ensure constant frame rate between animations
                window(bg, pad_y=offset_y - HEIGHT)  # Draw main menu screen
                new_window(new_bg, pad_y=offset_y)  # Draw confirm quit screen
                car.draw()
                controller_popup()
                update_screen(full_screen=True)  # Since entire window moves, update entire screen

    elif direction == 'left':
        for offset_x in range(0, WIDTH + 1, menu_scroll_speed):
            clock.tick(FPS)  # Ensure constant FPS between animations
            window(bg, pad_x=offset_x)
            new_window(new_bg, pad_x=offset_x - WIDTH)  # Draw main menu screen with an offset
            car.draw()
            controller_popup()
            update_screen(full_screen=True)  # Update entire screen

    elif direction == 'right':
        for offset_x in reversed(range(0, WIDTH + 1, menu_scroll_speed)):
            clock.tick(FPS)  # Ensure constant FPS between animations
            window(bg, pad_x=offset_x - WIDTH)
            new_window(new_bg, pad_x=offset_x)  # Draw main menu screen with an offset
            car.draw()
            controller_popup()
            update_screen(full_screen=True)  # Update entire screen


def controller_popup(surf=Window):
    global controller_prompts
    for prompt in controller_prompts:
        if prompt[2]:  # If controller prompt cooldown is active
            if prompt[1]:
                text1 = prompt[0] + ' is '
                text2 = 'connected'
                colour = GREEN_CAR
            else:
                text1 = prompt[0] + ' has '
                text2 = 'disconnected'
                colour = RED_CAR
            if prompt[2] >= pygame.time.get_ticks():  # If time limit has not expired then show
                render1 = pygame.font.Font(fonts.load(), 35).render(text1, False, WHITE)
                render2 = pygame.font.Font(fonts.load(), 35).render(text2, False, colour)
                render3 = pygame.font.Font(fonts.load(), 35).render('.', False, WHITE)
                render = pygame.surface.Surface((render1.get_width() + render2.get_width() + render3.get_width(),
                                                 render1.get_height()))
                render.fill(BLACK)
                render.set_colorkey(BLACK)
                render.blit(render1, (0, 0))
                render.blit(render2, (render1.get_width(), 0))
                render.blit(render3, (render1.get_width() + render2.get_width(), 0))
                if Debug:
                    pygame.draw.rect(render, colour, render.get_rect(), 1)
                shadow_rect = pygame.rect.Rect(render.get_rect().left - 5, render.get_rect().top - 5,
                                               render.get_rect().width + 15, render.get_rect().height + 5)
                shadow_surf = pygame.surface.Surface((shadow_rect.width, shadow_rect.height))
                shadow_surf.fill(WHITE)
                shadow_surf.set_colorkey(WHITE)
                pygame.draw.rect(shadow_surf, BLACK, shadow_rect)
                shadow_surf.set_alpha(95)
                surf.blit(shadow_surf, (5, 5 + render.get_height() * controller_prompts.index(prompt)))
                surf.blit(render, (10, 5 + render.get_height() * controller_prompts.index(prompt)))
                add_screen_update(shadow_rect, 5, 5 + render.get_height() * controller_prompts.index(prompt))
            else:  # If expired then reset to default value(s)
                controller_prompts.remove(prompt)


# -------- DRAWING FUNCTIONS -------- #
def tile(x, y, material, ver, grid=True, scale=tile_scale, surf=Window, update=True):
    if grid:
        x *= tile_scale[0]
        y *= tile_scale[1]

    img = assets.tile(material, ver)  # Convert material and version into directory

    for loaded in loaded_assets:
        if img == loaded[0]:  # If assets has been previously loaded...
            raw_surf = loaded[1]  # Load raw assets and format
            image = pygame.transform.scale(raw_surf, scale)
            surf.blit(image, (x, y))
            if update:
                add_screen_update(image.get_rect(), x, y)  # Set area on screen drawn to be updated later...
            return

    raw_surf = pygame.image.load(img).convert()  # Load assets and save for future
    raw_surf.set_colorkey(BLACK)
    if Debug:
        rect = raw_surf.get_rect()
        pygame.draw.rect(raw_surf, WHITE, (rect[0], rect[1], rect[2], rect[3] - 1), 1)  # Outline tile (debugging)
    loaded_assets.append([img, raw_surf])  # Add loaded assets to loaded assets

    image = pygame.transform.scale(raw_surf, scale)  # Format loaded assets
    surf.blit(image, (x, y))  # Draw assets to screen buffer
    if update:
        add_screen_update(image.get_rect(), x, y)  # Set area on screen drawn to be updated later...


def draw_triangle(pos: tuple[int, int], direction: str,
                  width=18, height=18, colour=WHITE, border=None, border_width=4, surface=Window):
    points = []
    if direction == 'up':
        points.append((pos[0], pos[1] - height / 2))
        points.append((pos[0] + width / 2, pos[1] + height / 2))
        points.append((pos[0] - width / 2, pos[1] + height / 2))
    elif direction == 'down':
        points.append((pos[0] - width / 2, pos[1] - height / 2))
        points.append((pos[0] + width / 2, pos[1] - height / 2))
        points.append((pos[0], pos[1] + height / 2))
    elif direction == 'left':
        points.append((pos[0] + width / 2, pos[1] - height / 2))
        points.append((pos[0] + width / 2, pos[1] + height / 2))
        points.append((pos[0] - width / 2, pos[1]))
    elif direction == 'right':
        points.append((pos[0] + width / 2, pos[1]))
        points.append((pos[0] - width / 2, pos[1] + height / 2))
        points.append((pos[0] - width / 2, pos[1] - height / 2))

    pygame.draw.polygon(surface, colour, points)

    if border:
        pygame.draw.polygon(surface, border, points, border_width)

    # if Debug:
    #     pygame.draw.rect(surface, WHITE, (pos[0] - width/2, pos[1] - height/2, width + 1,  height + 1), 1)
    if surface == Window:
        screen_updates.append((pos[0] - border_width * 2 - width // 2, pos[1] - border_width * 2 - height // 2,
                               width + width // 2, height + height // 2))


def draw_slider(pos: tuple[int, int], size: tuple[int, int],
                value: float or int, min_value: float or int, max_value: float or int, center_x=True,
                fill_color=RED_CAR, surface=Window, border_width=2, border_radius=7):
    surf = pygame.surface.Surface((size[0], size[1]))
    surf.set_colorkey(BLACK)

    ratio = round((size[0] - border_width - 1) / max_value * value)
    if value > min_value:
        pygame.draw.line(surf, fill_color, (border_width, (size[1] / 2) - 1),
                         (ratio, (size[1] / 2) - 1), size[1] - border_width * 2)

    pygame.draw.rect(surf, WHITE, (0, 0, size[0], size[1]), width=border_width, border_radius=border_radius)

    if center_x:
        surface.blit(surf, (pos[0] - size[0] / 2, pos[1] - size[1] / 2))
    else:
        surface.blit(surf, pos)


# Draws text on screen
def draw_text(x, y, text, colour, size, bold=False, bar=False, three_d=False,
              center_x=True, return_rect=False, surf=Window):
    font = pygame.font.Font(fonts.load(bold, bar, three_d), size)
    render = font.render(str(text), True, colour)
    if center_x:
        x -= render.get_width() // 2  # Centre text x position
    if Debug:
        pygame.draw.rect(render, WHITE, render.get_rect(), 1)
    surf.blit(render, (x, y))
    add_screen_update(render.get_rect(), x, y)  # Set area on screen drawn to be updated later...
    if return_rect:
        return render.get_rect()


def render_key(value: str, size=50):
    surf = pygame.surface.Surface((size, size))
    surf.set_colorkey(BLACK)

    pygame.draw.rect(surf, WHITE, (0, 0, size, size), 4, 12)

    if len(value) == 1:
        font = pygame.font.Font(fonts.load(), 40)
        render = font.render(value, False, WHITE)
        surf.blit(render, (((size - render.get_width()) // 2) + 1,
                           ((size - render.get_height()) // 2)))
    else:
        draw_triangle((size // 2, size // 2), value, width=size // 2, height=size // 2, surface=surf)

    return surf


# Draws player controls
def draw_controls(x, y, ver: str or pygame.joystick.Joystick, surface=Window, return_rect=False):
    if type(ver) == str and ver != 'controller':
        surf = pygame.surface.Surface((170, 110))
        surf.set_colorkey(BLACK)
        centre = surf.get_width() // 2
        key_size = 50

        if ver == 'wasd':
            surf.blit(render_key('W', key_size), (centre - key_size // 2, 0))
            surf.blit(render_key('A', key_size), (centre - key_size // 2 - key_size - 10, key_size + 10))
            surf.blit(render_key('S', key_size), (centre - key_size // 2, key_size + 10))
            surf.blit(render_key('D', key_size), (centre - key_size // 2 + key_size + 10, key_size + 10))

        elif ver == 'arrows':
            surf.blit(render_key('up', key_size), (centre - key_size // 2, 0))
            surf.blit(render_key('left', key_size), (centre - key_size // 2 - key_size - 10, key_size + 10))
            surf.blit(render_key('down', key_size), (centre - key_size // 2, key_size + 10))
            surf.blit(render_key('right', key_size), (centre - key_size // 2 + key_size + 10, key_size + 10))

        else:
            raise ValueError('draw_controls | ver can only be wasd, arrows or a controller, not ' + str(ver))

    else:
        surf = pygame.transform.scale(pygame.image.load(assets.controller()), (128, 88))
        surf.set_colorkey(BLACK)

    if Debug:
        pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)

    surface.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))
    add_screen_update(surf.get_rect())
    if return_rect:
        return surf.get_rect()


# Draws any assets on screen
def draw_asset(asset, pos, rotation, scale, return_rect=False):
    global screen_updates
    for loaded in loaded_assets:
        if asset == loaded[0]:  # If assets has been previously loaded...
            raw_surf = loaded[1]  # Load raw assets and format
            surf = pygame.transform.rotate(pygame.transform.scale(raw_surf, scale), rotation)
            if Debug:
                pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)
            Window.blit(surf, pos)
            add_screen_update(surf.get_rect(), pos[0], pos[1])  # Add area to update on screen
            if return_rect:
                return surf.get_rect()
            else:
                return

    # If assets has not been loaded before...
    raw_surf = pygame.image.load(asset).convert()  # Load assets and save for future
    raw_surf.set_colorkey(BLACK)
    loaded_assets.append([asset, raw_surf])
    surf = pygame.transform.rotate(pygame.transform.scale(raw_surf, scale), rotation)
    Window.blit(surf, pos)
    add_screen_update(surf.get_rect(), pos[0], pos[1])  # Set area on screen drawn to be updated later...
    if return_rect:
        return surf.get_rect()


def fade_to_black(speed=12, show_loading=False, paused=False, car=None):
    alpha = Window.get_alpha()
    if not alpha:
        alpha = 255

    Secondary_window.fill(BLACK)

    if show_loading:
        draw_text(CENTRE[0], CENTRE[1] - 50, 'Retro Rampage', WHITE, 100,
                  bar=True, three_d=True, surf=Secondary_window)
        draw_text(CENTRE[0], CENTRE[1] + 150, 'Loading...', WHITE, 50, surf=Secondary_window)

    elif paused:
        paused_window()

    for alpha in reversed(range(0, alpha, speed)):
        clock.tick(FPS)
        Window.set_alpha(alpha)
        Display.blit(pygame.transform.scale(Secondary_window, Display_resolution), (0, 0))
        Display.blit(pygame.transform.scale(Window, Display_resolution), (0, 0))
        if car:
            car.draw()
        pygame.display.update()

    Window.set_alpha(0)  # Ensure final transparency is 0


def fade_from_black(speed=12, show_loading=False, paused=False, window=''):
    alpha = Window.get_alpha()

    Secondary_window.fill(BLACK)

    if show_loading:
        draw_text(CENTRE[0], CENTRE[1] - 50, 'Retro Rampage', WHITE, 100,
                  bar=True, three_d=True, surf=Secondary_window)
        draw_text(CENTRE[0], CENTRE[1] + 150, 'Loading...', WHITE, 50, surf=Secondary_window)

    elif paused:
        if window == 'settings':
            settings_window(Window_screenshot, surf=Secondary_window)
        elif window == 'confirm quit':
            confirm_quit_window(Window_screenshot, surf=Secondary_window)
        else:
            paused_window()

    for alpha in range(alpha, 256, speed):
        clock.tick(FPS)
        Window.set_alpha(alpha)  # Set transparency
        Display.blit(pygame.transform.scale(Secondary_window, Display_resolution), (0, 0))
        Display.blit(pygame.transform.scale(Window, Display_resolution), (0, 0))
        pygame.display.update()

    Window.set_alpha(255)  # Remove transparency


def cycle_veh_right(player: Player):
    if player.veh_name == 'Race Car':
        player.veh_name = 'Family Car'
    elif player.veh_name == 'Family Car':
        player.veh_name = 'Sports Car'
    elif player.veh_name == 'Sports Car':
        player.veh_name = 'Luxury Car'
    elif player.veh_name == 'Luxury Car':
        player.veh_name = 'Truck'
    elif player.veh_name == 'Truck':
        player.veh_name = 'Race Car'
    player.update_image()
    return player


def cycle_veh_left(player: Player):
    if player.veh_name == 'Family Car':
        player.veh_name = 'Race Car'
    elif player.veh_name == 'Race Car':
        player.veh_name = 'Truck'
    elif player.veh_name == 'Truck':
        player.veh_name = 'Luxury Car'
    elif player.veh_name == 'Luxury Car':
        player.veh_name = 'Sports Car'
    elif player.veh_name == 'Sports Car':
        player.veh_name = 'Family Car'
    player.update_image()
    return player


def cycle_veh_colour_right(player: Player):
    if player.veh_colour == YELLOW_CAR:
        player.veh_colour = BLACK_CAR
    elif player.veh_colour == BLACK_CAR:
        player.veh_colour = BLUE_CAR
    elif player.veh_colour == BLUE_CAR:
        player.veh_colour = GREEN_CAR
    elif player.veh_colour == GREEN_CAR:
        player.veh_colour = RED_CAR
    elif player.veh_colour == RED_CAR:
        player.veh_colour = YELLOW_CAR
    player.update_image()
    return player


def cycle_veh_colour_left(player: Player):
    if player.veh_colour == BLACK_CAR:
        player.veh_colour = YELLOW_CAR
    elif player.veh_colour == YELLOW_CAR:
        player.veh_colour = RED_CAR
    elif player.veh_colour == RED_CAR:
        player.veh_colour = GREEN_CAR
    elif player.veh_colour == GREEN_CAR:
        player.veh_colour = BLUE_CAR
    elif player.veh_colour == BLUE_CAR:
        player.veh_colour = BLACK_CAR
    player.update_image()
    return player


def cycle_controls_left(control):
    if control == 'wasd':
        if controllers:
            control = 'controller'
        elif 'arrows' not in controls:
            control = 'arrows'
        else:
            return False
    elif control == 'controller':
        if 'arrows' not in controls:
            control = 'arrows'
        elif 'wasd' not in controls:
            control = 'wasd'
        else:
            return False
    elif control == 'arrows':
        if 'wasd' not in controls:
            control = 'wasd'
        elif controllers:
            control = 'controller'
        else:
            return False
    return control


def cycle_controls_right(control):
    if control == 'wasd':
        if 'arrows' not in controls:
            control = 'arrows'
        elif controllers:
            control = 'controller'
        else:
            return False
    elif control == 'arrows':
        if controllers:
            control = 'controller'
        elif 'wasd' not in controls:
            control = 'wasd'
        else:
            return False
    elif control == 'controller':
        if 'wasd' not in controls:
            control = 'wasd'
        elif 'arrows' not in controls:
            control = 'arrows'
        else:
            return False
    return control


def increase_position(player, amount=1, reset=False):
    if not reset:
        return player[0], player[1], player[2], player[3], player[4], player[5] + amount
    else:
        return player[0], player[1], player[2], player[3], player[4], 0


def decrease_position(player, amount=1, reset=False):
    if not reset:
        return player[0], player[1], player[2], player[3], player[4], player[5] - amount
    else:
        return player[0], player[1], player[2], player[3], player[4], 0


def rand_vehicle():
    rand = randint(1, 5)
    if rand == 1:
        return 'Family Car'
    elif rand == 2:
        return 'Sports Car'
    elif rand == 3:
        return 'Luxury Car'
    elif rand == 4:
        return 'Truck'
    else:
        return 'Race Car'


def rand_color():
    rand = randint(1, 5)
    if rand == 1:
        return RED_CAR
    elif rand == 2:
        return YELLOW_CAR
    elif rand == 3:
        return GREEN_CAR
    elif rand == 4:
        return BLUE_CAR
    else:
        return BLACK_CAR


# -------- MUSIC & SOUND FUNCTIONS -------- #
def menu_music():
    if not Mute_volume:
        playing = pygame.mixer.music.get_busy()
        if not playing:
            global current_song
            current_song = sounds.menu_track(randint(0, 11))
            pygame.mixer.music.load(current_song)
            pygame.mixer.music.set_volume(Music_volume)
            pygame.mixer.music.play()


def game_music(stage, leaderboard=False):
    if not Mute_volume:
        global current_song
        playing = pygame.mixer.music.get_busy()
        while stage > 3:
            stage -= 2
        while stage < 0:
            stage += 1
        if not playing or sounds.game_track(stage) != current_song:
            if leaderboard:
                if not pygame.mixer.music.get_busy():
                    current_song = sounds.game_track(4)
                    pygame.mixer.music.load(sounds.game_track(4))
                    pygame.mixer.music.set_volume(Music_volume)
                    pygame.mixer.music.play()
            else:
                if not pygame.mixer.music.get_busy():
                    current_song = sounds.game_track(stage)
                    pygame.mixer.music.load(sounds.game_track(stage))
                    pygame.mixer.music.set_volume(Music_volume)
                    pygame.mixer.music.play()
                elif current_song != sounds.game_track(stage):
                    pygame.mixer.music.stop()
                    current_song = sounds.game_track(stage)
                    pygame.mixer.music.load(sounds.game_track(stage))
                    pygame.mixer.music.set_volume(Music_volume)
                    pygame.mixer.music.play(fade_ms=200)


def play_sound(event: str):
    if Mute_volume and event != 'error':
        return

    if event == 'error':
        sound = pygame.mixer.Sound(sounds.negative('error', 3))
        pygame.mixer.Sound.set_volume(sound, Sfx_volume)
        pygame.mixer.Sound.play(sound)
        return

    elif event == 'boot':
        boot_1 = pygame.mixer.Sound(sounds.pause_sound(6))
        boot_2 = pygame.mixer.Sound(sounds.pause_sound(7, out=True))
        pygame.mixer.Sound.set_volume(boot_1, Sfx_volume)
        pygame.mixer.Sound.set_volume(boot_2, Sfx_volume)
        pygame.mixer.Sound.play(boot_1)
        sleep(0.5)
        pygame.mixer.Sound.play(boot_2)
        return

    if event == 'collision':
        rand = randint(3, 7)
        while rand == 5:  # Random 3-7 excluding 5
            rand = randint(3, 7)
        sound_dir = sounds.impact(rand)
    elif event == 'power up':
        sound_dir = sounds.positive(3)
    elif event == 'lightning':
        sound_dir = sounds.explosion('medium', 10)
    elif event == 'bullet':
        sound_dir = sounds.machine_gun(6)
    elif event == 'boost':
        sound_dir = sounds.alarm(8)
    elif event == 'repair':
        sound_dir = sounds.interaction(6)
    elif event == 'lap advance':
        sound_dir = sounds.positive(18)
    elif event == 'lap finish':
        sound_dir = sounds.positive(7)
    elif event == 'menu button':
        sound_dir = sounds.menu(4)
    elif event == 'option up':
        sound_dir = sounds.menu(2)
    elif event == 'option down':
        sound_dir = sounds.menu(3)
    elif event == 'controller connect':
        sound_dir = sounds.pause_sound(4)
    elif event == 'controller disconnect':
        sound_dir = sounds.pause_sound(4, out=True)
    elif event == 'text entry':
        sound_dir = sounds.menu(1)
    elif event == 'start button':
        sound_dir = sounds.menu(4, select=True)
    elif event == 'save button':
        sound_dir = sounds.menu(2, select=True)
    elif event == 'traffic light advance':
        sound_dir = sounds.bleep(2)
    elif event == 'traffic light finish':
        sound_dir = sounds.bleep(11)
    elif event == 'pause in':
        sound_dir = sounds.pause_sound(3)
    elif event == 'pause out':
        sound_dir = sounds.pause_sound(3, out=True)
    else:
        raise ValueError('play_sound() - Unknown event: "' + str(event) + '"')

    for audio in loaded_sounds:
        if audio[0] == sound_dir:
            pygame.mixer.Sound.play(audio[1])
            return

    sound = pygame.mixer.Sound(sound_dir)
    pygame.mixer.Sound.set_volume(sound, Sfx_volume)
    pygame.mixer.Sound.play(sound)
    loaded_sounds.append((sound_dir, sound))


def game_music_loop():
    if not Mute_volume:
        while Music_loop:
            if not Window_sleep:
                if Current_lap > Total_laps:  # Advance game music every lap except end and starting lap
                    game_music(Current_lap - 2)
                else:
                    game_music(Current_lap - 1)
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                sleep(0.5)
        return  # Make sure to return properly as this is a thread
    return


def menu_music_loop():
    if not Mute_volume:
        while Music_loop:
            if not Window_sleep:
                if current_window != 'leaderboard':
                    menu_music()
                else:
                    game_music(4, leaderboard=True)
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                sleep(0.5)
        return  # Make sure to return properly as this is a thread
    return


# -------- DISPLAY SCALING & UPDATING FUNCTIONS -------- #
def increase_resolution():
    # Cycles up through supported resolutions
    global Display, Display_resolution, Display_scaling
    if Desktop_info[Screen][0] >= 854 >= Display_resolution[1] and \
            Desktop_info[Screen][1] >= 360 >= Display_resolution[1]:
        Display_resolution = 854, 480  # 480p
    elif Desktop_info[Screen][1] >= 480 >= Display_resolution[1]:
        Display_resolution = 1280, 720  # 720p
    elif Desktop_info[Screen][1] >= 720 >= Display_resolution[1]:
        Display_resolution = 1920, 1080  # 1080p
    elif Desktop_info[Screen][1] >= 1080 >= Display_resolution[1]:
        Display_resolution = 2560, 1440  # 1440p
    elif Desktop_info[Screen][1] >= 1440 >= Display_resolution[1]:
        Display_resolution = 3840, 2160  # 4K
    elif Desktop_info[Screen][1] >= 2160 >= Display_resolution[1]:
        Display_resolution = 640, 360  # 360p

    elif Display_resolution[1] > Desktop_info[Screen][1]:
        Display_resolution = 640, 360

    if Window_resolution != Display_resolution:
        Display_scaling = True
        Display = pygame.display.set_mode(Display_resolution, display=Screen)
    else:
        Display_scaling = False
        Display = pygame.display.set_mode(Display_resolution, display=Screen, flags=pygame.FULLSCREEN)
        pygame.display.set_caption('Retro Rampage')  # Set display name
        pygame.display.set_icon(pygame.image.load(assets.icon()))  # Set display icon
    pygame.mouse.set_pos(*scale_to_display((619, 311)))


def decrease_resolution():
    # Cycles through supported resolutions
    global Display, Display_resolution, Display_scaling
    if Desktop_info[Screen][1] >= 2160 and Display_resolution[1] == 2160:
        Display_resolution = 2560, 1440
    elif Desktop_info[Screen][1] >= 1440 and Display_resolution[1] == 1440:
        Display_resolution = 1920, 1080
    elif Desktop_info[Screen][1] >= 1080 and Display_resolution[1] == 1080:
        Display_resolution = 1280, 720
    elif Desktop_info[Screen][1] >= 720 and Display_resolution[1] == 720:
        Display_resolution = 854, 480
    elif Desktop_info[Screen][1] >= 480 and Display_resolution[1] == 480:
        Display_resolution = 640, 360
    elif Desktop_info[Screen][1] >= 360 and Display_resolution[1] == 360:
        Display_resolution = Desktop_info[Screen]

    if Window_resolution != Display_resolution:
        Display_scaling = True
        Display = pygame.display.set_mode(Display_resolution, display=Screen)
    else:
        Display_scaling = False
        Display = pygame.display.set_mode(Display_resolution, display=Screen)
        pygame.display.toggle_fullscreen()
        pygame.display.set_caption('Retro Rampage')  # Set display name
        pygame.display.set_icon(pygame.image.load(assets.icon()))  # Set display icon
    pygame.mouse.set_pos(*scale_to_display((409, 311)))


def scale_to_display(pos: tuple[int, int]):  # Scale position from window to display
    return ceil(pos[0] / WIDTH * Display_resolution[0]), ceil(pos[1] / HEIGHT * Display_resolution[1])


def scale_to_window(pos: tuple[int, int]):  # Scale position from display to window
    return ceil(pos[0] / Display_resolution[0] * WIDTH), ceil(pos[1] / Display_resolution[1] * HEIGHT)


def scale_rect(scaled_rect, x=None, y=None):
    if x and y:
        scaled_rect[0] += x
        scaled_rect[1] += y
    scaled_rect[0], scaled_rect[1] = scale_to_display((scaled_rect[0], scaled_rect[1]))
    scaled_rect[2], scaled_rect[3] = scale_to_display((scaled_rect[2], scaled_rect[3]))
    return scaled_rect


def add_screen_update(rect, x=None, y=None):  # Calculate assets area and move region to x y position for screen update
    if Display_scaling:
        rect = scale_rect(rect, x, y)
    else:
        if x and y:
            rect[0] += x
            rect[1] += y
    screen_updates.append(rect)


# Only update parts of the screen that have changed since the last frame or update the entire screen
# Also converts the virtual screen (always 1080p) to the actual screen (not always 1080p) to make code simpler
def update_screen(full_screen=False, rect=None, surf=Window):
    global screen_updates
    if rect:
        Display.blit(pygame.transform.scale(surf, Display.get_size()), (0, 0))
        pygame.display.update(rect)
    else:
        if full_screen or len(screen_updates) > 15 or Debug:  # If in debugging mode then always update entire screen
            Display.blit(pygame.transform.scale(surf, Display.get_size()), (0, 0))  # Scale and draw window to screen
            pygame.display.update()  # Update entire screen
        else:
            Display.blit(pygame.transform.scale(surf, Display.get_size()), (0, 0))  # Scale window and draw
            pygame.display.update(screen_updates)  # Update specific areas on display

        screen_updates = []  # After update screen has been called reset updates buffer to None as updates have updated


def controller_added():
    global controllers, controller_prompts, controls
    controller = pygame.joystick.Joystick(len(controllers))
    controllers.append(controller)
    controller_prompts.append((short_controller_name(controller.get_name()),
                               True, pygame.time.get_ticks() + 4000))
    play_sound('controller connect')


def controller_removed(instance_id):
    global controller_prompts
    controller = 0
    for controller_id in controllers:
        if controller_id.get_instance_id() == instance_id:
            controller = controllers[controllers.index(controller_id)]
    controller_prompts.append((short_controller_name(controller.get_name()),
                               False, pygame.time.get_ticks() + 4000))
    for player in Players:
        if player.controls == controller:
            player.controls = player.default_controls

    controller.quit()
    controllers.remove(controller)
    if controller in controls:
        controls.remove(controller)
    play_sound('controller disconnect')


def short_controller_name(name: str):
    if 'Xbox 360' in name:
        return 'Xbox 360 controller (wired)'
    elif 'Xbox One' in name and 'For Windows' in name:
        return 'Xbox One controller (wired)'
    elif name == 'Xbox One S Controller':
        return 'Xbox One S controller (wireless)'
    elif name == 'Xbox Series X Controller':
        return 'Xbox Series X controller (wireless)'
    elif 'Xbox One' in name:
        return 'Xbox One controller'
    else:
        if 'Controller (' in name:
            return 'Controller (wired)'
        else:
            return 'Controller'


# Get mouse position but scale between display and window from (screen size) to 1080p
def get_mouse_pos():
    pos = pygame.mouse.get_pos()
    if Display_scaling:
        return scale_to_window(pos)
    else:
        return pos


# -------- GAME LOOPS -------- #
def game():  # All variables that are not constant
    global Player_positions, Race_time, Countdown, Window_screenshot, button_trigger, \
        Debug, Screen, Menu_animation, Mute_volume, Music_volume, Sfx_volume, loaded_assets, loaded_sounds, \
        Current_lap, Window_sleep, Game_end, Music_loop, music_thread, current_window, Game_paused
    layers = []
    Game_paused = False
    current_window = ''
    game_countdown = 0
    game_countdown_timer = 0
    Player_positions = []
    power_ups = []
    triggered_power_ups = []
    Race_time = pygame.time.get_ticks()
    Game_end = False
    game_quit = False
    Music_loop = True
    saved_timer = 0
    lap_timer = 0
    music_thread = Thread(target=game_music_loop)

    if Map == 'racetrack':
        layers.append(pygame.transform.scale(pygame.image.load(maps.racetrack('bg')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.racetrack('obj')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.racetrack('trk')), (WIDTH, HEIGHT)))

        full_map = pygame.Surface((WIDTH, HEIGHT))
        for layer in layers:
            full_map.blit(layer, (0, 0))

        checkpoint_positions = maps.racetrack('checkpoints')  # Checkpoint position loading and rect generation
        checkpoint_rectangles = []
        for point in checkpoint_positions:
            checkpoint_rectangles.append(pygame.rect.Rect(*point))

        for pos in range(1, 7):
            full_map.blit(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(assets.tile(
                'road', 84)), (50, 80)), paths.Racetrack.start_pos(pos)[2]),
                (paths.Racetrack.start_pos(pos)[0] - 40, paths.Racetrack.start_pos(pos)[1] - 25))

    elif Map == 'snake':
        layers.append(pygame.transform.scale(pygame.image.load(maps.snake('bg')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.snake('obj')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.snake('trk')), (WIDTH, HEIGHT)))

        full_map = pygame.Surface((WIDTH, HEIGHT))
        for layer in layers:
            full_map.blit(layer, (0, 0))

        checkpoint_positions = maps.snake('checkpoints')  # Checkpoint position loading and rect generation
        checkpoint_rectangles = []
        for point in checkpoint_positions:
            checkpoint_rectangles.append(pygame.rect.Rect(*point))

        for pos in range(1, 7):
            full_map.blit(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(assets.tile(
                'road', 84)), (50, 80)), paths.Snake.start_pos(pos)[2]),
                (paths.Snake.start_pos(pos)[0] - 40, paths.Snake.start_pos(pos)[1] - 25))

    elif Map == 'dog bone':
        layers.append(pygame.transform.scale(pygame.image.load(maps.dog_bone('bg')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.dog_bone('obj')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.dog_bone('trk')), (WIDTH, HEIGHT)))

        full_map = pygame.Surface((WIDTH, HEIGHT))
        for layer in layers:
            full_map.blit(layer, (0, 0))

        checkpoint_positions = maps.dog_bone('checkpoints')  # Checkpoint position loading and rect generation
        checkpoint_rectangles = []
        for point in checkpoint_positions:
            checkpoint_rectangles.append(pygame.rect.Rect(*point))

        for pos in range(1, 7):
            full_map.blit(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(assets.tile(
                'road', 84)), (50, 80)), paths.DogBone.start_pos(pos)[2]),
                (paths.DogBone.start_pos(pos)[0] - 40, paths.DogBone.start_pos(pos)[1] - 25))

    elif Map == 'hairpin':
        layers.append(pygame.transform.scale(pygame.image.load(maps.hairpin('bg')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.hairpin('obj')), (WIDTH, HEIGHT)))
        layers.append(pygame.transform.scale(pygame.image.load(maps.hairpin('trk')), (WIDTH, HEIGHT)))

        full_map = pygame.Surface((WIDTH, HEIGHT))
        for layer in layers:
            full_map.blit(layer, (0, 0))

        checkpoint_positions = maps.hairpin('checkpoints')  # Checkpoint position loading and rect generation
        checkpoint_rectangles = []
        for point in checkpoint_positions:
            checkpoint_rectangles.append(pygame.rect.Rect(*point))

        for pos in range(1, 7):
            full_map.blit(pygame.transform.rotate(pygame.transform.scale(pygame.image.load(assets.tile(
                'road', 84)), (50, 80)), paths.Hairpin.start_pos(pos)[2]),
                (paths.Hairpin.start_pos(pos)[0] - 40, paths.Hairpin.start_pos(pos)[1] - 25))

    else:
        raise ValueError('Map is not any track | Map = ' + str(Map))

    track_mask = pygame.mask.from_surface(layers[2])

    if Debug:  # If debug outline track mask in red and outline lap triggers
        # CHECKPOINT TRIGGERS
        checkpoint_surfaces = []
        for point in checkpoint_rectangles:  # Convert each rect into an invisible surface
            checkpoint_surfaces.append(pygame.surface.Surface((point.width, point.height)))  # Create GREEN outline
            checkpoint_surfaces[len(checkpoint_surfaces) - 1].set_colorkey(BLACK)
            pygame.draw.rect(checkpoint_surfaces[len(checkpoint_surfaces) - 1], GREEN_CAR,
                             (0, 0, point.width, point.height), 1)

        # TRACK MASK OUTLINE
        for pos in track_mask.outline():  # Outline track mask
            pygame.draw.circle(full_map, RED, (pos[0], pos[1]), 1)
    else:
        checkpoint_surfaces = []

    track_mask.invert()
    if not Debug:  # Hide mouse when not in debug mode
        pygame.mouse.set_visible(False)

    player_list = []
    for player in range(0, Player_amount):
        player_list.append(Car(Players[player]))

    npc_list = []
    if Npc_amount != 0:
        npc_pos = 1
        while len(npc_list) <= Npc_amount:
            if Player_amount == 1 and npc_pos != Players[0].start_pos or Player_amount == 2 and \
                    npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos or Player_amount == 3 and \
                    npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos and \
                    npc_pos != Players[2].start_pos or Player_amount == 4 and npc_pos != Players[0].start_pos and \
                    npc_pos != Players[1].start_pos and npc_pos != Players[2].start_pos and npc_pos != Players[3] or \
                    Player_amount == 5 and npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos and \
                    npc_pos != Players[2].start_pos and npc_pos != Players[3] and npc_pos != Players[4].start_pos or \
                    Player_amount == 5 and npc_pos != Players[0].start_pos and npc_pos != Players[1].start_pos and \
                    npc_pos != Players[2].start_pos and npc_pos != Players[3] and npc_pos != Players[4].start_pos and \
                    npc_pos != Players[5].start_pos:
                name = Npc_names[randint(0, len(Npc_names) - 1)]  # Only use one name per NPC
                while name[1] or name[0].lower() == Players[0].name.lower() or Player_amount >= 2 and \
                        name[0].lower() == Players[1].name.lower() or Player_amount >= 3 and \
                        name[0].lower() == Players[2].name.lower() or Player_amount >= 4 and \
                        name[0].lower() == Players[3].name.lower() or Player_amount >= 5 and \
                        name[0].lower() == Players[4].name.lower() or Player_amount == 6 and \
                        name[0].lower() and Players[5].name.lower():
                    name = Npc_names[randint(0, len(Npc_names) - 1)]
                name[1] = True
                if Npc_force_veh:
                    vehicle = Npc_force_veh
                else:
                    vehicle = rand_vehicle()
                if Npc_force_colour:
                    colour = Npc_force_colour
                else:
                    colour = rand_color()
                if npc_pos == 1:
                    npc_list.append(NpcCar(vehicle, colour, (40, 70), name[0], Map, 1))
                elif npc_pos == 2:
                    npc_list.append(NpcCar(vehicle, colour, (40, 70), name[0], Map, 2))
                elif npc_pos == 3:
                    npc_list.append(NpcCar(vehicle, colour, (40, 70), name[0], Map, 3))
                elif npc_pos == 4:
                    npc_list.append(NpcCar(vehicle, colour, (40, 70), name[0], Map, 4))
                elif npc_pos == 5:
                    npc_list.append(NpcCar(vehicle, colour, (40, 70), name[0], Map, 5))
                elif npc_pos == 6:
                    npc_list.append(NpcCar(vehicle, colour, (40, 70), name[0], Map, 6))
                else:
                    name[1] = False
                    break
            npc_pos += 1

    if not player_list and not npc_list:
        raise ValueError("There are no players or NPCs!")

    Window.blit(full_map, (0, 0))
    for player in player_list:
        player.draw()
    for npc in npc_list:
        npc.draw()

    gameplay_gui(player_list, 0, 0)
    fade_from_black(show_loading=True)

    if Countdown and not Debug:
        for pos_y in range(-108, 1, 2):  # Animate traffic light into screen
            clock.tick(FPS)
            Window.blit(pygame.image.load(assets.traffic_light(0)), (822, pos_y))
            if Debug:
                pygame.draw.rect(Window, WHITE, (822, pos_y, 276, 108), 1)
            screen_updates.append((822, pos_y, 276, 108))
            for player in player_list:
                player.draw()
            for npc in npc_list:
                npc.draw()
            update_screen(full_screen=True)

        pygame.time.wait(1000)  # Wait a second for the user to adjust to new environment
        tl_stage = 0  # traffic light stage
        start_time = pygame.time.get_ticks()
        while Countdown:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE:
                        # print(get_mouse_pos())  # DEBUGGING
                        pygame.quit()
                        quit()

                elif event.type == pygame.FULLSCREEN:
                    pygame.display.toggle_fullscreen()
                    update_screen(full_screen=True)

            if pygame.time.get_ticks() >= start_time + 5000:
                Window.blit(pygame.image.load(assets.traffic_light(4)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                update_screen()
                play_sound('traffic light finish')
                pygame.time.wait(150)
                Countdown = False
            elif pygame.time.get_ticks() >= start_time + 4000:
                Window.blit(pygame.image.load(assets.traffic_light(3)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                if tl_stage != 3:
                    play_sound('traffic light advance')
                    tl_stage = 3
            elif pygame.time.get_ticks() >= start_time + 3000:
                Window.blit(pygame.image.load(assets.traffic_light(2)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                if tl_stage != 2:
                    play_sound('traffic light advance')
                    tl_stage = 2
            elif pygame.time.get_ticks() >= start_time + 2000:
                Window.blit(pygame.image.load(assets.traffic_light(1)), (822, 0))
                screen_updates.append((822, 0, 276, 108))
                if tl_stage != 1:
                    play_sound('traffic light advance')
                    tl_stage = 1

            for player in player_list:
                player.draw()
            for npc in npc_list:
                npc.draw()

            gameplay_gui(player_list, 0, 0)
            update_screen(full_screen=True)

    while not Game_end and not game_quit:  # Main game loop
        if Player_positions:
            if Current_lap != Player_positions[0][3].laps:
                Current_lap = Player_positions[0][3].laps
                if Current_lap > Total_laps:
                    play_sound('lap finish')
                else:
                    play_sound('lap advance')
                    lap_timer = pygame.time.get_ticks() + 3000
        else:
            Current_lap = 0

        if not Window_sleep:
            clock.tick(20)  # Set FPS in game to 20 so the cars are not too fast, since they move every frame
        else:
            clock.tick(5)

        if not music_thread.is_alive() and not Mute_volume:
            music_thread = Thread(target=game_music_loop)
            music_thread.start()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Music_loop = False
                if music_thread.is_alive():
                    music_thread.join(timeout=0.25)
                pygame.quit()
                quit()

            elif event.type == pygame.FULLSCREEN:
                pygame.display.toggle_fullscreen()
                update_screen(full_screen=True)

            elif event.type == pygame.WINDOWFOCUSLOST and not game_countdown:
                if not game_countdown:
                    if not Game_paused:
                        Game_paused = True
                        play_sound('pause out')
                        Music_volume = ((Music_volume * 10) / 30)
                        pygame.mixer.music.set_volume(Music_volume)
                        pygame.mouse.set_visible(True)
                        Window_screenshot = Window.copy()
                        Window_screenshot.set_alpha(80)
                        fade_to_black(paused=True, speed=15)
                    Window_sleep = True

            if event.type == pygame.WINDOWFOCUSGAINED:
                Window_sleep = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    update_screen(full_screen=True)

                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    if not game_countdown:
                        if not Game_paused:
                            Game_paused = True
                            play_sound('pause out')
                            Music_volume = round(Music_volume / 2, 3)
                            pygame.mixer.music.set_volume(Music_volume)
                            pygame.mouse.set_visible(True)
                            Window_screenshot = Window.copy()
                            Window_screenshot.set_alpha(80)
                            fade_to_black(paused=True, speed=15)
                        else:
                            Game_paused = False
                            play_sound('pause in')
                            Music_volume = round(Music_volume * 2, 3)
                            pygame.mixer.music.set_volume(Music_volume)
                            if not Debug:
                                pygame.mouse.set_visible(False)
                            fade_from_black(paused=True, speed=15, window=current_window)
                            current_window = ''

                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:  # DEBUGGING
                    Music_loop = False
                    print(get_mouse_pos())
                    print(recorded_keys)
                    if music_thread.is_alive():
                        music_thread.join(timeout=0.25)
                    pygame.quit()
                    quit()

        for player in player_list:
            if player.controller:
                if player.controller.get_button(7):
                    if not game_countdown:
                        if not Game_paused:
                            Game_paused = True
                            play_sound('pause out')
                            Music_volume = round(Music_volume / 2, 3)
                            pygame.mixer.music.set_volume(Music_volume)
                            pygame.mouse.set_visible(True)
                            Window_screenshot = Window.copy()
                            Window_screenshot.set_alpha(80)
                            fade_to_black(paused=True, speed=15)
                        else:
                            Game_paused = False
                            play_sound('pause in')
                            Music_volume = round(Music_volume * 2, 3)
                            pygame.mixer.music.set_volume(Music_volume)
                            if not Debug:
                                pygame.mouse.set_visible(False)
                            fade_from_black(paused=True, speed=15)
                    break

        if Game_paused:
            mouse_pos = get_mouse_pos()  # Get current mouse position and scale between display and virtual display

            if not current_window:
                paused_window()  # Always start window with default state

                # RESUME BUTTON
                if 768 <= mouse_pos[0] <= 1151 and 359 <= mouse_pos[1] <= 467:  # Check resume button co-ords
                    x = CENTRE[0] - 192
                    y = CENTRE[1] - 180
                    tile(x, y, 'sand road', 73, grid=False, surf=Secondary_window)  # Resume button
                    tile(x + 128, y, 'sand road', 88, grid=False, surf=Secondary_window)
                    tile(x + 256, y, 'sand road', 57, grid=False, surf=Secondary_window)
                    draw_text(x + 193, y + 20, 'Resume', BLACK, 70, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        Game_paused = False
                        play_sound('pause in')
                        Music_volume = round(Music_volume * 2, 3)
                        pygame.mixer.music.set_volume(Music_volume)
                        if not Debug:
                            pygame.mouse.set_visible(False)
                        fade_from_black(paused=True, speed=9)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # SETTINGS BUTTON
                elif 768 <= mouse_pos[0] <= 1151 and 509 <= mouse_pos[1] <= 617:
                    x = CENTRE[0] - 192
                    y = CENTRE[1] - 30
                    tile(x, y, 'sand road', 73, grid=False, surf=Secondary_window)  # Settings button
                    tile(x + 128, y, 'sand road', 88, grid=False, surf=Secondary_window)
                    tile(x + 256, y, 'sand road', 57, grid=False, surf=Secondary_window)
                    draw_text(x + 190, y + 20, 'Settings', BLACK, 70, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('menu button')
                        current_window = 'settings'
                        Music_volume = round(Music_volume * 2, 3)
                        pygame.mixer.music.set_volume(Music_volume)
                        Secondary_window.fill(BLACK)
                        settings_window(Window_screenshot, surf=Secondary_window)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # QUIT BUTTON
                elif 832 <= mouse_pos[0] <= 1087 and 660 <= mouse_pos[1] <= 767:
                    x = CENTRE[0] - 128
                    y = CENTRE[1] + 120
                    tile(x, y, 'sand road', 73, grid=False, surf=Secondary_window)  # Quit button
                    tile(x + 128, y, 'sand road', 57, grid=False, surf=Secondary_window)
                    draw_text(x + 130, y + 20, 'Quit', BLACK, 70, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('menu button')
                        current_window = 'confirm quit'
                        Secondary_window.fill(BLACK)
                        confirm_quit_window(Window_screenshot, surf=Secondary_window)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            elif current_window == 'settings':
                Secondary_window.fill(BLACK)
                settings_window(Window_screenshot, surf=Secondary_window)  # Always draw default state first
                mouse_pos = get_mouse_pos()  # Get current mouse position

                # Resolution left
                if 396 <= mouse_pos[0] <= 421 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((409, 311), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and Display_resolution <= Desktop_info[Screen]:
                        button_trigger = True
                        play_sound('option down')
                        decrease_resolution()

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Resolution right
                elif 606 <= mouse_pos[0] <= 631 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((619, 311), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and Display_resolution <= Desktop_info[Screen]:
                        button_trigger = True
                        play_sound('option up')
                        increase_resolution()

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Screen left
                elif 872 <= mouse_pos[0] <= 897 and 298 <= mouse_pos[1] <= 324:
                    if Screen + 1 <= 1:
                        draw_triangle((885, 311), 'left', width=25, height=25, border=RED, surface=Secondary_window)
                    else:
                        draw_triangle((885, 311), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            Screen -= 1

                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Screen right
                elif 1022 <= mouse_pos[0] <= 1048 and 298 <= mouse_pos[1] <= 324:
                    if Screen + 1 >= len(Desktop_info):
                        draw_triangle((1035, 311), 'right', width=25, height=25, border=RED, surface=Secondary_window)
                    else:
                        draw_triangle((1035, 311), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            Screen += 1

                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Animations left
                elif 1290 <= mouse_pos[0] <= 1315 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((1303, 311), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('option down')
                        if Menu_animation:
                            Menu_animation = False
                        else:
                            Menu_animation = True

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Animations right
                elif 1500 <= mouse_pos[0] <= 1526 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((1513, 311), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('option up')
                        if Menu_animation:
                            Menu_animation = False
                        else:
                            Menu_animation = True

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Mute left
                elif 1270 <= mouse_pos[0] <= 1296 and 649 <= mouse_pos[1] <= 675:
                    draw_triangle((1283, 662), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            Music_loop = True
                            pygame.mixer.music.unpause()
                        else:
                            Mute_volume = True
                            Music_loop = False
                            pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_sound('option down')

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Mute right
                elif 1520 <= mouse_pos[0] <= 1546 and 649 <= mouse_pos[1] <= 675:
                    draw_triangle((1533, 662), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            Music_loop = True
                            pygame.mixer.music.unpause()
                        else:
                            play_sound('option up')
                            Mute_volume = True
                            Music_loop = False
                            pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_sound('option up')

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Debug left
                elif 1285 <= mouse_pos[0] <= 1310 and 864 <= mouse_pos[1] <= 890:
                    draw_triangle((1298, 878), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        play_sound('option down')
                        button_trigger = True
                        if Debug:
                            Debug = False
                        else:
                            Debug = True
                        loaded_assets = []  # Reload all assets with/without outlines

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Debug right
                elif 1505 <= mouse_pos[0] <= 1531 and 864 <= mouse_pos[1] <= 890:
                    draw_triangle((1518, 878), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        play_sound('option up')
                        button_trigger = True
                        if Debug:
                            Debug = False
                        else:
                            Debug = True

                        loaded_assets = []  # Reload all assets with/without outlines

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Music volume left
                elif 822 <= mouse_pos[0] <= 847 and 649 <= mouse_pos[1] <= 675:
                    if Music_volume <= 0:
                        draw_triangle((835, 662), 'left', width=25, height=25, border=RED, surface=Secondary_window)
                    else:
                        draw_triangle((835, 662), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume - 0.01 <= 0:
                                Music_volume = 0
                            elif Music_volume - 0.01 > 0:
                                Music_volume = round(Music_volume - 0.01, 3)
                            play_sound('option down')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Music volume right
                elif 1072 <= mouse_pos[0] <= 1097 and 649 <= mouse_pos[1] <= 675:
                    if Music_volume >= 1:
                        draw_triangle((1085, 662), 'right', width=25, height=25, border=RED, surface=Secondary_window)
                    else:
                        draw_triangle((1085, 662), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume + 0.01 >= 1:
                                Music_volume = 1
                            elif Music_volume + 0.01 < 1:
                                Music_volume = round(Music_volume + 0.01, 3)
                            play_sound('option up')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Sfx volume left
                elif 391 <= mouse_pos[0] <= 416 and 649 <= mouse_pos[1] <= 675:
                    if Sfx_volume <= 0:
                        draw_triangle((404, 662), 'left', width=25, height=25, border=RED, surface=Secondary_window)
                    else:
                        draw_triangle((404, 662), 'left', width=25, height=25, border=GREY, surface=Secondary_window)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume - 0.01 <= 0:
                                Sfx_volume = 0
                            elif Sfx_volume - 0.01 > 0:
                                Sfx_volume = round(Sfx_volume - 0.01, 4)
                            loaded_sounds = []  # Reload all sounds at new volume
                            play_sound('option down')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Sfx volume right
                elif 611 <= mouse_pos[0] <= 636 and 649 <= mouse_pos[1] <= 675:
                    if Sfx_volume >= 1:
                        draw_triangle((624, 662), 'right', width=25, height=25, border=RED, surface=Secondary_window)
                    else:
                        draw_triangle((624, 662), 'right', width=25, height=25, border=GREY, surface=Secondary_window)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume + 0.01 >= 1:
                                Sfx_volume = 1
                            elif Sfx_volume + 0.01 < 1:
                                Sfx_volume = round(Sfx_volume + 0.01, 4)
                            loaded_sounds = []  # Reload all sounds at new volume
                            play_sound('option up')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # BACK BUTTON
                elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100), surf=Secondary_window)
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100), surf=Secondary_window)
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        saved_timer = None
                        current_window = None
                        Music_volume = round(Music_volume / 2, 3)
                        pygame.mixer.music.set_volume(Music_volume)
                        play_sound('menu button')  # Play button click sound
                        paused_window()

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # SAVE BUTTON
                elif 800 <= mouse_pos[0] <= 1118 and 864 <= mouse_pos[1] <= 972 and not saved_timer:
                    pos_x = 800
                    pos_y = 864
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, surf=Secondary_window)  # Save button
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False, surf=Secondary_window)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False, surf=Secondary_window)
                    draw_text(pos_x + 160, pos_y + 20, 'Save', BLACK, 70, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:  # If any mouse button is pressed while over start button...
                        button_trigger = True
                        play_sound('save button')  # Play button click sounds
                        save_settings()
                        # print('Saved current settings to file.')  # DEBUGGING
                        saved_timer = pygame.time.get_ticks() + 3000
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                if saved_timer:
                    if saved_timer >= pygame.time.get_ticks():
                        draw_text(CENTRE[0], 980, 'Settings saved!', WHITE, 35, surf=Secondary_window)
                    else:
                        saved_timer = None

            elif current_window == 'confirm quit':
                Secondary_window.fill(BLACK)
                confirm_quit_window(Window_screenshot, surf=Secondary_window)
                draw_text(CENTRE[0], 300, 'All progress will be lost!', WHITE, 50, surf=Secondary_window)
                mouse_pos = get_mouse_pos()  # Get current mouse position

                # YES BUTTON
                if 347 <= mouse_pos[0] <= 642 and 486 <= mouse_pos[1] <= 593:
                    pos_x = 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, surf=Secondary_window)  # Yes button
                    tile(pos_x + 85, pos_y, 'sand road', 88, grid=False, surf=Secondary_window)
                    tile(pos_x + 168, pos_y, 'sand road', 57, grid=False, surf=Secondary_window)
                    draw_text(pos_x + 153, pos_y + 20, 'Yes', BLACK, 70, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        Music_volume = round(Music_volume * 2, 3)
                        play_sound('menu button')  # Play button click sounds
                        game_quit = True

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # NO BUTTON
                elif 1307 <= mouse_pos[0] <= 1602 and 486 <= mouse_pos[1] <= 593:
                    pos_x = CENTRE[0] + 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, surf=Secondary_window)  # No button
                    tile(pos_x + 85, pos_y, 'sand road', 88, grid=False, surf=Secondary_window)
                    tile(pos_x + 168, pos_y, 'sand road', 57, grid=False, surf=Secondary_window)
                    draw_text(pos_x + 153, pos_y + 20, 'No', BLACK, 70, surf=Secondary_window)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('menu button')  # Play button click sounds
                        current_window = None
                        paused_window()

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            if Game_paused:
                update_screen(surf=Secondary_window)

        else:  # If game playing
            Window.blit(full_map, (0, 0))

            if Countdown > -108:  # animate traffic light out of screen
                Window.blit(pygame.image.load(assets.traffic_light(4)), (822, Countdown * 2))
                if Debug:
                    pygame.draw.rect(Window, WHITE, (822, Countdown * 2, 276, 108), 1)
                Countdown -= 2

            if len(power_ups) < 10 * Player_amount and powerups:  # Spawn random power-ups
                rand = randint(0, 1400 // (10 + Player_amount + Npc_amount))
                if not rand:
                    rand = randint(0, 3 if Npc_amount else 2)
                    if not rand:
                        ver = 'repair'
                    elif rand == 1:
                        ver = 'boost'
                    elif rand == 2:
                        ver = 'bullet'
                    elif rand == 3:
                        ver = 'lightning'
                    else:
                        raise ValueError('game() [ver] Incorrect value: ' + str(rand))

                    surf = pygame.transform.scale(pygame.image.load(assets.power_up(ver)), (30, 30))
                    surf.set_colorkey(BLACK)
                    if Debug:  # Draw outline of power up
                        border = pygame.Surface((30, 30))
                        border.set_colorkey(BLACK)
                        pygame.draw.rect(border, WHITE, (0, 0, 30, 30), 1)
                        surf.blit(border, (0, 0))
                    mask = pygame.mask.from_surface(surf)
                    on_track = False
                    while not on_track:
                        pos_x = randint(0, WIDTH)
                        pos_y = randint(0, HEIGHT)
                        if not track_mask.overlap(mask, (pos_x, pos_y)):
                            on_track = True
                            power_ups.append((surf, (pos_x, pos_y, 30, 30), (pos_x, pos_y),
                                              mask, ver, pygame.time.get_ticks() + 15000))  # 15s timeout trigger

            for power_up in power_ups:
                if power_up[5] <= pygame.time.get_ticks():
                    power_ups.remove(power_up)
                else:
                    Window.blit(power_up[0], power_up[1])

            for player in player_list:
                player.update()
            for player in range(0, len(player_list)):  # For every player,
                player_list[player].check_track_collisions(track_mask)  # Track collisions
                player_list[player].check_checkpoints(checkpoint_rectangles)  # Checkpoint collisions
                # player_list[player].check_laps(finish_line_rect, halfway_line_rect)  # Lap collisions
                if player_list[player].laps > Total_laps and not game_countdown:
                    game_countdown = pygame.time.get_ticks() + 6000  # Start 5s countdown (start at 6 before shown)
                if len(player_list) == 2 and player == 0:
                    player_list[player].check_car_collision(player_list[player + 1])  # Collisions between players
                elif len(player_list) == 2 and player == 1:
                    player_list[player].check_car_collision(player_list[player - 1])
                for power_up in power_ups:  # Check powerup collisions for each player
                    if player_list[player].mask.overlap(power_up[3], (power_up[1][0] - player_list[player].rect.left,
                                                                      power_up[1][1] - player_list[player].rect.top)):
                        if power_up[4] == 'lightning':  # Lightning powerup targets first to last
                            player_list[player].power_up('lightning_rumble')#
                            for vehicle in Player_positions:
                                if vehicle[3].type == 'NPC':
                                    if not vehicle[3].penalty_time:
                                        vehicle[3].power_up(power_up[4])
                                        break
                                elif vehicle[3].type == 'Player':
                                    if not vehicle[3].bullet_penalty:
                                        vehicle[3].power_up(power_up[4])
                                        break
                        else:
                            player_list[player].power_up(power_up[4])
                        play_sound('power up')
                        triggered_power_ups.append((power_up[4], power_up[2]))
                        power_ups.remove(power_up)

            for npc_pos in range(0, len(npc_list)):
                npc_list[npc_pos].update()  # Update position
                npc_list[npc_pos].check_track_collisions(track_mask)  # Track collisions
                npc_list[npc_pos].check_checkpoints(checkpoint_rectangles)  # Checkpoint collisions
                if npc_list[npc_pos].laps > Total_laps and not game_countdown:
                    game_countdown = pygame.time.get_ticks() + 6000  # Start 5s countdown (start at 6 before shown)
                for other_npc in range(len(npc_list)):
                    if npc_pos != other_npc:
                        npc_list[npc_pos].check_car_collision(npc_list[other_npc])  # Collisions between NPCs
                for player in range(len(player_list)):
                    npc_list[npc_pos].check_car_collision(player_list[player])  # Collisions between player and NPC
                    player_list[player].check_car_collision(npc_list[npc_pos])

            for power_up in triggered_power_ups:
                if len(power_up) < 3:  # Load black outline of power up
                    surf = pygame.Surface((30, 30))
                    surf.fill(WHITE)
                    img = pygame.transform.scale(pygame.image.load(assets.power_up(
                        power_up[0], active=False)), (30, 30))
                    surf.blit(img, (0, 0))
                    surf.set_colorkey(WHITE)
                    surf.set_alpha(255)
                    triggered_power_ups[triggered_power_ups.index(power_up)] = power_up[0], power_up[1], surf
                else:
                    surf = power_up[2]
                alpha = surf.get_alpha()
                if not surf.get_alpha() - 20:
                    triggered_power_ups.remove(power_up)
                else:
                    surf.set_alpha(alpha - 20)
                    Window.blit(surf, power_up[1])

            for player in player_list:
                player.draw()
            for npc_pos in npc_list:
                npc_pos.draw()

            if Debug:
                for point in checkpoint_surfaces:
                    Window.blit(point, checkpoint_rectangles[checkpoint_surfaces.index(point)].topleft)

            if game_countdown:  # Countdown for game finish
                game_countdown_timer = game_countdown - pygame.time.get_ticks()
                if game_countdown_timer // 1000 <= 0:
                    Game_end = True

            Player_positions = get_car_positions(player_list, npc_list)  # Update player positions

            print(player_list[0].laps, player_list[0].checkpoint_count, player_list[0].checkpoint_time)

            gameplay_gui(player_list, game_countdown_timer, lap_timer)  # Draw GUI
            update_screen(full_screen=True)  # Update entire screen

        if Window_sleep:
            sleep(0.5)

    if not game_quit:
        Race_time = pygame.time.get_ticks() - Race_time  # Convert ticks into real time
        seconds = Race_time // 1000
        minutes = 0
        hours = 0
        if seconds >= 60:
            minutes = seconds // 60
            seconds -= minutes * 60
        if minutes >= 60:
            hours = minutes // 60
            minutes -= hours * 60
        if seconds and not minutes and not hours:
            Race_time = str(seconds) + 's'
        elif seconds and minutes and not hours:
            Race_time = str(minutes) + 'm ' + str(seconds) + 's'
        elif seconds and minutes and hours:
            Race_time = str(hours) + 'h ' + str(minutes) + 'm ' + str(seconds) + 's'

    pygame.mixer.music.fadeout(250)
    Music_loop = False
    for player in player_list:
        if player.controller:
            player.controller.stop_rumble()
    fade_to_black(show_loading=True)
    pygame.time.wait(1000)
    return game_quit


def main():
    global Player_amount, Npc_amount, Total_laps, Debug, loaded_assets, Music_volume, Screen, \
        Sfx_volume, loaded_sounds, Mute_volume, Menu_animation, Map, selected_text_entry, button_trigger, Window_sleep,\
        Music_loop, music_thread, powerups, Npc_force_veh, Npc_force_colour, current_window, Players, controllers, \
        controls, selected_text_entry

    Music_loop = True
    menu_loop = True  # Set game sub-loop to menus
    saved_timer = None  # Timer for settings save
    leaderboard = False
    current_window = 'main menu'  # Set beginning window to main menu
    prev_window = ''  # Set previous window to None as game is booting
    car = MenuCar()
    bg = menu_background(top=True, right=True, bottom=True, left=True)  # Set initial values of background(s)
    new_bg = bg
    music_thread = Thread(target=menu_music_loop)

    Players.append(Player(0))

    if Intro_screen and not Debug:
        intro_bg = menu_background()
        Window.blit(intro_bg, (0, 0))
        draw_text(CENTRE[0], CENTRE[1] - 150, 'Retro Rampage', WHITE, 150, bar=True, three_d=True)
        update_screen(full_screen=True)
        play_sound('boot')
        pygame.time.wait(2000)

    while True:  # Entire infinite game loop
        while menu_loop:  # When player is in the menus...
            if not Window_sleep:
                clock.tick(FPS)  # Update the pygame clock every cycle
            else:
                clock.tick(2)

            if not music_thread.is_alive() and not Mute_volume:
                music_thread = Thread(target=menu_music_loop)
                music_thread.start()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Music_loop = False
                    if music_thread.is_alive():
                        music_thread.join(timeout=0.25)
                    pygame.quit()
                    quit()

                elif event.type == pygame.JOYDEVICEADDED:
                    controller_added()
                elif event.type == pygame.JOYDEVICEREMOVED:
                    for player in Players:
                        if player.controls == pygame.joystick.Joystick and \
                                event.__dict__['instance_id'] == player.controls.get_instance_id():
                            if player.id == 1 or player.id == 2:
                                current_window = 'choose players'
                            elif player.id == 3 or player.id == 4:
                                current_window = 'choose players 2'
                            else:
                                current_window = 'choose players 3'
                    controller_removed(event.__dict__['instance_id'])

                elif event.type == pygame.FULLSCREEN:
                    pygame.display.toggle_fullscreen()
                    Window.blit(bg, (0, 0))
                    update_screen(full_screen=True)

                elif event.type == pygame.WINDOWFOCUSLOST:
                    Window_sleep = True
                    if not Mute_volume:
                        pygame.mixer.music.pause()

                elif event.type == pygame.WINDOWFOCUSGAINED:
                    Window_sleep = False
                    if not Mute_volume:
                        pygame.mixer.music.unpause()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                        Window.blit(bg, (0, 0))
                        update_screen(full_screen=True)

                    elif event.key == pygame.K_ESCAPE:  # DEBUGGING
                        # print(get_mouse_pos())
                        Music_loop = False
                        if music_thread.is_alive():
                            music_thread.join(timeout=0.25)
                        pygame.quit()
                        quit()

                    elif event.key == pygame.K_RETURN and selected_text_entry:  # If press enter then stop input
                        selected_text_entry = 0

                    elif event.key == pygame.K_BACKSPACE:
                        Players[selected_text_entry - 1].name = Players[selected_text_entry - 1].name[:-1]

                    if selected_text_entry and len(Players[selected_text_entry - 1].name) <= 12 and \
                            event.key != pygame.K_BACKSPACE and event.key != pygame.K_DELETE and \
                            event.key != pygame.K_TAB:
                        Players[selected_text_entry - 1].name += event.unicode
                        Players[selected_text_entry - 1].name = Players[selected_text_entry - 1].name.title()

            # Main Window
            if current_window == 'main menu':
                if prev_window != current_window:  # On first transition to window, draw background
                    bg = new_bg  # Set previously new background to current background
                    main_window(bg)  # Draw all assets on background
                    car.draw()
                    if prev_window == 'leaderboard' or prev_window == 'tutorial':
                        fade_from_black()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set initial update to complete

                main_window(bg)  # Always start window with default state
                mouse_pos = get_mouse_pos()  # Get current mouse position then scale between display and virtual display
                # print(mouse_pos)

                # QUIT BUTTON
                if 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:  # Check quit button co-ords
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100), update=False)  # Quit button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100), update=False)
                    draw_text(pos_x + 98, pos_y + 21, 'Quit', BLACK, 60)
                    # add_screen_update()
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'confirm quit'  # Set window to change to confirm quit
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(main_window, confirm_quit_window, bg, new_bg, car, 'down')
                        else:
                            confirm_quit_window(bg)
                            car.rotate(180)
                            update_screen(full_screen=True)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # START BUTTON
                elif 340 <= mouse_pos[0] <= 657 and 324 <= mouse_pos[1] <= 431:  # If mouse is over start button...
                    pos_x = 340
                    pos_y = 324
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'choose map'  # Change current window to choose players
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(bottom=True, top=True)
                        get_map_preview()  # Run map preview on startup to declare values
                        if Menu_animation:
                            car.animate('up', bg)
                            animate_window(main_window, choose_map_window, bg, new_bg, car, 'up')
                        else:
                            choose_map_window(new_bg)
                            car.rotate(0)
                            car.move(960, 940)
                            update_screen(full_screen=True)  # Update the screen

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # CREDITS BUTTON
                elif 338 <= mouse_pos[0] <= 671 and 648 <= mouse_pos[1] <= 755:  # Check quit button co-ords
                    pos_x = 340
                    pos_y = 648
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)
                    tile(pos_x + 128, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 205, pos_y, 'sand road', 57, grid=False)
                    draw_text(pos_x + 163, pos_y + 20, 'Credits', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'credits'  # Change current window to choose players
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(right=True)
                        if Menu_animation:
                            car.animate('left', bg)
                            animate_window(main_window, credits_window, bg, new_bg, car, 'left')
                        else:
                            credits_window(new_bg)
                            car.rotate(90)
                            update_screen(full_screen=True)  # Update the screen

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # SETTINGS BUTTON
                elif 1220 <= mouse_pos[0] <= 1604 and 324 <= mouse_pos[1] <= 432:
                    x = 1220
                    y = 324
                    tile(x, y, 'sand road', 73, grid=False)  # Settings button
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    draw_text(x + 190, y + 20, 'Settings', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'settings'  # Change current window to choose players
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(left=True)
                        if Menu_animation:
                            car.animate('right', bg)
                            animate_window(main_window, settings_window, bg, new_bg, car, 'right')
                        else:
                            settings_window(new_bg)
                            car.rotate(270)
                            update_screen(full_screen=True)  # Update the screen

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # TUTORIAL BUTTON
                elif 1220 <= mouse_pos[0] <= 1604 and 648 <= mouse_pos[1] <= 755:
                    x = 1220
                    y = 648
                    tile(x, y, 'sand road', 73, grid=False)  # Tutorial button
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    draw_text(x + 190, y + 20, 'tutorial', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'tutorial'  # Change current window to choose players
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background()
                        fade_to_black(car=car)
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            # Choose Map Window
            elif current_window == 'choose map':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_map_window(bg)
                    car.move(960, 940)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                choose_map_window(bg)
                mouse_pos = get_mouse_pos()
                # print(mouse_pos)

                # Map left
                if 403 <= mouse_pos[0] <= 443 and 500 <= mouse_pos[1] <= 580:
                    if maps.map_index.index(Map) <= 0:
                        draw_triangle((map_preview_pos[0] - 50,  # Map arrows
                                       map_preview_pos[1] + map_preview_size[1] // 2),
                                      'left', width=40, height=80, border=RED)
                    else:
                        draw_triangle((map_preview_pos[0] - 50,  # Map arrows
                                       map_preview_pos[1] + map_preview_size[1] // 2),
                                      'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            Map = maps.map_index[maps.map_index.index(Map) - 1]
                            get_map_preview()
                            update_screen(full_screen=True)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Map right
                if 1477 <= mouse_pos[0] <= 1517 and 500 <= mouse_pos[1] <= 580:
                    if maps.map_index.index(Map) >= len(maps.map_index) - 1:
                        draw_triangle((map_preview_pos[0] + map_preview_size[0] + 50,
                                       map_preview_pos[1] + map_preview_size[1] // 2), 'right', width=40, height=80,
                                      border=RED)
                    else:
                        draw_triangle((map_preview_pos[0] + map_preview_size[0] + 50,
                                       map_preview_pos[1] + map_preview_size[1] // 2), 'right', width=40, height=80,
                                      border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            Map = maps.map_index[maps.map_index.index(Map) + 1]
                            get_map_preview()
                            update_screen(full_screen=True)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # BACK BUTTON
                if 528 <= mouse_pos[0] <= 783 and 890 <= mouse_pos[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Back button
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    draw_text(x + 130, y + 20, 'Back', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'main menu'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, right=True, bottom=True, left=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(choose_map_window, main_window, bg, new_bg, car, 'down')
                        else:
                            main_window(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # SELECT BUTTON
                elif 1100 <= mouse_pos[0] <= 1417 and 890 <= mouse_pos[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Select button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Select', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:  # If any mouse button is pressed while over start button...
                        button_trigger = True
                        current_window = 'choose players'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('up', bg)
                            animate_window(choose_map_window, choose_players_window, bg, new_bg, car, 'up')
                        else:
                            choose_players_window(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            # Choose Players Window
            elif current_window == 'choose players':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_players_window(bg)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated
                    selected_text_entry = 0

                choose_players_window(bg)
                mouse_pos = get_mouse_pos()

                # SINGLE PLAYER BUTTON
                if Player_amount != 1 and 400 <= mouse_pos[0] <= 717 and 476 <= mouse_pos[1] <= 583:
                    x = 400
                    y = 476
                    tile(x, y, 'sand road', 73, grid=False)  # Single Player button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Single', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 1
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'controller':
                                    controls.remove(Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_sound('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # DUAL PLAYER BUTTON
                elif Player_amount != 2 and 1200 <= mouse_pos[0] <= 1517 and 476 <= mouse_pos[1] <= 583:
                    x = 1200
                    y = 476
                    tile(x, y, 'sand road', 73, grid=False)  # Dual Player button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Dual', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 2
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'controller':
                                    controls.remove(Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_sound('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # 3 PLAYER BUTTON
                elif Player_amount != 3 and 93 <= mouse_pos[0] <= 476 and 825 <= mouse_pos[1] <= 932 and controllers:
                    x = 93
                    y = 825
                    tile(x, y, 'sand road', 73, grid=False)
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    draw_text(x + 190, y + 20, '3 Player', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 3
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'controller':
                                    controls.remove(Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_sound('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # 4 PLAYER BUTTON
                elif Player_amount != 4 and 492 <= mouse_pos[0] <= 875 and 825 <= mouse_pos[1] <= 932 and \
                        len(controllers) >= 2:
                    x = 492
                    y = 825
                    tile(x, y, 'sand road', 73, grid=False)  # Settings button
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    draw_text(x + 190, y + 20, '4 Player', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 4
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'controller':
                                    controls.remove(Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_sound('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # 5 PLAYER BUTTON
                elif Player_amount != 5 and 1044 <= mouse_pos[0] <= 1427 and 825 <= mouse_pos[1] <= 932 and \
                        len(controllers) >= 3:
                    x = 1044
                    y = 825
                    tile(x, y, 'sand road', 73, grid=False)  # Settings button
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    draw_text(x + 190, y + 20, '5 Player', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 5
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'controller':
                                    controls.remove(Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_sound('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # 6 PLAYER BUTTON
                elif Player_amount != 6 and 1443 <= mouse_pos[0] <= 1826 and 825 <= mouse_pos[1] <= 932 and \
                        len(controllers) >= 4:
                    x = 1443
                    y = 825
                    tile(x, y, 'sand road', 73, grid=False)  # Settings button
                    tile(x + 128, y, 'sand road', 88, grid=False)
                    tile(x + 256, y, 'sand road', 57, grid=False)
                    draw_text(x + 190, y + 20, '6 Player', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        selected_text_entry = 0
                        Player_amount = 6
                        while len(Players) != Player_amount:
                            if len(Players) < Player_amount:
                                Players.append(Player(len(Players)))
                            elif len(Players) > Player_amount:
                                if Players[len(Players) - 1].controls != 'controller':
                                    controls.remove(Players[len(Players) - 1].controls)
                                Players.pop(len(Players) - 1)
                        play_sound('menu button')
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # BACK BUTTON
                elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        current_window = 'choose map'  # Set window to change to confirm quit
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(choose_players_window, choose_map_window, bg, new_bg, car, 'down')
                        else:
                            choose_map_window(new_bg)
                            car.rotate(180)
                            update_screen(full_screen=True)

                        selected_text_entry = 0

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                if Player_amount == 1:
                    # PLAYER 1 CONTROLS LEFT
                    if 827 <= mouse_pos[0] <= 852 and 355 <= mouse_pos[1] <= 406 and type(Players[0].controls) == str:
                        if not cycle_controls_left(Players[0].controls):
                            draw_triangle((840, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((840, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'controller':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = cycle_controls_left(Players[0].controls)
                                if Players[0].controls != 'controller':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 CONTROLS RIGHT
                    elif 1067 <= mouse_pos[0] <= 1107 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[0].controls) == str:
                        if not cycle_controls_right(Players[0].controls):
                            draw_triangle((1080, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1080, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'controller':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = cycle_controls_right(Players[0].controls)
                                if Players[0].controls != 'controller':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 TEXT ENTRY
                    elif 754 <= mouse_pos[0] <= 1166 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 1:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 1
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # BACK BUTTON
                    elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                        tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                        draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose map'  # Set window to change to confirm quit
                            play_sound('menu button')  # Play button click sounds
                            new_bg = menu_background(top=True, bottom=True)
                            if Menu_animation:
                                car.animate('down', bg)
                                animate_window(choose_players_window, choose_map_window, bg, new_bg, car, 'down')
                            else:
                                choose_map_window(new_bg)
                                car.rotate(180)
                                update_screen(full_screen=True)

                            selected_text_entry = 0

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # START BUTTON
                    elif 800 <= mouse_pos[0] <= 1117 and 940 <= mouse_pos[1] <= 1047 and Players[0].name.strip() and \
                            Players[0].controls != 'controller':
                        # Ensure player(s) can only start the game if all have chosen names
                        pos_x = 800
                        pos_y = 940
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                        buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose vehicle'
                            for player in Players:
                                player.name = player.name.strip()
                            play_sound('menu button')  # Play button click sound
                            new_bg = menu_background(bottom=True, top=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                animate_window(choose_players_window, choose_vehicle_window, bg, new_bg, car, 'up')
                            else:
                                choose_vehicle_window(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0

                elif Player_amount >= 2:
                    # PLAYER 1 CONTROLS LEFT
                    if 427 <= mouse_pos[0] <= 452 and 355 <= mouse_pos[1] <= 406 and type(Players[0].controls) == str:
                        if not cycle_controls_left(Players[0].controls):
                            draw_triangle((440, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((440, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'controller':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = cycle_controls_left(Players[0].controls)
                                if Players[0].controls != 'controller':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 CONTROLS RIGHT
                    elif 667 <= mouse_pos[0] <= 692 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[0].controls) == str:
                        if not cycle_controls_right(Players[0].controls):
                            draw_triangle((680, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((680, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[0].controls != 'controller':
                                    controls.remove(Players[0].controls)
                                Players[0].controls = cycle_controls_right(Players[0].controls)
                                if Players[0].controls != 'controller':
                                    controls.append(Players[0].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 TEXT ENTRY
                    elif 354 <= mouse_pos[0] <= 766 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 1:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 1
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # PLAYER 2 CONTROLS LEFT
                    elif 1227 <= mouse_pos[0] <= 1252 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[1].controls) == str:
                        if not cycle_controls_left(Players[1].controls):
                            draw_triangle((1240, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1240, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[1].controls != 'controller':
                                    controls.remove(Players[1].controls)
                                Players[1].controls = cycle_controls_left(Players[1].controls)
                                if Players[1].controls != 'controller':
                                    controls.append(Players[1].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 2 CONTROLS RIGHT
                    elif 1467 <= mouse_pos[0] <= 1493 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[1].controls) == str:
                        if not cycle_controls_right(Players[1].controls):
                            draw_triangle((1480, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1480, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[1].controls != 'controller':
                                    controls.remove(Players[1].controls)
                                Players[1].controls = cycle_controls_right(Players[1].controls)
                                if Players[1].controls != 'controller':
                                    controls.append(Players[1].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 2 TEXT ENTRY
                    elif 1154 <= mouse_pos[0] <= 1566 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 2:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 2
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # BACK BUTTON
                    elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                        tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                        draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose map'  # Set window to change to confirm quit
                            play_sound('menu button')  # Play button click sounds
                            new_bg = menu_background(top=True, bottom=True)
                            if Menu_animation:
                                car.animate('down', bg)
                                animate_window(choose_players_window, choose_map_window, bg, new_bg, car, 'down')
                            else:
                                choose_map_window(new_bg)
                                car.rotate(180)
                                update_screen(full_screen=True)

                            selected_text_entry = 0

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # START BUTTON
                    elif 800 <= mouse_pos[0] <= 1117 and 940 <= mouse_pos[1] <= 1047 and \
                            Players[0].name.strip() and Players[0].controls != 'controller' and \
                            Players[1].name.strip() and Players[1].controls != 'controller':
                        # Ensure player(s) can only start the game if all have chosen names
                        pos_x = 800
                        pos_y = 940
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                        buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            if Player_amount == 2:
                                current_window = 'choose vehicle'
                            else:
                                current_window = 'choose players 2'
                            for player in Players:
                                player.name = player.name.strip()
                            play_sound('menu button')  # Play button click sound
                            new_bg = menu_background(bottom=True, top=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                if Player_amount == 2:
                                    animate_window(choose_players_window, choose_vehicle_window,
                                                   bg, new_bg, car, 'up')
                                else:
                                    animate_window(choose_players_window, choose_players_window_2,
                                                   bg, new_bg, car, 'up')
                            else:
                                if Player_amount == 2:
                                    choose_vehicle_window(new_bg)
                                else:
                                    choose_players_window_2(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0

                player = Players[0]
                if player.controls == 'controller':
                    for controller in controllers:
                        if controller not in controls and controller.get_button(0):
                            player.controls = controller  # Scan all controllers to bind
                            controls.append(controller)
                elif player.controls in controllers and player.controls in controls:
                    if player.controls.get_button(1):  # Remove controller from bound list to bind again
                        controls.remove(player.controls)
                        player.controls = 'controller'

                if Player_amount > 1:
                    player = Players[1]
                    if player.controls == 'controller':
                        for controller in controllers:
                            if controller not in controls and controller.get_button(0):
                                player.controls = controller  # Scan all controllers to bind
                                controls.append(controller)
                    elif player.controls in controllers and player.controls in controls:
                        if player.controls.get_button(1):  # Remove controller from bound list to bind again
                            controls.remove(player.controls)
                            player.controls = 'controller'

            # Choose Players Window 2
            elif current_window == 'choose players 2':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_players_window_2(bg)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated
                    selected_text_entry = 0

                choose_players_window_2(bg)
                mouse_pos = get_mouse_pos()

                if Player_amount == 3:
                    # PLAYER 3 CONTROLS LEFT
                    if 827 <= mouse_pos[0] <= 852 and 355 <= mouse_pos[1] <= 406 and type(Players[2].controls) == str:
                        if not cycle_controls_left(Players[2].controls):
                            draw_triangle((840, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((840, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[2].controls != 'controller':
                                    controls.remove(Players[2].controls)
                                Players[2].controls = cycle_controls_left(Players[2].controls)
                                if Players[2].controls != 'controller':
                                    controls.append(Players[2].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 3 CONTROLS RIGHT
                    elif 1067 <= mouse_pos[0] <= 1107 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[2].controls) == str:
                        if not cycle_controls_right(Players[2].controls):
                            draw_triangle((1080, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1080, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[2].controls != 'controller':
                                    controls.remove(Players[2].controls)
                                Players[2].controls = cycle_controls_right(Players[2].controls)
                                if Players[2].controls != 'controller':
                                    controls.append(Players[2].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 3 TEXT ENTRY
                    elif 754 <= mouse_pos[0] <= 1166 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 3:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 3
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # BACK BUTTON
                    elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                        tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                        draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose players'  # Set window to change to confirm quit
                            play_sound('menu button')  # Play button click sounds
                            new_bg = menu_background(top=True, bottom=True)
                            if Menu_animation:
                                car.animate('down', bg)
                                animate_window(choose_players_window_2, choose_players_window, bg, new_bg, car, 'down')
                            else:
                                choose_players_window(new_bg)
                                car.rotate(180)
                                update_screen(full_screen=True)

                            selected_text_entry = 0

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # START BUTTON
                    elif 800 <= mouse_pos[0] <= 1117 and 940 <= mouse_pos[1] <= 1047 and \
                            Players[2].name.strip() and Players[2].controls != 'controller':
                        # Ensure player(s) can only start the game if all have chosen names
                        pos_x = 800
                        pos_y = 940
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                        buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            if Player_amount == 3:
                                current_window = 'choose vehicle'
                            else:
                                current_window = 'choose players 3'
                            for player in Players:
                                player.name = player.name.strip()
                            play_sound('menu button')  # Play button click sound
                            new_bg = menu_background(bottom=True, top=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                if Player_amount == 3:
                                    animate_window(choose_players_window_2, choose_vehicle_window, bg, new_bg, car,
                                                   'up')
                                else:
                                    animate_window(choose_players_window_2, choose_players_window_3, bg, new_bg, car,
                                                   'up')
                            else:
                                if Player_amount == 3:
                                    choose_vehicle_window(new_bg)
                                else:
                                    choose_players_window_3(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0

                elif Player_amount >= 4:
                    # PLAYER 1 CONTROLS LEFT
                    if 427 <= mouse_pos[0] <= 452 and 355 <= mouse_pos[1] <= 406 and type(Players[2].controls) == str:
                        if not cycle_controls_left(Players[2].controls):
                            draw_triangle((440, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((440, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[2].controls != 'controller':
                                    controls.remove(Players[2].controls)
                                Players[2].controls = cycle_controls_left(Players[2].controls)
                                if Players[2].controls != 'controller':
                                    controls.append(Players[2].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 CONTROLS RIGHT
                    elif 667 <= mouse_pos[0] <= 692 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[2].controls) == str:
                        if not cycle_controls_right(Players[2].controls):
                            draw_triangle((680, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((680, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[2].controls != 'controller':
                                    controls.remove(Players[2].controls)
                                Players[2].controls = cycle_controls_right(Players[2].controls)
                                if Players[2].controls != 'controller':
                                    controls.append(Players[2].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 2 CONTROLS LEFT
                    elif 1227 <= mouse_pos[0] <= 1252 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[3].controls) == str:
                        if not cycle_controls_left(Players[3].controls):
                            draw_triangle((1240, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1240, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[3].controls != 'controller':
                                    controls.remove(Players[3].controls)
                                Players[3].controls = cycle_controls_left(Players[3].controls)
                                if Players[3].controls != 'controller':
                                    controls.append(Players[3].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 2 CONTROLS RIGHT
                    elif 1467 <= mouse_pos[0] <= 1493 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[3].controls) == str:
                        if not cycle_controls_right(Players[3].controls):
                            draw_triangle((1480, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1480, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[3].controls != 'controller':
                                    controls.remove(Players[3].controls)
                                Players[3].controls = cycle_controls_right(Players[3].controls)
                                if Players[3].controls != 'controller':
                                    controls.append(Players[3].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 TEXT ENTRY
                    elif 354 <= mouse_pos[0] <= 766 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 3:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 3
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # PLAYER 2 TEXT ENTRY
                    elif 1154 <= mouse_pos[0] <= 1566 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 4:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 4
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # BACK BUTTON
                    elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                        tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                        draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose players'  # Set window to change to confirm quit
                            play_sound('menu button')  # Play button click sounds
                            new_bg = menu_background(top=True, bottom=True)
                            if Menu_animation:
                                car.animate('down', bg)
                                animate_window(choose_players_window_2, choose_players_window, bg, new_bg, car, 'down')
                            else:
                                choose_players_window(new_bg)
                                car.rotate(180)
                                update_screen(full_screen=True)

                            selected_text_entry = 0

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # START BUTTON
                    elif 800 <= mouse_pos[0] <= 1117 and 940 <= mouse_pos[1] <= 1047 and \
                            Players[2].name.strip() and Players[2].controls != 'controller' and \
                            Players[3].name.strip() and Players[3].controls != 'controller':
                        # Ensure player(s) can only start the game if all have chosen names
                        pos_x = 800
                        pos_y = 940
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                        buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            if Player_amount == 4:
                                current_window = 'choose vehicle'
                            else:
                                current_window = 'choose players 3'
                            for player in Players:
                                player.name = player.name.strip()
                            play_sound('menu button')  # Play button click sound
                            new_bg = menu_background(bottom=True, top=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                if Player_amount == 4:
                                    animate_window(choose_players_window_2, choose_vehicle_window,
                                                   bg, new_bg, car, 'up')
                                else:
                                    animate_window(choose_players_window_2, choose_players_window_3,
                                                   bg, new_bg, car, 'up')
                            else:
                                if Player_amount == 4:
                                    choose_vehicle_window(new_bg)
                                else:
                                    choose_players_window_3(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0

                # BACK BUTTON
                elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        current_window = 'choose players'  # Set window to change to confirm quit
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(choose_players_window_2, choose_players_window, bg, new_bg, car, 'down')
                        else:
                            choose_players_window(new_bg)
                            car.rotate(180)
                            update_screen(full_screen=True)

                        selected_text_entry = 0

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                    selected_text_entry = 0

                player = Players[2]
                if player.controls == 'controller':
                    for controller in controllers:
                        if controller not in controls and controller.get_button(0):
                            player.controls = controller  # Scan all controllers to bind
                            controls.append(controller)
                elif player.controls in controllers and player.controls in controls:
                    if player.controls.get_button(1):  # Remove controller from bound list to bind again
                        controls.remove(player.controls)
                        player.controls = 'controller'

                if Player_amount > 3:
                    player = Players[3]
                    if player.controls == 'controller':
                        for controller in controllers:
                            if controller not in controls and controller.get_button(0):
                                player.controls = controller  # Scan all controllers to bind
                                controls.append(controller)
                    elif player.controls in controllers and player.controls in controls:
                        if player.controls.get_button(1):  # Remove controller from bound list to bind again
                            controls.remove(player.controls)
                            player.controls = 'controller'

            # Choose Players Window 3
            elif current_window == 'choose players 3':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_players_window_3(bg)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated
                    selected_text_entry = 0

                choose_players_window_3(bg)
                mouse_pos = get_mouse_pos()

                if Player_amount == 5:
                    # PLAYER 5 CONTROLS LEFT
                    if 827 <= mouse_pos[0] <= 852 and 355 <= mouse_pos[1] <= 406 and type(Players[4].controls) == str:
                        if not cycle_controls_left(Players[4].controls):
                            draw_triangle((840, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((840, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[4].controls != 'controller':
                                    controls.remove(Players[4].controls)
                                Players[4].controls = cycle_controls_left(Players[4].controls)
                                if Players[4].controls != 'controller':
                                    controls.append(Players[4].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 5 CONTROLS RIGHT
                    elif 1067 <= mouse_pos[0] <= 1107 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[2].controls) == str:
                        if not cycle_controls_right(Players[2].controls):
                            draw_triangle((1080, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1080, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[2].controls != 'controller':
                                    controls.remove(Players[2].controls)
                                Players[2].controls = cycle_controls_right(Players[2].controls)
                                if Players[2].controls != 'controller':
                                    controls.append(Players[2].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 5 TEXT ENTRY
                    elif 754 <= mouse_pos[0] <= 1166 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 1:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 3
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # BACK BUTTON
                    elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                        tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                        draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose map'  # Set window to change to confirm quit
                            play_sound('menu button')  # Play button click sounds
                            new_bg = menu_background(top=True, bottom=True)
                            if Menu_animation:
                                car.animate('down', bg)
                                animate_window(choose_players_window_3, choose_players_window_2,
                                               bg, new_bg, car, 'down')
                            else:
                                choose_players_window_2(new_bg)
                                car.rotate(180)
                                update_screen(full_screen=True)

                            selected_text_entry = 0

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # START BUTTON
                    elif 800 <= mouse_pos[0] <= 1117 and 940 <= mouse_pos[1] <= 1047 and Players[4].name.strip() and \
                            Players[4].controls != 'controller':
                        # Ensure player(s) can only start the game if all have chosen names
                        pos_x = 800
                        pos_y = 940
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                        buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose vehicle'
                            for player in Players:
                                player.name = player.name.strip()
                            play_sound('menu button')  # Play button click sound
                            new_bg = menu_background(bottom=True, top=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                animate_window(choose_players_window_2, choose_vehicle_window, bg, new_bg, car, 'up')
                            else:
                                choose_vehicle_window(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0

                elif Player_amount == 6:
                    # PLAYER 1 CONTROLS LEFT
                    if 427 <= mouse_pos[0] <= 452 and 355 <= mouse_pos[1] <= 406 and type(Players[4].controls) == str:
                        if not cycle_controls_left(Players[4].controls):
                            draw_triangle((440, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((440, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[4].controls != 'controller':
                                    controls.remove(Players[4].controls)
                                Players[4].controls = cycle_controls_left(Players[4].controls)
                                if Players[4].controls != 'controller':
                                    controls.append(Players[4].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 CONTROLS RIGHT
                    elif 667 <= mouse_pos[0] <= 692 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[4].controls) == str:
                        if not cycle_controls_right(Players[4].controls):
                            draw_triangle((680, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((680, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[4].controls != 'controller':
                                    controls.remove(Players[4].controls)
                                Players[4].controls = cycle_controls_right(Players[4].controls)
                                if Players[4].controls != 'controller':
                                    controls.append(Players[4].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 2 CONTROLS LEFT
                    elif 1227 <= mouse_pos[0] <= 1252 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[5].controls) == str:
                        if not cycle_controls_left(Players[5].controls):
                            draw_triangle((1240, 380), 'left', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1240, 380), 'left', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[5].controls != 'controller':
                                    controls.remove(Players[5].controls)
                                Players[5].controls = cycle_controls_left(Players[5].controls)
                                if Players[5].controls != 'controller':
                                    controls.append(Players[5].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 2 CONTROLS RIGHT
                    elif 1467 <= mouse_pos[0] <= 1493 and 355 <= mouse_pos[1] <= 406 and \
                            type(Players[5].controls) == str:
                        if not cycle_controls_right(Players[5].controls):
                            draw_triangle((1480, 380), 'right', border=RED, width=25, height=50)
                        else:
                            draw_triangle((1480, 380), 'right', border=GREY, width=25, height=50)
                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                if Players[5].controls != 'controller':
                                    controls.remove(Players[5].controls)
                                Players[5].controls = cycle_controls_right(Players[5].controls)
                                if Players[5].controls != 'controller':
                                    controls.append(Players[5].controls)
                            elif button_trigger and not buttons[0]:
                                button_trigger = False

                    # PLAYER 1 TEXT ENTRY
                    elif 354 <= mouse_pos[0] <= 766 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 5:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 5
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # PLAYER 2 TEXT ENTRY
                    elif 1154 <= mouse_pos[0] <= 1566 and 764 <= mouse_pos[1] <= 802:
                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger and selected_text_entry != 6:
                            button_trigger = True
                            play_sound('text entry')
                            selected_text_entry = 6
                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # BACK BUTTON
                    elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                        pos_x = 210
                        pos_y = 112
                        tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                        tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                        draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose map'  # Set window to change to confirm quit
                            play_sound('menu button')  # Play button click sounds
                            new_bg = menu_background(top=True, bottom=True)
                            if Menu_animation:
                                car.animate('down', bg)
                                animate_window(choose_players_window, choose_map_window, bg, new_bg, car, 'down')
                            else:
                                choose_map_window(new_bg)
                                car.rotate(180)
                                update_screen(full_screen=True)

                            selected_text_entry = 0

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    # START BUTTON
                    elif 800 <= mouse_pos[0] <= 1117 and 940 <= mouse_pos[1] <= 1047 and \
                            Players[4].name.strip() and Players[4].controls != 'controller' and \
                            Players[5].name.strip() and Players[5].controls != 'controller':
                        # Ensure player(s) can only start the game if all have chosen names
                        pos_x = 800
                        pos_y = 940
                        tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                        tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                        tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                        draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                        buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                        if buttons[0] and not button_trigger:
                            selected_text_entry = 0
                            button_trigger = True
                            current_window = 'choose vehicle'
                            for player in Players:
                                player.name = player.name.strip()
                            play_sound('menu button')  # Play button click sound
                            new_bg = menu_background(bottom=True, top=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                animate_window(choose_players_window_3, choose_vehicle_window, bg, new_bg, car, 'up')
                            else:
                                choose_vehicle_window(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                        elif button_trigger and not buttons[0]:
                            button_trigger = False

                    elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                        selected_text_entry = 0

                # BACK BUTTON
                elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        current_window = 'choose players'  # Set window to change to confirm quit
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(choose_players_window_3, choose_players_window_2, bg, new_bg, car,
                                           'down')
                        else:
                            choose_players_window_2(new_bg)
                            car.rotate(180)
                            update_screen(full_screen=True)

                        selected_text_entry = 0

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                elif pygame.mouse.get_pressed()[0] and selected_text_entry:
                    selected_text_entry = 0

                player = Players[4]
                if player.controls == 'controller':
                    for controller in controllers:
                        if controller not in controls and controller.get_button(0):
                            player.controls = controller  # Scan all controllers to bind
                            controls.append(controller)
                elif player.controls in controllers and player.controls in controls:
                    if player.controls.get_button(1):  # Remove controller from bound list to bind again
                        controls.remove(player.controls)
                        player.controls = 'controller'

                if Player_amount > 5:
                    player = Players[5]
                    if player.controls == 'controller':
                        for controller in controllers:
                            if controller not in controls and controller.get_button(0):
                                player.controls = controller  # Scan all controllers to bind
                                controls.append(controller)
                    elif player.controls in controllers and player.controls in controls:
                        if player.controls.get_button(1):  # Remove controller from bound list to bind again
                            controls.remove(player.controls)
                            player.controls = 'controller'

            # Choose Vehicle Window
            elif current_window == 'choose vehicle':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_vehicle_window(bg)  # Draw assets on background
                    car.move(960, 940)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated
                    selected_text_entry = 0

                choose_vehicle_window(bg)

                mouse_pos = get_mouse_pos()
                # print(mouse_pos)

                # BACK BUTTON
                if 528 <= mouse_pos[0] <= 783 and 890 <= mouse_pos[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Back button
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    draw_text(x + 130, y + 20, 'Back', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Player_amount == 1 or Player_amount == 2:
                            current_window = 'choose players'
                        elif Player_amount == 3 or Player_amount == 4:
                            current_window = 'choose players 2'
                        else:
                            current_window = 'choose players 3'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            if Player_amount == 1 or Player_amount == 2:
                                animate_window(choose_vehicle_window, choose_players_window, bg, new_bg, car, 'down')
                            elif Player_amount == 3 or Player_amount == 4:
                                animate_window(choose_vehicle_window, choose_players_window_2, bg, new_bg, car, 'down')
                            else:
                                animate_window(choose_vehicle_window, choose_players_window_3, bg, new_bg, car, 'down')
                        else:
                            if Player_amount == 1 or Player_amount == 2:
                                choose_players_window(new_bg)
                            elif Player_amount == 3 or Player_amount == 4:
                                choose_players_window_2(new_bg)
                            else:
                                choose_players_window_3(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # START BUTTON
                elif 1100 <= mouse_pos[0] <= 1417 and 890 <= mouse_pos[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Select button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Start', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        if Player_amount <= 2:
                            current_window = 'race settings'
                            new_bg = menu_background(bottom=True)
                        else:
                            current_window = 'choose vehicle 2'
                            new_bg = menu_background(top=True, bottom=True)
                        play_sound('menu button')  # Play button click sound
                        if Menu_animation:
                            car.animate('up', bg)
                            if Player_amount <= 2:
                                animate_window(choose_vehicle_window, race_settings_window, bg, new_bg, car, 'up')
                            else:
                                animate_window(choose_vehicle_window, choose_vehicle_window_2, bg, new_bg, car, 'up')
                        else:
                            if Player_amount <= 2:
                                race_settings_window(new_bg)
                            else:
                                choose_vehicle_window_2(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                if Player_amount == 1:
                    # 1P VEHICLE LEFT BUTTON
                    if 595 <= mouse_pos[0] <= 635 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((615, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE RIGHT BUTTON
                    elif 1285 <= mouse_pos[0] <= 1325 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((1305, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR LEFT BUTTON
                    elif 827 <= mouse_pos[0] <= 852 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((CENTRE[0] - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR RIGHT BUTTON
                    elif 1067 <= mouse_pos[0] <= 1093 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((CENTRE[0] + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                elif Player_amount >= 2:
                    pos_x = CENTRE[0] // 2 + 10
                    # 1P VEHICLE LEFT BUTTON
                    if 125 <= mouse_pos[0] <= 165 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE RIGHT BUTTON
                    elif 815 <= mouse_pos[0] <= 855 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR LEFT BUTTON
                    elif 357 <= mouse_pos[0] <= 382 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR RIGHT BUTTON
                    elif 597 <= mouse_pos[0] <= 623 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[0])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
                    # 2P VEHICLE LEFT BUTTON
                    if 1065 <= mouse_pos[0] <= 1105 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE RIGHT BUTTON
                    elif 1755 <= mouse_pos[0] <= 1795 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE COLOUR LEFT BUTTON
                    elif 1297 <= mouse_pos[0] <= 1322 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE COLOUR RIGHT BUTTON
                    elif 1537 <= mouse_pos[0] <= 1562 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[1])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

            # Choose Vehicle Window 2
            elif current_window == 'choose vehicle 2':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_vehicle_window_2(bg)  # Draw assets on background
                    car.move(960, 940)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                choose_vehicle_window_2(bg)

                mouse_pos = get_mouse_pos()
                # print(mouse_pos)

                # BACK BUTTON
                if 528 <= mouse_pos[0] <= 783 and 890 <= mouse_pos[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Back button
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    draw_text(x + 130, y + 20, 'Back', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'choose vehicle'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(choose_vehicle_window_2, choose_vehicle_window, bg, new_bg, car, 'down')
                        else:
                            choose_vehicle_window(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # START BUTTON
                elif 1100 <= mouse_pos[0] <= 1417 and 890 <= mouse_pos[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Select button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Start', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        if Player_amount <= 4:
                            current_window = 'race settings'
                            new_bg = menu_background(bottom=True)
                        else:
                            current_window = 'choose vehicle 3'
                            new_bg = menu_background(top=True, bottom=True)
                        play_sound('menu button')  # Play button click sound
                        if Menu_animation:
                            car.animate('up', bg)
                            if Player_amount <= 4:
                                animate_window(choose_vehicle_window_2, race_settings_window, bg, new_bg, car, 'up')
                            else:
                                animate_window(choose_vehicle_window_2, choose_vehicle_window_3, bg, new_bg, car, 'up')
                        else:
                            if Player_amount <= 4:
                                race_settings_window(new_bg)
                            else:
                                choose_vehicle_window_3(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                if Player_amount == 3:
                    # 1P VEHICLE LEFT BUTTON
                    if 595 <= mouse_pos[0] <= 635 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((615, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE RIGHT BUTTON
                    elif 1285 <= mouse_pos[0] <= 1325 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((1305, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR LEFT BUTTON
                    elif 827 <= mouse_pos[0] <= 852 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((CENTRE[0] - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR RIGHT BUTTON
                    elif 1067 <= mouse_pos[0] <= 1093 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((CENTRE[0] + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                elif Player_amount >= 4:
                    pos_x = CENTRE[0] // 2 + 10
                    # 1P VEHICLE LEFT BUTTON
                    if 125 <= mouse_pos[0] <= 165 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE RIGHT BUTTON
                    elif 815 <= mouse_pos[0] <= 855 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR LEFT BUTTON
                    elif 357 <= mouse_pos[0] <= 382 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR RIGHT BUTTON
                    elif 597 <= mouse_pos[0] <= 623 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[2])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
                    # 2P VEHICLE LEFT BUTTON
                    if 1065 <= mouse_pos[0] <= 1105 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[3])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE RIGHT BUTTON
                    elif 1755 <= mouse_pos[0] <= 1795 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[3])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE COLOUR LEFT BUTTON
                    elif 1297 <= mouse_pos[0] <= 1322 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[3])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE COLOUR RIGHT BUTTON
                    elif 1537 <= mouse_pos[0] <= 1562 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[3])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

            # Choose Vehicle Window 3
            elif current_window == 'choose vehicle 3':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    choose_vehicle_window_3(bg)  # Draw assets on background
                    car.move(960, 940)
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                choose_vehicle_window_3(bg)

                mouse_pos = get_mouse_pos()
                # print(mouse_pos)

                # BACK BUTTON
                if 528 <= mouse_pos[0] <= 783 and 890 <= mouse_pos[1] <= 997:
                    x = 528
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Back button
                    tile(x + 128, y, 'sand road', 57, grid=False)
                    draw_text(x + 130, y + 20, 'Back', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'choose vehicle 2'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            animate_window(choose_vehicle_window_3, choose_vehicle_window_2, bg, new_bg, car, 'down')
                        else:
                            choose_vehicle_window_2(new_bg)
                            car.rotate(180)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # START BUTTON
                elif 1100 <= mouse_pos[0] <= 1417 and 890 <= mouse_pos[1] <= 997:
                    x = 1100
                    y = 890
                    tile(x, y, 'sand road', 73, grid=False)  # Select button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Start', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:
                        selected_text_entry = 0
                        button_trigger = True
                        current_window = 'race settings'
                        play_sound('menu button')  # Play button click sound
                        new_bg = menu_background(bottom=True)
                        if Menu_animation:
                            car.animate('up', bg)
                            animate_window(choose_vehicle_window, race_settings_window, bg, new_bg, car, 'up')
                        else:
                            race_settings_window(new_bg)
                            car.rotate(0)
                            car.move(*CENTRE)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                if Player_amount == 5:
                    # 1P VEHICLE LEFT BUTTON
                    if 595 <= mouse_pos[0] <= 635 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((615, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[4])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE RIGHT BUTTON
                    elif 1285 <= mouse_pos[0] <= 1325 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((1305, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[4])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR LEFT BUTTON
                    elif 827 <= mouse_pos[0] <= 852 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((CENTRE[0] - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[4])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR RIGHT BUTTON
                    elif 1067 <= mouse_pos[0] <= 1093 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((CENTRE[0] + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[4])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                elif Player_amount >= 6:
                    pos_x = CENTRE[0] // 2 + 10
                    # 1P VEHICLE LEFT BUTTON
                    if 125 <= mouse_pos[0] <= 165 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[5])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE RIGHT BUTTON
                    elif 815 <= mouse_pos[0] <= 855 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[5])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR LEFT BUTTON
                    elif 357 <= mouse_pos[0] <= 382 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[5])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 1P VEHICLE COLOUR RIGHT BUTTON
                    elif 597 <= mouse_pos[0] <= 623 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[5])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    pos_x = CENTRE[0] + CENTRE[0] // 2 - 10
                    # 2P VEHICLE LEFT BUTTON
                    if 1065 <= mouse_pos[0] <= 1105 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x - 345, CENTRE[1]), 'left', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_left(Players[6])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE RIGHT BUTTON
                    elif 1755 <= mouse_pos[0] <= 1795 and 500 <= mouse_pos[1] <= 580:
                        draw_triangle((pos_x + 345, CENTRE[1]), 'right', width=40, height=80, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_right(Players[6])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE COLOUR LEFT BUTTON
                    elif 1297 <= mouse_pos[0] <= 1322 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x - 120, CENTRE[1] + 183), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            cycle_veh_colour_left(Players[6])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # 2P VEHICLE COLOUR RIGHT BUTTON
                    elif 1537 <= mouse_pos[0] <= 1562 and 710 <= mouse_pos[1] <= 735:
                        draw_triangle((pos_x + 120, CENTRE[1] + 183), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            cycle_veh_colour_right(Players[6])
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

            # Race Settings window
            elif current_window == 'race settings':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    race_settings_window(bg)  # Draw assets on background
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                race_settings_window(bg)
                mouse_pos = get_mouse_pos()
                # print(mouse_pos)

                if Player_amount != 6:
                    # Npc amount left
                    if 381 <= mouse_pos[0] <= 407 and 297 <= mouse_pos[1] <= 324:
                        if Npc_amount <= 0:
                            draw_triangle((390, 311), 'left', width=25, height=25, border=RED)
                        else:
                            draw_triangle((390, 311), 'left', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                Npc_amount -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Npc amount right
                    elif 621 <= mouse_pos[0] <= 647 and 297 <= mouse_pos[1] <= 324:
                        if Npc_amount >= 6 - Player_amount:
                            draw_triangle((632, 311), 'right', width=25, height=25, border=RED)
                        else:
                            draw_triangle((632, 311), 'right', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option up')
                                Npc_amount += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Npc vehicle left
                    elif 388 <= mouse_pos[0] <= 413 and 493 <= mouse_pos[1] <= 518:
                        if Npc_force_veh - 1 < 0:
                            draw_triangle((401, 506), 'left', width=25, height=25, border=RED)
                        else:
                            draw_triangle((401, 506), 'left', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                Npc_force_veh -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Npc vehicle right
                    elif 608 <= mouse_pos[0] <= 633 and 493 <= mouse_pos[1] <= 518:
                        if Npc_force_veh + 1 > 5:
                            draw_triangle((621, 506), 'right', width=25, height=25, border=RED)
                        else:
                            draw_triangle((621, 506), 'right', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option up')
                                Npc_force_veh += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Npc colour left
                    elif 388 <= mouse_pos[0] <= 413 and 688 <= mouse_pos[1] <= 713:
                        if not Npc_force_colour:
                            draw_triangle((401, 701), 'left', width=25, height=25, border=RED)
                        else:
                            draw_triangle((401, 701), 'left', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                if Npc_force_colour == BLACK_CAR:
                                    Npc_force_colour = BLUE_CAR
                                elif Npc_force_colour == BLUE_CAR:
                                    Npc_force_colour = GREEN_CAR
                                elif Npc_force_colour == GREEN_CAR:
                                    Npc_force_colour = YELLOW_CAR
                                elif Npc_force_colour == YELLOW_CAR:
                                    Npc_force_colour = RED_CAR
                                elif Npc_force_colour == RED_CAR:
                                    Npc_force_colour = None
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Npc colour right
                    elif 608 <= mouse_pos[0] <= 633 and 688 <= mouse_pos[1] <= 713:
                        if Npc_force_colour == BLACK_CAR:
                            draw_triangle((621, 701), 'right', width=25, height=25, border=RED)
                        else:
                            draw_triangle((621, 701), 'right', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option up')
                                if not Npc_force_colour:
                                    Npc_force_colour = RED_CAR
                                elif Npc_force_colour == RED_CAR:
                                    Npc_force_colour = YELLOW_CAR
                                elif Npc_force_colour == YELLOW_CAR:
                                    Npc_force_colour = GREEN_CAR
                                elif Npc_force_colour == GREEN_CAR:
                                    Npc_force_colour = BLUE_CAR
                                elif Npc_force_colour == BLUE_CAR:
                                    Npc_force_colour = BLACK_CAR
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Laps left
                    elif 1335 <= mouse_pos[0] <= 1360 and 297 <= mouse_pos[1] <= 324:
                        if Total_laps <= 1:
                            draw_triangle((1348, 311), 'left', width=25, height=25, border=RED)
                        else:
                            draw_triangle((1348, 311), 'left', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                Total_laps -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Laps right
                    elif 1455 <= mouse_pos[0] <= 1481 and 297 <= mouse_pos[1] <= 324:
                        if Total_laps >= 10:
                            draw_triangle((1468, 311), 'right', width=25, height=25, border=RED)
                        else:
                            draw_triangle((1468, 311), 'right', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option up')
                                Total_laps += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Powerups left
                    elif 847 <= mouse_pos[0] <= 872 and 298 <= mouse_pos[1] <= 324:
                        draw_triangle((860, 311), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # Powerups right
                    elif 1047 <= mouse_pos[0] <= 1072 and 298 <= mouse_pos[1] <= 323:
                        draw_triangle((1060, 311), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # P1 start left
                    elif 1305 <= mouse_pos[0] <= 1330 and 493 <= mouse_pos[1] <= 518:
                        if Player_amount == 2:
                            if Players[0].start_pos - 1 < 1 or Players[0].start_pos - 2 < 1 and \
                                    Players[0].start_pos - 1 == Players[1].start_pos and Player_amount == 2:
                                draw_triangle((1318, 506), 'left', width=25, height=25, border=RED)
                            else:
                                draw_triangle((1318, 506), 'left', width=25, height=25, border=GREY)

                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_sound('option down')
                                    if Players[0].start_pos - 1 == Players[1].start_pos and Player_amount == 2:
                                        Players[0].start_pos -= 2
                                    else:
                                        Players[0].start_pos -= 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False

                        else:
                            if Players[0].start_pos - 1 < 1:
                                draw_triangle((1318, 506), 'left', width=25, height=25, border=RED)
                            else:
                                draw_triangle((1318, 506), 'left', width=25, height=25, border=GREY)

                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_sound('option down')
                                    Players[0].start_pos -= 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False

                    # P1 start right
                    elif 1485 <= mouse_pos[0] <= 1510 and 493 <= mouse_pos[1] <= 518:
                        if Player_amount == 2:
                            if Players[0].start_pos + 1 > 6 or Players[0].start_pos + 1 == Players[1].start_pos and \
                                    Players[0].start_pos + 2 > 6 and Player_amount == 2:
                                draw_triangle((1498, 506), 'right', width=25, height=25, border=RED)
                            else:
                                draw_triangle((1498, 506), 'right', width=25, height=25, border=GREY)

                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_sound('option down')
                                    if Players[0].start_pos + 1 == Players[1].start_pos and Player_amount == 2:
                                        Players[0].start_pos += 2
                                    else:
                                        Players[0].start_pos += 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False
                        else:
                            if Players[0].start_pos + 1 > 6:
                                draw_triangle((1498, 506), 'right', width=25, height=25, border=RED)
                            else:
                                draw_triangle((1498, 506), 'right', width=25, height=25, border=GREY)

                                buttons = pygame.mouse.get_pressed()
                                if buttons[0] and not button_trigger:
                                    button_trigger = True
                                    play_sound('option down')
                                    Players[0].start_pos += 1
                                elif not buttons[0] and button_trigger:
                                    button_trigger = False

                    # P2 start left
                    elif 1305 <= mouse_pos[0] <= 1330 and 688 <= mouse_pos[1] <= 713 and Player_amount >= 2:
                        if Players[1].start_pos - 1 < 1 or Players[1].start_pos - 2 < 1 and \
                                Players[1].start_pos - 1 == Players[0].start_pos:
                            draw_triangle((1318, 701), 'left', width=25, height=25, border=RED)
                        else:
                            draw_triangle((1318, 701), 'left', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                if Players[1].start_pos - 1 == Players[0].start_pos and Player_amount == 2:
                                    Players[1].start_pos -= 2
                                else:
                                    Players[1].start_pos -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # P2 start right
                    elif 1485 <= mouse_pos[0] <= 1510 and 688 <= mouse_pos[1] <= 713 and Player_amount >= 2:
                        if Players[1].start_pos + 1 > 6 or Players[1].start_pos + 1 == Players[0].start_pos and \
                                Players[1].start_pos + 2 > 6:
                            draw_triangle((1498, 701), 'right', width=25, height=25, border=RED)
                        else:
                            draw_triangle((1498, 701), 'right', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                if Players[1].start_pos + 1 == Players[0].start_pos and Player_amount == 2:
                                    Players[1].start_pos += 2
                                else:
                                    Players[1].start_pos += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # P3 start left
                    elif 0 <= mouse_pos[0] <= 1 and 0 <= mouse_pos[1] <= 1 and Player_amount >= 3:
                        pass

                    # P3 start right
                    elif 0 <= mouse_pos[0] <= 1 and 0 <= mouse_pos[1] <= 1 and Player_amount >= 3:
                        pass

                    # P4 start left
                    elif 0 <= mouse_pos[0] <= 1 and 0 <= mouse_pos[1] <= 1 and Player_amount >= 4:
                        pass

                    # P4 start right
                    elif 0 <= mouse_pos[0] <= 1 and 0 <= mouse_pos[1] <= 1 and Player_amount >= 4:
                        pass

                    # P5 start left
                    elif 0 <= mouse_pos[0] <= 1 and 0 <= mouse_pos[1] <= 1 and Player_amount >= 5:
                        pass

                    # P5 start right
                    elif 0 <= mouse_pos[0] <= 1 and 0 <= mouse_pos[1] <= 1 and Player_amount >= 5:
                        pass

                else:
                    # Laps left
                    if 887 <= mouse_pos[0] <= 912 and 298 <= mouse_pos[1] <= 323:
                        if Total_laps <= 1:
                            draw_triangle((900, 311), 'left', width=25, height=25, border=RED)
                        else:
                            draw_triangle((900, 311), 'left', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option down')
                                Total_laps -= 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Laps right
                    elif 1007 <= mouse_pos[0] <= 1032 and 298 <= mouse_pos[1] <= 323:
                        if Total_laps >= 10:
                            draw_triangle((1020, 311), 'right', width=25, height=25, border=RED)
                        else:
                            draw_triangle((1020, 311), 'right', width=25, height=25, border=GREY)

                            buttons = pygame.mouse.get_pressed()
                            if buttons[0] and not button_trigger:
                                button_trigger = True
                                play_sound('option up')
                                Total_laps += 1
                            elif not buttons[0] and button_trigger:
                                button_trigger = False

                    # Powerups left
                    elif 847 <= mouse_pos[0] <= 872 and 688 <= mouse_pos[1] <= 713:
                        draw_triangle((860, 701), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                    # Powerups right
                    elif 1047 <= mouse_pos[0] <= 1072 and 688 <= mouse_pos[1] <= 713:
                        draw_triangle((1060, 701), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            if powerups:
                                powerups = False
                            else:
                                powerups = True
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # BACK BUTTON
                if 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Player_amount == 1 or Player_amount == 2:
                            current_window = 'choose vehicle'
                        elif Player_amount == 3 or Player_amount == 4:
                            current_window = 'choose vehicle 2'
                        else:
                            current_window = 'choose vehicle 3'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, bottom=True)
                        if Menu_animation:
                            car.animate('down', bg)
                            if Player_amount == 1 or Player_amount == 2:
                                animate_window(race_settings_window, choose_vehicle_window, bg, new_bg, car, 'down')
                            elif Player_amount == 3 or Player_amount == 4:
                                animate_window(race_settings_window, choose_vehicle_window_2, bg, new_bg, car, 'down')
                            else:
                                animate_window(race_settings_window, choose_vehicle_window_3, bg, new_bg, car, 'down')
                        else:
                            if Player_amount == 1 or Player_amount == 2:
                                choose_vehicle_window(new_bg)
                            elif Player_amount == 3 or Player_amount == 4:
                                choose_vehicle_window_2(new_bg)
                            else:
                                choose_vehicle_window_3(new_bg)
                            car.rotate(180)
                            update_screen(full_screen=True)

                    elif button_trigger and not buttons[0]:
                        button_trigger = False

                # START BUTTON
                elif 800 <= mouse_pos[0] <= 1118 and 850 <= mouse_pos[1] <= 958:  # If mouse is over start button...
                    pos_x = 800
                    pos_y = 850
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Draw active start button
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    draw_text(pos_x + 160, pos_y + 20, 'Start', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:  # If any mouse button is pressed while over start button...
                        button_trigger = True
                        play_sound('start button')  # Play button click sounds
                        pygame.mixer.music.fadeout(250)
                        menu_loop = False
                    elif button_trigger and not buttons[0]:
                        button_trigger = False

            # Confirm Quit Window
            elif current_window == 'confirm quit':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    confirm_quit_window(bg)  # Draw assets on background
                    car.draw()
                    controller_popup()
                    if prev_window == 'leaderboard':
                        fade_from_black()
                        leaderboard = True
                    else:
                        leaderboard = False
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                confirm_quit_window(bg)  # Always draw default state first
                mouse_pos = get_mouse_pos()  # Get current mouse position

                # YES BUTTON
                if 347 <= mouse_pos[0] <= 642 and 486 <= mouse_pos[1] <= 593:
                    pos_x = 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Yes button
                    tile(pos_x + 85, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 168, pos_y, 'sand road', 57, grid=False)
                    draw_text(pos_x + 153, pos_y + 20, 'Yes', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('menu button')  # Play button click sounds
                        pygame.mixer.fadeout(50)
                        pygame.mixer.music.fadeout(500)
                        Music_loop = False
                        if music_thread.is_alive():
                            music_thread.join(timeout=0.25)
                        sleep(0.5)
                        pygame.quit()
                        quit()

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # NO BUTTON
                elif 1307 <= mouse_pos[0] <= 1602 and 486 <= mouse_pos[1] <= 593:
                    pos_x = CENTRE[0] + 347
                    pos_y = CENTRE[1] - (tile_scale[1] // 2)
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)  # No button
                    tile(pos_x + 85, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 168, pos_y, 'sand road', 57, grid=False)
                    draw_text(pos_x + 153, pos_y + 20, 'No', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('menu button')  # Play button click sounds
                        if leaderboard:
                            current_window = 'leaderboard'
                            fade_to_black()
                        else:
                            current_window = 'main menu'
                            new_bg = menu_background(top=True, right=True, bottom=True, left=True)
                            if Menu_animation:
                                car.animate('up', bg)
                                animate_window(confirm_quit_window, main_window, bg, new_bg, car, 'up')
                            else:
                                main_window(new_bg)
                                car.rotate(0)
                                update_screen(full_screen=True)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            # Credits window
            elif current_window == 'credits':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    credits_window(bg)  # Draw assets on background
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                credits_window(bg)  # Always draw default state first
                mouse_pos = get_mouse_pos()  # Get current mouse position

                # BACK BUTTON
                if 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'main menu'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, right=True, bottom=True, left=True)
                        if Menu_animation:
                            car.animate('right', bg)
                            animate_window(credits_window, main_window, bg, new_bg, car, 'right')
                        else:
                            main_window(new_bg)
                            car.rotate(270)
                            update_screen(full_screen=True)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            # Tutorial window
            elif current_window == 'tutorial':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    tutorial_window(bg)  # Draw assets on background
                    fade_from_black()
                    controller_popup()
                    update_screen(full_screen=True)
                    prev_window = current_window  # Set current window to updated

                tutorial_window(bg)  # Always draw default state first
                mouse_pos = get_mouse_pos()  # Get current mouse position

                # BACK BUTTON
                if 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'main menu'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, right=True, bottom=True, left=True)
                        fade_to_black()

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            # Settings window
            elif current_window == 'settings':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    settings_window(bg)  # Draw assets on background
                    car.draw()
                    controller_popup()
                    update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                settings_window(bg)  # Always draw default state first
                mouse_pos = get_mouse_pos()  # Get current mouse position
                # print(mouse_pos)

                # Resolution left
                if 396 <= mouse_pos[0] <= 421 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((409, 311), 'left', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and Display_resolution <= Desktop_info[Screen]:
                        button_trigger = True
                        play_sound('option down')
                        decrease_resolution()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Resolution right
                elif 606 <= mouse_pos[0] <= 631 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((619, 311), 'right', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger and Display_resolution <= Desktop_info[Screen]:
                        button_trigger = True
                        play_sound('option up')
                        increase_resolution()
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Screen left
                elif 872 <= mouse_pos[0] <= 897 and 298 <= mouse_pos[1] <= 324:
                    if Screen + 1 <= 1:
                        draw_triangle((885, 311), 'left', width=25, height=25, border=RED)
                    else:
                        draw_triangle((885, 311), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option down')
                            Screen -= 1
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Screen right
                elif 1022 <= mouse_pos[0] <= 1048 and 298 <= mouse_pos[1] <= 324:
                    if Screen + 1 >= len(Desktop_info):
                        draw_triangle((1035, 311), 'right', width=25, height=25, border=RED)
                    else:
                        draw_triangle((1035, 311), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            play_sound('option up')
                            Screen += 1
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Animations left
                elif 1290 <= mouse_pos[0] <= 1315 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((1303, 311), 'left', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('option down')
                        if Menu_animation:
                            Menu_animation = False
                        else:
                            Menu_animation = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Animations right
                elif 1500 <= mouse_pos[0] <= 1526 and 298 <= mouse_pos[1] <= 324:
                    draw_triangle((1513, 311), 'right', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        play_sound('option up')
                        if Menu_animation:
                            Menu_animation = False
                        else:
                            Menu_animation = True
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Mute left
                elif 1270 <= mouse_pos[0] <= 1296 and 649 <= mouse_pos[1] <= 675:
                    draw_triangle((1283, 662), 'left', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            Music_loop = True
                            pygame.mixer.music.unpause()
                        else:
                            Mute_volume = True
                            Music_loop = False
                            pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_sound('option down')

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Mute right
                elif 1520 <= mouse_pos[0] <= 1546 and 649 <= mouse_pos[1] <= 675:
                    draw_triangle((1533, 662), 'right', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        if Mute_volume:
                            Mute_volume = False
                            Music_loop = True
                            pygame.mixer.music.unpause()
                        else:
                            play_sound('option up')
                            Mute_volume = True
                            Music_loop = False
                            pygame.mixer.music.pause()
                        loaded_sounds = []
                        play_sound('option up')

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Debug left
                elif 1285 <= mouse_pos[0] <= 1310 and 864 <= mouse_pos[1] <= 890:
                    draw_triangle((1298, 878), 'left', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        play_sound('option down')
                        button_trigger = True
                        if Debug:
                            Debug = False
                        else:
                            Debug = True
                        loaded_assets = []  # Reload all assets with/without outlines
                        bg = menu_background(left=True)
                        car.rotate(car.rotation - 1)
                        car.rotate(car.rotation + 1)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Debug right
                elif 1505 <= mouse_pos[0] <= 1531 and 864 <= mouse_pos[1] <= 890:
                    draw_triangle((1518, 878), 'right', width=25, height=25, border=GREY)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        play_sound('option up')
                        button_trigger = True
                        if Debug:
                            Debug = False
                        else:
                            Debug = True
                        loaded_assets = []  # Reload all assets with/without outlines
                        bg = menu_background(left=True)
                        car.rotate(car.rotation - 1)
                        car.rotate(car.rotation + 1)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # Music volume left
                elif 822 <= mouse_pos[0] <= 847 and 649 <= mouse_pos[1] <= 675:
                    if Music_volume <= 0:
                        draw_triangle((835, 662), 'left', width=25, height=25, border=RED)
                    else:
                        draw_triangle((835, 662), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume - 0.01 <= 0:
                                Music_volume = 0
                            elif Music_volume - 0.01 > 0:
                                Music_volume = round(Music_volume - 0.01, 4)
                            play_sound('option down')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Music volume right
                elif 1072 <= mouse_pos[0] <= 1097 and 649 <= mouse_pos[1] <= 675:
                    if Music_volume >= 1:
                        draw_triangle((1085, 662), 'right', width=25, height=25, border=RED)
                    else:
                        draw_triangle((1085, 662), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Music_volume + 0.01 >= 1:
                                Music_volume = 1
                            elif Music_volume + 0.01 < 1:
                                Music_volume = round(Music_volume + 0.01, 4)
                            play_sound('option up')
                            pygame.mixer.music.set_volume(Music_volume)
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Sfx volume left
                elif 391 <= mouse_pos[0] <= 416 and 649 <= mouse_pos[1] <= 675:
                    if Sfx_volume <= 0:
                        draw_triangle((404, 662), 'left', width=25, height=25, border=RED)
                    else:
                        draw_triangle((404, 662), 'left', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume - 0.01 <= 0:
                                Sfx_volume = 0
                            elif Sfx_volume - 0.01 > 0:
                                Sfx_volume = round(Sfx_volume - 0.01, 4)
                            loaded_sounds = []  # Reload all sounds at new volume
                            play_sound('option down')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # Sfx volume right
                elif 611 <= mouse_pos[0] <= 636 and 649 <= mouse_pos[1] <= 675:
                    if Sfx_volume >= 1:
                        draw_triangle((624, 662), 'right', width=25, height=25, border=RED)
                    else:
                        draw_triangle((624, 662), 'right', width=25, height=25, border=GREY)

                        buttons = pygame.mouse.get_pressed()
                        if buttons[0] and not button_trigger:
                            button_trigger = True
                            if Sfx_volume + 0.01 >= 1:
                                Sfx_volume = 1
                            elif Sfx_volume + 0.01 < 1:
                                Sfx_volume = round(Sfx_volume + 0.01, 4)
                            loaded_sounds = []  # Reload all sounds at new volume
                            play_sound('option up')
                        elif not buttons[0] and button_trigger:
                            button_trigger = False

                # BACK BUTTON
                elif 210 <= mouse_pos[0] <= 409 and 112 <= mouse_pos[1] <= 211:
                    pos_x = 210
                    pos_y = 112
                    tile(pos_x, pos_y, 'sand road', 73, grid=False, scale=(100, 100))  # Back button
                    tile(pos_x + 100, pos_y, 'sand road', 57, grid=False, scale=(100, 100))
                    draw_text(pos_x + 100, pos_y + 23, 'Back', BLACK, 55)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        saved_timer = None
                        current_window = 'main menu'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, right=True, bottom=True, left=True)
                        if Menu_animation:
                            car.animate('left', bg)
                            animate_window(settings_window, main_window, bg, new_bg, car, 'left')
                        else:
                            main_window(new_bg)
                            car.rotate(90)
                            update_screen(full_screen=True)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                # SAVE BUTTON
                elif 800 <= mouse_pos[0] <= 1118 and 864 <= mouse_pos[1] <= 972 and not saved_timer:
                    pos_x = 800
                    pos_y = 864
                    tile(pos_x, pos_y, 'sand road', 73, grid=False)  # Save button
                    tile(pos_x + 65, pos_y, 'sand road', 88, grid=False)
                    tile(pos_x + 190, pos_y, 'sand road', 57, grid=False)
                    draw_text(pos_x + 160, pos_y + 20, 'Save', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()  # Get current mouse button state(s)
                    if buttons[0] and not button_trigger:  # If any mouse button is pressed while over start button...
                        button_trigger = True
                        play_sound('save button')  # Play button click sounds
                        save_settings()
                        # print('Saved current settings to file.')  # DEBUGGING
                        saved_timer = pygame.time.get_ticks() + 3000
                    elif not buttons[0] and button_trigger:
                        button_trigger = False

                if saved_timer:
                    if saved_timer >= pygame.time.get_ticks():
                        draw_text(CENTRE[0], 980, 'Settings saved!', WHITE, 35)
                    else:
                        saved_timer = None

            # Credits window
            elif current_window == 'leaderboard':
                if prev_window != current_window:  # On first transition to window draw background
                    bg = new_bg  # Generate new background
                    leaderboard_window(bg)  # Draw assets on background
                    controller_popup()
                    if Window.get_alpha() or Window.get_alpha() == 0:
                        fade_from_black()
                    else:
                        update_screen(full_screen=True)  # Update entire screen
                    prev_window = current_window  # Set current window to updated

                leaderboard_window(bg)  # Always draw default state first
                mouse_pos = get_mouse_pos()  # Get current mouse position
                # print(mouse_pos)

                # FINISH BUTTON
                if 800 <= mouse_pos[0] <= 1117 and 764 <= mouse_pos[1] <= 871:
                    x = 800
                    y = 764
                    tile(x, y, 'sand road', 73, grid=False)  # Finish button
                    tile(x + 65, y, 'sand road', 88, grid=False)
                    tile(x + 190, y, 'sand road', 57, grid=False)
                    draw_text(x + 160, y + 20, 'Finish', BLACK, 70)

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] and not button_trigger:
                        button_trigger = True
                        current_window = 'main menu'
                        play_sound('menu button')  # Play button click sounds
                        new_bg = menu_background(top=True, right=True, bottom=True, left=True)
                        pygame.mixer.music.fadeout(250)
                        fade_to_black()
                        main_window(new_bg)

                    elif not buttons[0] and button_trigger:
                        button_trigger = False

            else:
                raise ValueError('current_window == ' + str(current_window))

            if current_window != 'leaderboard' and current_window != 'tutorial':
                car.draw()
            controller_popup()
            if current_window == 'choose map':
                update_screen(full_screen=True)
            else:
                update_screen()

        Music_loop = False
        fade_to_black(show_loading=True)  # Start game
        game_quit = game()  # Begin game
        if game_quit:
            new_bg = menu_background(top=True, right=True, bottom=True, left=True)
            main_window(new_bg)
            current_window = 'main menu'
        else:
            new_bg = menu_background()
            leaderboard_window(new_bg)
            current_window = 'leaderboard'
        car.rotate(0)
        car.move(*CENTRE)
        fade_from_black(show_loading=True)
        if not pygame.mouse.get_visible():
            pygame.mouse.set_visible(True)
        menu_loop = True
        Music_loop = True


if __name__ == '__main__':
    if Debug:  # If in debug mode then do not handle errors
        main()
    else:
        try:
            main()
        except KeyboardInterrupt:
            Music_loop = False
            if music_thread.is_alive():
                music_thread.join(timeout=0.25)
            pygame.quit()
            quit()
        except Exception as error:  # If error and debug is off then update screen with error and quit
            print(error)
            Music_loop = False
            if music_thread.is_alive():
                music_thread.join(timeout=0.25)
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.time.wait(100)
            Display.fill(BLACK)
            play_sound('error')
            error_type = str(type(error)).replace("<class '", '').replace("'>", '')
            try:
                Display.blit(pygame.font.Font(fonts.load(), 50).render(error_type, True, WHITE, 50), (0, 0))
                Display.blit(pygame.font.Font(fonts.load(), 50).render(str(error), True, WHITE, 50), (0, 50))
            except FileNotFoundError:
                Display.blit(pygame.font.Font(None, 50).render(error_type, True, WHITE, 50), (0, 0))
                Display.blit(pygame.font.Font(None, 50).render(str(error), True, WHITE, 50), (0, 50))
            pygame.display.update()
            pygame.time.wait(3000)
            pygame.quit()
            quit()

    pygame.quit()
    quit()

elif __name__ == 'main':
    Display = pygame.display.set_mode([840, 480])
    Display_resolution = 840, 480
    Music_volume = 0.02
    Sfx_volume = 0.02
    try:
        Window.blit(pygame.font.Font(fonts.load(bar=True), 100).render('Retro Rampage', True, WHITE),
                    (CENTRE[0] - 412, CENTRE[1] - 60))
        Window.blit(pygame.font.Font(fonts.load(), 100).render('Testing mode', True, WHITE),
                    (CENTRE[0] - 346, CENTRE[1] + 60))

    except FileNotFoundError:
        Window.blit(pygame.font.Font(None, 100).render('Retro Rampage', True, WHITE),
                    (CENTRE[0] - 256, CENTRE[1] - 60))
        Window.blit(pygame.font.Font(None, 100).render('Testing mode', True, WHITE),
                    (CENTRE[0] - 224, CENTRE[1] + 60))
    Display.blit(pygame.transform.scale(Window, Display_resolution), (0, 0))
    pygame.display.update()
    pygame.time.wait(500)
