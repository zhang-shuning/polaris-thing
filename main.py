import pygame

running = True
pygame.init()
screen = pygame.display.set_mode((320,180),vsync=1,flags = pygame.FULLSCREEN|pygame.SCALED)
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.mouse.set_cursor(*pygame.cursors.arrow)
while running:
    
    # event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # drawing
    screen.fill((50,50,50))

    # updates the screen
    pygame.display.flip()