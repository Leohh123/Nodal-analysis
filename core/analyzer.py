from sympy import solve
from .common import Var, Direction
from .element import CurrentSource, VoltageSource, CCCS, VCCS, CCVS, VCVS


source_list = (CurrentSource, VoltageSource, CCCS, VCCS, CCVS, VCVS)


class Analyzer(object):
    def __init__(self, node_count, elements):
        self.node_count = node_count
        self.elements = elements
        self.edges = [[] for i in range(self.node_count)]
        for e in elements:
            self.edges[e.pos_id].append([e.neg_id, e.eid, Direction.forward])
            self.edges[e.neg_id].append([e.pos_id, e.eid, Direction.backward])
        self.equation_set = []

    def run(self):
        for cur_nid in range(1, self.node_count):
            self_g, each_eq, current_in = 0, 0, 0
            for to_nid, cur_eid, dc in self.edges[cur_nid]:
                elem = self.elements[cur_eid]
                self_g += elem.G
                if to_nid != 0:
                    each_eq += elem.G * Var.un(to_nid)
                if isinstance(elem, source_list):
                    if dc == Direction.forward:
                        current_in -= elem.I
                    else:
                        current_in += elem.I
            tmp_eq = self_g * Var.un(cur_nid) - each_eq - current_in
            self.equation_set.append(tmp_eq)
        vars_ = [Var.un(i) for i in range(1, self.node_count)]
        for e in self.elements:
            if e.add_eq is not None:
                self.equation_set.append(e.add_eq)
                vars_.append(Var.i(e.eid))
        return solve(self.equation_set, vars_)

    @staticmethod
    def get_data(result):
        if result is None:
            return None
        res_list = filter(lambda x: str(x[0])[0] == "U", list(result.items()))
        return list(map(lambda x: [str(x[0]), float(x[1])], res_list))
