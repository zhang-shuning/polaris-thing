import pygame

running = True
pygame.init()
screen = pygame.display.set_mode((320,180))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
