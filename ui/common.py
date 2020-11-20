class Color(object):
    white = [255, 255, 255]
    black = [0, 0, 0]
    grey = [128, 128, 128]
    red = [255, 0, 0]
    green = [0, 255, 0]
    blue = [0, 0, 255]
    transparency = [0, 0, 0, 0]


class Utils(object):
    @staticmethod
    def interval(l, r, x):
        return min(r, (max(l, x)))

    @staticmethod
    def in_interval(l, r, x):
        return l <= x and x <= r

    @staticmethod
    def array2d(x, y, default=None):
        return [[default for j in range(y)] for i in range(x)]

    @staticmethod
    def ordered_pair(x, y):
        return [x, y] if x <= y else [y, x]

    @staticmethod
    def same_keys(a, b):
        return sorted(list(a.keys())) == sorted(list(b.keys()))


class Direction(object):
    up = "up"
    down = "down"
    left = "left"
    right = "right"

    delta_x = {"up": 0, "down": 0, "left": -1, "right": 1}
    delta_y = {"up": -1, "down": 1, "left": 0, "right": 0}

    nxt = {"up": "right", "right": "down", "down": "left", "left": "up"}

    angle = {"right": 0, "up": 90, "left": 180, "down": 270}
    angle_text = {"right": 0, "up": 90, "left": 0, "down": 90}
    angle_none = {"right": 0, "up": 0, "left": 0, "down": 0}

    @staticmethod
    def move(st_pos, dc, step):
        pos_x = st_pos[0] + Direction.delta_x[dc] * step
        pos_y = st_pos[1] + Direction.delta_y[dc] * step
        return [pos_x, pos_y]

    @staticmethod
    def turn(dc, times):
        for i in range(times):
            dc = Direction.nxt[dc]
        return dc


class UnionFind(object):
    def __init__(self, n):
        self.n = n
        self.parent = [i for i in range(self.n)]
        self.tag = [-1 for i in range(self.n)]
        self.group_count = 0

    def find(self, x):
        result = x
        while self.parent[result] != result:
            result = self.parent[result]
        while x != result:
            tmp = self.parent[x]
            self.parent[x] = result
            x = tmp
        return result

    def merge(self, x, y):
        self.parent[self.find(x)] = self.find(y)

    def is_same(self, x, y):
        return self.find(x) == self.find(y)

    def arrange(self):
        for i in range(self.n):
            result = self.find(i)
            if self.tag[result] == -1:
                self.tag[result] = self.group_count
                self.group_count += 1
            if i != result:
                self.tag[i] = self.tag[result]
        return self.group_count

    def set_tag(self, x, new_tag):
        old_tag = self.tag[x]
        if old_tag == new_tag:
            return
        for i in range(self.n):
            if self.tag[i] == old_tag:
                self.tag[i] = new_tag
            elif self.tag[i] == new_tag:
                self.tag[i] = old_tag


ABOUT_INFO = [
    "Thank you for your interest in this project :)",
    "Developed by Leohh",
    "Github: https://github.com/Leohh123/Nodal-analysis"
]
