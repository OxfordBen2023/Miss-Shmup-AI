import pygame
import torch
from model import Linear_Qnet
import numpy as np

from pygame.math import Vector2 as Vector
import random
from sys import exit

from src.Player import Player
from src.Enemy import *
from src.Bullet import Bullet
from src.Impact import Impact
from src.Config import *

#REWARDS
# Die by collision -50
# Kill enemy +10
# Max the game +50
# score 4/5 ==> +5
# score < 4 ==> -10


SPEED = 100
ACTION_SPEED = 2


class GameAI:
	def __init__(self, auto_play = False):
		pygame.init()
		self.auto_play = auto_play
		self.toggle = False
		self.screen = pygame.display.set_mode((RESOLUTION_X,RESOLUTION_Y))
		pygame.display.set_caption('Miss Shmup')
		self.sky_surface = pygame.image.load('assets/graphics/starSky.png').convert()
		self.reward = 0
		self.score = 0
		self.count = 0
		self.clock = pygame.time.Clock()
		self.startTime = 0
		self.chrono = 0
		self.reinit()
		self.model = Linear_Qnet(6 , 256 , 5)
		self.model.load(file_path='model/model.pth')
		self.best_move = 'idle'

	def reinit(self):
		self.score = 0
		self.startTime = pygame.time.get_ticks()		
		self.player_single_grp = pygame.sprite.GroupSingle()
		self.player = Player()
		self.player_single_grp.add(self.player)
		self.bullet_group = pygame.sprite.Group()
		self.enemy_group = pygame.sprite.Group()
		self.impact_group = pygame.sprite.Group()
		for _ in range(5):
			enemy_speed = 1 + random.random()
			spawn_x = random.randint(600,760)
			spawn_y = random.randint(50,350)
			dir_x = random.uniform(.7,1.2)
			dir_y = random.uniform(-.1,.1)
			self.enemy_group.add(Enemy((spawn_x,spawn_y),(dir_x, dir_y), enemy_speed*ACTION_SPEED))
		self.block_hit_list = []
		
	# returns the distance of a collision with a given enemy. On a given square.
	def line_collision(self, enemy, x_offset, y_offset, width, height, draw=True):

		# For optimisation, border detection test runs first.
		if (self.player.rect.right < 0 or 
		self.player.rect.left > RESOLUTION_X or
		self.player.rect.top < 0 or 
		self.player.rect.bottom > RESOLUTION_Y):
			return -1

		# Compute starting place of ray casting:
		direction = Vector(enemy.direction).normalize()
		en_x = enemy.rect.right if direction[0] <= 0  else enemy.rect.left
		en_y = enemy.rect.top if direction[1] >= 0  else enemy.rect.bottom
		# centralise better if angle is low:
		if abs(direction[1])<0.3:
			en_y = enemy.rect.centery
		if abs(direction[0])<0.3:
			en_x = enemy.rect.centerx			
		enemy_center = Vector(en_x, en_y)

		end_line = enemy_center - 1000 * direction
		test_x = self.player.rect.centerx + x_offset
		test_y = self.player.rect.centery + y_offset
		test_rect = pygame.Rect(test_x-width/2,test_y-height/2, width,height)

		collision_points = test_rect.clipline (enemy_center, end_line)
		if test_rect.colliderect(enemy):
			return -1
		
		if draw:
			pygame.draw.rect(self.screen, 'green', test_rect, 1)
		if collision_points:
			if draw:
				pygame.draw.line(self.screen, 'red', enemy_center, collision_points[0], 1)
			return Vector(enemy_center - collision_points[0]).length()

		else: return []
	
	# danger level computation for a given square.
	def danger_level(self, direction, samples, offset, width, height, draw=True):
		# compute_border_danger
		pos = Vector(self.player.rect.centerx + direction[0], self.player.rect.centery + direction[1])
		closest_boundary = min([pos[0], pos[1], RESOLUTION_X-pos[0], RESOLUTION_Y-pos[1]])
		treshold_dist = 50
		if closest_boundary > treshold_dist:
			closest_boundary = treshold_dist
		danger = ((treshold_dist - closest_boundary) / treshold_dist ) * 1.5

		# Add enemy danger
		dist_treshold = 200
		for x in range(samples):
			for enemy in self.enemy_group:
				dist = self.line_collision(enemy, direction[0]*(x+offset), direction[1]*(x+offset), width, height, draw)
				if dist:
					if dist > dist_treshold: 
						dist = dist_treshold
					danger += (dist_treshold - dist)/dist_treshold
					if dist < 0:
						danger += 2
		return danger

	def new_spawn(self):
			enemy_speed = 1 + random.random()
			spawn_x = random.randint(-60,RESOLUTION_X+60)
			spawn_y = random.randint(-60,RESOLUTION_Y+60)
			# stick spawning on a border
			borderise = random.randint(0,3)
			if borderise == 0 :
				spawn_x  = -40
			elif borderise == 1:
				spawn_x = RESOLUTION_X +40
			elif borderise == 2:
				spawn_y = -40
			else:
				spawn_y = RESOLUTION_Y +40

			# Aim at ship
			direction = Vector(spawn_x - self.player.rect.centerx, spawn_y - self.player.rect.centery)
			direction = direction.normalize()
			
			dir_x = direction[0]
			dir_y = direction[1]
			self.enemy_group.add(Enemy((spawn_x,spawn_y),(dir_x, dir_y), enemy_speed*ACTION_SPEED))

	def is_bullet(self):
		ship_hight = self.player.rect.center[1]
		is_bullet_right = False
		for bullet in self.bullet_group:
			top_enemy = bullet.rect.y
			down_enemy = bullet.rect.bottom
			if ship_hight > top_enemy and ship_hight < down_enemy:
				is_bullet_right = True
		return True if is_bullet_right else False

	def auto_fire(self):
		ship_hight = self.player.rect.center[1]
		ship_nose = self.player.rect.right
		can_hit = False
		for enemy in self.enemy_group:
			top_enemy = enemy.rect.y
			down_enemy = enemy.rect.bottom
			front_enemy = enemy.rect.left
			if ship_hight > top_enemy and ship_hight < down_enemy and ship_nose + 2 < front_enemy:
				can_hit = True
		return True if can_hit else False
	
	# returns the states for the angent. (Also used in the game, when using robot-play)
	def game_state(self):
		player_y = self.player.rect.center[1]
		player_nose = self.player.rect.right
		state = []
		up = 0
		down = 0

		for enemy in self.enemy_group:
			if enemy.rect.y > player_y and enemy.rect.left > player_nose:
				down += 1
			elif enemy.rect.y < player_y and enemy.rect.left > player_nose:
				up +=1

		state.append(int(self.auto_fire()))

		self.best_move = self.automatic_play(draw=False)  
		state.append(1 if self.best_move == 'up' else 0)
		state.append(1 if self.best_move == 'down' else 0)
		state.append(1 if self.best_move == 'right' else 0)
		state.append(1 if self.best_move == 'left' else 0)
		state.append(1 if self.best_move == 'idle' else 0)
		
		return np.array(state, dtype=int)
	
	def player_input(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if	event.type == pygame.KEYDOWN :
				if event.key == pygame.K_SPACE :
					self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))
				if event.key == pygame.K_ESCAPE or event.key == pygame.K_m :
					self.toggle = True
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP] and self.player.rect.y > 0:
			self.player.rect.y -= 4
		if keys[pygame.K_DOWN] and self.player.rect.bottom < RESOLUTION_Y:
			self.player.rect.y += 4
		if keys[pygame.K_RIGHT] and self.player.rect.right < RESOLUTION_X:
			self.player.rect.x += 4
		if keys[pygame.K_LEFT] and self.player.rect.x > 0:
			self.player.rect.x -= 4
		if keys[pygame.K_x]:
			final_move = [0,0,0,0,0]
			state0 = torch.tensor(self.game_state(), dtype = torch.float)
			prediction = self.model(state0)
			print(prediction)
			move = torch.argmax(prediction).item()
			print(move)
			final_move[move]=1
			self.ai_input(final_move)

	def ai_input(self, action):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		if action == [1,0,0,0,0] and self.player.rect.y > 0:
			self.player.rect.y -= 4*ACTION_SPEED
		if action == [0,1,0,0,0] and self.player.rect.bottom < RESOLUTION_Y:
			self.player.rect.y += 4*ACTION_SPEED
		if action == [0,0,1,0,0] and self.player.rect.right < RESOLUTION_X:
			self.player.rect.x += 4*ACTION_SPEED
		if action == [0,0,0,1,0] and self.player.rect.x > 0:
			self.player.rect.x -= 4*ACTION_SPEED
		if action == [0,0,0,0,1]:
			self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))

	def move_by_direction(self, direction):
		# UP
		if direction == 'up':
			self.player.rect.y -= 4*ACTION_SPEED
		# DOWN
		elif direction == 'down':
			self.player.rect.y += 4*ACTION_SPEED
		# RIGHT
		elif  direction == 'right':
			self.player.rect.x += 4*ACTION_SPEED
		# LEFT
		elif  direction == 'left':
			self.player.rect.x -= 4*ACTION_SPEED
		else:
			pass #self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))
	
	# return the main direction of a vector between +X, -X, +Y and -Y (best_move). And the next best direction (side_move)
	def vector_to_directions(self, vector):
		if abs(vector[0])<abs(vector[1]):
			best_move = 'up' if vector[1] <= 0 else 'down'
			sideway_move = 'left' if vector[0] <= 0 else 'right'
		else:
			best_move = 'left' if vector[0] <= 0 else 'right'
			sideway_move = 'up' if vector[1] <= 0 else 'down'
		return best_move, sideway_move

	# 'manual' artificial intelligence for enemy dodging, returns the best computed direction.
	def automatic_play(self, draw=True):
		w = self.player.rect.width
		h = self.player.rect.height
		danger_dict = {
 			"idle": self.danger_level((0,0) , 1 , 1, w*1.1, h*1.1, draw),
  			"right": self.danger_level((60,0) , 1 , 1, w/2, h*1.2, draw),
			"left": self.danger_level((-60,0) , 1 , 1, w/2, h*1.2 ,draw),
			"up" : self.danger_level((0,-30) , 1 , 1, w, h*1, draw),
			"down": self.danger_level((0,30) , 1 , 1, w, h*1, draw),
			"up_right_corner": self.danger_level((50,-30) , 1 , 1, w*.3, h, draw),
			"up_left_corner": self.danger_level((-50,-30) , 1 , 1, w*.3, h, draw),
			"down_right_corner": self.danger_level((50,30) , 1 , 1, w*.3, h, draw),
			"down_left_corner": self.danger_level((-50,30) , 1 , 1, w*.3, h, draw),
				}
		minimum = min(danger_dict.values())
		possible_moves = ['idle', 'up', 'down','right','left']
		good_moves = [k for k, v in danger_dict.items() if v == minimum]
		good_moves = [v for v in good_moves if v in possible_moves]

		gradient_direction_x = (
			danger_dict.get("left")
		+ 0.5* danger_dict.get("up_left_corner")
		+ 0.5* danger_dict.get("down_left_corner")
		-danger_dict.get("right")
		- 0.5*danger_dict.get("up_right_corner")
		- 0.5*danger_dict.get("down_right_corner")
		)

		gradient_direction_y = ( 
			danger_dict.get("up")
			+ 0.5* danger_dict.get("up_left_corner")
			+ 0.5* danger_dict.get("up_right_corner")
			- danger_dict.get("down")
			- 0.5*danger_dict.get("down_right_corner")
			- 0.5*danger_dict.get("down_left_corner")
		)
		p_center = Vector(self.player.rect.centerx, self.player.rect.centery)
		escape_vector = Vector( gradient_direction_x*50, gradient_direction_y*50)

		if draw:
			pygame.draw.line(self.screen, 'yellow', p_center, p_center+escape_vector , 8)

		# If danger is low, go back to the safest space on the screen.
		if escape_vector.length() < 7:
			safe_space = Vector(200, 200)
			to_safe_space = Vector(safe_space[0]-self.player.rect.centerx, safe_space[1]-self.player.rect.centery)
			if draw:
				pygame.draw.line(self.screen, 'green', safe_space, (self.player.rect.centerx, self.player.rect.centery), 2 )

			best_move, _ = self.vector_to_directions(to_safe_space)

			if to_safe_space.length() < 5:
				best_move = 'idle'
			return best_move

		# Normal avoidance based on least danger
		else:
			best_move, sideway_move = self.vector_to_directions(escape_vector)
			# Test if not 'framed' between ennemys or borders
			if danger_dict.get(best_move)>.9 and danger_dict.get(best_move) > danger_dict.get(sideway_move):
				best_move = sideway_move
			return best_move


	def run(self, action, training = False): 
		self.screen.blit(self.sky_surface,(0,0))
		reward = 0
		done = False
		# Should be optimised (Too many call of the automatic-play method) :
		if training:
			p_pos_before = Vector(self.player.rect.center)
			self.ai_input(action)
			p_pos_after = Vector(self.player.rect.center)

		if not training:
			self.player_input()
			if self.auto_play == True:
				self.move_by_direction(self.automatic_play(draw=True))


		#Collision of player bullet with ennemies.
		for bullet in self.bullet_group:
			self.block_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_group, True)
			if self.block_hit_list:
				bullet.kill()
				reward = 10
				self.score += 1
				self.impact_group.add(Impact(self.block_hit_list[0].rect.center))

		if training:
			# Rewards if follow the spoon feeded avoidance
			has_moved = self.vector_to_directions( p_pos_after - p_pos_before )[0]
			if has_moved == self.best_move:
				reward += 5

		
		#Collision of ennemies with the player
		for enemy in self.enemy_group:
			hit = pygame.sprite.spritecollide(enemy, self.player_single_grp, True)
			if hit:
				print("GAME OVER")
				self.toggle = True
				reward = -10
				done = True
				return reward, self.score, done
		# Infinite respawn
		if len(self.enemy_group)<4:
			self.new_spawn()
		
			
		self.enemy_group.draw(self.screen)
		self.bullet_group.draw(self.screen)
		self.impact_group.draw(self.screen)
		self.player_single_grp.draw(self.screen)

		self.player.update()
		self.enemy_group.update()
		self.bullet_group.update()
		self.impact_group.update()

		self.clock.tick(SPEED)

		# self.chrono is not used as now.
		self.chrono = pygame.time.get_ticks()-self.startTime
		pygame.display.update()

		return reward, self.score, done
