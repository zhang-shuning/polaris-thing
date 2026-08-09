from __future__ import annotations
from typing import override, overload
from sys import exit
import enum
import math
import pygame
from pygame.typing import Point

import scripts.map_save

HORIZONTAL_SIZE = 640
VERTICAL_SIZE = 360

RESUME_GAME = "Resume Game"
LEVEL_SELECTOR_NAME = "Level\n Selector"
RETURN_MENU = "Back To \nMain Menu"
QUIT_TEXT = "Quit Game"
escape_loaded = False
RANGE = 120

#Physics constants
#Most of these are multiplied by frametime * 60/1000
FUZZY_ZERO = 0.001 #Amount where velocity rounds to 0
HORIZONTAL_ACCELERATION_COEFFICIENT = 30 #Coefficient on acceleration
GRAVITY = 10 #Coefficient on gravity
FAST_FALL_COEFFICIENT = 0.2 # Coeficient on fast falling
INSTANT_JUMP_VELOCITY = 3 # Minimum velocity gained while jumping
JUMP_HOLD_COEFICIENT = 10 # Coefficient for the speed of holding the jump button after a jump
JUMP_HOLD_TIME = 0.06 # Amount of seconds  to hold after a jump while getting acceleration
JUMP_HORIZONTAL_PART = 15 #Coefficient on increased jump height for horizontal velocity
HORIZONTAL_AIR_RESISTANCE = .95 # Coefficient on x axis air resistance
VERTICAL_AIR_RESISTANCE = .95 # Coefficient on y axis air resistance
WALL_HORIZONTAL_SPEED_PENELTY = .95 #Speed penelety for touching a wall

BLACK_HOLE_STRENGTH = 30
MAX_BLACK_HOLE_ACCELERATION = 10 #Controls max black hole acceleration in a single tick

running = True
pygame.init()
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),vsync=1,flags = pygame.FULLSCREEN|pygame.SCALED)
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.mouse.set_cursor(*pygame.cursors.arrow)
clock = pygame.time.Clock()

#Gameplay
surface_list:list[ScreenSurface] = []
collider_list:list[ScreenSurface] = []
black_hole_list:list[ScreenSurface] = []
screen_offset:int = 0
screen_end:int = HORIZONTAL_SIZE

#Menus
menu_loaded:bool = False
level_selector_loaded:bool = False
button_pos_dict:dict[str, pygame.Rect] = {}
small_text = pygame.font.Font(size=12)
medium_text = pygame.font.Font()
big_text = pygame.font.Font(size=36)
map_number = -1

def make_button(font:pygame.Font, text:str, position:tuple[int], text_color = (255, 255, 255), rectangle_color = (0, 0, 0)) -> None:
    rendered_font = font.render(text, True, text_color)
    font_rect = rendered_font.get_rect(center = position)
    pygame.draw.rect(screen, rectangle_color, font_rect)
    screen.blit(rendered_font, font_rect)
    if text not in button_pos_dict:
        button_pos_dict[text] = font_rect

class ScreenEnum(enum.Enum):
    GAME = enum.auto()
    MAIN_MENU = enum.auto()
    LEVEL_SELECTOR = enum.auto()
    ESCAPE_MENU = enum.auto()


current_screen = ScreenEnum.MAIN_MENU

def set_collider(ss:ScreenSurface):
    '''Sets the ss to a collider and a surface'''
    collider_list.append(ss)
    surface_list.append(ss)

def set_surface(ss:ScreenSurface):
    '''Sets the ss to a surface'''
    surface_list.append(ss)

def set_black_hole(ss:ScreenSurface):
    '''Sets the ss to be a blakc hole'''
    black_hole_list.append(ss)
    surface_list.append(ss)

class ScreenSurface():
    '''
    A surface that gets drawn onto the screen while the state is the game
    Used by colliders and to render something
    Drawn around a rect, which the hitbox flag shows
    Group 1 is surface
    Group 2 is collider
    Group 3 is black holw
    '''
    def __init__(self, surface:pygame.Surface, rect:pygame.Rect, rect_offset = (0, 0), enabled = True, show_hitbox=False, map=None, group=0) -> None:
        self.surface = surface
        self.rect = rect
        self.x_vel = 0
        self.y_vel = 0
        self.enabled = enabled
        self.show_hitbox = show_hitbox
        self.rect_offset = rect_offset
        self.map = map
        self.group = group
        if group == 1:
            set_surface(self)
        elif group == 2:
            set_collider(self)
        elif group == 3:
            set_black_hole(self)

    def draw(self):
        '''Draws onto the screen'''
        if not self.enabled:
            return
        #Check if it's not on the screen to the right
        if self.rect.x + self.rect.width < screen_offset:
            return
        #Check if it's not on the screen to the left
        if self.rect.x > screen_offset + HORIZONTAL_SIZE:
           return
        screen.blit(source=self.surface,
                    dest=(self.rect.x - screen_offset - self.rect_offset[0], self.rect.y - self.rect_offset[1]))
        if self.show_hitbox:
            pygame.draw.rect(surface=screen,
                            color=(255, 0, 0), 
                            rect=(self.rect.x - screen_offset, self.rect.y,
                            self.rect.width, self.rect.height),
                            width=1)

class Player(ScreenSurface):
    '''This would be kinda a general moving class, but the only moving thing is the player'''
    @override
    def __init__(self, surface: pygame.Surface, rect: pygame.Rect, rect_offset=(0, 0), enabled=True, show_hitbox=False) -> None:
        super().__init__(surface, rect, rect_offset, enabled, show_hitbox)
        self.x_vel:float = 0
        self.y_vel:float = 0
        self.x_pos:float = rect.x
        self.y_pos:float = rect.x
        self.res_y_pos = 200
        self.res_x_pos = 200
        self.grounded:bool = False
        self.grounded_timer:float = 0
        self.in_build:bool = True
        self.first:bool = True

    def check_x_collisions(self):
        #Check collisions, if collided, set x position to the x
        #Can be put into smaller steps if going through walls becomes an issue
        x_intersect_index = self.rect.collidelist(collider_list)
        if x_intersect_index != -1:
            collided_distance = collider_list[x_intersect_index].rect.x
            #Checks which way it collided from
            if self.x_vel > 0:
                self.x_pos = collided_distance - self.rect.width
                self.rect.x = collided_distance - self.rect.width
                self.x_vel *= WALL_HORIZONTAL_SPEED_PENELTY
            elif self.x_vel < 0:
                collided_size = collider_list[x_intersect_index].rect.width
                self.x_pos = collided_distance + collided_size
                self.rect.x = collided_distance + collided_size 
                self.x_vel *= WALL_HORIZONTAL_SPEED_PENELTY

    def check_y_collisions(self):
        #Repeat for y collisions
        y_intersect_index = self.rect.collidelist(collider_list)
        if y_intersect_index != -1:
            collided_distance = collider_list[y_intersect_index].rect.y
            if self.y_vel > 0:
                self.y_pos = collided_distance - self.rect.height
                self.rect.y = collided_distance - self.rect.height
                self.y_vel = 0
                self.grounded = True
                self.grounded_timer = JUMP_HOLD_TIME
            elif self.y_vel < 0:
                collided_size = collider_list[y_intersect_index].rect.height
                self.y_pos = collided_distance + collided_size
                self.rect.y = collided_distance + collided_size
                self.y_vel = 0

    def move(self):
        '''
        Method for player movement, called every frame the player is active
        '''
        #Try adding X velocity
        self.x_pos += self.x_vel
        self.rect.x = round(self.x_pos)
        self.check_x_collisions()

        self.y_pos += self.y_vel
        self.rect.y = round(self.y_pos)
        self.check_y_collisions()

    def handle_black_hole(self):
        #Vectors because surely that will help
        for black_hole in black_hole_list:
            dx = black_hole.rect.centerx - self.x_pos
            dy = black_hole.rect.centery - self.y_pos
            dist_sq = dx**2 + dy**2
            dist = math.sqrt(dist_sq)
            strength = min(BLACK_HOLE_STRENGTH/dist, MAX_BLACK_HOLE_ACCELERATION)
            self.x_vel += strength*dx/dist
            self.y_vel += strength*dy/dist
            if black_hole.rect.colliderect(self.rect):
                self.respawn()

    def respawn(self):
        self.y_pos = self.res_y_pos
        self.x_pos = self.res_x_pos
        self.x_vel = 0
        self.y_vel = 0

def create_black_hole(coordinates:tuple[int, int], show_hitbox = False):
    black_hole_test = ScreenSurface(pygame.image.load("assets/temphole.png"),
                                     rect=pygame.Rect((coordinates), (8, 8)), map="assets/temphole.png",
                                     rect_offset=(12,12), show_hitbox=show_hitbox, group=3)

def load_map(number):
    collider_list.clear()
    surface_list.clear()
    black_hole_list.clear()
    maps = scripts.map_save.read_map(number)
    try:
        if maps is not None:
            for i in maps:
                ScreenSurface(pygame.image.load(i[0]), group=i[1], rect = pygame.Rect(i[2]), map=i[0])
            connect_textures()
            tile_dict = {}
        else:
            print("That map does not exist")
    except ValueError:
        print("Map does not exist, something might've broken!")


player = Player(surface=pygame.image.load("assets/player.png"),
                rect=pygame.Rect((0, 0), (28, 28)), rect_offset=(2, 2))

tile_size = (32,32)
def connect_textures():
    tile_dict = {}
    for ss in collider_list:
        tile_dict[str(ss.rect.topleft)] = ss
    for ss in collider_list:
        if tile_dict[str(ss.rect.topleft)] != None:
            block_left = False
            block_right = False
            block_up = False
            block_down = False
            if tile_dict.get(str((ss.rect.x-32, ss.rect.y))) != None: block_left = True
            if tile_dict.get(str((ss.rect.x+32, ss.rect.y))) != None: block_right = True
            if tile_dict.get(str((ss.rect.x, ss.rect.y-32))) != None: block_up = True
            if tile_dict.get(str((ss.rect.x, ss.rect.y+32))) != None: block_down = True
            truth_list = [block_left,block_right,block_up,block_down]
            rotateable = False
            rotateable180 = False
            match truth_list:
                case [1,0,0,0]:
                    tile_img = 'assets/horiblock.png'
                    tile_pos = (64,0)  
                    
                case [0,1,0,0]:
                    tile_img = 'assets/horiblock.png'
                    tile_pos = (0,0)
                case [1,1,0,0]:
                    tile_img = 'assets/horiblock.png'
                    tile_pos = (32,0)
                    rotateable180 = True   
                case [0,0,1,0]:
                    tile_img = 'assets/verblock.png'
                    tile_pos = (0,64)  
                case [0,0,0,1]:
                    tile_img = 'assets/verblock.png'
                    tile_pos = (0,0)   
                case [0,0,1,1]:
                    tile_img = 'assets/verblock.png'
                    tile_pos = (0,32) 
                    rotateable180 = True        
                case [0,1,0,1]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (0,0)       
                case [1,1,0,1]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (32,0)
                case [1,0,0,1]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (64,0)   
                case [0,1,1,1]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (0,32)   
                case [1,1,1,1]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (32,32)
                    rotateable = True  
                case [1,0,1,1]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (64,32) 
                case [0,1,1,0]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (0,64) 
                case [1,1,1,0]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (32,64)     
                case [1,0,1,0]:
                    tile_img = 'assets/bigone.png'
                    tile_pos = (64,64)                                  
                case _:
                    tile_img = 'assets/block1.png'
                    tile_pos = (0,0)
            tile_surface = pygame.image.load(tile_img)
            pygame.Surface.convert_alpha(tile_surface)
            if rotateable:
                random_num = pygame.time.get_ticks()%4
                tile_dict[str(ss.rect.topleft)].surface = (
                pygame.transform.rotate(pygame.Surface.subsurface(tile_surface,((tile_pos),(32,32))),random_num*90))
            elif rotateable180:   
                random_num = pygame.time.get_ticks()%2
                tile_dict[str(ss.rect.topleft)].surface = (
                pygame.transform.rotate(pygame.Surface.subsurface(tile_surface,((tile_pos),(32,32))),random_num*180))
            else:
                tile_dict[str(ss.rect.topleft)].surface = pygame.Surface.subsurface(tile_surface,((tile_pos),(32,32)))


while running:
    delta_time = clock.tick(60)/1000
    player.grounded_timer -= delta_time
    # event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == ScreenEnum.MAIN_MENU:
                if button_pos_dict[LEVEL_SELECTOR_NAME].collidepoint(pygame.mouse.get_pos()):
                    current_screen = ScreenEnum.LEVEL_SELECTOR
                elif button_pos_dict[QUIT_TEXT].collidepoint(pygame.mouse.get_pos()):
                    running = False

            elif current_screen == ScreenEnum.LEVEL_SELECTOR:
                if button_pos_dict[RETURN_MENU].collidepoint(pygame.mouse.get_pos()):
                    current_screen = ScreenEnum.MAIN_MENU
                for i in range(1, 26):
                    if button_pos_dict[str(i)].collidepoint(pygame.mouse.get_pos()):
                        load_map(i)
                        current_screen = ScreenEnum.GAME
                        map_number = i
                        break
            elif current_screen == ScreenEnum.ESCAPE_MENU:
                if button_pos_dict[RESUME_GAME].collidepoint(pygame.mouse.get_pos()):
                    current_screen = ScreenEnum.GAME
                elif button_pos_dict[RETURN_MENU].collidepoint(pygame.mouse.get_pos()):
                    current_screen = ScreenEnum.MAIN_MENU
                    map_number = -1
            if player.first:
                player.first = False
            elif event.button == 1 and player.in_build and current_screen == ScreenEnum.GAME:
                mouse_pos = pygame.mouse.get_pos()
                box_x = mouse_pos[0]//32
                box_y = mouse_pos[1]//32
                
                rect = pygame.Rect(box_x*32, box_y*32, 32,32)
                if not any(rect == collider.rect for collider in collider_list):
                    ScreenSurface(surface=pygame.image.load("assets/block1.png"),
                                            rect=rect, map = "assets/block1.png", group=2)
                    connect_textures()
                    tile_dict = {}
            elif event.button == 3 and current_screen == ScreenEnum.GAME:
                mouse_pos = pygame.mouse.get_pos()
                box_x = mouse_pos[0]//32
                box_y = mouse_pos[1]//32
                
                rect = pygame.Rect(box_x*32, box_y*32, 32,32)
                index = rect.collidelist(surface_list)
                if index != 1:
                    for surface in surface_list:
                        if surface.rect == rect:
                            surface_list.remove(surface)
                            try:
                                black_hole_list.remove(surface)
                            except ValueError:
                                pass
                            try:
                                collider_list.remove(surface)
                            except ValueError:
                                pass
                            connect_textures()
                            tile_dict = {}
                            break
            elif event.button == 1 and not player.in_build and current_screen == ScreenEnum.GAME:
                create_black_hole(pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and current_screen == ScreenEnum.GAME:
                escape_loaded = False
                current_screen = ScreenEnum.ESCAPE_MENU
            if event.key == pygame.K_b:
                player.in_build = not player.in_build
            if event.key == pygame.K_s and current_screen == ScreenEnum.GAME and event.mod & pygame.KMOD_CTRL:
                scripts.map_save.write_map([(surface.map, surface.group, tuple(surface.rect)) for surface in surface_list], map_number)


    keys = pygame.key.get_pressed()
    #Clears screen
    screen.blit(pygame.image.load('assets/background.png'))
    match current_screen:
        case ScreenEnum.GAME:
            #In game 
            fps = round(clock.get_fps())
            make_button(big_text,f'{fps}',(200,50))
            if pygame.Rect(player.rect.x, player.rect.y, player.rect.width, player.rect.height).collidelist(collider_list) != -1:
                player.grounded_timer = 6
            #Horizontal movement
            player.x_vel += delta_time*HORIZONTAL_ACCELERATION_COEFFICIENT*(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
            
            #Gravity
            player.y_vel += delta_time*GRAVITY
            #Fast fall
            if not keys[pygame.K_UP]:
                player.y_vel += keys[pygame.K_DOWN] * delta_time * abs(FAST_FALL_COEFFICIENT)
            #Jumping
            if player.grounded and keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                #Minimum jump velocity
                if player.y_vel > 0:
                    player.y_vel = -INSTANT_JUMP_VELOCITY
                else:
                    #Higher velocity for longer hold and faster horizontal speed
                    player.y_vel -= JUMP_HOLD_COEFICIENT * min(delta_time, (delta_time+player.grounded_timer))
                    player.y_vel -= JUMP_HORIZONTAL_PART * delta_time * abs(player.x_vel)
            #X axis air resistance
            player.x_vel *= HORIZONTAL_AIR_RESISTANCE
            player.x_vel *= HORIZONTAL_AIR_RESISTANCE
            if abs(player.x_vel) < FUZZY_ZERO:
                player.x_vel = 0
            if abs(player.y_vel) < FUZZY_ZERO:
                player.y_vel = 0
            player.handle_black_hole()
            #Player moves
            player.move()
            if player.grounded_timer < 0:
                player.grounded = False
            #Offset is updated and everything is drawn
            relative_screen_distance = player.x_pos - screen_offset
            #Scroll right
            #if relative_screen_distance > HORIZONTAL_SIZE//2:
                #screen_offset = player.x_pos - HORIZONTAL_SIZE//2
                #if screen_offset > screen_end:
                    #screen_offset = screen_end
            #Scroll left
            if relative_screen_distance < HORIZONTAL_SIZE//3:
                screen_offset = player.x_pos - HORIZONTAL_SIZE//3
                if screen_offset < 0:
                    screen_offset = 0
            #Player is a surface but it's done seperately so that the player does not need to be readded
            if player.y_pos > VERTICAL_SIZE:
                player.respawn()

            player.draw()
            for surface in surface_list:
                surface.draw()
           # for i in range(HORIZONTAL_SIZE//32 + 1):
            #    pygame.draw.line(screen, (255,255,255),(i*32,0),(i*32,VERTICAL_SIZE))
            #for n in range(VERTICAL_SIZE//32 + 1):
            #    pygame.draw.line(screen, (255,255,255),(0,n*32),(HORIZONTAL_SIZE,n*32))
            #updates the screen
            pygame.display.flip()
            menu_loaded = False
        case ScreenEnum.MAIN_MENU:
            #Main menu
            if not menu_loaded:
                pygame.mouse.set_visible(True)
                make_button(big_text, LEVEL_SELECTOR_NAME, (HORIZONTAL_SIZE/2, VERTICAL_SIZE/2))
                make_button(big_text, QUIT_TEXT, (HORIZONTAL_SIZE - 80, VERTICAL_SIZE - 20))
                menu_loaded = True
                level_selector_loaded = False
                escape_loaded = False
                player.first = True
                pygame.display.flip()
        case ScreenEnum.ESCAPE_MENU:

            if not escape_loaded:
                make_button(big_text, RESUME_GAME, (HORIZONTAL_SIZE/2, VERTICAL_SIZE/2))
                make_button(big_text, RETURN_MENU, (HORIZONTAL_SIZE/10+20, VERTICAL_SIZE-25))
                level_selector_loaded = False
                menu_loaded = False
                escape_loaded = True
                player.first = True
                pygame.display.flip()
        case ScreenEnum.LEVEL_SELECTOR:
            if not level_selector_loaded:
                make_button(big_text, "LEVELS", (HORIZONTAL_SIZE/2, 15))
                make_button(big_text, RETURN_MENU, (HORIZONTAL_SIZE/10+20, VERTICAL_SIZE-25))
                for i in range(5):
                    for j in range(5):
                        make_button(big_text, f"{1+i*5+j}", ((HORIZONTAL_SIZE//7)*(1.5+i), (VERTICAL_SIZE//7)*(1.5+j)))
                level_selector_loaded = True
                menu_loaded = False
                escape_loaded = False
                player.first = True
                pygame.display.flip()

