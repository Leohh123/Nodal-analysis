import pygame
from pygame.locals import *
from .widget import Textbox


class Logger(object):
    def __init__(self, run):
        self.run = run
        self.width = self.run.place_width
        self.height = self.run.log_height
        self.pos_x = 0
        self.pos_y = self.run.place_height + self.run.cmd_height
        self.font_size = int(self.height * 0.8)
        self.font = pygame.font.Font(self.run.font_path, self.font_size)
        self.textbox = Textbox(self.run, self.width, self.height, self.pos_x,
                               self.pos_y, self.font)

    def log(self, msg):
        self.textbox.set_text(msg)

    def render(self):
        self.textbox.render()
