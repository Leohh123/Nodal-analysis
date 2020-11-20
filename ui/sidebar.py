import pygame
from pygame.locals import *
from .widget import MultiLineBox


class Sidebar(object):
    def __init__(self, run):
        self.run = run
        self.width = self.run.sidebar_width
        self.height = self.run.height
        self.pos_x = self.run.place_width
        self.pos_y = 0
        self.font_size = int(self.run.cmd_height * 0.8)
        self.font = pygame.font.Font(self.run.font_path, self.font_size)
        self.mlbox = MultiLineBox(
            self.run, self.width, self.height, self.pos_x, self.pos_y, self.font)

    def log_all(self, msg_list):
        for msg in msg_list:
            self.mlbox.add_line(msg)

    def log_one(self, msg):
        self.mlbox.add_line(msg)

    def clear(self):
        self.mlbox.clear()

    def render(self):
        self.mlbox.render()
