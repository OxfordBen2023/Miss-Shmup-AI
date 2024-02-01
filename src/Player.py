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

		self.jump_sound = pygame.mixer.Sound('assets/audio/jump.mp3')
		self.jump_sound.set_volume(0.02)

	def animation_state(self):
		self.player_index += 0.1
		if self.player_index >= len(self.player_walk):self.player_index = 0
		self.image = self.player_walk[int(self.player_index)]

	def update(self):
		self.animation_state()
