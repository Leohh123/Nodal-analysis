import pygame
from pygame.locals import *
from sys import exit
from .common import Color, Utils, Direction
from .component import Resistance, CurrentSource, VoltageSource, CCCS, VCCS, CCVS, VCVS
from .widget import Textbox
from .cmd import CMD
from .logger import Logger
from .sidebar import Sidebar


class Run(object):
    def __init__(self, width, height, caption, callback):
        pygame.init()
        self.width = width
        self.height = height
        self.screen_size = [self.width, self.height]
        self.screen = pygame.display.set_mode(self.screen_size, 0, 32)
        self.caption = caption
        self.callback = callback
        pygame.display.set_caption(self.caption)
        self.icon_path = "./ui/assets/image/icon.png"
        surface_icon = pygame.image.load(self.icon_path)
        pygame.display.set_icon(surface_icon)
        self.sidebar_width = int(self.width * 0.2)
        self.cmd_height = 25
        self.log_height = 25
        self.place_space = 16
        self.place_offset = 5
        self.place_width = self.width - self.sidebar_width
        self.place_height = self.height - self.cmd_height - self.log_height
        self.place_col = (self.place_width -
                          self.place_offset) // self.place_space
        self.place_row = (self.place_height -
                          self.place_offset) // self.place_space
        self.font_path = "./ui/assets/font/cambria.ttc"
        self.components = []
        self.wires = []
        self.logger = Logger(self)
        self.sidebar = Sidebar(self)
        self.cmd = CMD(self, self.logger, self.sidebar)

    def render_background(self):
        self.screen.fill(Color.white)
        for i in range(self.place_col):
            for j in range(self.place_row):
                pos_x = self.place_offset + self.place_space * i
                pos_y = self.place_offset + self.place_space * j
                self.screen.set_at([pos_x, pos_y], Color.grey)

    def get_placement(self, x, y):
        place_x = Utils.interval(
            0, self.place_col - 1, round((x - self.place_offset) / self.place_space))
        place_y = Utils.interval(
            0, self.place_row - 1, round((y - self.place_offset) / self.place_space))
        return [place_x, place_y]

    def ok_placement(self, x, y):
        return Utils.in_interval(0, self.place_col - 1, x) and \
            Utils.in_interval(0, self.place_row - 1, y)

    def get_pos(self, x, y):
        pos_x = self.place_offset + self.place_space * x
        pos_y = self.place_offset + self.place_space * y
        return [pos_x, pos_y]

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                elif event.type == KEYDOWN:
                    self.cmd.key_down(event)
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.cmd.mouse_down(*event.pos)
            self.render_background()
            for c in self.components:
                c.render()
            for w in self.wires:
                w.render()
            self.cmd.render()
            self.logger.render()
            self.sidebar.render()
            pygame.display.update()
