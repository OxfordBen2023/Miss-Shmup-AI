import pygame
from src.Config import *

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		player_walk_1 = pygame.image.load('assets/graphics/player/player_idle_1.png').convert_alpha()
		player_walk_2 = pygame.image.load('assets/graphics/player/player_idle_2.png').convert_alpha()
		self.player_walk = [player_walk_1,player_walk_2]
		self.player_index = 0
		self.image = self.player_walk[self.player_index]
		self.rect = self.image.get_rect(center = (100,200))
		self.gravity = 0
		self.collider_zones_group = pygame.sprite.Group()
		self.width = self.image.get_width()
		self.height = self.image.get_height()

		self.collider_zones_group.add(PlayerZone((30,30),(self.width+12,6), 'up'))
		self.collider_zones_group.add(PlayerZone((30,30),(self.width+12,6), 'down'))
		self.collider_zones_group.add(PlayerZone((30,30),(6,self.height+12), 'left'))
		self.collider_zones_group.add(PlayerZone((30,30),(12,self.height+12), 'right'))


		self.jump_sound = pygame.mixer.Sound('assets/audio/jump.mp3')
		self.jump_sound.set_volume(0.02)

	def place_zones(self):
		for zone in self.collider_zones_group:
			if zone.name == 'up':
				zone.rect.midbottom = self.rect.midtop
			elif zone.name == 'down':
				zone.rect.midtop = self.rect.midbottom
			elif zone.name == 'left':
				zone.rect.midright = self.rect.midleft
			elif zone.name == 'right':
				zone.rect.midleft = self.rect.midright


	def animation_state(self):
		self.player_index += 0.1
		if self.player_index >= len(self.player_walk):self.player_index = 0
		self.image = self.player_walk[int(self.player_index)]


	def update(self):
		self.animation_state()

class PlayerZone(pygame.sprite.Sprite):
	def __init__(self,emit, size, name):
		super().__init__()
		self.name = name
		self.image = pygame.Surface(size)
		self.image.fill((230,0,0))
		self.rect = self.image.get_rect(center = (emit))

