import pygame
from pygame.locals import *
import math
from pygame.locals import K_d, K_RETURN, K_c, K_n, K_MINUS, K_EQUALS, K_LEFTBRACKET, K_RIGHTBRACKET
import time
from random import uniform, choices
from pprint import pprint
import json

from .car import Car
from .car import mate as car_mate
from .checkpoint import Checkpoint
from .finishline import FinishLine
from .track import Track

MANUAL_MODE = "manual"
EVOLVE_MODE = "evolve"
TIME_LIMIT = 60

pygame.font.init()
font = pygame.font.SysFont(None, 32)

class Game:
    def __init__(self, trackname : str, mode : str = MANUAL_MODE, cars_per_generation=25):
        self._running = True
        self._display_surface = None
        self._frame_per_sec = pygame.time.Clock()
        self._fps = 60

        self._cars = pygame.sprite.Group()
        self._checkpoints : [Checkpoint] = []
        self._trackname = trackname
        self._tracksg = pygame.sprite.Group()
        self._car_spawn_position = None
        self._car_spawn_rotation = None

        self._show_checkpoints = False
        self._finishline = None
        self._show_distances = False
        self._show_finishline = False

        self._mode = mode
        self._generation = 1
        self._start_time = None

        self._cars_per_generation = cars_per_generation
        self._mutation_rate = 0.005
        self._parent_cutoff = 10

    def get_time_since_start(self):
        if self._start_time is None:
            return None
        return time.time() - self._start_time

    def add_car(self, car : Car):
        self._cars.add(car)

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
            if car._crashed:
                continue
            for angle in [-60, -30, 0, 30, 60]:
                endpoint, distance = self._track.distance_to_wall(car, angle)
                car.add_distance(angle, endpoint, distance)
            if self._mode == MANUAL_MODE:
                pressed_keys = pygame.key.get_pressed()
                acceleration, rotation = car.get_keyboard_move(pressed_keys)
            else:
                acceleration, rotation = car.get_nn_move()
            car.move(acceleration, rotation)
            # Calculate if the car impacts
            trackCollions = pygame.sprite.spritecollide(car, self._tracksg, False, pygame.sprite.collide_mask)
            if len(trackCollions) > 0:
                car.crash(self.get_time_since_start())
            for checkpoint in self._checkpoints:
                # if checkpoint.check_collision(car.rect):
                if checkpoint.check_collision(car):
                    car.cross_checkpoint(checkpoint, self.get_time_since_start())
            if self._finishline.check_collision(car):
                car.cross_finish_line()

    def on_render(self):
        self._display_surface.fill((69, 68, 67))
        self._display_surface.blit(self._track.surf, self._track.rect)

        # Car drawing
        for car in self._cars:
            car.render()
            self._display_surface.blit(car.surf, car.rect)
            
        # Checkpoints
        if self._show_checkpoints:
            for checkpoint in self._checkpoints:
                checkpoint.draw(self._display_surface)
            # Draw the finish line as well
            if self._finishline is not None:
                self._finishline.draw(self._display_surface)
        pygame.display.update()
        self._frame_per_sec.tick(self._fps)

        # Distances Drawing
        if self._show_distances:
            for car in self._cars:
                for angle in car._distance_endpoints:
                    pygame.draw.line(self._display_surface, (0, 255, 0), car.get_center(), car._distance_endpoints[angle], width=1)

        # Generation Title
        generation_title = font.render(f"Generation {self._generation}", True, (255, 255, 255))
        track_size = self._track.get_size()
        # self._display_surface.blit(generation_title, (10, track_size[1] - 30))
        self._display_surface.blit(generation_title, (10, 10))

        # Parent title
        parent_title = font.render(f"The top {self._parent_cutoff} cars will survive and mate", True, (255, 255, 255))
        self._display_surface.blit(parent_title, (10, 40))

        # Mutation title
        if self._mutation_rate > 0.0:
            mutation_title = font.render(f"The mutation rate is {round(self._mutation_rate * 100, 2)}%", True, (255, 255, 255))
            self._display_surface.blit(mutation_title, (10, 70))

        pygame.display.update()

    def on_cleanup(self):
        self._start_time = None

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
        self._show_checkpoints = True

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
                        # Since instant double tapping is *really* annoying and common on trackpads, let's
                        # make sure this is not a line with too small a size to be worth adding
                        checkpoint_end = pygame.mouse.get_pos()
                        distance = ( (checkpoint_end[0] - checkpoint_start[0])**2 + (checkpoint_end[1] - checkpoint_start[1])**2 )**0.5
                        if distance < 2:
                            continue
                        checkpoint = Checkpoint(checkpoint_start, checkpoint_end)
                        self._checkpoints.append(checkpoint)
                        checkpoint_start = None
                
                # Handle if the D key is pressed
                elif event.type == pygame.KEYDOWN and event.key == K_d:
                    # If the D key was pressed and we were drawing a new checkpoint, cancel
                    if checkpoint_start is not None:
                        checkpoint_start = None
                        continue
                    # Otherwise - remove the last drawn checkpoint
                    elif len(self._checkpoints) > 0:
                        self._checkpoints = self._checkpoints[:-1]
        
        self._show_checkpoints = False

    def set_finish_line(self):
        pressed_keys = pygame.key.get_pressed()
        finishline_start = None
        self._show_checkpoints = True
        self._show_finishline = True

        while(self._finishline is None):
            pressed_keys = pygame.key.get_pressed()
            self.on_render()
            for checkpoint in self._checkpoints:
                checkpoint.draw(self._display_surface)
                pygame.display.update()
                
            if finishline_start is not None:
                pygame.draw.line(self._display_surface, (0, 255, 0), finishline_start, pygame.mouse.get_pos(), width=3)
                pygame.display.update()

            for event in pygame.event.get():
                left, _, _ = pygame.mouse.get_pressed()
                if left:
                    if finishline_start is None:
                        finishline_start = pygame.mouse.get_pos()
                    else:
                        # Since instant double tapping is *really* annoying and common on trackpads, let's
                        # make sure this is not a line with too small a size to be worth adding
                        finishline_end = pygame.mouse.get_pos()
                        distance = ( (finishline_end[0] - finishline_start[0])**2 + (finishline_end[1] - finishline_start[1])**2 )**0.5
                        if distance < 2:
                            continue
                        self._finishline = FinishLine(finishline_start, finishline_end)
                
                # Handle if the D key is pressed
                elif event.type == pygame.KEYDOWN and event.key == K_d:
                    # If the D key was pressed and we were drawing a new checkpoint, cancel
                    if finishline_start is not None:
                        finishline_start = None
                        continue
                    if self._finishline is not None:
                        self._finishline = None
        
        self._show_checkpoints = False
        self._show_finishline = False
    
    def setup(self):
        self.set_car_spawn()
        # Spawn a car
        car = Car(self._car_spawn_position, self._car_spawn_rotation)
        self.add_car(car)
        self.set_checkpoints()
        self.set_finish_line()
        if self._mode == MANUAL_MODE:
            # We're actually done by this point in manual mode. So just return
            return
        elif self._mode == EVOLVE_MODE:
            self._show_distances = False
            # Now that we've set the checkpoints, kill the one car we hvae
            del car
            self._cars = pygame.sprite.Group()

    def cars_alive(self):
        count = 0
        for car in self._cars:
            if not car._crashed:
                count += 1
        return count

    def on_execute(self):
        self._start_time = time.time()
        manual_stop = False
        while(self._running and self.get_time_since_start() < TIME_LIMIT and self.cars_alive() > 0 and not manual_stop):
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_c]:
                self._show_checkpoints = not self._show_checkpoints
            if pressed_keys[K_d]:
                self._show_distances = not self._show_distances
            if pressed_keys[K_n]:
                # The N key can accidentally be held down too long skipping
                # the next generation - annoying. So only pay attention to
                # the skip key if its been at least 5 seconds.
                if time.time() - self._start_time > 5:
                    manual_stop = True
            if pressed_keys[K_MINUS]:
                self._mutation_rate -= 0.001
                if self._mutation_rate < 0.0:
                    self._mutation_rate = 0.0
                print(f"Mutation rate set to {int(self._mutation_rate * 100)}%")
            if pressed_keys[K_EQUALS]:
                self._mutation_rate += 0.001
                if self._mutation_rate > 1.0:
                    self._mutation_rate = 1.0
                print(f"Mutation rate set to {int(self._mutation_rate * 100)}%")
            if pressed_keys[K_LEFTBRACKET]:
                self._parent_cutoff -= 1
                if self._parent_cutoff <= 2:
                    self._parent_cutoff = 2
                else:
                    print(f"The top {self._parent_cutoff} cars will be used as parents")
            if pressed_keys[K_RIGHTBRACKET]:
                self._parent_cutoff += 1
                if self._parent_cutoff >= self._cars_per_generation:
                    self._parent_cutoff = self._cars_per_generation - 5
                else:
                    print(f"The top {self._parent_cutoff} cars will be used as parents")
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        for car in self._cars:
            car.add_end_score(self.get_time_since_start())
        self.on_cleanup()

    def manual_play(self):
        self._mode = MANUAL_MODE
        self.on_execute()

    def evolve(self):
        self._mode = EVOLVE_MODE
        # init our first generation
        for i in range(0, self._cars_per_generation):
            self.add_car(Car(self._car_spawn_position, self._car_spawn_rotation))

        while(self._running):
            print(f"===== GENERATION {self._generation} =====")    
            self.on_execute()
            
            # Now that execute is over, let's order the cars by their scores.
            cars = sorted(self._cars, key=lambda car : car._score, reverse=True)
            self._cars = cars[0:self._parent_cutoff]
            self.on_render()
            time.sleep(3)

            next_generation = cars[0:self._parent_cutoff]
            parents = cars[0:self._parent_cutoff] # This is duplicated solely for the mate_counter
            scores = [car._score for car in next_generation]
            print("SCORES", [car._score for car in next_generation])
            # random.choices does *not* work with negative weights. It also fails if
            # all weights are zreo. offset the scores such that the lowest possible
            # weight + 1 is the minimum value.
            offset = abs(min(scores))
            scores = [score + offset + 1 for score in scores]

            mate_counter = {}
            while len(next_generation) < self._cars_per_generation:
                # The probability of each car being chosen is based on their total scores
                car_a = choices(cars[0:self._parent_cutoff], weights=scores)[0]
                car_b = None
                while car_b is None or car_a == car_b: # we want to prevent a self mate - outside of mutation it would result in no difference, plus the car could go blind
                    car_b = choices(cars[0:self._parent_cutoff], weights=scores)[0]
                
                # Update the mate counter
                car_a_parent_index = parents.index(car_a)
                car_b_parent_index = parents.index(car_b)
                if car_a_parent_index not in mate_counter:
                    mate_counter[car_a_parent_index] = 0
                mate_counter[car_a_parent_index] += 1
                if car_b_parent_index not in mate_counter:
                    mate_counter[car_b_parent_index] = 0
                mate_counter[car_b_parent_index] += 1

                # Create the new car
                new_car  = car_mate(car_a, car_b, mutation=self._mutation_rate)
                next_generation.append(new_car)

            # Print the mate counter:
            print("Mate Counter")
            pprint(mate_counter)

            # Reset each parent that made it to the next generation
            for car in next_generation:
                car.reset()

            # Add some new genes to the gene pool by adding a few completely newbie cars
            # for i in range(0, self._new_cars_per_generation):
            #     self.add_car(Car(self._car_spawn_position, self._car_spawn_rotation))

            # In case we generated too many...
            # next_generation = next_generation[0:self._cars_per_generation]
            self.on_cleanup()
            self._cars = pygame.sprite.Group()
            for car in next_generation:
                self.add_car(car)
            self._generation += 1

    def init(self):
        if self.on_init() == False:
            self._running = False

    def play(self):
        if self.on_init() == False:
            self._running = False

    def save(self, filepath : str):
        with open(filepath, 'w') as writefile:
            settings = {
                "trackname": self._trackname,
                "mode": self._mode,
                "checkpoints": [],
                "finish_line": [self._finishline._start_at[0], self._finishline._start_at[1], self._finishline._end_at[0], self._finishline._end_at[1]],
                "car_start_pos": self._car_spawn_position,
                "car_start_rot": self._car_spawn_rotation,
                "cars_per_generation": self._cars_per_generation
            }

            for checkpoint in self._checkpoints:
                settings["checkpoints"].append([checkpoint._start_at[0], checkpoint._start_at[1], checkpoint._end_at[0], checkpoint._end_at[1]],)

            json.dump(settings, writefile)
    

def load_from_file(filepath : str) -> Game:
    with open(filepath, 'r') as readfile:
        settings = json.load(readfile)

        game = Game(settings['trackname'], mode=settings['mode'], cars_per_generation=settings['cars_per_generation'])
        for checkpoint in settings['checkpoints']:
            game._checkpoints.append(Checkpoint((checkpoint[0], checkpoint[1]), (checkpoint[2], checkpoint[3])))
        game._finishline = FinishLine((settings["finish_line"][0], settings["finish_line"][1]), (settings["finish_line"][2], settings["finish_line"][3]))
        game._car_spawn_position = settings['car_start_pos']
        game._car_spawn_rotation = settings['car_start_rot']

        return game