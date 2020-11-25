import pygame
from pygame.locals import *
from .car import Car
from .checkpoint import Checkpoint
from .track import Track
import math
from pygame.locals import K_d, K_RETURN

class Game:
    def __init__(self, trackname : str):
        self._running = True
        self._display_surface = None
        self._frame_per_sec = pygame.time.Clock()
        self._fps = 60

        self._cars : [Car] = pygame.sprite.Group()
        self._checkpoints : [Checkpoint] = []
        self._trackname = trackname
        self._tracksg = pygame.sprite.Group()
        self._car_spawn_position = None
        self._car_spawn_rotation = None

        self._show_checkpoints = False

    def add_car(self, car : Car):
        self._cars.add(car)

    def add_checkpoint(self, checkpoint : Checkpoint):
        self._checkpoints.add(checkpoint)

    def on_init(self):
        pygame.init()
        self._track = Track(self._trackname)
        self._tracksg.add(self._track)
        self._display_surface = pygame.display.set_mode(self._track.get_size())
        self._running = True
        pygame.display.set_caption("Car Game")

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        for car in self._cars:
            car.move()
            # Calculate if the car impacts
            trackCollions = pygame.sprite.spritecollide(car, self._tracksg, False, pygame.sprite.collide_mask)
            if len(trackCollions) > 0:
                car.crash()
            for checkpoint in self._checkpoints:
                if checkpoint.check_collision(car.rect):
                    car.cross_checkpoint(checkpoint)
            for angle in [-60, -30, 0, 30, 60]:
                endpoint, distance = self._track.distance_to_wall(car, angle)
                car.add_distance(angle, endpoint, distance)

    def on_render(self):
        self._display_surface.fill((69, 68, 67))
        self._display_surface.blit(self._track.surf, self._track.rect)
        for car in self._cars:
            car.render()
            self._display_surface.blit(car.surf, car.rect)
            
        if self._show_checkpoints:
            for checkpoint in self._checkpoints:
                checkpoint.draw(self._display_surface)
        pygame.display.update()
        self._frame_per_sec.tick(self._fps)

        # Draw each distance measuring line
        for car in self._cars:
            for angle in car._distance_endpoints:
                pygame.draw.line(self._display_surface, (0, 255, 0), car.get_center(), car._distance_endpoints[angle], width=1)

        pygame.display.update()

    def on_cleanup(self):
        pass

    def set_car_spawn(self):
        while(self._car_spawn_rotation is None):
            self.on_render()
            if self._car_spawn_position is not None:
                pygame.draw.line(self._display_surface, (255, 0, 0), self._car_spawn_position, pygame.mouse.get_pos(), width=3)
                pygame.display.update()
            for event in pygame.event.get():
                # self.on_event(event)
                left, _, _ = pygame.mouse.get_pressed()
                if left:
                    if self._car_spawn_position is None:
                        self._car_spawn_position = pygame.mouse.get_pos()
                    else:
                        # Figure out our rotation angle from the new point
                        point = pygame.mouse.get_pos()
                        radians = math.atan2(point[0]-self._car_spawn_position[0], point[1]-self._car_spawn_position[1])

                        self._car_spawn_rotation = math.degrees(radians) - 90

    def set_checkpoints(self):
        pressed_keys = pygame.key.get_pressed()
        checkpoint_start = None
        checkpoint_id = 0

        while(not pressed_keys[K_RETURN]):
            pressed_keys = pygame.key.get_pressed()
            self.on_render()
            for checkpoint in self._checkpoints:
                checkpoint.draw(self._display_surface)
                pygame.display.update()
                
            if checkpoint_start is not None:
                pygame.draw.line(self._display_surface, (255, 255, 0), checkpoint_start, pygame.mouse.get_pos(), width=3)
                pygame.display.update()

            for event in pygame.event.get():
                left, _, _ = pygame.mouse.get_pressed()
                if left:
                    if checkpoint_start is None:
                        checkpoint_start = pygame.mouse.get_pos()
                    else:
                        checkpoint = Checkpoint(str(checkpoint_id), checkpoint_start, pygame.mouse.get_pos())
                        self._checkpoints.append(checkpoint)
                        checkpoint_start = None
                        checkpoint_id += 1
                
                # Handle if the D key is pressed
                elif event.type == pygame.KEYDOWN and event.key == K_d:
                    # If the D key was pressed and we were drawing a new checkpoint, cancel
                    if checkpoint_start is not None:
                        checkpoint_start = None
                        continue
                    # Otherwise - remove the last drawn checkpoint
                    elif len(self._checkpoints) > 0:
                        self._checkpoints = self._checkpoints[:-1]

    def setup(self):
        self.set_car_spawn()
        # Spawn a car
        car = Car("one", self._car_spawn_position, self._car_spawn_rotation)
        self.add_car(car)
        self.set_checkpoints()

    def on_execute(self):
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def manual_play(self):
        self.on_execute()

    def init(self):
        if self.on_init() == False:
            self._running = False


    def play(self):
        if self.on_init() == False:
            self._running = False
