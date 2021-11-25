#!/usr/bin/python
import pygame, os, sys, random
from pygame.locals import *

class Villain:
    def __init__(self, x, y, speed, scale, imgPath):
        self.speed = speed
        self.img = pygame.transform.rotozoom(pygame.image.load(imgPath), 180, scale)
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        sy = self.speed
        self.rect.y += sy
        
    def draw(self, surface):
        surface.blit(self.img, (self.rect.x, self.rect.y))

    def isVisible(self):
        return self.rect.x < 800 and self.rect.y < 600
    
    #def maskCollision(self, sprite):
        #return pygame.sprite.collide_mask(self.img,
    
shipImg = pygame.transform.scale(pygame.image.load('Resources_PyGame/ShipSprite.png'), (120, 170))
shipRect = shipImg.get_rect()
shipMask = pygame.mask.from_surface(shipImg)
playerY = 480
mousex, mousey = (0, playerY)

pygame.init()
fpsClock = pygame.time.Clock()
mainSurface = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Ships Prototype')

blue = pygame.Color(32, 160, 230)

villainCollection = []

counter = 0

while True:
    mainSurface.fill(blue)

    mainSurface.blit(shipImg, shipRect)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
            if (mousex < 800 - 55):
                shipRect.topleft = (mousex, playerY)
            else:
                shipRect.topleft = (800 - 55, playerY)
        
    if counter == 90:
        villainCollection.append(Villain(random.randrange(770), -100, 3, random.uniform(0.07, 0.1), 'Resources_PyGame/ShipSprite.png'))
        counter = 0

    for a in villainCollection:
        a.update()
        if a.isVisible():
            a.draw(mainSurface)
            if shipRect.colliderect(a):
                #if a.maskCollision(shipImg):
                villainCollection.remove(a)
        else:
            villainCollection.remove(a)

    counter += 1
    pygame.display.update()
    fpsClock.tick(30)
