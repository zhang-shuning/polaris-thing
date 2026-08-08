from typing import override
import pygame
from pygame.typing import Point

HORIZONTAL_SIZE = 320
VERTICAL_SIZE = 180

running = True
pygame.init()
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),vsync=1,flags = pygame.FULLSCREEN|pygame.SCALED)
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.mouse.set_cursor(*pygame.cursors.arrow)
clock = pygame.time.Clock()

surface_list:list[ScreenSurface] = []
collider_list:list[ScreenSurface] = []
screen_offset:int = 0
screen_end:int = 0

def set_collider(ss:ScreenSurface):
    '''Sets the ss to a collider and a surface'''
    collider_list.append(ss)
    surface_list.append(ss)

def set_surface(ss:ScreenSurface):
    '''Sets the ss to a surface'''
    surface_list.append(ss)

class ScreenSurface():
    '''
    A surface that gets drawn onto the screen that scrolls off the screen.
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
        self.rect.x += rect_offset[0]
        self.rect.y += rect_offset[1]

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
            collided_distance = collider_list[y_intersect_index].rect.x
            if self.y_vel > 0:
                self.y_pos = collided_distance - self.rect.height
                self.rect.y = collided_distance - self.rect.height
            elif self.y_vel < 0:
                collided_size = collider_list[y_intersect_index].rect.height
                self.y_pos = collided_distance + collided_size
                self.rect.y = collided_distance + collided_size

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

player = Player(surface=pygame.image.load("assets/temphole.png"), rect_offset=(8, 8),
                rect=pygame.Rect((0, 0), (16, 16)), show_hitbox=True)
set_collider(ScreenSurface(surface=pygame.image.load("assets/temphole.png"), rect_offset=(8, 8),
                           rect=pygame.Rect((100, 0), (16, 16)), show_hitbox=True))

while running:
    clock.tick(60)
    # event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    player.x_vel = 1
    #Clears screen
    screen.fill((50,50,50))
    #Player moves
    player.move()
    #Offset is updated and everything is drawn
    relative_screen_distance = player.x_pos - screen_offset
    #Scroll right
    if relative_screen_distance > HORIZONTAL_SIZE//2:
        screen_offset = player.x_pos - HORIZONTAL_SIZE//2
    #Scroll left
    if relative_screen_distance < HORIZONTAL_SIZE//3:
        screen_offset = player.x_pos - HORIZONTAL_SIZE//3
        if screen_offset < 0:
            screen_offset = 0
    #Player is a surface but it's done seperately so that the player does not to be readded
    player.draw()
    for i in surface_list:
        i.draw()


    # updates the screen
    pygame.display.flip()