import pygame
from pygame.math import Vector2 as Vector
import random
from sys import exit

from src.Player import Player
from src.Enemy import *
from src.Bullet import Bullet
from src.Impact import Impact
from src.Config import *

#REWARDS
# Die by collision 0 (to implement better later)
# Kill enemy +10
# Max the game +50
# score 4/5 ==> +5
# score < 4 ==> -10

# ACTION
# Move up
# Move down
# fire

# STATES
# has enemy in fire line > function autofire
# how many targatable enemy up
# how many targatable enemy down

# STATES TO IMPLEMENT
# is danger up
# is danger down
# target killed (score)
# missed target

SPEED = 100
DURATION = 800000/SPEED
# Duration was used to end the game. Now reinit arrives only by deah or if len(enemys)==0.
ACTION_SPEED = 2


class GameAI:
	def __init__(self):
		pygame.init()
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

	# return witch direction to go regarding the target
	def get_to_target(self, target_x, target_y, width, height):
		p_pos = self.player.rect.center
		moove_list = []
		if p_pos[0] < target_x:
			moove_list.append("right")
		elif p_pos[0]>target_x + width:
			moove_list.append("left")
		if p_pos[1] < target_y:
			moove_list.append("down")
		elif p_pos[1] > target_y + height:
			moove_list.append("up")
		if len(moove_list) == 0:
			moove_list.append("idle")
		if not "up" in moove_list and not 'down' in moove_list:
			moove_list.append("up")
			moove_list.append("down")
		if not "right" in moove_list and not 'left' in moove_list:
			moove_list.append("right")
			moove_list.append("left")
		color = 'blue' if moove_list[0] == 'idle' else 'brown'
		pygame.draw.rect(self.screen, color, pygame.Rect(target_x, target_y, width, height), 1)
		return moove_list
	
	def to_target(self, target_x, target_y, width, height):
		reward = 0
		p_pos = self.player.rect.center
		if p_pos[0] > target_x and p_pos[0]<target_x + width and p_pos[1] > target_y and p_pos[1] < target_y + height:
			reward = 1
		pygame.draw.rect(self.screen, 'blue', pygame.Rect(target_x, target_y, width, height), 1)
		return True if reward > 0 else False 
	
	# returns the distance of a collision with an enemy. with ofset from player position and custom width and height.
	def line_collision(self, enemy, x_offset, y_offset, width, height):

		# Compute starting place of ray casting 
		direction = Vector(enemy.direction).normalize()
		en_x = enemy.rect.right if direction[0] <= 0  else enemy.rect.left
		en_y = enemy.rect.top if direction[1] >= 0  else enemy.rect.bottom
		# centralise better is angle is low
		if abs(direction[1])<0.3:
			en_y = enemy.rect.centery
		if abs(direction[0])<0.3:
			en_x = enemy.rect.centerx			
		enemy_center = Vector(en_x, en_y)

		end_line = enemy_center - 1000 * direction
		speed = enemy.speed

		test_x = self.player.rect.centerx + x_offset
		test_y = self.player.rect.centery + y_offset
		test_rect = pygame.Rect(test_x-width/2,test_y-height/2, width,height)

		if (self.player.rect.right < 0 or 
	  		self.player.rect.left > RESOLUTION_X or
			self.player.rect.top < 0 or 
			self.player.rect.bottom > RESOLUTION_Y):
			return -1
		collision_points = test_rect.clipline (enemy_center, end_line)
		if test_rect.colliderect(enemy):
			return -1
		
		pygame.draw.rect(self.screen, 'green', test_rect, 1)
		if collision_points:
			pygame.draw.line(self.screen, 'red', enemy_center, collision_points[0], 1)
			return Vector(enemy_center - collision_points[0]).length()

		else: return []
		
	def danger_level(self, direction, samples, offset, width, height):

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
				dist = self.line_collision(enemy, direction[0]*(x+offset), direction[1]*(x+offset), width, height)
				if dist:
					if dist > dist_treshold: 
						dist = dist_treshold
					danger += (dist_treshold - dist)/dist_treshold
					if dist < 0:
						danger += 2
		return danger




	def reinit(self):
		self.score = 0
		self.startTime = pygame.time.get_ticks()		
		self.player_single_grp = pygame.sprite.GroupSingle()
		self.player = Player()
		self.player_single_grp.add(self.player)
		self.bullet_group = pygame.sprite.Group()
		self.enemy_group = pygame.sprite.Group()
		self.impact_group = pygame.sprite.Group()
		for x in range(5):
			enemy_speed = 1 + random.random()
			spawn_x = random.randint(600,760)
			spawn_y = random.randint(50,350)
			dir_x = random.uniform(.7,1.2)
			dir_y = random.uniform(-.1,.1)
			self.enemy_group.add(Enemy((spawn_x,spawn_y),(dir_x, dir_y), enemy_speed*ACTION_SPEED))
		self.block_hit_list = []

	# NOT USED rough attempt to sample the place with the less enemy on a simple grid
	def target(self):
		target_col = 3
		target_lin = 2
		x_spacing = RESOLUTION_X / target_col
		y_spacing = RESOLUTION_Y / target_lin
		target_list = []
		for x in range(target_col):
			for y in range(target_lin):
				target_list.append((x_spacing*(0.5+x),y_spacing*(0.5+y)))
		best_target_dist = 0
		best_index = 0
		for index, target in enumerate(target_list):
			max_distance = 0
			for enemy in self.enemy_group:
				dif = Vector(target)-Vector(enemy.rect.center)
				distance = dif.length()
				if distance > max_distance:
					max_distance = distance
			if max_distance > best_target_dist:
				best_target_dist = max_distance
				best_index = index
		return target_list[best_index]

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
	
	def player_input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP] and self.player.rect.y > 0:
			self.player.rect.y -= 4
		if keys[pygame.K_DOWN] and self.player.rect.bottom < RESOLUTION_Y:
			self.player.rect.y += 4
		if keys[pygame.K_RIGHT] and self.player.rect.right < RESOLUTION_X:
			self.player.rect.x += 4
		if keys[pygame.K_LEFT] and self.player.rect.x > 0:
			self.player.rect.x -= 4

	def ai_input(self, action):
		if action == [1,0,0,0,0] and self.player.rect.y > 0:
			self.player.rect.y -= 4*ACTION_SPEED
		if action == [0,1,0,0,0] and self.player.rect.bottom < RESOLUTION_Y:
			self.player.rect.y += 4*ACTION_SPEED
		if action == [0,0,1,0,0] and self.player.rect.right < RESOLUTION_X:
			self.player.rect.x += 4*ACTION_SPEED
		if action == [0,0,0,1,0] and self.player.rect.x > 0:
			self.player.rect.x -= 4*ACTION_SPEED
		if action == [0,0,0,0,1]:
			pass #self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))

	def automatic_play(self):
		w = self.player.rect.width
		h = self.player.rect.height
		danger_dict = {
 			"idle": self.danger_level((0,0) , 1 , 1, w*1.1, h*1.1),
  			"right": self.danger_level((60,0) , 1 , 1, w/2, h*1.2),
			"left": self.danger_level((-60,0) , 1 , 1, w/2, h*1.2),
			"up" : self.danger_level((0,-30) , 1 , 1, w, h*1),
			"down": self.danger_level((0,30) , 1 , 1, w, h*1),
			"up_right_corner": self.danger_level((50,-30) , 1 , 1, w*.3, h),
			"up_left_corner": self.danger_level((-50,-30) , 1 , 1, w*.3, h),
			"down_right_corner": self.danger_level((50,30) , 1 , 1, w*.3, h),
			"down_left_corner": self.danger_level((-50,30) , 1 , 1, w*.3, h),
				}
		print(danger_dict)
		minimum = min(danger_dict.values())
		danger_level = sum(danger_dict.values())
		possible_moves = ['idle', 'up', 'down','right','left']
		good_moves = [k for k, v in danger_dict.items() if v == minimum]
		good_moves = [v for v in good_moves if v in possible_moves]
		print(f"good moves: {good_moves}")

		# pushed right by the left danger and by the 'safey' of the right side.
		gradient_direction_x = (
			danger_dict.get("left")
		+ 0.5* danger_dict.get("up_left_corner")
		+ 0.5* danger_dict.get("down_left_corner")
		-danger_dict.get("right")
		- 0.5*danger_dict.get("up_right_corner")
		- 0.5*danger_dict.get("down_right_corner")
		)

		# pushed down by the up danger and by the 'safey' of the down side.
		gradient_direction_y = ( 
			danger_dict.get("up")
			+ 0.5* danger_dict.get("up_left_corner")
			+ 0.5* danger_dict.get("up_right_corner")
			- danger_dict.get("down")
			- 0.5*danger_dict.get("down_right_corner")
			- 0.5*danger_dict.get("down_left_corner")
		)
		p_center = Vector(self.player.rect.centerx, self.player.rect.centery)
		vector = Vector( gradient_direction_x*50, gradient_direction_y*50)
		color = 'blue' if vector.length() < 10 else 'red'
		pygame.draw.line(self.screen, color, p_center, p_center+vector , 8)

		if vector.length() < 5:
			#Idle, (or go back in a safe space, or kill)
			safe_space = Vector(200, 200)
			to_safe_space = Vector(safe_space[0]-self.player.rect.centerx, safe_space[1]-self.player.rect.centery)
			pygame.draw.line(self.screen, 'green', safe_space, (self.player.rect.centerx, self.player.rect.centery), 2 )
			if to_safe_space[0]<to_safe_space[1]:
				best_move = 'up' if to_safe_space[1] <= 0 else 'down'
			else:
				best_move = 'left' if to_safe_space[0] <= 0 else 'right'			
			if to_safe_space.length() < 5:
				pass #idle
			else:
				# UP
				if best_move == 'up':
					self.player.rect.y -= 4*ACTION_SPEED
				# DOWN
				elif best_move == 'down':
					self.player.rect.y += 4*ACTION_SPEED
				# RIGHT
				elif  best_move == 'right':
					self.player.rect.x += 4*ACTION_SPEED
				# LEFT
				elif  best_move == 'left':
					self.player.rect.x -= 4*ACTION_SPEED
				else:
					pass #self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))
		else:
			if abs(vector[0])<abs(vector[1]):
				best_move = 'up' if vector[1] <= 0 else 'down'
				sideway_move = 'left' if vector[0] <= 0 else 'right'
			else:
				best_move = 'left' if vector[0] <= 0 else 'right'
				sideway_move = 'up' if vector[1] <= 0 else 'down'

			# Test if not 'framed' between ennemys or borders
			if danger_dict.get(best_move)>.9 and danger_dict.get(best_move) > danger_dict.get(sideway_move):
				best_move = sideway_move

			# UP
			if best_move == 'up':
				self.player.rect.y -= 4*ACTION_SPEED
			# DOWN
			elif best_move == 'down':
				self.player.rect.y += 4*ACTION_SPEED
			# RIGHT
			elif  best_move == 'right':
				self.player.rect.x += 4*ACTION_SPEED
			# LEFT
			elif  best_move == 'left':
				self.player.rect.x -= 4*ACTION_SPEED
			else:
				pass #self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))
	
	def run(self, action): 
		self.screen.blit(self.sky_surface,(0,0))
		reward = 0
		done = False
		self.ai_input(action)
		self.player_input()
		self.automatic_play()
		self.player.place_zones()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if	event.type == pygame.KEYDOWN :
				if event.key == pygame.K_SPACE :
					self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))


		#Collision of our bullet with ennemies.
		for bullet in self.bullet_group:
			self.block_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_group, True)
			if self.block_hit_list:
				bullet.kill()
				reward = 10
				self.score += 1
				self.impact_group.add(Impact(self.block_hit_list[0].rect.center))
		
		# reward center
		if self.to_target(150, 100, 500, 200):
			self.count += 1
			if self.count > 50:
				reward += 10
				self.count = 0
				self.score += 1

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


		#End game when player did not collide
		if len(self.enemy_group)==0:
			print("GAME OVER BY ALL ENEMIES OUT !")
			self.toggle = True
			if self.score == 5:
				reward = 50
			elif self.score == 4:
				reward = 5
			else:
				reward = -10
			done = True
			return reward, self.score, done
		
			
		self.enemy_group.draw(self.screen)
		self.bullet_group.draw(self.screen)
		self.impact_group.draw(self.screen)
		self.player_single_grp.draw(self.screen)
		self.player.collider_zones_group.draw(self.screen)



		self.player.update()
		self.enemy_group.update()
		self.bullet_group.update()
		self.impact_group.update()

		self.clock.tick(SPEED)
		# self.chrono is not used as now.
		self.chrono = pygame.time.get_ticks()-self.startTime
		pygame.display.update()

		return reward, self.score, done
