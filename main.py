from __future__ import annotations
from typing import override
from sys import exit
import enum
import pygame
from pygame.typing import Point

HORIZONTAL_SIZE = 640
VERTICAL_SIZE = 360

FUZZY_ZERO = 0.001
GRAVITY = 0.1
START_GAME_NAME = "Start Game"

running = True
pygame.init()
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),vsync=1,flags = pygame.FULLSCREEN|pygame.SCALED)
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.mouse.set_cursor(*pygame.cursors.arrow)
clock = pygame.time.Clock()

#Gameplay
surface_list:list[ScreenSurface] = []
collider_list:list[ScreenSurface] = []
screen_offset:int = 0
screen_end:int = HORIZONTAL_SIZE

#Menus
menu_loaded:bool = False
button_pos_dict:dict[str, pygame.Rect] = {}

small_text = pygame.font.Font(size=12)
medium_text = pygame.font.Font()
big_text = pygame.font.Font(size=36)

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

current_screen = ScreenEnum.MAIN_MENU

def set_collider(ss:ScreenSurface):
    '''Sets the ss to a collider and a surface'''
    collider_list.append(ss)
    surface_list.append(ss)

def set_surface(ss:ScreenSurface):
    '''Sets the ss to a surface'''
    surface_list.append(ss)

class ScreenSurface():
    '''
    A surface that gets drawn onto the screen while the state is the game
    Used by colliders and to render something
    Drawn around a rect, which the hitbox flag shows
    '''
    def __init__(self, surface:pygame.Surface, rect:pygame.Rect, rect_offset = (0, 0), enabled = True, show_hitbox=False) -> None:
        self.surface = surface
        self.rect = rect
        self.x_vel = 0
        self.y_vel = 0
        self.enabled = enabled
        self.show_hitbox = show_hitbox
        self.rect_offset = rect_offset
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
        self.x_vel = 0
        self.y_vel = 0
        self.x_pos = rect.x
        self.y_pos = rect.x
        self.res_y_pos = 100
        self.res_x_pos = 100
        self.grounded = False
        self.grounded_timer = 0
        self.in_build = True

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
            elif self.x_vel < 0:
                collided_size = collider_list[x_intersect_index].rect.width
                self.x_pos = collided_distance + collided_size
                self.rect.x = collided_distance + collided_size 

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
                self.grounded_timer = 80*3/50
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

player = Player(surface=pygame.image.load("assets/block1.png"),
                rect=pygame.Rect((0, 0), (32,32)))

while running:
    delta_time = clock.tick(60)*3/50
    player.grounded_timer -= delta_time
    # event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == ScreenEnum.MAIN_MENU:
                if button_pos_dict[START_GAME_NAME].collidepoint(pygame.mouse.get_pos()):
                    current_screen = ScreenEnum.GAME
            if event.button == 1 and player.in_build:
                mouse_pos = pygame.mouse.get_pos()
                box_x = mouse_pos[0]//32
                box_y = mouse_pos[1]//32
                
                rect = pygame.Rect(box_x*32, box_y*32, 32,32)
                set_collider(ScreenSurface(surface=pygame.image.load("assets/block1.png"),
                                            rect=rect))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit(0)
            if event.key == pygame.K_b:
                player.in_build = not player.in_build
                print(player.in_build)

    keys = pygame.key.get_pressed()
    #Clears screen
    screen.fill((50,50,50))

    match current_screen:
        case ScreenEnum.GAME:
            #In game
            player.x_vel += delta_time*.25*(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
            player.y_vel += delta_time*GRAVITY
            if player.grounded and keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                print("very real jump", player.y_vel)
                if player.y_vel > 0:
                    player.y_vel -= 2
                else:
                    player.y_vel -= .5*min(delta_time,(delta_time+player.grounded_timer))
            player.x_vel *= delta_time*0.95
            if abs(player.x_vel) < FUZZY_ZERO:
                player.x_vel = 0
            if abs(player.y_vel) < FUZZY_ZERO:
                player.y_vel = 0
            #Player moves
            player.move()
            if player.grounded_timer < 0:
                player.grounded = False
            #Offset is updated and everything is drawn
            relative_screen_distance = player.x_pos - screen_offset
            #Scroll right
            if relative_screen_distance > HORIZONTAL_SIZE//2:
                screen_offset = player.x_pos - HORIZONTAL_SIZE//2
                if screen_offset > screen_end:
                    screen_offset = screen_end
            #Scroll left
            if relative_screen_distance < HORIZONTAL_SIZE//3:
                screen_offset = player.x_pos - HORIZONTAL_SIZE//3
                if screen_offset < 0:
                    screen_offset = 0
            #Player is a surface but it's done seperately so that the player does not to be readded
            if player.y_pos > VERTICAL_SIZE:
                player.y_pos = player.res_y_pos
                player.x_pos = player.res_x_pos

            player.draw()
            for surface in surface_list:
                surface.draw()
            for i in range(HORIZONTAL_SIZE//32):
                pygame.draw.line(screen, (255,255,255),(i*32,0),(i*32,VERTICAL_SIZE))
            for n in range(VERTICAL_SIZE//32):
                pygame.draw.line(screen, (255,255,255),(0,n*32),(HORIZONTAL_SIZE,n*32))
            pygame.draw.line(screen, (255,255,255),(0,11*32),(HORIZONTAL_SIZE,11*32))
            #updates the screen
            pygame.display.flip()
        case ScreenEnum.MAIN_MENU:
            #Main menu
            if not menu_loaded:
                pygame.mouse.set_visible(True)
                make_button(big_text, START_GAME_NAME, (HORIZONTAL_SIZE/2, VERTICAL_SIZE/2))
                menu_loaded = True
                pygame.display.flip()
