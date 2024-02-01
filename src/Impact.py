from src.Config import *
import pygame

class Impact(pygame.sprite.Sprite):
	def __init__(self,emit):
		super().__init__()
		self.image = pygame.Surface([40, 40])
		self.image.fill((255,255,255))
		self.rect = self.image.get_rect(center = (emit))
		self.age = 0

	def update(self):
		self.destroy()
		self.age += 0.5

	def destroy(self):
		if self.rect.x < 0 or self.rect.x > RESOLUTION_X or self.rect.y < 0 or self.rect.y > RESOLUTION_Y :
			self.kill()
		if self.age > 1:
			self.kill()
