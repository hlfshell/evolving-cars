import pygame
from pygame.locals import *
from car import Car
from checkpoint import Checkpoint
from track import Track
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
        # self._track_group = pygame.sprite.Group()
        self._trackname = trackname
        self._car_spawn_position = None
        self._car_spawn_rotation = None

    def add_car(self, car : Car):
        self._cars.add(car)

    def add_checkpoint(self, checkpoint : Checkpoint):
        self._checkpoints.add(checkpoint)

    def on_init(self):
        pygame.init()
        self._track = Track(self._trackname)
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
            # trackCollions = pygame.sprite.spritecollide(car, self._track, False)
            checkpointCollisions = pygame.sprite.spritecollide(car, self._checkpoints, False)
            for collision in checkpointCollisions:
                car.crash(collision)


    def on_render(self):
        self._display_surface.fill((255,255,255))
        self._display_surface.blit(self._track._surface, self._track._rect)
        for car in self._cars:
            car.render()
            self._display_surface.blit(car.surf, car.rect)
        pygame.display.update()
        self._frame_per_sec.tick(self._fps)

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

    def on_execute(self):       
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def play(self):
        if self.on_init() == False:
            self._running = False

        self.set_car_spawn()
        # Spawn a car
        car = Car("one", self._car_spawn_position, self._car_spawn_rotation)
        self.add_car(car)
        self.set_checkpoints()
        self.on_execute()

if __name__ == "__main__":
    game = Game("track1.png")
    # car = Car("one", (20, 30))
    # checkpoint = Checkpoint("abc123", (20, 20), (30, 30))
    # game.add_car(car)
    # game.add_checkpoint(checkpoint)
    game.play()
    # game.on_execute()