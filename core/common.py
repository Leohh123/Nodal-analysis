from sympy import symbols


class Var(object):
    @staticmethod
    def i(eid):
        return symbols("I{}".format(eid))

    @staticmethod
    def un(nid):
        if nid == 0:
            return 0
        return symbols("U{}".format(nid))

    @staticmethod
    def u(pos_id, neg_id):
        return Var.un(pos_id) - Var.un(neg_id)


class Direction(object):
    forward = "forward"
    backward = "backward"
