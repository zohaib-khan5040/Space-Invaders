import pygame
import os
import time
import random
import sys

pygame.font.init()
# Initializing
WIDTH, HEIGHT = 750, 750
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load assets
sourceFileDir = os.path.dirname(os.path.abspath(__file__))
fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_ship_red_small.png"))
RED_SHIP = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_ship_green_small.png"))
GREEN_SHIP = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_ship_blue_small.png"))
BLUE_SHIP = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_ship_yellow.png"))
YELLOW_SHIP = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_laser_red.png"))
RED_LASER = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_laser_green.png"))
GREEN_LASER = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_laser_blue.png"))
BLUE_LASER = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"pixel_laser_yellow.png"))
YELLOW_LASER = pygame.image.load(fondImgPath)

fondImgPath = os.path.join(sourceFileDir, os.path.join('assets',"background-black.png"))
BACKGROUND = pygame.transform.scale(pygame.image.load(fondImgPath), (WIDTH,HEIGHT))

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self,screen):
        screen.blit(self.img, (self.x,self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self,obj)


# General Ship class
class Ship:

    # cooldown is half a second (fps)
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        # Define cooldown period for lasers
        self.cooldown_counter = 0
    
    def draw(self, screen):
        screen.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(screen)

    def move_lasers(self,vel,obj):
        """ Moves lasers across the screen and checks for collisions """
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
    def cooldown(self):

        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

# Player ship inherits
class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health=100)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        # Masks for collisions
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def healthbar(self,screen):
        pygame.draw.rect(screen, (255,0,0), (self.x, self.y+self.ship_img.get_height()+10, self.ship_img.get_width(), 10))
        pygame.draw.rect(screen, (0,255,0), (self.x, self.y+self.ship_img.get_height()+10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    
    def draw(self,screen):
        super().draw(screen)
        self.healthbar(screen)

class Enemy(Ship):
    COLORMAP = {
        "red":(RED_SHIP,RED_LASER),
        "green":(GREEN_SHIP,GREEN_LASER),
        "blue":(GREEN_SHIP,GREEN_LASER)
    }

    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health=100)
        self.ship_img, self.laser_img = self.COLORMAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self,vel):
        self.y += vel
    
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

def collide(obj1, obj2):
    # from the docs
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None


def main():
    running = True
    FPS = 60
    level = 0
    lives = 5
    player_vel = 5
    laser_vel = 5

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player = Player(300,650)
    font = pygame.font.SysFont("comicsans",50)
    lost_font = pygame.font.SysFont("comicsans",60)
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        SCREEN.blit(BACKGROUND, (0,0))
        # Draw text
        lives_label = font.render("Lives: {}".format(lives), 1, (255,255,255))
        level_label = font.render("Level: {}".format(level), 1, (255,255,255))
        SCREEN.blit(lives_label, (10,10))
        SCREEN.blit(level_label, (WIDTH-level_label.get_width()-10, 10))

        # Draw all the ships (.draw inherited from Ship)
        player.draw(SCREEN)

        for enemy in enemies:
            enemy.draw(SCREEN)
        
        if lost:
            lost_label = lost_font.render("YOU LOST",1,(255,255,255))
            SCREEN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2, 350))

        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            # three second timer before stopping the game
            if lost_count > FPS*3:
                running = False
            else: 
                continue

        if len(enemies) == 0:
            # Move to the next level
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,WIDTH-100),random.randrange(-900,-100),random.choice(["red","blue","green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                running = False
        
        # Allowing for movement (plus restrictions)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and (player.x + player_vel + player.get_width() < WIDTH):
            player.x += player_vel
        if keys[pygame.K_LEFT] and (player.x - player_vel > 0):
            player.x -= player_vel
        if keys[pygame.K_DOWN] and (player.y + player_vel + player.get_height() + 15 < HEIGHT):
            player.y += player_vel
        if keys[pygame.K_UP] and (player.y - player_vel > 0):
            player.y -= player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel,player)

            # Allow enemies to shoot at you at random
            if random.randrange(0,4*60) == 1:
                enemy.shoot()

            # Decrement lives if enemy goes off screen- remove it too            
            if collide(enemy,player):
                lives -= 1
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans",70)
    running = True
    while running:
        SCREEN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press the mouse to begin.",1,(255,255,255))
        SCREEN.blit(title_label, (WIDTH/2 -title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()        

if __name__=='__main__':
    main_menu()