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

class ScreenSurface():
    '''A surface that gets drawn onto the screen'''
    def __init__(self, surface:pygame.Surface, rect:pygame.Rect, enabled = True, hitbox_enabled=False) -> None:
        self.surface = surface
        self.rect = rect
        self.x_vel = 0
        self.y_vel = 0
        self.enabled = enabled
        self.hitbox_enabled = hitbox_enabled

    def draw(self):
        '''Draws onto the screen'''
        if not self.enabled:
            return
        screen.blit(source=self.surface, dest=self.rect)
        if self.hitbox_enabled:
            pygame.draw.rect(surface=screen,
                            color=(255, 0, 0), 
                            rect=(self.rect),
                            width=1)

class Player(ScreenSurface):
    @override
    def __init__(self, surface: pygame.Surface, rect: pygame.Rect, enabled=True, hitbox_enabled=False) -> None:
        super().__init__(surface, rect, enabled, hitbox_enabled)
        self.x_vel = 0
        self.y_vel = 0
        self.x_pos = 0
        self.y_pos = 0

    def move(self):
        '''
        Method for player movement, called every frame the player is active
        '''
        #Try adding X velocity
        self.x_pos += self.x_vel
        self.rect.x = round(self.x_pos)
        #Check collisions, if collided, set x position to the x
        #Can be put into smaller steps if going through walls becomes an issue
        x_intersect_index = self.rect.collidelist(collider_list)
        if not x_intersect_index:
            self.rect.x = collider_list[x_intersect_index].x

        #Repeat for y collisions
        self.y_pos += self.y_vel
        self.rect.y = round(self.y_pos)
        y_intersect_index = self.rect.collidelist(collider_list)
        if not y_intersect_index:
            self.rect.y = collider_list[y_intersect_index].y

player = Player(surface=pygame.image.load("assets/temphole.png"), rect=pygame.Rect((0, 0), (16, 16)), hitbox_enabled=True)

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
    #Scroll right
    if player.x_pos - screen_offset > HORIZONTAL_SIZE/2:
        screen_offset =  
    #Player is a surface but it's done seperately so that the player does not to be readded
    player.draw()
    for i in surface_list:
        i.draw()


    # updates the screen
    pygame.display.flip()