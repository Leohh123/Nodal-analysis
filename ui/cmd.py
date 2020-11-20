import pygame
from pygame.locals import *
from .widget import Textarea
from .common import Direction, Utils, UnionFind, ABOUT_INFO
from sys import exit
from .component import Resistance, CurrentSource, VoltageSource, CCCS, VCCS, CCVS, VCVS, Wire


class CMD(object):
    def __init__(self, run, logger, sidebar):
        self.run = run
        self.width = self.run.place_width
        self.height = self.run.cmd_height
        self.pos_x = 0
        self.pos_y = self.run.place_height
        self.font_size = int(self.height * 0.8)
        self.font = pygame.font.Font(self.run.font_path, self.font_size)
        self.textarea = Textarea(self.run, self.width, self.height, self.pos_x,
                                 self.pos_y, self.font, self, lambda x: "(cmd) {}".format(x))
        self.textarea.start()
        self.logger = logger
        self.sidebar = sidebar
        self.direction = Direction.right
        self.components = self.run.components
        self.wires = self.run.wires
        self.cur_component = None
        self.grid_eid = Utils.array2d(
            self.run.place_col, self.run.place_row, -1)
        self.grid_nid = Utils.array2d(
            self.run.place_col, self.run.place_row, -1)
        self.grid_vis = Utils.array2d(
            self.run.place_col, self.run.place_row, False)
        self.node_count = 0
        self.cur_wire = None
        self.is_numbered = False
        self.storage = []

    def solve(self, cmd):
        items = list(map(lambda s: s.lower(), cmd.strip().split()))
        try:
            assert self.cur_wire is None, "You are placing wires"
            assert len(items) > 0, "Empty Command"
            if items[0] in ["exit", "quit"]:
                self.logger.log("Bye")
                exit()
            elif items[0] in ["direction", "dc"]:
                if items[1] in ["u", "up"]:
                    self.direction = Direction.up
                elif items[1] in ["d", "down"]:
                    self.direction = Direction.down
                elif items[1] in ["l", "left"]:
                    self.direction = Direction.left
                elif items[1] in ["r", "right"]:
                    self.direction = Direction.right
                else:
                    raise Exception("Invalid direction")
                self.logger.log("Set direction: {}".format(self.direction))
            elif items[0] in ["select", "se"]:
                if items[1] == "r":
                    self.cur_component = Resistance
                elif items[1] == "cs":
                    self.cur_component = CurrentSource
                elif items[1] == "vs":
                    self.cur_component = VoltageSource
                elif items[1] == "cccs":
                    self.cur_component = CCCS
                elif items[1] == "vccs":
                    self.cur_component = VCCS
                elif items[1] == "ccvs":
                    self.cur_component = CCVS
                elif items[1] == "vcvs":
                    self.cur_component = VCVS
                elif items[1] == "w":
                    self.cur_component = Wire
                else:
                    raise Exception("Invalid component")
                self.logger.log("Select component: {}".format(
                    self.cur_component.__name__))
            elif items[0] == "set":
                eid = int(items[1])
                assert eid < len(self.components), "Invalid component ID"
                cur_comp = self.components[eid]
                if isinstance(cur_comp, Resistance):
                    cur_comp.R = float(items[2])
                elif isinstance(cur_comp, CurrentSource):
                    cur_comp.I = float(items[2])
                elif isinstance(cur_comp, VoltageSource):
                    cur_comp.U = float(items[2])
                elif isinstance(cur_comp, (CCCS, CCVS)):
                    assert int(items[3]) < len(self.components), \
                        "Invalid control element ID"
                    cur_comp.A = float(items[2])
                    cur_comp.cid = int(items[3])
                elif isinstance(cur_comp, (VCCS, VCVS)):
                    assert int(items[3]) < self.node_count and \
                        int(items[4]) < self.node_count, \
                        "Invalid node ID"
                    cur_comp.A = float(items[2])
                    cur_comp.ct_pos_id = int(items[3])
                    cur_comp.ct_neg_id = int(items[4])
                else:
                    raise Exception("Unknown component type")
                self.logger.log(
                    "Successfully update component #{}".format(eid))
            elif items[0] in ["debug", "dbg"]:
                self.logger.log(str(eval(" ".join(items[1:]))))
            elif items[0] == "clear":
                self.clear()
                self.logger.log("Cleared")
            elif items[0] in ["number", "num"]:
                if len(items) >= 3:
                    eid, polar = int(items[1]), items[2]
                    assert eid < len(self.components), "Invalid component ID"
                    assert polar in ["pos", "neg"], "Invalid polarity"
                    self.set_number([eid, polar])
                    self.logger.log(
                        "Numbered, and set #{}({}) as GND".format(eid, polar))
                else:
                    self.set_number()
                    self.logger.log("Numbered")
            elif items[0] == "run":
                self.calculate()
            elif items[0] in ["sp", "superposition"]:
                assert len(items) >= 2, "Empty result ID"
                rids = list(map(int, items[1:]))
                assert False not in [x < len(self.storage) for x in rids], \
                    "Invalid result ID"
                self.superposition(rids)
            elif items[0] in ["th", "thevenin"]:
                pos_id, neg_id = int(items[1]), int(items[2])
                assert pos_id < self.node_count and neg_id < self.node_count, \
                    "Invalid node ID"
                if len(items) >= 5:
                    ims = [float(items[3]), float(items[4])]
                    self.thevenin(pos_id, neg_id, ims)
                else:
                    self.thevenin(pos_id, neg_id)
            elif items[0] in ["pr", "print"]:
                rid = int(items[1])
                assert rid < len(self.storage), "Invalid result ID"
                self.print_result(**self.storage[rid])
                self.logger.log("Printed")
            elif items[0] == "about":
                self.print_info(ABOUT_INFO, "About:")
            else:
                raise Exception("Invalid command")
        except IndexError as err:
            self.logger.log("Error: Incorrect number of parameters")
        except Exception as err:
            self.logger.log("Error: {}".format(str(err)))

    def render(self):
        self.textarea.render()

    def key_down(self, event):
        self.textarea.key_down(event)

    def mouse_down(self, pos_x, pos_y):
        self.place(*self.run.get_placement(pos_x, pos_y))

    def ok_placement(self, nx, ny):
        return self.run.ok_placement(nx, ny) and not self.grid_vis[nx][ny]

    def ok_wire_ends(self, nx, ny):
        return self.run.ok_placement(nx, ny) and self.grid_nid[nx][ny] >= 0

    def ok_to_place_component(self, x, y, dc, dist=6):
        for i in range(dist + 1):
            nx, ny = Direction.move([x, y], dc, i)
            if not self.ok_placement(nx, ny):
                return False
        return True

    def placed_component(self, x, y, dc, pos_id, neg_id, eid, dist=6):
        for i in range(dist + 1):
            nx, ny = Direction.move([x, y], dc, i)
            self.grid_vis[nx][ny] = True
            if i == 0:
                self.grid_eid[nx][ny] = eid
                self.grid_nid[nx][ny] = pos_id
            elif i == dist:
                self.grid_eid[nx][ny] = eid
                self.grid_nid[nx][ny] = neg_id

    def place(self, place_x, place_y):
        try:
            if self.cur_component is None:
                raise Exception("You haven't select any components")
            if self.cur_component is Wire:
                if not self.run.ok_placement(place_x, place_y):
                    raise Exception("The wire cannot be placed here")
                nid = self.grid_nid[place_x][place_y]
                cur_pos = self.run.get_pos(place_x, place_y)
                if self.cur_wire is None:
                    if self.ok_wire_ends(place_x, place_y):
                        self.cur_wire = Wire(run=self.run, pos_id=0, neg_id=0)
                        self.cur_wire.add_point(cur_pos)
                        self.cur_wire.start_at(nid)
                        self.wires.append(self.cur_wire)
                        self.logger.log(
                            "Create a wire from position ({}, {})".format(place_x, place_y))
                    else:
                        raise Exception("The wire cannot start from here")
                else:
                    if self.ok_wire_ends(place_x, place_y):
                        self.cur_wire.add_point(cur_pos)
                        self.cur_wire.end_at(nid)
                        self.cur_wire = None
                        self.logger.log(
                            "The wire ends at position ({}, {})".format(place_x, place_y))
                    else:
                        if self.ok_placement(place_x, place_y):
                            self.cur_wire.add_point(cur_pos)
                            self.logger.log(
                                "Add a wire node at position ({}, {})".format(place_x, place_y))
                        else:
                            raise Exception("The wire cannot be placed here")
            else:
                if not self.ok_to_place_component(place_x, place_y, self.direction):
                    raise Exception("The component cannot be placed here")
                st_pos = self.run.get_pos(place_x, place_y)
                pos_id = self.node_count
                neg_id = self.node_count + 1
                eid = len(self.components)
                tmp_component = self.cur_component(
                    eid=eid, run=self.run, st_pos=st_pos, dc=self.direction, pos_id=pos_id, neg_id=neg_id)
                self.node_count += 2
                self.components.append(tmp_component)
                self.placed_component(
                    place_x, place_y, self.direction, pos_id, neg_id, eid)
            self.del_number()
        except Exception as err:
            self.logger.log("Error: {}".format(str(err)))

    def clear(self):
        self.components.clear()
        self.wires.clear()
        self.direction = Direction.right
        self.cur_component = None
        self.grid_eid = Utils.array2d(
            self.run.place_col, self.run.place_row, -1)
        self.grid_nid = Utils.array2d(
            self.run.place_col, self.run.place_row, -1)
        self.grid_vis = Utils.array2d(
            self.run.place_col, self.run.place_row, False)
        self.node_count = 0
        self.cur_wire = None
        self.is_numbered = False

    def set_number(self, ground=None):
        uf = UnionFind(self.node_count)
        for w in self.wires:
            uf.merge(w.pos_id, w.neg_id)
        self.node_count = uf.arrange()
        if ground is not None:
            eid, polar = ground
            nid = getattr(self.components[eid], "{}_id".format(polar))
            uf.set_tag(nid, 0)
        vis = [False for i in range(self.node_count)]
        for c in self.components:
            c.pos_id = uf.tag[c.pos_id]
            c.neg_id = uf.tag[c.neg_id]
            if not vis[c.pos_id]:
                c.display_pos()
                vis[c.pos_id] = True
            if not vis[c.neg_id]:
                c.display_neg()
                vis[c.neg_id] = True
        for w in self.wires:
            w.pos_id = uf.tag[w.pos_id]
            w.neg_id = uf.tag[w.neg_id]
        for i in range(self.run.place_col):
            for j in range(self.run.place_row):
                if self.grid_nid[i][j] >= 0:
                    self.grid_nid[i][j] = uf.tag[self.grid_nid[i][j]]
        self.is_numbered = True

    def del_number(self):
        for c in self.components:
            c.display_pos(False)
            c.display_neg(False)

    def get_data(self):
        elements = []
        for c in self.components:
            tmp = {
                "name": c.__class__.__name__,
                "args": [],
                "kwargs": {
                    "eid": c.eid,
                    "pos_id": c.pos_id,
                    "neg_id": c.neg_id
                }
            }
            if isinstance(c, Resistance):
                tmp["args"] = [c.R]
            elif isinstance(c, CurrentSource):
                tmp["args"] = [c.I]
            elif isinstance(c, VoltageSource):
                tmp["args"] = [c.U]
            elif isinstance(c, (CCCS, CCVS)):
                tmp["args"] = [c.A, c.cid]
            elif isinstance(c, (VCCS, VCVS)):
                tmp["args"] = [c.A, c.ct_pos_id, c.ct_neg_id]
            else:
                raise Exception("Unknown component type")
            elements.append(tmp)
        return {
            "node_count": self.node_count,
            "elements": elements
        }

    def print_result(self, result, title):
        units = {"R": u"\u03a9", "U": "V", "I": "A"}
        msg_list = list(map(lambda x: "{} = {:.2f} {}".format(
            x[0], x[1], units[x[0][0]]), result))
        self.sidebar.clear()
        self.sidebar.log_one(title)
        self.sidebar.log_all(msg_list)

    def print_info(self, msg_list, title=None):
        self.sidebar.clear()
        if title is not None:
            self.sidebar.log_one(title)
        self.sidebar.log_all(msg_list)

    def calculate(self):
        assert self.is_numbered, "You haven't numbered them yet"
        data = self.get_data()
        result = self.run.callback(data)
        if result is None:
            raise Exception(
                "Calculation error, please check the circuit connection")
        item = {
            "result": result,
            "title": "Result #{}:".format(len(self.storage))
        }
        self.print_result(**item)
        self.storage.append(item)
        self.logger.log("Analysis has been completed")

    def thevenin(self, pos_id, neg_id, ims=[1.0, 2.0]):
        assert self.is_numbered, "You haven't numbered them yet"
        assert len(ims) == 2, "Two impressed currents are required"
        assert ims[0] != ims[1], "The impressed currents cannot be the same"
        res_u = []
        for im in ims:
            data = self.get_data()
            cs_comp = {
                "name": CurrentSource.__name__,
                "args": [im],
                "kwargs": {
                    "eid": len(self.components),
                    "pos_id": neg_id,
                    "neg_id": pos_id
                }
            }
            data["elements"].append(cs_comp)
            tmp_res = self.run.callback(data)
            if tmp_res is None:
                raise Exception(
                    "Calculation error, please check the circuit connection")
            tmp_res.append(["U0", 0.0])
            res_dict = dict(tmp_res)
            sym_pos = "U{}".format(pos_id)
            sym_neg = "U{}".format(neg_id)
            assert sym_pos in res_dict and sym_neg in res_dict, \
                "Calculation error, please check the circuit connection"
            res_u.append(res_dict[sym_pos] - res_dict[sym_neg])
        uoc = (ims[0] * res_u[1] - ims[1] * res_u[0]) / (ims[0] - ims[1])
        req = (res_u[0] - res_u[1]) / (ims[0] - ims[1])
        item = {
            "result": [["Uoc", uoc], ["Req", req]],
            "title": "Thevenin's EC #{} of pos({}), neg({}):".format(len(self.storage), pos_id, neg_id)
        }
        self.print_result(**item)
        self.storage.append(item)
        self.logger.log(
            "The Thevenin's EC has been obtained with impressed currents: {:.2f} A, {:.2f} A".format(*ims))

    def superposition(self, rids):
        res_dict = dict(self.storage[rids[0]]["result"])
        for rid in rids[1:]:
            tmp_res = dict(self.storage[rid]["result"])
            assert Utils.same_keys(res_dict, tmp_res), \
                "The results do not have a unified format"
            for k, v in tmp_res.items():
                res_dict[k] += v
        result = list(res_dict.items())
        item = {
            "result": result,
            "title": "Superposition #{} of {}:".format(
                len(self.storage),
                ", ".join(["#{}".format(rid) for rid in rids])
            )
        }
        self.print_result(**item)
        self.storage.append(item)
        self.logger.log("Superposition completed")
