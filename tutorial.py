import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join



pygame.display.set_caption("Platformer")


HEIGHT, WIDTH = 1000,800  #width and height of the window
FPS = 60  #frames per second
PLAYER_VEL = 5  #speed the player move arround

window = pygame.display.set_mode((HEIGHT, WIDTH))

def flip(sprites):
    return [pygame.transform.flip(sprite,True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width,height, direction = False):#loop animations, dir1 and dir2 is to load other images and instead of only one character
    path = join("assets", dir1, dir2) #determine the path to the images
    images = [f for f in listdir(path) if isfile(join(path, f))] #load every file in maskdude and split individual images

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()#convert_alpha will allowed me to load a transparent background image
        
        sprites = []
        for i in range(sprite_sheet.get_width()//width): #this width is going to be the width of an individual image inside the animation 
            surface = pygame.Surface((width,height),pygame.SRCALPHA,32) #SRCALPHA-->This tells Pygame that the surface should support transparency, meaning you can make parts of it see-through.
            rect = pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect) #blit = draw #drawing sprite sheet in the frame i want in (0,0) of the new surface
            sprites.append(pygame.transform.scale2x(surface)) #scale2x = scale them and doule their size ex: 32 by 32 --> 64 by 64

        if direction:
            all_sprites [image.replace(".png","")+"_right"] = sprites
            all_sprites [image.replace(".png","")+"_left"] = flip(sprites) #if u want a multidirectional animation, then u need to add two keys to our dictionary here for every single one of our animations.
        else:
            all_sprites [image.replace(".png","")] = sprites
    
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96, 0,  size, size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

class Player (pygame.sprite.Sprite): 
    COLOR = (0, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3
    def __init__ (self, x, y, width, height):
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0  #apply a velocity in a direction
        self.y_vel = 0 
        self.mask = None
        self.direction = "left" # <-- the direction is to tracking what direction my player's  facing
        self.ftime = 0 #fall time
        self.animation_count = 0

    def move(self, dx ,dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0 # <-- reset the count to change the animation frame, it made the animation don't look wonky from going left to right

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def loop(self, fps):
        #self.y_vel += min(1,(self.ftime/fps )*self.GRAVITY) #bigger the fall time faster the fall speed
        self.move(self.x_vel,self.y_vel)

        self.ftime += 1
        self.update_sprite()
        print(fps)
        
    def update_sprite(self):
        sprite_sheet = "idle" #<-- defualt spreadsheet
        if self.x_vel != 0:
            sprite_sheet = "run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count+=1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self,windo):
        windo.blit(self.sprite,(self.rect.x,self.rect.y))

class Object(pygame.sprite.Sprite): #just to define all of the properties that needed for valid sprite
    def __init__(self,x,y,width,height,name = None):  
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, windo):
        windo.blit(self.image,(self.rect.x,self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets", "background", name)) #load image files
    _, _, width, height = image.get_rect() #to get their rectangular area of the image
    tiles = [] 
    for i in range(WIDTH//width+4):
        for j in range(HEIGHT//height+4):
            #how many tiles need to create in the X and the Y direction to fill the whole screen
            pos = (i*width,j*height)
            tiles.append(pos)

    return tiles, image #<-- the image here is to let me know what image I need to use

def draw(window, background, bg_image, player, blocks):
    for tile in background:
        window.blit(bg_image, tile)  # Draw tiles on window

    for block in blocks:
        block.draw(window)  # Draw blocks

    player.draw(window)

    pygame.display.update()

def handle_move(player):
    keyz = pygame.key.get_pressed( )
    player.x_vel = 0
    if keyz[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keyz[pygame.K_d]:
        player.move_right (PLAYER_VEL)

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brown.png")

    block_size = 96

    player = Player(100,100,50,50)
    blocks = [Block(0,HEIGHT - block_size,block_size)]
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
            for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]

    run = True 
    while run:
        clock.tick(FPS) #to regulate the the frame rate accoss different divice

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #to stop the game 
                run = False
                break
             
        player.loop(FPS)
        handle_move(player)
        draw(window, background, bg_image, player, floor)

    pygame.quit()
    quit()
 
if __name__ == "__main__": # checks if the script is being run as the main program 
    main(window)