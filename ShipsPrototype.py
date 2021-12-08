#!/usr/bin/python
import pygame, os, sys, random
from pygame.locals import *

class Villain:
    def __init__(self, x, y, speed, scale, img):
        self.speed = speed
        self.img = pygame.transform.rotozoom(img, 180, scale)
        self.rect = self.img.get_rect()
        self.rect = self.rect.inflate(round(-75 * scale), 0)
        self.rect.x = x
        self.rect.y = y
        self.fatal = True

    def update(self):
        sy = self.speed
        self.rect.y += sy
        
    def draw(self, surface):
        surface.blit(self.img, (self.rect.x, self.rect.y))

    def isVisible(self):
        return self.rect.x < 800 and self.rect.y < 600

class Player:
    def __init__(self, playerY, scale, img):
        self.img = pygame.transform.scale(img, scale)
        self.rect = self.img.get_rect()
        self.rect = self.rect.inflate(-75, 0)
        self.pseudo_rect = self.rect.inflate(-50, -50)
        self.lives = 3
        self.fatal = False
        mousex, mousey = (0, playerY)

    def motion(self, playerY):
        mousex, mousey = event.pos
        if (mousex < 800 - 55):
            self.rect.topleft = (mousex, playerY)
            self.pseudo_rect.topleft = (mousex + 50, playerY + 50)
        else:
            self.rect.topleft = (800 - 55, playerY)
            self.pseudo_rect.topleft = ((800 - 55) + 50, playerY + 50)

    def draw(self, surface):
        surface.blit(self.img, self.rect)

    def hide(self):
        self.hidden = True
        self.rect.center = (400, 700) #hide player below the screen
        self.hide_timer = pygame.time.get_ticks()

    def update(self, playerY):
        #unhide player
        if self.hidden and (pygame.time.get_ticks() - self.hide_timer > 1000):
            self.hidden = False
            mousex, mousey = (0, playerY)

class Explosion:
    def __init__(self, center, img):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosionAnim):
                objCollection.remove(explosion)
            else:
                center = self.rect.center
                self.img = explosionAnim[self.frame]
                self.rect = self.img.get_rect()
                self.rect.center = center
                
    def draw(self, surface):
            surface.blit(self.img, self.rect)

    def isVisible(self):
        return self.rect.x < 800 and self.rect.y < 600

def loadify(imgPath):
    return pygame.image.load(imgPath).convert_alpha()

def drawText(surface, text, size, x, y):
    font = pygame.font.Font(fontName, size)
    textSurface = font.render(text, True, (255, 255, 255))
    textRect = textSurface.get_rect()
    textRect.midtop = (x, y)
    surface.blit(textSurface, textRect)

def showGameOver(surface):
    drawText(surface, "BATTLESHIPS", 64, WIDTH / 2, HEIGHT / 4)
    drawText(surface, "Move the mouse to sail left and right, Avoid obstacles", 22, WIDTH / 2, HEIGHT / 2)
    drawText(surface, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        fpsClock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP and not event.key == pygame.K_ESCAPE:
                waiting = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            

pygame.init()
fpsClock = pygame.time.Clock()
WIDTH = 800
HEIGHT = 600
FPS = 30
mainSurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ships Prototype')

blue = pygame.Color(32, 160, 230)
fontName = pygame.font.match_font('arial')
shipImg = loadify('resources/ShipSprite02.png')
explosionAnim = []
for i in range(6):
    fileName = 'resources/Explosion0{}.png'.format(i)
    exploImg = loadify(fileName)
    exploImg = pygame.transform.scale(exploImg, (120, 120))
    explosionAnim.append(exploImg)

counter = 0
gameOver = True
running = True

while running:
    if gameOver:
        showGameOver(mainSurface)
        gameOver = False
        objCollection = []
        player = Player(460, (140, 190), shipImg)
        
    mainSurface.fill(blue)
    player.draw(mainSurface)
    drawText(mainSurface, str(player.lives), 18, 400, 10)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION:
            player.motion(460)
        
    if counter == 90:
        objCollection.append(Villain(random.randrange(670), -100, 3, random.uniform(0.4, 0.6), shipImg))
        counter = 0

    for a in objCollection:
        a.update()
        if a.isVisible():
            a.draw(mainSurface)
            if player.rect.colliderect(a):
                if player.pseudo_rect.colliderect(a) and a.fatal:
                    explosion = Explosion(a.rect.center, exploImg)
                    objCollection.append(explosion)
                    explosion.update
                    objCollection.remove(a)
                    player.lives -= 1
                    player.hide()
                    player.update(480)
        else:
            objCollection.remove(a)

    if player.lives == 0:
        gameOver = True

    counter += 1
    pygame.display.update()
    fpsClock.tick(FPS)
