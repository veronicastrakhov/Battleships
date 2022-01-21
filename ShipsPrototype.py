#!/usr/bin/python

# CREDITS:
# Adventure Begins by Bart Kelsy on opengameart.org
# Bomb Explosion 8bit SFX by Luke.RUSTLTD on opengameart.org
# Coin01 SFX by crazyduckgames on opengameart.org

import pygame, os, sys, random
from pygame.locals import *

# CLASSES:

# Parent class with functions that are used often
class baseClass:
    def __init__(self, speed, img, fatal, collect): # Initialize self. Deadly? Gives points?
        self.speed = speed
        self.img = img
        self.rect = self.img.get_rect()
        self.fatal = fatal
        self.collect = collect

    def draw(self, surface):
        surface.blit(self.img, self.rect)

    def isVisible(self): #Checks if object is on screen
        return self.rect.x < 800 and self.rect.y < 600

    def update(self): # Move towards the bottom of the screen
        sy = self.speed
        self.rect.y += sy
        
class Villain(baseClass): # Only deadly mob, represented by ships
    def __init__(self, x, y, speed, scale, img, fatal, collect):
        super().__init__(speed, img, fatal, collect)
        self.img = pygame.transform.rotozoom(img, 180, scale)
        self.rect = self.img.get_rect()
        self.rect = self.rect.inflate(round(-120 * scale),(-120 * scale))
        self.rect.x = x
        self.rect.y = y

class Player(baseClass): # The player, moves with the mouse on the x-axis
    def __init__(self, playerY, scale, img):
        self.img = pygame.transform.scale(img, scale)
        self.rect = self.img.get_rect()
        self.rect = self.rect.inflate(-30, -40)
        self.lives = 3
        self.frame = 0
        mousex, mousey = (WIDTH / 2, playerY)

    def motion(self, playerY, pos): # Controls player mouse motion
        mousex, mousey = pos
        if (mousex < WIDTH - 55):
            self.rect.topleft = (mousex, playerY)
        else:
            self.rect.topleft = (WIDTH - 55, playerY)

class Explosion(baseClass): # Appears when hit with deadly object
    def __init__(self, center, img, fatal, collect):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.fatal = False
        self.collect = False

    def update(self): # Plays animation
        exploSound.play()
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosionAnim):
                objCollectionMid.remove(self)
            else:
                center = self.rect.center
                self.img = explosionAnim[self.frame]
                self.rect = self.img.get_rect()
                self.rect.center = center

class Cloud(baseClass): # Drawn above all objects, does not interact with other objects
    def __init__(self, x, y, speed, scale, img, fatal, collect):
        super().__init__(speed, img, fatal, collect)
        self.img = pygame.transform.scale(img, scale)
        self.rect.x = x
        self.rect.y = y

class Coin(baseClass): # Collectable object, gives player points
    def __init__(self, x, y, speed, img, fatal, collect):
        super().__init__(speed, img, fatal, collect)
        center = self.rect.center
        self.rect.x = x
        self.rect.y = y
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self): # Plays animation
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
        if self.frame == len(coinAnim):
            self.frame = 0
        else:
            center = self.rect.center
            self.img = coinAnim[self.frame]
            self.rect = self.img.get_rect()
            self.rect.center = center
        sy = self.speed
        self.rect.y += sy

# FUNCTIONS

def loadify(imgPath): # Load image and converts to alpha
    return pygame.image.load(imgPath).convert_alpha()

def drawText(surface, text, size, x, y): # Handles drawing text onto the screen
    font = pygame.font.Font(fontName, size)
    textSurface = font.render(text, True, (255, 255, 255), (219, 111, 9))
    textRect = textSurface.get_rect()
    textRect.midtop = (x, y)
    surface.blit(textSurface, textRect)

def showGameOver(surface, text, text2, img, showScore, pointsGained): # Shows at the beginning of game and when the player dies
    surface.blit(img, (0, 0))
    drawText(surface, text, 64, WIDTH / 2, HEIGHT / 4)
    drawText(surface, text2, 22, WIDTH / 2, HEIGHT / 2)
    drawText(surface, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 0.8)
    if showScore: # If player earned points, print the amount gained
        drawText(surface, pointsGained, 22, WIDTH / 2, HEIGHT * 0.6)
    pygame.display.flip()
    waiting = True
    while waiting: # Wait until the player starts the game
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

def spawn(lastUpdate, freq): # Handles creating objects depending on how frequently they appear
    shouldSpawn = (pygame.time.get_ticks() - lastUpdate > freq)
    return shouldSpawn

# SETTING UP:

#Pygame and screen
pygame.init()
pygame.mixer.init()
fpsClock = pygame.time.Clock()
WIDTH = 800
HEIGHT = 600
FPS = 30
mainSurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ships Prototype')
blue = pygame.Color(32, 160, 230)
fontName = pygame.font.match_font('arial')

# Images
shipImg = loadify('resources/ShipSprite02.png')
cloudImg = loadify('resources/Cloud.png')
background = loadify('resources/Waves.jpg')
bkgdY = HEIGHT

# Animated objects
explosionAnim = []
for i in range(7):
    fileName = 'resources/Explosion0{}.png'.format(i)
    exploImg = loadify(fileName)
    exploImg = pygame.transform.scale(exploImg, (120, 120))
    explosionAnim.append(exploImg)
    
coinAnim = []
for i in range(10):
    fileName = 'resources/Coin0{}.png'.format(i)
    coinImg = loadify(fileName)
    coinImg = pygame.transform.scale(coinImg, (35, 35))
    coinAnim.append(coinImg)

# Different player images based on health
lives3 = loadify('resources/PlayerSprite00.png')
lives2 = loadify('resources/PlayerSprite01.png')
lives1 = loadify('resources/PlayerSprite02.png')

# Screens that will be shown after using the showGameOver function
startScreen = loadify('resources/StartScreen.jpg')
overScreen = loadify('resources/GameOverScreen.jpg')

# Sounds and music
exploSound = pygame.mixer.Sound('resources/8bit_bomb_explosion.wav')
pygame.mixer.Sound.set_volume(exploSound, 0.3)
coinSound = pygame.mixer.Sound('resources/coin01.wav')
pygame.mixer.Sound.set_volume(coinSound, 0.05)
pygame.mixer.music.load('resources/little town - orchestral.ogg')
pygame.mixer.music.set_volume(0.05)

# Misc
villainLastUpdate = pygame.time.get_ticks()
otherLastUpdate = pygame.time.get_ticks()
objCollectionMid = []
objCollectionTop = []
highscore = 0
gameOver = True
running = True

# Loop music
pygame.mixer.music.play(loops=-1)

# MAIN GAME LOOP:

while running:
    if gameOver:
        showGameOver(mainSurface, "BATTLESHIPS", "Move the mouse to sail left and right, Avoid obstacles", startScreen, False, 0)
        gameOver = False
        player = Player(490, (130, 120), lives3)
        player.motion(490, ((WIDTH / 2) - 65, 490))
        score = 0

    # Scrolling background        
    mainSurface.fill(blue)
    relY = bkgdY % background.get_rect().width
    mainSurface.blit(background,(0, relY - background.get_rect().width))
    if relY < HEIGHT:
        mainSurface.blit(background, (0, relY))
    bkgdY += 0.5
    player.draw(mainSurface)
    
    for event in pygame.event.get(): # Check if player has quit or moved
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION:
            player.motion(490, event.pos)

    if spawn(villainLastUpdate, 3000): # Spawn enemy ships every 3 seconds
        objCollectionMid.append(Villain(random.randrange(670), -200, 4, random.uniform(0.4, 0.6), shipImg, True, False))
        villainLastUpdate = pygame.time.get_ticks()

    if spawn(otherLastUpdate, 2000): # Spawn coins and clouds every 2 seconds
        objCollectionTop.append(Cloud(random.randrange(670), -100, 1, (150, 80), cloudImg, False, False))
        objCollectionMid.append(Coin(random.randrange(670), -100, 2, coinImg, False, True))
        otherLastUpdate = pygame.time.get_ticks()

    # Check objects in the middle collection
    # Has the player hit a deadly object or a collectable object?
    for a in objCollectionMid:
        a.update()
        if a.isVisible():
            a.draw(mainSurface)
            if player.rect.colliderect(a) and a.fatal: # Lose life, play explosion
                explosion = Explosion(a.rect.center, exploImg, False, False)
                explosion2 = Explosion(player.rect.center, exploImg, False, False)
                objCollectionMid.append(explosion)
                objCollectionMid.append(explosion2)
                explosion.update
                explosion2.update
                objCollectionMid.remove(a)
                player.lives -= 1

                # Change player images
                if player.lives == 2:
                    player.img = pygame.transform.scale(lives2, (130, 120))
                    player.draw(mainSurface)
                elif player.lives == 1:
                    player.img = pygame.transform.scale(lives1, (130, 120))
                    player.draw(mainSurface)

            # Collect coin        
            elif player.rect.colliderect(a) and a.collect:
                coinSound.play()
                score += 100
                objCollectionMid.remove(a)
                
    # Update objects in top collection                
    for a in objCollectionTop:
        a.update()
        if a.isVisible():
            a.draw(mainSurface)
        else:
            objCollectionTop.remove(a)

    # Draw score at the top of the screen
    drawText(mainSurface, str(score), 18, WIDTH/2, 10)

    # If the player dies, show game over with score
    if player.lives == 0 and explosion2 not in objCollectionMid:
        objCollectionMid = []
        objCollectionTop = []
        if score > highscore:
            highscore = score
            showGameOver(mainSurface, "GAME OVER", "New Highscore!", overScreen, True, str(highscore))
        else:
            showGameOver(mainSurface, "GAME OVER", "The captain goes down with the ship!", overScreen, True, str(score))
        gameOver = False
        player = Player(490, (130, 120), lives3)
        player.motion(490, ((WIDTH / 2) - 65, 490))
        score = 0
        
    pygame.display.update()
    fpsClock.tick(FPS)
