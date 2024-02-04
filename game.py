import pygame
import os
import sys
from random import randint
import pygame
import os
import sys
from random import randint


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
counter, text = 2000, '300'.rjust(3)

FPS = 60
clock = pygame.time.Clock()

#флаг генерации бонуса
bonus_create = 1
#количество бонусов в текущей игре
bonus_score = 0
running = True
#количество бонусов в цикле игр
global_bonus_score = 0

#создаем группы объектов
sprite_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
bonus_group = pygame.sprite.Group()

fontUI = pygame.font.Font(None, 30)

# загружаем объекты
tile_image = {'wall': load_image('box.png'),
              'empty': load_image('grass.png')}
player_image = load_image('mar.png')
bonus_image = load_image('bonus.png')
tile_width = tile_height = 50


class ScreenFrame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class SpriteGroup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for inet in self:
            inet.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# генерация марио на карте и его перемещания
class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(tile_width * self.pos[0] + 15,
                                               tile_height * self.pos[1] + 5)


# создание и генерация бонусов на карте
class Bonus(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bonus_group)
        self.image = bonus_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)
        self.timer = 600


    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            objects.remove(self)

        for obj in objects:
            if obj.type == 'tank' and self.rect.colliderect(obj.rect):
                if self.bonusNum == 0:
                    if obj.rank < len(imgTanks) - 1:
                        obj.rank += 1
                        objects.remove(self)
                        break
                elif self.bonusNum == 1:
                    obj.hp += 1
                    objects.remove(self)
                    break


    def draw(self):
        screen.blit(self.image, self.rect)


def terminate():
    pygame.quit()
    sys.exit()


# создание стартового окна
def start_screen():
    intro_text = ["Цель игры:", '',
                  "Собрать как можно больше",
                  "бонусов-звездочек",
                  "за отведенное время",
                  "и побить свой рекорд)"]
    fon = pygame.transform.scale(load_image('fon.jpg'), size)
    screen.blit((fon), (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
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
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


# создание финишного окна
def finish_screen():
    global bonus_score
    global global_bonus_score
    if global_bonus_score < bonus_score:
        global_bonus_score = bonus_score
    intro_text = ["Игра завершена", '',
                  "Набрано бонусов за игру: " + str(bonus_score),
                  "Лучший результат: " + str(global_bonus_score),
                  "Играть снова - ",
                  "нажмите кнопку мыши"]
    fon = pygame.transform.scale(load_image('fon_finish.jpg'), size)
    screen.blit((fon), (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        global counter, text
        counter, text = 300, '300'.rjust(3)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == event.type == pygame.MOUSEBUTTONDOWN:
                global bonus_create
                bonus_create = 1
                bonus_score = 0
                global running
                running = True
                bonus.kill()
                return
        pygame.display.flip()


def load_level(filename):
    filename = 'data/' + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


# считываем карту
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(1, len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = '.'
    return new_player, x, y


# отрисовка спрайтов и карты
def move(hero, movement, bonus):
    x, y = hero.pos
    if movement == 'up':
        if y > 0 and level_map[y - 1][x] == '.':
            hero.move(x, y - 1)
    elif movement == 'down':
        if y < max_y - 1 and level_map[y + 1][x] == '.':
            hero.move(x, y + 1)
    elif movement == 'left':
        if x > 0 and level_map[y][x - 1] == '.':
            hero.move(x - 1, y)
    elif movement == 'right':
        if x < max_x - 1 and level_map[y][x + 1] == '.':
            hero.move(x + 1, y)

    # проверяем столкновение с бонусом
    if hero.pos == bonus.pos:
        global bonus_score
        bonus_score = bonus_score + 1
        bonus.kill()
        global bonus_create
        bonus_create = 1
        global bonusTimer
        bonusTimer = 0


# отрисовка таймера игры
def draw_my_timer(screen, time_left):
    font = pygame.font.Font(None, 36)
    text = font.render("Time left: " + str(time_left), True, (255, 255, 255))
    screen.blit(text, (250, 250))


class UI:
    def __init__(self):
        pass


    def update(self):
        pass


    def draw(self):
        clock.tick(60)
        textTime = fontUI.render('Время', 1, 'red')
        rect = textTime.get_rect(center=(5 * 70, 5 + 11))
        textTimeTick = fontUI.render(str(obj.hp), 1, 'red')
        rect = textTimeTick.get_rect(center=(5 * 70 + 32, 5 + 11))
        screen.blit(text, rect)

objects = []
bonusTimer = 0


if __name__ == '__main__':
    pygame.display.set_caption('Марио')
    player = None
    ranning = True
    clock = pygame.time.Clock()
    #выводим текст со временем игры
    font = pygame.font.SysFont('Consolas', 30)


    start_screen()
    level_map = load_level('map.txt')
    hero, max_x, max_y = generate_level(level_map)

    MYEVENTTYPE = pygame.USEREVENT + 1
    while ranning:
        #считаем, не пора ли выводить game over
        counter -= 1
        text = str(counter).rjust(3) if counter > 0 else 'game over!'
        if counter == 0:
            running = False
            finish_screen()

        text_bonus = str(bonus_score) if bonus_score > 0 else 'bonus'
        pygame.time.set_timer(MYEVENTTYPE, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move(hero, 'up', bonus)
                if event.key == pygame.K_DOWN:
                    move(hero, 'down', bonus)
                if event.key == pygame.K_RIGHT:
                    move(hero, 'right', bonus)
                if event.key == pygame.K_LEFT:
                    move(hero, 'left', bonus)
            elif event.type == MYEVENTTYPE:
                if bonus_create == 1:
                    x, y = 0,0
                    while level_map[y][x] != '.':
                        x = randint(1, 9)
                        y = randint(2, 9)
                    bonus = Bonus(x, y)
                    bonus_create = 0

        screen.fill(pygame.Color('black'))
        sprite_group.draw(screen)
        hero_group.draw(screen)
        bonus_group.draw(screen)
        pygame.display.flip()

        screen.blit(font.render(text, True, (255, 255, 255)), (5, 5))
        screen.blit(font.render(text_bonus, True, (255, 255, 255)), (300, 5))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()