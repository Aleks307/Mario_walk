import os
import sys
import pygame

FPS = 50
pygame.init()
SIZE = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption("Перемещение героя")

def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}

player_image = load_image('mario.png')

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, *args):
        if args and args[0].type == pygame.KEYDOWN:
            left = pygame.key.get_pressed()[pygame.K_LEFT]
            up = pygame.key.get_pressed()[pygame.K_UP]
            down = pygame.key.get_pressed()[pygame.K_DOWN]
            right = pygame.key.get_pressed()[pygame.K_RIGHT]
            if not any((left, up, down, right)):
                return
            move_to = right - left, down - up
            x, y = move_to
            new_pos_x = self.pos_x + x
            new_pos_y = self.pos_y + y
            if 0 <= new_pos_x < len(CURRENT_LEVEL[0]) \
                    and 0 <= new_pos_y < len(CURRENT_LEVEL) \
                    and CURRENT_LEVEL[new_pos_y][new_pos_x] == '.':
                self.pos_x = new_pos_x
                self.pos_y = new_pos_y
                self.rect = self.image.get_rect().move(
                    tile_width * self.pos_x + 15, tile_height * self.pos_y + 5)

player = None

def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                CURRENT_LEVEL[y][x] = '.'
    return new_player, x, y


start_screen()
CURRENT_LEVEL = load_level('level_1.txt')
player, level_x, level_y = generate_level(CURRENT_LEVEL)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            player.move(event)
    screen.fill(pygame.Color("black"))
    all_sprites.draw(screen)
    player_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()