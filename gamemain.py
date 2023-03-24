#Setup vars
import pygame, sys, random, time
from pygame.locals import *
pygame.init()
vec = pygame.math.Vector2
HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platform Jumper!")
#sounds
pygame.mixer.music.load("Super_Mario_Bros_Snow.mp3")
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(loops=-1)
JUMP_SOUND = pygame.mixer.Sound("Mario_Jump.mp3")
JUMP_SOUND.set_volume(0.5)

#player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.surf = pygame.image.load("snowman.png")       
        self.rect = self.surf.get_rect()
        
        self.pos = vec((10, 360))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.jumping = False
        self.score = 0

    #Handle movement
    def move(self):
        self.acc = vec(0,0.5)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        
        self.rect.midbottom = self.pos

    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if hits:
                if self.pos.y < hits[0].rect.bottom: 
                    if hits[0].point == True:
                        hits[0].point = False
                        self.score += 1
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False
                

#Platform class
class platform(pygame.sprite.Sprite):
    def __init__(self, width = 0, height = 18):
        super().__init__()
        if width == 0:
            width = random.randint(50,120)

            self.image = pygame.image.load("platform.png")
            self.surf = pygame.transform.scale(self.image, (width, height))
            self.rect = self.surf.get_rect(center = (random.randint(0, WIDTH-10), random.randint(0, HEIGHT-40)))
        self.point = True
        self.speed = random.randint(-1, 1)
        self.moving = True

    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving == True:
            self.rect.move_ip(self.speed, 0)
            if hits:
                P1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH

    def generateCoin(self):
        if(self.speed == 0):
            coins.add(Coin((self.rect.centerx, self.rect.centery - 50)))

#Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.image = pygame.image.load("Coin.png")
        self.rect = self.image.get_rect()

        self.rect.topleft = pos

    def update(self):
        if self.rect.colliderect(P1.rect):
            P1.score += 5
            self.kill()
        
def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform,groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
        C = False

def plat_gen():
    while len(platforms) < 6:
        width = random.randrange(50, 100)
        p = None
        C = True

        while C:
            p = platform()
            p.rect.center = (random.randrange(0, WIDTH - width), random.randrange(-50, 0))
            C = check(p, platforms)
        
        p.generateCoin()
        platforms.add(p)
        all_sprites.add(p)

PT1 = platform(450, 80)
P1 = Player()
PT1.point = False
PT1.moving = False
#Draw sprites
background = pygame.image.load("background.png")
PT1.surf = pygame.image.load("platform.png")
#PT1.surf.fill((255, 0, 0))
PT1.surf = pygame.transform.scale(PT1.surf, (450,80))
PT1.rect = PT1.surf.get_rect(center =(WIDTH/2, HEIGHT -10))


all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)

platforms = pygame.sprite.Group()
platforms.add(PT1)

coins = pygame.sprite.Group()

for x in range(random.randint(4,5)):
    C = True
    pl = platform()
    while C:
        pl = platform()
        C = check(pl, platforms)
    pl.generateCoin()
    platforms.add(pl)
    all_sprites.add(pl)

while True:
    P1.update()
    #Game loop
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if P1.jumping == False:
                    JUMP_SOUND.play()
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                P1.cancel_jump()
    #Game over check  
    if P1.rect.top > HEIGHT:
        for entity in all_sprites:
            displaysurface.fill((255, 0, 0))
            game_over_font = pygame.font.SysFont('Verdana', 40)
            game_over = game_over_font.render("Game Over", True, (0,0,0))
            displaysurface.blit(game_over, (WIDTH/4.5, HEIGHT/2.5))
            pygame.display.update()
            entity.kill()
            time.sleep(2)
            pygame.quit()
            sys.exit()
    #platform remove
    if P1.rect.top <= HEIGHT / 3:
        P1.pos.y += abs(P1.vel.y)
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()

        for coin in coins:
            coin.rect.y += abs(P1.vel.y)
            if coin.rect.top >= HEIGHT:
                coin.kill()

    displaysurface.fill((0,0,0))
    displaysurface.blit(background, (0,0))
    plat_gen()

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()

    for coin in coins:
        displaysurface.blit(coin.image, coin.rect)
        coin.update()

    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(P1.score), True, (255, 255, 255))
    displaysurface.blit(g, (WIDTH/2, 10))
    
    pygame.display.update()
    FramePerSec.tick(FPS)