from src.config import *
import pygame

class Enemy(pygame.sprite.Sprite):
	def __init__(self,emit, direction, speed, size=30):
		super().__init__()
		self.size = size
		self.image = pygame.Surface([size, size])
		self.image.fill((80,80,80))
		self.rect = self.image.get_rect(center = (emit))
		self.speed = speed
		self.direction = direction
		self.position = emit

	def moove(self):
		# self.position variable is used to preserve float value precision
		self.position = (self.position[0] - self.speed * self.direction[0],  self.position[1] - self.speed * self.direction[1])

		self.rect.centerx = self.position[0] 
		self.rect.centery = self.position[1]


	def update(self):
		self.destroy()
		self.moove()

	def destroy(self):
		if self.rect.x < -60 or self.rect.x > RESOLUTION_X + 60 or self.rect.y < -60 or self.rect.y > RESOLUTION_Y + 60 :
			self.kill()
