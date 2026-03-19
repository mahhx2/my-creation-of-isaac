import pygame
import random
import sys
import math

# Board settings
ROW_COUNT = 21
COLUMN_COUNT = 19
TILE_SIZE = 32
BOARD_WIDTH = COLUMN_COUNT * TILE_SIZE
BOARD_HEIGHT = ROW_COUNT * TILE_SIZE
FPS = 20

MAZE = [
    "XXXXXXXXXXXXXXXXXXX",
    "X        X        X",
    "X XX XXX X XXX XX X",
    "X                 X",
    "X XX X XXXXX X XX X",
    "X    X       X    X",
    "XXXX XXXX XXXX XXXX",
    "OOOX X       X XOOO",
    "XXXX X XXrXX X XXXX",
    "O       bpo       O",
    "XXXX X XXXXX X XXXX",
    "OOOX X       X XOOO",
    "XXXX X XXXXX X XXXX",
    "X        X        X",
    "X XX XXX X XXX XX X",
    "X  X     P     X  X",
    "XX X X XXXXX X X XX",
    "X    X   X   X    X",
    "X XXXXXX X XXXXXX X",
    "X                 X",
    "XXXXXXXXXXXXXXXXXXX"
]

DIRECTIONS = ['U', 'D', 'L', 'R']

# Colors
COLOR_BG   = (0, 0, 0)
COLOR_FOOD = (255, 255, 255)
COLOR_TEXT = (255, 255, 255)

GHOST_COLORS = {
    'b': (0, 200, 255),
    'o': (255, 165, 0),
    'p': (255, 105, 180),
    'r': (255, 0, 0),
}


def collision(a, b):
    return (a.x < b.x + b.width and
            a.x + a.width > b.x and
            a.y < b.y + b.height and
            a.y + a.height > b.y)


class Block:
    def __init__(self, kind, x, y, width, height, color=None, color_key=None):
        self.kind = kind
        self.color = color
        self.color_key = color_key
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.start_x = x
        self.start_y = y
        self.direction = 'R'
        self.velocity_x = 0
        self.velocity_y = 0

    def update_velocity(self):
        speed = TILE_SIZE // 4
        if self.direction == 'U':
            self.velocity_x, self.velocity_y = 0, -speed
        elif self.direction == 'D':
            self.velocity_x, self.velocity_y = 0, speed
        elif self.direction == 'L':
            self.velocity_x, self.velocity_y = -speed, 0
        elif self.direction == 'R':
            self.velocity_x, self.velocity_y = speed, 0

    def update_direction(self, direction, walls):
        prev_direction = self.direction
        self.direction = direction
        self.update_velocity()
        self.x += self.velocity_x
        self.y += self.velocity_y
        for wall in walls:
            if collision(self, wall):
                self.x -= self.velocity_x
                self.y -= self.velocity_y
                self.direction = prev_direction
                self.update_velocity()
                return

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y

    def draw(self, surface, images):
        if self.kind == 'wall':
            surface.blit(images['wall'], (self.x, self.y))

        elif self.kind == 'food':
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        elif self.kind == 'pacman':
            img = images.get(f'pacman_{self.direction}', images['pacman_R'])
            surface.blit(img, (self.x, self.y))

        elif self.kind == 'ghost':
            img = images.get(self.color_key)
            if img:
                surface.blit(img, (self.x, self.y))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("sans-serif", 16)

        # Load all images
        self.images = {
            'pacman_R': pygame.transform.scale(pygame.image.load("pacmanRight.png"), (TILE_SIZE, TILE_SIZE)),
            'pacman_L': pygame.transform.scale(pygame.image.load("pacmanLeft.png"),  (TILE_SIZE, TILE_SIZE)),
            'pacman_U': pygame.transform.scale(pygame.image.load("pacmanUp.png"),    (TILE_SIZE, TILE_SIZE)),
            'pacman_D': pygame.transform.scale(pygame.image.load("pacmanDown.png"),  (TILE_SIZE, TILE_SIZE)),
            'b': pygame.transform.scale(pygame.image.load("blueGhost.png"),   (TILE_SIZE, TILE_SIZE)),
            'o': pygame.transform.scale(pygame.image.load("orangeGhost.png"), (TILE_SIZE, TILE_SIZE)),
            'p': pygame.transform.scale(pygame.image.load("pinkGhost.png"),   (TILE_SIZE, TILE_SIZE)),
            'r': pygame.transform.scale(pygame.image.load("redGhost.png"),    (TILE_SIZE, TILE_SIZE)),
            'wall': pygame.transform.scale(pygame.image.load("wall.png"), (TILE_SIZE, TILE_SIZE)),
        }

        self.walls = []
        self.foods = []
        self.ghosts = []
        self.pacman = None
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.load_map()
        self.randomize_ghosts()

    def load_map(self):
        self.walls.clear()
        self.foods.clear()
        self.ghosts.clear()

        for r in range(ROW_COUNT):
            for c in range(COLUMN_COUNT):
                char = MAZE[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE

                if char == 'X':
                    self.walls.append(Block('wall', x, y, TILE_SIZE, TILE_SIZE))
                elif char in GHOST_COLORS:
                    ghost = Block('ghost', x, y, TILE_SIZE, TILE_SIZE,
                                  color=GHOST_COLORS[char], color_key=char)
                    self.ghosts.append(ghost)
                elif char == 'P':
                    self.pacman = Block('pacman', x, y, TILE_SIZE, TILE_SIZE)
                elif char == ' ':
                    food = Block('food', x + 14, y + 14, 4, 4, color=(255, 255, 255))
                    self.foods.append(food)

    def randomize_ghosts(self):
        for ghost in self.ghosts:
            ghost.update_direction(random.choice(DIRECTIONS), self.walls)

    def reset_positions(self):
        self.pacman.reset()
        self.pacman.velocity_x = 0
        self.pacman.velocity_y = 0
        for ghost in self.ghosts:
            ghost.reset()
            ghost.update_direction(random.choice(DIRECTIONS), self.walls)

    def move(self):
        # Move Pac-Man
        self.pacman.x += self.pacman.velocity_x
        self.pacman.y += self.pacman.velocity_y

        for wall in self.walls:
            if collision(self.pacman, wall):
                self.pacman.x -= self.pacman.velocity_x
                self.pacman.y -= self.pacman.velocity_y
                break

        # Ghost logic
        for ghost in self.ghosts:
            if collision(ghost, self.pacman):
                self.lives -= 1
                if self.lives == 0:
                    self.game_over = True
                    return
                self.reset_positions()
                return

            # Force ghosts upward when at ghost house exit row
            if ghost.y == TILE_SIZE * 9 and ghost.direction not in ('U', 'D'):
                ghost.update_direction('U', self.walls)

            ghost.x += ghost.velocity_x
            ghost.y += ghost.velocity_y

            hit_wall = any(collision(ghost, wall) for wall in self.walls)
            out_of_bounds = ghost.x <= 0 or ghost.x + ghost.width >= BOARD_WIDTH

            if hit_wall or out_of_bounds:
                ghost.x -= ghost.velocity_x
                ghost.y -= ghost.velocity_y
                ghost.update_direction(random.choice(DIRECTIONS), self.walls)

        # Food collision
        eaten = None
        for food in self.foods:
            if collision(self.pacman, food):
                eaten = food
                self.score += 10
                break
        if eaten:
            self.foods.remove(eaten)

        # Next level when all food eaten
        if len(self.foods) == 0:
            self.load_map()
            self.reset_positions()

    def draw(self):
        self.screen.fill(COLOR_BG)

        for wall in self.walls:
            wall.draw(self.screen, self.images)
        for food in self.foods:
            food.draw(self.screen, self.images)
        for ghost in self.ghosts:
            ghost.draw(self.screen, self.images)
        self.pacman.draw(self.screen, self.images)

        # HUD
        if self.game_over:
            msg = f"Game Over! Score: {self.score}  —  Press any arrow key to restart"
        else:
            msg = f"Lives: {self.lives}   Score: {self.score}"
        text = self.font.render(msg, True, COLOR_TEXT)
        self.screen.blit(text, (TILE_SIZE // 2, TILE_SIZE // 4))

        pygame.display.flip()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                self.load_map()
                self.reset_positions()
                self.lives = 3
                self.score = 0
                self.game_over = False
                self.randomize_ghosts()
                return

            if event.key in (pygame.K_UP, pygame.K_w):
                self.pacman.update_direction('U', self.walls)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.pacman.update_direction('D', self.walls)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.pacman.update_direction('L', self.walls)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.pacman.update_direction('R', self.walls)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_input(event)

            if not self.game_over:
                self.move()

            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()