import pygame
import pygame.gfxdraw
from pygame.locals import *
from .common import Direction, Color


class Component(object):
    def __init__(self, run, st_pos, dc, pos_id, neg_id, eid=None, line_width=1, node_radius=2):
        self.run = run
        self.st_pos = st_pos
        self.dc = dc
        self.pos_id = pos_id
        self.neg_id = neg_id
        self.eid = eid
        self.line_width = line_width
        self.node_radius = node_radius
        self.font_size = 14
        self.font = pygame.font.Font(self.run.font_path, self.font_size)
        if eid is not None:
            self.ol_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * -1)
            self.ml_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 1)
            self.m1_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 2)
            self.md_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 3)
            self.m2_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 4)
            self.mr_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 5)
            self.ed_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 6)
            self.or_pos = Direction.move(
                self.st_pos, self.dc, self.run.place_space * 7)
        self.pos_disp = False
        self.neg_disp = False

    def display_pos(self, opt=True):
        self.pos_disp = opt

    def display_neg(self, opt=True):
        self.neg_disp = opt

    def render_ends(self):
        pygame.draw.aaline(self.run.screen, Color.black,
                           self.st_pos, self.m1_pos, self.line_width)
        pygame.draw.aaline(self.run.screen, Color.black,
                           self.m2_pos, self.ed_pos, self.line_width)
        for pos in [self.st_pos, self.ed_pos]:
            pygame.gfxdraw.aacircle(
                self.run.screen, *pos, self.node_radius, Color.black)
            pygame.gfxdraw.filled_circle(
                self.run.screen, *pos, self.node_radius, Color.black)
        dist = self.run.place_space
        if self.run.cmd.is_numbered:
            if self.pos_disp:
                self.render_text("({})".format(self.pos_id),
                                 self.ol_pos, dist, angle_dict=Direction.angle_none)
            if self.neg_disp:
                self.render_text("({})".format(self.neg_id),
                                 self.or_pos, dist, angle_dict=Direction.angle_none)

    def render_rect(self):
        v1_pos = Direction.move(self.m1_pos, Direction.turn(
            self.dc, 3), self.run.place_space * 0.25)
        v2_pos = Direction.move(self.m2_pos, Direction.turn(
            self.dc, 3), self.run.place_space * 0.25)
        v3_pos = Direction.move(self.m2_pos, Direction.turn(
            self.dc, 1), self.run.place_space * 0.25)
        v4_pos = Direction.move(self.m1_pos, Direction.turn(
            self.dc, 1), self.run.place_space * 0.25)
        pygame.draw.aalines(self.run.screen, Color.black, True, [
                            v1_pos, v2_pos, v3_pos, v4_pos])

    def render_text(self, text, pos, dist, below=False, angle_dict=Direction.angle_text):
        surface = self.font.render(text, True, Color.black)
        rot_surface = pygame.transform.rotate(surface, angle_dict[self.dc])
        center = Direction.move(pos, Direction.turn(
            self.dc, 1 if below else 3), dist)
        w, h = rot_surface.get_size()
        upper_left = [center[0] - w / 2, center[1] - h / 2]
        self.run.screen.blit(rot_surface, upper_left)

    def render_circle(self):
        pygame.gfxdraw.aacircle(
            self.run.screen, *self.md_pos, self.run.place_space, Color.black)

    def render_vertical_line(self, dist):
        v1_pos = Direction.move(self.md_pos, Direction.turn(
            self.dc, 3), dist)
        v2_pos = Direction.move(self.md_pos, Direction.turn(
            self.dc, 1), dist)
        pygame.draw.aaline(self.run.screen, Color.black, v1_pos, v2_pos)

    def render_horizontal_line(self):
        pygame.draw.aaline(self.run.screen, Color.black,
                           self.m1_pos, self.m2_pos)

    def render_arrow(self):
        size = self.run.place_space * 0.5
        t_pos = Direction.move(self.mr_pos, Direction.turn(self.dc, 2), size)
        v1_pos = Direction.move(t_pos, Direction.turn(self.dc, 1), size * 0.25)
        v2_pos = Direction.move(t_pos, Direction.turn(self.dc, 3), size * 0.25)
        pygame.gfxdraw.aapolygon(
            self.run.screen, [v1_pos, v2_pos, self.mr_pos], Color.black)
        pygame.gfxdraw.filled_polygon(
            self.run.screen, [v1_pos, v2_pos, self.mr_pos], Color.black)

    def render_sgn(self):
        self.render_text("+", self.ml_pos, self.run.place_space)
        self.render_text("-", self.mr_pos, self.run.place_space)

    def render_rhombus(self):
        v1_pos = Direction.move(self.md_pos, Direction.turn(
            self.dc, 3), self.run.place_space * 0.75)
        v2_pos = Direction.move(self.md_pos, Direction.turn(
            self.dc, 1), self.run.place_space * 0.75)
        pygame.draw.aaline(self.run.screen, Color.black, v1_pos, self.m1_pos)
        pygame.draw.aaline(self.run.screen, Color.black, v1_pos, self.m2_pos)
        pygame.draw.aaline(self.run.screen, Color.black, v2_pos, self.m1_pos)
        pygame.draw.aaline(self.run.screen, Color.black, v2_pos, self.m2_pos)


class Resistance(Component):
    def __init__(self, R=0.0, **kwargs):
        super(Resistance, self).__init__(**kwargs)
        self.R = R

    def render(self):
        self.render_ends()
        self.render_rect()
        self.render_arrow()
        self.render_text(u"{}\u03a9".format(self.R), self.md_pos,
                         self.run.place_space * 0.35 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 0.35 + self.font_size / 2, True)


class CurrentSource(Component):
    def __init__(self, I=0.0, **kwargs):
        super(CurrentSource, self).__init__(**kwargs)
        self.I = I

    def render(self):
        self.render_ends()
        self.render_circle()
        self.render_vertical_line(self.run.place_space)
        self.render_arrow()
        self.render_text("{}A".format(self.I), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2, True)


class VoltageSource(Component):
    def __init__(self, U=0.0, **kwargs):
        super(VoltageSource, self).__init__(**kwargs)
        self.U = U

    def render(self):
        self.render_ends()
        self.render_circle()
        self.render_horizontal_line()
        self.render_sgn()
        self.render_arrow()
        self.render_text("{}V".format(self.U), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2, True)


class CCCS(Component):
    def __init__(self, A=0.0, cid=0, **kwargs):
        super(CCCS, self).__init__(**kwargs)
        self.A = A
        self.cid = cid

    def render(self):
        self.render_ends()
        self.render_rhombus()
        self.render_vertical_line(self.run.place_space * 0.75)
        self.render_arrow()
        self.render_text("{} I{}".format(self.A, self.cid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2, True)


class VCCS(Component):
    def __init__(self, A=0.0, ct_pos_id=0, ct_neg_id=0, **kwargs):
        super(VCCS, self).__init__(**kwargs)
        self.A = A
        self.ct_pos_id = ct_pos_id
        self.ct_neg_id = ct_neg_id

    def render(self):
        self.render_ends()
        self.render_rhombus()
        self.render_vertical_line(self.run.place_space * 0.75)
        self.render_arrow()
        self.render_text("{} U{},{}".format(self.A, self.ct_pos_id, self.ct_neg_id), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2, True)


class CCVS(Component):
    def __init__(self, A=0.0, cid=0, **kwargs):
        super(CCVS, self).__init__(**kwargs)
        self.A = A
        self.cid = cid

    def render(self):
        self.render_ends()
        self.render_rhombus()
        self.render_horizontal_line()
        self.render_sgn()
        self.render_arrow()
        self.render_text("{} I{}".format(self.A, self.cid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2, True)


class VCVS(Component):
    def __init__(self, A=0.0, ct_pos_id=0, ct_neg_id=0, **kwargs):
        super(VCVS, self).__init__(**kwargs)
        self.A = A
        self.ct_pos_id = ct_pos_id
        self.ct_neg_id = ct_neg_id

    def render(self):
        self.render_ends()
        self.render_rhombus()
        self.render_horizontal_line()
        self.render_sgn()
        self.render_arrow()
        self.render_text("{} U{},{}".format(self.A, self.ct_pos_id, self.ct_neg_id), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2)
        self.render_text("#{}".format(self.eid), self.md_pos,
                         self.run.place_space * 1.1 + self.font_size / 2, True)


class Wire(Component):
    '''Required parameters: run, pos_id, neg_id'''

    def __init__(self, **kwargs):
        super(Wire, self).__init__(**kwargs, st_pos=None, dc=None)
        self.pts = []

    def start_at(self, pos_id):
        self.pos_id = pos_id

    def end_at(self, neg_id):
        self.neg_id = neg_id

    def add_point(self, pos):
        self.pts.append(pos)

    def render(self):
        if len(self.pts) >= 2:
            pygame.draw.aalines(self.run.screen, Color.black, False, self.pts)
