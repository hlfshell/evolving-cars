import pygame
vector = pygame.math.Vector2
from PIL import Image
import numpy as np
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
from .checkpoint import Checkpoint

im = Image.open('assets/car_sprite.png')
im = im.resize((28, 14))

CRASH = -200
CHECKPOINT = 100

class Car(pygame.sprite.Sprite):

    def __init__(
        self, id : str,
        position : (int, int),
        rotation : int = 0,
        color : (int, int, int) = None
        ):
        super().__init__()

        self._crashed = False

        self._id = id
        self._position = position
        self._rotation = rotation

        if color is None:
            color =  list(np.random.choice(range(256), size=3))
        # replace that car color of "white" with the chosen color
        imagedata = np.array(im)
        red, green, blue = imagedata[:,:,0], imagedata[:,:,1], imagedata[:,:,2]
        mask = (red > 250) & (green > 250) & (blue > 250)
        imagedata[:,:,:3][mask] = [color[0], color[1], color[2]]

        self._image_shape = (imagedata.shape[0:2][1], imagedata.shape[0:2][0])
        self._image_data = imagedata.astype('uint8')

        self.surf = pygame.image.frombuffer(self._image_data, self._image_shape, 'RGBA')
        self.image = self.surf
        self.rect = self.surf.get_rect(center = self._position)
    
        self._velocity = vector(0,0)
        self._acceleration = vector(0,0)

        self._score = 0

        self._checkpoints = {}

        self._distances = {}
        self._distance_endpoints = {}

    def get_center(self):
        return self._position

    def get_rotation(self):
        return self._rotation

    def move(self):
        if self._crashed:
            return
            
        acceleration = 0

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self._rotation += 1
        elif pressed_keys[K_RIGHT]:
            self._rotation += -1
        self._rotation = self._rotation % 360

        if pressed_keys[K_UP]:
            acceleration = 0.5
        elif pressed_keys[K_DOWN]:
            acceleration = -0.5
        else:
            current_magnitude = self._velocity.magnitude()
            deaccelerate = 0.05
            # if current_magnitude < 0:
            #     if current_magnitude + deaccelerate > 0:
            #         acceleration = -current_magnitude
            #     else:
            #         acceleration = deaccelerate
            # else:
            if current_magnitude - deaccelerate < 0:
                acceleration = -current_magnitude
            else:
                acceleration = -deaccelerate
            
        velocity_magnitude = self._velocity.magnitude() + acceleration
        if velocity_magnitude > 10:
            velocity_magnitude = 10

        rotation = -self._rotation
        # rotation = self._rotation

        self._velocity = vector(velocity_magnitude, 0).rotate(rotation)
        self._position += self._velocity

    def render(self):
        surface = pygame.image.frombuffer(self._image_data, self._image_shape, 'RGBA')
        self.surf = pygame.transform.rotate(surface, self._rotation)
        self.image = self.surf # This is obtuse but it's how mask collisions work
        self.rect = self.surf.get_rect(center = self._position)

    def crash(self):
        self._score += CRASH
        self._crashed = True

    def cross_checkpoint(self, checkpoint : Checkpoint):
        if checkpoint._id not in self._checkpoints:
            self._score += CHECKPOINT
            self._checkpoints[checkpoint._id] = True

    def add_distance(self, angle, end_point, distance):
        self._distance_endpoints[angle] = end_point
        self._distances[angle] = distance