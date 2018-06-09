import math
from math import sqrt
import pyglet
from random import randrange
import random


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

ACCELERATION = 70
ROTATION_SPEED = 90

ENEMIES_SPEED = 60
ENEMIES_ROTATION_SPEED = 4

LASER_SPEED = 100
GUMMI_BEAR_SPEED = 120

pressed_keys = set()
batch = pyglet.graphics.Batch()
objects = []


def pic_load(pic_name):
	'''Function for loading images and setting anchor to the middle.'''
	picture = pyglet.image.load(pic_name)
	picture.anchor_x = picture.width // 2
	picture.anchor_y = picture.height // 2
	return picture
	
def radius_calc(name):
	'''Function for calculating a radius of circumscribed circle around a rectangle. '''
	pic = pyglet.image.load(name)
	rad = sqrt(((pic.width/2)**2)+((pic.width/2)**2))
	return rad
	
spaceship_pic = pic_load('puddle_jumper.png')

asteroids_pic = {1 : pic_load('wrejti.png'), 
						2: pic_load('oraji.png'), 
						3: pic_load('hatak.png'), 
						4: pic_load('hatak2.png')}

laser_pic = pic_load('fire.png')						

gummibear_pics = (pic_load('gummibear_red.png'), pic_load('gummi_bear_yellow.png'), pic_load('gummi_bear_green.png'))

mess_pic = pic_load('deadspaceshipmess.png')

SPACESHIP_RADIUS = radius_calc('puddle_jumper.png')

ENEMY_RADIUS = {
    1: radius_calc('wrejti.png'),
    2: radius_calc('oraji.png'),
    3: radius_calc('hatak.png'),
    4: radius_calc('hatak2.png'),
}

laser_rad = radius_calc('fire.png')

gummibear_rad = radius_calc('gummibear_red.png')

mess_rad = radius_calc('deadspaceshipmess.png')

class SpaceObject:
	'''The 'main' class. From this class inherits all others classes. '''
	def __init__(self, window, picture, radius, x, y, speed_x = 0, speed_y = 0, rotation = 0):
		self.sprite = pyglet.sprite.Sprite(picture, batch = batch)
		self.sprite.x = x
		self.sprite.y = y
		self.radius = radius
		self.speed_x = speed_x
		self.speed_y = speed_y
		self.rotation = rotation
		self.window = window
		

	def tick(self, dt):
		'''Method tick. It reply for moving.'''
		self.sprite.x = self.sprite.x + dt * self.speed_x
		self.sprite.y = self.sprite.y + dt * self.speed_y		
				
		if self.sprite.x < 0:
			self.sprite.x = self.sprite.x + self.window.width
		if self.sprite.y < 0:
			self.sprite.y = self.sprite.y + self.window.height
		if self.sprite.x > self.window.width:
			self.sprite.x = self.sprite.x - self.window.width
		if self.sprite.y > self.window.height:
			self.sprite.y = self.sprite.y - self.window.height
		
		self.sprite.rotation = 90 - self.rotation
		
	def hit_by_enemy(self, spaceship):
		'''Method hit_by_enemy is used in other class.'''
		return None
		
	def hit_by_laser(self, enemies):
		'''Method hit_by_laser is used in other class.'''
		return None
		
	def hit_by_gummibear(self, enemies):
		'''Method hit_by_gummibear is used in other class.'''
		return None
		
	def delete(self):
		'''Method for deleting object after colision.'''
		objects.remove(self)
		self.sprite.delete()

		
class Spaceship(SpaceObject):
	'''Class Spaceship. Inherits from Spaceobject, creates players ship.'''
	def __init__(self, window, rotation = 90):
		self.time = 0
		

		super().__init__(window = window, 
								picture = spaceship_pic, 
								x = window.width / 2,
								y = window.height * 1/4,
								radius = SPACESHIP_RADIUS,
								speed_x = 0,
								speed_y = 0,
								rotation = rotation
							)

							
	def tick(self, dt):
		self.time = self.time - 1*dt

		
		if pyglet.window.key.LEFT in pressed_keys:
			self.rotation = self.rotation + dt * ROTATION_SPEED
		if pyglet.window.key.RIGHT in pressed_keys:
			self.rotation = self.rotation - dt * ROTATION_SPEED
		if pyglet.window.key.UP in pressed_keys:
			self.speed_x = self.speed_x + dt * ACCELERATION * math.cos(math.radians(self.rotation))
			self.speed_y = self.speed_y + dt * ACCELERATION * math.sin(math.radians(self.rotation))
		if pyglet.window.key.DOWN in pressed_keys:
			self.speed_x = self.speed_x - dt * ACCELERATION * math.cos(math.radians(self.rotation))
			self.speed_y = self.speed_y - dt * ACCELERATION * math.sin(math.radians(self.rotation))
		if pyglet.window.key.SPACE in pressed_keys:
			if self.time <= 0:
				self.kill_enemy()
				self.time = 0.3
		if pyglet.window.key.G in pressed_keys:
			if self.time <= 0:
				self.gummi_bear_attack()
				self.time = 0.3
				
		super().tick(dt)
		
		for thing in objects:
			overlap = overlaps(self, thing)
			if overlap == True:
				thing.hit_by_enemy(self)

 
	def kill_enemy(self):
		'''Method create object Laser and put it into objects[].'''
		weapon = Laser(self.window, rotation = self.rotation,
                      x = self.sprite.x, y = self.sprite.y,
                      speed_x_ship = self.speed_x, speed_y_ship = self.speed_y,)
                      
		objects.append(weapon)
		
	def gummi_bear_attack(self):
		'''Method create object GummieBearAttack and put it into objects[].'''
		gummi = GummiBearAttack(self.window, rotation = self.rotation, 
                      x = self.sprite.x, y = self.sprite.y,
                      speed_x_ship = self.speed_x, speed_y_ship = self.speed_y,)
                      
		objects.append(gummi)

	
class Enemies(SpaceObject):
	'''Class Enemies. Inherits from Spaceobject, creates enemies ships.'''
	def __init__(self, window, enemies_type, rotation_speed):			
		site = random.choice(['right', 'up'])
		self.rotation_speed = rotation_speed
		
		
		if enemies_type == 1 or enemies_type == 2:
			if site == 'right':
				x = window.width
				y = randrange(0, window.height)
				rotation = int(random.choice(['180', '0']))
				if rotation == 180:
					speed_x = randrange(-ENEMIES_SPEED, -10)
					speed_y = randrange(-ENEMIES_SPEED, -10)
				else:
					speed_x = randrange(10, ENEMIES_SPEED)
					speed_y = randrange(10, ENEMIES_SPEED)
			
			elif site == 'up':
				x = randrange(0, window.width)
				y = 0
				rotation = int(random.choice(['270', '90']))
				if rotation == 270:
					speed_x = randrange(-ENEMIES_SPEED, -10)
					speed_y = randrange(-ENEMIES_SPEED, -10)
				else:
					speed_x = randrange(10, ENEMIES_SPEED)
					speed_y = randrange(10, ENEMIES_SPEED)
			
		elif enemies_type == 3 or enemies_type == 4:
			rotation = randrange(0, 360)
			if site == 'right':
				x = window.width
				y = randrange(0, window.height)	
				speed_x = randrange(-ENEMIES_SPEED, ENEMIES_SPEED)
				speed_y = randrange(-ENEMIES_SPEED, ENEMIES_SPEED)

			elif site == 'up':
				x = randrange(0, window.width)
				y = window.height
				speed_x = randrange(-ENEMIES_SPEED, ENEMIES_SPEED)
				speed_y = randrange(-ENEMIES_SPEED, ENEMIES_SPEED)
				
		super().__init__(window = window, 
								picture = asteroids_pic[enemies_type], 
								x = x, 
								y = y, 
								speed_x = speed_x,
								speed_y = speed_y,
								radius = ENEMY_RADIUS[enemies_type],
								rotation = rotation,
                        )

			
	
	def tick(self, dt):
	'''Method for moving of enemies. For cycle to control distance between 
		enemy and laser or gummibear. '''
		self.rotation = self.rotation + self.rotation_speed
		super().tick(dt)
		
		for obj in objects:
			overlap = overlaps(self, obj)
			if overlap == True:
				obj.hit_by_laser(self)
				obj.hit_by_gummibear(self)


	def hit_by_enemy(self, spaceship):
		spaceship.delete()
		self.dead_spaceship()
	
	def dead_spaceship(self):
		mess = DeadSpaceshipMess(self.window, 
											x = self.sprite.x, 
											y = self.sprite.y, 
											speed_x = 0, 
											speed_y = 0, 
											rotation = 0, 
											radius = 0)
		objects.append(mess)
		
		
	def slower(self):
		self.speed_x = self.speed_x / 2
		self.speed_y = self.speed_y / 2
		
		
class Laser(SpaceObject):
	def __init__(self, window, x, y, speed_x_ship, speed_y_ship, rotation = 0):
		self.bonsaj = 5
		speed_x = speed_x_ship + LASER_SPEED * math.cos(math.radians(rotation))
		speed_y = speed_y_ship + LASER_SPEED * math.sin(math.radians(rotation))
		super().__init__(window, 
								x = x + math.cos(math.radians(rotation)), 
								y = y + math.sin(math.radians(rotation)), 
								speed_x = speed_x,
								speed_y = speed_y,
								rotation = rotation, 
								picture = laser_pic, 
								radius = laser_rad,)
	
	def tick(self, dt):
		super().tick(dt)
		self.bonsaj = self.bonsaj - 1*dt
		if self.bonsaj < 0:
			self.delete()

	def hit_by_laser(self, enemies):
		enemies.delete()
		self.delete()
		

class GummiBearAttack(SpaceObject):
	def __init__(self, window, x, y, speed_x_ship, speed_y_ship, rotation = 0):
		self.bonsaj = 3
		speed_x = speed_x_ship + GUMMI_BEAR_SPEED * math.cos(math.radians(rotation))
		speed_y = speed_y_ship + GUMMI_BEAR_SPEED * math.sin(math.radians(rotation))
		super().__init__(window, 
								x=x + math.cos(math.radians(rotation)), 
								y=y + math.sin(math.radians(rotation)), 
								speed_x=speed_x,
								speed_y=speed_y,
								rotation=rotation, 
								picture=random.choice(gummibear_pics), 
								radius=gummibear_rad,)
	
	def tick(self, dt):
		super().tick(dt)
		self.bonsaj = self.bonsaj - 1*dt
		if self.bonsaj < 0:
			self.delete()

			
	def hit_by_gummibear(self, enemies):
		enemies.slower()
		self.delete()
		

class DeadSpaceshipMess(SpaceObject):
	def __init__(self, window, x, y, speed_x, speed_y, rotation, radius):
		self.radius = 5
		self.bonsaj = 1

		super().__init__(window, 
								x = x, y = y, 
								speed_x = speed_x,
								speed_y = speed_y,
								rotation = rotation,
								picture = mess_pic,
								radius = radius)

	def tick(self,dt):
		self.bonsaj = self.bonsaj - 1*dt
		if self.bonsaj <= 0:
			self.delete()

	
def tick(dt):
	for thing in objects:
		thing.tick(dt)

def draw():
    window.clear()
    batch.draw()
    
def distance(a, b, wrap_size):
    """Distance in one direction (x or y)"""
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result

def overlaps(a, b):
    """Returns true iff two space objects overlap"""
    distance_squared = (distance(a.sprite.x, b.sprite.x, window.width) ** 2 +
                        distance(a.sprite.y, b.sprite.y, window.height) ** 2)
    max_distance_squared = (a.radius + b.radius) ** 2
    return distance_squared < max_distance_squared

    
def key_pressed(key, modifiers):
    pressed_keys.add(key)

def key_released(key, modifiers):
    pressed_keys.discard(key)    

window = pyglet.window.Window(caption = 'Stargejt asteroids', width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

window.push_handlers(
    on_draw=draw,
    on_key_press=key_pressed,
    on_key_release=key_released,
)

pyglet.clock.schedule(tick)

objects.append(Spaceship(window))
	
objects.append(Enemies(window, 1, 0))
objects.append(Enemies(window, 2, 0))
objects.append(Enemies(window, 3, randrange(-ENEMIES_ROTATION_SPEED, ENEMIES_ROTATION_SPEED)))
objects.append(Enemies(window, 4, randrange(-ENEMIES_ROTATION_SPEED, ENEMIES_ROTATION_SPEED)))
	
pyglet.app.run()

