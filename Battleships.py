#!/usr/bin/python

# BATTLESHIPS
# Objective: Collect as many points as you can before your ship gets hit by mobs
# Controls: Use mouse to move left and right

# CREDITS:
# Art and code created by me, Veronica Strakhov. Contact me at veronicastrakhov@gmail.com
# Adventure Begins by Bart Kelsy on opengameart.org
# Bomb Explosion 8bit SFX by Luke.RUSTLTD on opengameart.org
# Coin01 SFX by crazyduckgames on opengameart.org

import pygame, os, sys, random
from pygame.locals import *

# CLASSES:

# Parent class of moving objects that are drawn on screen with functions that are used often
class baseObj:
    # Initialize self. Deadly? Gives points?
    def __init__(self, speed, img, fatal, collect):
        self.speed = speed
        self.img = img
        self.rect = self.img.get_rect()
        self.fatal = fatal
        self.collect = collect

    def draw(self, surface):
        surface.blit(self.img, self.rect)

    #Checks if object is on screen
    def isVisible(self): 
        return self.rect.x < infoObject.current_w and self.rect.y < infoObject.current_h

    # Move towards the bottom of the screen
    def update(self):
        sy = self.speed
        self.rect.y += sy
        
# Only deadly mob, represented by ships
class Villain(baseObj):
    def __init__(self, x, y, speed, scale, img, fatal, collect):
        super().__init__(speed, img, fatal, collect)
        self.img = pygame.transform.rotozoom(img, 180, scale)
        self.rect = self.img.get_rect()
        self.rect = self.rect.inflate(round(-120 * scale),(-120 * scale))
        self.rect.x = x
        self.rect.y = y

# The player, moves with the mouse on the x-axis
class Player(baseObj):
    def __init__(self, playerY, scale, img):
        self.img = pygame.transform.scale(img, scale)
        self.rect = self.img.get_rect()
        self.rect = self.rect.inflate(-30, -40)
        self.lives = 3
        self.frame = 0
        mousex, mousey = (WIDTH / 2, playerY)

    # Controls player mouse motion
    def motion(self, playerY, pos):
        mousex, mousey = pos
        if (mousex < WIDTH - 55):
            self.rect.topleft = (mousex, playerY)
        else:
            self.rect.topleft = (WIDTH - 95, playerY)

# Appears when hit with deadly object
class Explosion(baseObj):
    def __init__(self, center, img, fatal, collect):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.fatal = False
        self.collect = False

    # Plays animation
    def update(self):
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

# Drawn above all objects, does not interact with other objects
class Cloud(baseObj):
    def __init__(self, x, y, speed, scale, img, fatal, collect):
        super().__init__(speed, img, fatal, collect)
        self.img = pygame.transform.scale(img, scale)
        self.rect.x = x
        self.rect.y = y

# Collectable object, gives player points
class Coin(baseObj):
    def __init__(self, x, y, speed, img, fatal, collect):
        super().__init__(speed, img, fatal, collect)
        center = self.rect.center
        self.rect.x = x
        self.rect.y = y
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    # Plays animation
    def update(self):
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

# Load image and converts to alpha
def loadify(imgPath):
    return pygame.image.load(imgPath).convert_alpha()

# Handles drawing text onto the screen
def drawText(surface, text, size, x, y):
    font = pygame.font.Font(fontName, size)
    textSurface = font.render(text, True, (255, 255, 255), (219, 111, 9))
    textRect = textSurface.get_rect()
    textRect.midtop = (x, y)
    surface.blit(textSurface, textRect)

# Shows at the beginning of game and when the player dies
def showGameOver(surface, text, text2, img, showScore, pointsGained):
    surface.blit(img, (0, 0))
    drawText(surface, text, 64, WIDTH / 2, HEIGHT / 4)
    drawText(surface, text2, 22, WIDTH / 2, HEIGHT / 2)
    drawText(surface, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 0.8)
    # If player earned points, print the amount gained
    if showScore:
        drawText(surface, pointsGained, 22, WIDTH / 2, HEIGHT * 0.6)
    pygame.display.flip()
    waiting = True
    # Wait until the player starts the game
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

# Handles creating objects depending on how frequently they appear
def spawn(lastUpdate, freq):
    shouldSpawn = (pygame.time.get_ticks() - lastUpdate > freq)
    return shouldSpawn

# SETTING UP:

# Pygame and screen
pygame.init()
pygame.mixer.init()
fpsClock = pygame.time.Clock()
infoObject = pygame.display.Info()
WIDTH = infoObject.current_w
HEIGHT = infoObject.current_h
FPS = 30
mainSurface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Ships Prototype')
blue = pygame.Color(32, 160, 230)
fontName = pygame.font.match_font('arial')

# Images
shipImg = loadify('resources/ShipSprite02.png')
cloudImg = loadify('resources/Cloud.png')
background = loadify('resources/Waves.jpg')
background = pygame.transform.scale(background, (WIDTH, background.get_height()))
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
startScreen = pygame.transform.scale(startScreen, (WIDTH, HEIGHT))
overScreen = loadify('resources/GameOverScreen.jpg')
overScreen = pygame.transform.scale(overScreen, (WIDTH, HEIGHT))

# Sounds and music
exploSound = pygame.mixer.Sound('resources/8bit_bomb_explosion.wav')
coinSound = pygame.mixer.Sound('resources/coin01.wav')
pygame.mixer.music.load('resources/little town - orchestral.ogg')

# Misc
villainLastUpdate = pygame.time.get_ticks()
otherLastUpdate = pygame.time.get_ticks()
objCollectionMid = []
objCollectionTop = []
highscore = 0
plyrY = infoObject.current_h - 90
plyrSize = (130, 120)
gameOver = True
running = True

# Loop music
pygame.mixer.music.play(loops=-1)

# MAIN GAME LOOP:

while running:
    if gameOver:
        showGameOver(mainSurface, "BATTLESHIPS", "Move the mouse to sail left and right, Avoid obstacles", startScreen, False, 0)
        gameOver = False
        player = Player(plyrY, plyrSize, lives3)
        player.motion(plyrY, ((WIDTH / 2) - 65, 490))
        score = 0

    # Scrolling background        
    mainSurface.fill(blue)
    relY = bkgdY % background.get_rect().height
    mainSurface.blit(background,(0, relY - background.get_rect().height))
    if relY < HEIGHT:
        mainSurface.blit(background, (0, relY))
    bkgdY += 0.5
    player.draw(mainSurface)

    # Check if player has quit or moved
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION:
            player.motion(plyrY, event.pos)

    # Spawn enemy ships every 1.5 seconds
    if spawn(villainLastUpdate, 1500):
        objCollectionMid.append(Villain(random.randrange(WIDTH - 75), -200, 4, random.uniform(0.4, 0.6), shipImg, True, False))
        villainLastUpdate = pygame.time.get_ticks()
    # Spawn coins and clouds every 3 seconds
    if spawn(otherLastUpdate, 3000):
        objCollectionTop.append(Cloud(random.randrange(WIDTH - 100), -100, 1, (150, 80), cloudImg, False, False))
        objCollectionMid.append(Coin(random.randrange(WIDTH - 30), -100, 2, coinImg, False, True))
        otherLastUpdate = pygame.time.get_ticks()

    # Check objects in the middle collection
    # Has the player hit a deadly object or a collectable object?
    for a in objCollectionMid:
        a.update()
        if a.isVisible():
            a.draw(mainSurface)
            if player.rect.colliderect(a) and a.fatal:
                # Lose life, play explosion
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
                    player.img = pygame.transform.scale(lives2, plyrSize)
                    player.draw(mainSurface)
                elif player.lives == 1:
                    player.img = pygame.transform.scale(lives1, plyrSize)
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
    drawText(mainSurface, str(score), 18, WIDTH / 2, 10)

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
        player = Player(plyrY, plyrSize, lives3)
        player.motion(plyrY, ((WIDTH / 2) - 65, plyrY))
        score = 0
        
    pygame.display.update()
    fpsClock.tick(FPS)
