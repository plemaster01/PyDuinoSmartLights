# pip install pyserial
import copy

import serial.tools.list_ports
import pygame, random

pygame.init()

font = pygame.font.Font('freesansbold.ttf', 32)
small_font = pygame.font.Font('freesansbold.ttf', 20)
WIDTH = 500
HEIGHT = 500
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Garage Lights')
timer = pygame.time.Clock()
fps = 60
lights = [0, 0, 0, 0, 0, 0]
colors = ['yellow', 'dark gray']
colors2 = ['dark gray', 'yellow']
ls = False
last_command = [1, 1, 1, 1, 1, 1]
ls_count = 0

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []

for one in ports:
    portsList.append(str(one))
    print(str(one))

# com = input("Select Com Port for Arduino #: ")
com = 3

for i in range(len(portsList)):
    if portsList[i].startswith("COM" + str(com)):
        use = "COM" + str(com)
        print(use)

serialInst.baudrate = 115200
serialInst.port = use
serialInst.open()


class Button:
    def __init__(self, x_pos, y_pos, text, width, height, active):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.width = width
        self.height = height
        self.active = active
        self.rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.width, self.height))

    def draw(self):
        pygame.draw.rect(screen, colors2[self.active], self.rect, 3, 5)
        screen.blit(small_font.render(self.text, True, 'white'), (self.x_pos + 5, self.y_pos + 15))


def draw_screen():
    pygame.draw.rect(screen, 'white', [100, HEIGHT - 50, 300, 50], 5, 5)
    screen.blit(font.render('GARAGE DOOR', True, 'white'), (120, HEIGHT - 40))
    pygame.draw.rect(screen, 'white', [20, 0, 120, 50], 5, 5)
    screen.blit(font.render('DOOR', True, 'white'), (30, 10))
    LEDs = []
    for i in range(6):
        row = i // 3
        col = i % 3
        LEDs.append(pygame.draw.rect(screen, colors[lights[i]],
                                     [(1 + row) * WIDTH / 3 - 10, col * HEIGHT / 4 + 50, 20, 100]))
    all_on = Button(WIDTH - 100, 20, 'All On', 100, 50, False)
    all_on.draw()
    all_off = Button(WIDTH - 100, 80, 'All Off', 100, 50, False)
    all_off.draw()
    right_on = Button(WIDTH - 100, 140, 'Right', 100, 50, False)
    right_on.draw()
    left_on = Button(WIDTH - 100, 200, 'Left', 100, 50, False)
    left_on.draw()
    stagger = Button(WIDTH - 100, 260, 'Stagger', 100, 50, False)
    stagger.draw()
    random = Button(WIDTH - 100, 320, 'Random', 100, 50, False)
    random.draw()
    light_show = Button(WIDTH - 100, 380, 'Routine', 100, 50, ls)
    light_show.draw()
    buttons = [all_on.rect, all_off.rect, right_on.rect, left_on.rect, stagger.rect, random.rect, light_show.rect]
    # left half, right half, all on, all off, stagger, outers, random, light show
    return LEDs, buttons


def transmit(lts):
    command = str(lts[0]) + str(lts[1]) + str(lts[2]) + str(lts[3]) + str(lts[4]) + str(lts[5]) + '0' + '0'
    serialInst.write(command.encode('utf-8'))
    print(command)


def ls_sequence(count):
    count += 1
    if count < 120:
        lites = [0, 0, 0, 0, 0, 0]
    elif count < 240:
        lites = [0, 1, 1, 0, 1, 1]
    elif count < 360:
        lites = [1, 0, 1, 1, 0, 1]
    elif count < 480:
        lites = [1, 1, 0, 1, 1, 0]
    elif count < 600:
        lites = [0, 0, 0, 1, 1, 1]
    elif count < 720:
        lites = [1, 1, 1, 0, 0, 0]
    elif count < 840:
        lites = [0, 1, 0, 0, 1, 0]
    elif count < 960:
        lites = [1, 0, 1, 1, 0, 1]
    else:
        lites = [0, 0, 0, 0, 0, 0]
        count = 0
    return count, lites


run = True
while run:
    screen.fill('black')
    timer.tick(fps)
    LED, button = draw_screen()
    if ls:
        ls_count, lights = ls_sequence(ls_count)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(6):
                if LED[i].collidepoint(event.pos):
                    if lights[i] == 0:
                        lights[i] = 1
                    else:
                        lights[i] = 0
            # buttons = [all_on, all_off, right_on, left_on, stagger, random, light_show]
            for i in range(len(button)):
                if button[0].collidepoint(event.pos):
                    lights = [0, 0, 0, 0, 0, 0]
                elif button[1].collidepoint(event.pos):
                    lights = [1, 1, 1, 1, 1, 1]
                elif button[2].collidepoint(event.pos):
                    lights = [1, 1, 1, 0, 0, 0]
                elif button[3].collidepoint(event.pos):
                    lights = [0, 0, 0, 1, 1, 1]
                elif button[4].collidepoint(event.pos):
                    if lights != [1, 0, 1, 0, 1, 0]:
                        lights = [1, 0, 1, 0, 1, 0]
                    else:
                        lights = [0, 1, 0, 1, 0, 1]
                elif button[5].collidepoint(event.pos):
                    lights = [random.randint(0, 1), random.randint(0, 1), random.randint(0, 1), random.randint(0, 1),
                              random.randint(0, 1), random.randint(0, 1)]
                elif button[6].collidepoint(event.pos):
                    if ls:
                        ls = False
                    else:
                        ls = True

    if lights != last_command:
        transmit(lights)
        last_command = copy.deepcopy(lights)
        print(f'message sent {lights}')

    pygame.display.flip()
pygame.quit()
