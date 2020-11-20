import pygame
from pygame.locals import *
from .common import Color, Utils
import threading


class Textarea(object):
    def __init__(self, run, width, height, pos_x, pos_y, font=None, cmd=None, formatter=lambda x: x):
        self.run = run
        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.chars = []
        self.cmd = cmd
        self.formatter = formatter
        self.surface = pygame.Surface([self.width, self.height])
        if font is not None:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 32)
        self.cursor = True
        self.history = []
        self.cur_line = 1

    def update_cursor(self):
        self.cursor = not self.cursor
        threading.Timer(0.5, self.update_cursor).start()

    def start(self):
        threading.Thread(target=self.update_cursor, daemon=True).start()

    @property
    def text(self):
        if self.cur_line < len(self.history):
            return self.history[self.cur_line]
        return "".join(self.chars)

    @property
    def text_show(self):
        return self.formatter("{}{}".format(self.text, "|" if self.cursor else ""))

    def render(self):
        self.surface.fill(Color.white)
        surface_text = self.font.render(self.text_show, True, Color.black)
        self.surface.blit(
            surface_text,
            [0, self.height - surface_text.get_height()],
            [0, 0, self.width, self.height]
        )
        self.run.screen.blit(self.surface, [self.pos_x, self.pos_y])

    def key_down(self, event):
        unic = event.unicode
        key = event.key
        if key in [K_UP, K_DOWN]:
            self.cur_line += 1 if key == K_DOWN else -1
            self.cur_line = Utils.interval(0, len(self.history), self.cur_line)
        elif self.cur_line < len(self.history):
            self.chars = list(self.history[self.cur_line])
            self.cur_line = len(self.history)
        if key == K_BACKSPACE:
            if len(self.chars) > 0:
                self.chars.pop()
            return
        if key == 13:
            if self.cmd is not None:
                self.cmd.solve(self.text)
            self.history.append(self.text)
            self.cur_line = len(self.history)
            self.chars.clear()
            return
        if key == K_DELETE:
            self.chars.clear()
            return
        try:
            if unic != "":
                ch = unic
            else:
                ch = chr(key)
            self.chars.append(ch)
        except:
            pass


class Textbox(object):
    def __init__(self, run, width, height, pos_x, pos_y, font=None, formatter=lambda x: x):
        self.run = run
        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.text = ""
        self.surface = pygame.Surface([self.width, self.height])
        if font is not None:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 32)
        self.formatter = formatter

    @property
    def text_show(self):
        return self.formatter(self.text)

    def render(self):
        self.surface.fill(Color.white)
        surface_text = self.font.render(self.text_show, True, Color.black)
        self.surface.blit(
            surface_text,
            [0, self.height - surface_text.get_height()],
            [0, 0, self.width, self.height]
        )
        self.run.screen.blit(self.surface, [self.pos_x, self.pos_y])

    def set_text(self, new_text):
        self.text = new_text


class MultiLineBox(object):
    def __init__(self, run, width, height, pos_x, pos_y, font=None):
        self.run = run
        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.lines = []
        self.surface = pygame.Surface([self.width, self.height])
        if font is not None:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 32)
        self.line_space = self.font.get_linesize()
        self.line_count = 0

    def add_line(self, text):
        self.lines.append(text)

    def clear(self):
        self.lines.clear()

    def render_line(self, text):
        surface = pygame.Surface([self.width, self.line_space])
        surface.fill(Color.white)
        surface_text = self.font.render(text, True, Color.black)
        surface.blit(
            surface_text,
            [0, (self.line_space - surface_text.get_height()) / 2],
            [0, 0, self.width, self.line_space]
        )
        self.surface.blit(
            surface,
            [0, self.pos_y + self.line_count * self.line_space],
            [0, 0, self.width, self.height]
        )
        self.line_count += 1

    def render_text(self, text):
        cur_text = ""
        for ch in text:
            tmp_width = self.font.size(cur_text + ch)[0]
            if tmp_width > self.width:
                self.render_line(cur_text)
                cur_text = ch
            else:
                cur_text += ch
        if cur_text != "":
            self.render_line(cur_text)

    def render(self):
        self.surface.fill(Color.white)
        self.line_count = 0
        for text in self.lines:
            self.render_text(text)
        self.run.screen.blit(self.surface, [self.pos_x, self.pos_y])
