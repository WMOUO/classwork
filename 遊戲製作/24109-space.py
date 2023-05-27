import pygame
import os
import random
#常數區
W = 500
H = 600
FPS = 60
SPEED = 6
BLACK = (0,0,0)
Green = (0,255,0)

#變數區
running = True
#初始化
pygame.init()
pygame.mixer.init()
die_sounds = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
bullets = pygame.sprite.Group()
shoot_sound = pygame.mixer.Sound(os.path.join("sound","shoot.wav"))
#設定螢幕尺寸及啟動時間控制
screen = pygame.display.set_mode((W,H))#(寬,高)
clock = pygame.time.Clock()
pygame.display.set_caption("給我電電的太空歷險")
#載入圖片
bg_img = pygame.image.load(os.path.join("img","background.png")).convert()
player_img = pygame.image.load(os.path.join("img","player.png")).convert()
rock_img = pygame.image.load(os.path.join("img","rock.png")).convert()
bullet_img = pygame.image.load(os.path.join("img","bullet.png")).convert()
expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img",
        f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join("img",
        f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
#載入遊戲音效
pygame.mixer.music.load(os.path.join("sound","bgm.ogg"))
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)
#載入音效

#玩家角色類別
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50,38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.speedx = SPEED
        self.rect.centerx = W/2
        self.rect.bottom = H-10
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

#玩家控制
    def update(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:self.rect.x -= self.speedx
        if self.rect.right > W:self.rect.right = W
        if self.rect.left < 0:self.rect.left = 0
#石頭角色類別
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.transform.scale(rock_img,(50,38))
        self.image = rock_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0,W)
        self.rect.y = random.randrange(-100,-40)
        self.speedx = random.randrange(-3,3)
        self.speedy = random.randrange(2,10)
        self.image_ori = self.image.copy()
        self.degree = 0
        self.rot = random.randrange(-3,3)
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.y > H:
            self.rect.x = random.randrange(0,W)
            self.rect.y = random.randrange(-100,-40)
            self.speedx = random.randrange(-3,3)
            self.speedy = random.randrange(2,10)
        self.rotate()
    def rotate(self):
        self.degree = (self.degree + self.rot) % 360
        self.image = pygame.transform.rotate(self.image_ori , self.degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
#子彈角色類別
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        shoot_sound.play()

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0 : self.kill()

def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)
    die_sounds.play()
#Explosion
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


#加入玩家角色
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
rocks = pygame.sprite.Group()
for _ in range(8):
    new_rock()


#遊戲主控區
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE : player.shoot()
    #設定每秒幀數
    screen.blit(bg_img,(0,0))
    clock.tick(FPS)

    all_sprites.update()
    all_sprites.draw(screen)

    hits = pygame.sprite.spritecollide(player, rocks, True,pygame.sprite.collide_circle)
    for hit in hits:
        new_rock()
        death_expl = Explosion(player.rect.center, 'player')
        all_sprites.add(death_expl)
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        new_rock()
    #更新畫面
    pygame.display.update()





#遊戲結束
pygame.quit()
