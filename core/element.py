from .common import Var
from sympy import Rational


class Element(object):
    def __init__(self, eid, pos_id, neg_id):
        self.eid = eid
        self.pos_id = pos_id
        self.neg_id = neg_id
        self.add_eq = None

    def set_args(self, R=0, U=0, I=0):
        self.R = R
        self.U = U
        self.I = I

    @property
    def G(self):
        if self.R == 0:
            return 0
        return Rational(1, self.R)


class Resistance(Element):
    def __init__(self, R, **kwargs):
        super(Resistance, self).__init__(**kwargs)
        self.set_args(I=Var.i(self.eid), R=R)
        self.add_eq = self.I * self.R - Var.u(self.pos_id, self.neg_id)


class CurrentSource(Element):
    def __init__(self, I, **kwargs):
        super(CurrentSource, self).__init__(**kwargs)
        self.set_args(I=I)


class VoltageSource(Element):
    def __init__(self, U, **kwargs):
        super(VoltageSource, self).__init__(**kwargs)
        self.set_args(I=Var.i(self.eid), U=U)
        self.add_eq = Var.u(self.pos_id, self.neg_id) - self.U


class CCCS(Element):
    def __init__(self, A, cid, **kwargs):
        super(CCCS, self).__init__(**kwargs)
        self.set_args(I=Var.i(self.eid))
        self.add_eq = self.I - A * Var.i(cid)


class VCCS(Element):
    def __init__(self, A, ct_pos_id, ct_neg_id, **kwargs):
        super(VCCS, self).__init__(**kwargs)
        self.set_args(I=Var.i(self.eid))
        self.add_eq = self.I - A * Var.u(ct_pos_id, ct_neg_id)


class CCVS(Element):
    def __init__(self, A, cid, **kwargs):
        super(CCVS, self).__init__(**kwargs)
        self.set_args(I=Var.i(self.eid), U=A * Var.i(cid))
        self.add_eq = Var.u(self.pos_id, self.neg_id) - self.U


class VCVS(Element):
    def __init__(self, A, ct_pos_id, ct_neg_id, **kwargs):
        super(VCVS, self).__init__(**kwargs)
        self.set_args(I=Var.i(self.eid), U=A * Var.u(ct_pos_id, ct_neg_id))
        self.add_eq = Var.u(self.pos_id, self.neg_id) - self.U
