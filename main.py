import pygame
from pygame.typing import Point

running = True
pygame.init()
screen = pygame.display.set_mode((320,180),vsync=1,flags = pygame.FULLSCREEN|pygame.SCALED)
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.mouse.set_cursor(*pygame.cursors.arrow)

collider_list:list[pygame.Rect] = []

class player():
    def __init__(self, surface:pygame.Surface, frect:pygame.FRect) -> None:
        self.surface = surface
        self.frect = frect
        self.x_vel = 0
        self.y_vel = 0

    def move(self):
        '''
        Function for player movement, called every frame the player is active
        '''
        #Try adding X velocity
        self.frect.x += self.x_vel
        #Check collisions, if collided, set x position to the x
        #Can be put into smaller steps if going through walls becomes an issue
        x_intersect_index = self.frect.collidelist(collider_list)
        if not x_intersect_index:
            self.frect.x = collider_list[x_intersect_index].x

        #Repeat for y collisions
        self.frect.y += self.y_vel
        y_intersect_index = self.frect.collidelist(collider_list)
        if not y_intersect_index:
            self.frect.y = collider_list[y_intersect_index].y

    def draw(self):
        pass

while running:
    
    # event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # drawing
    screen.fill((50,50,50))
    # updates the screen
    pygame.display.flip()