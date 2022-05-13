"""
Multi-graded Free Resolutions


"""

from .free import FreeResolution

class MultiGradedFreeResolution(FreeResolution):
    def __init__(self):
        pass

    def __len__(self):
        pass


def multi_graded_free_resolution(S, degrees):
    mres = I._singular_().res(0)

    L = PolynomialRing(ZZ, names='t1,t2')

    def degree(p):
        for exp in p.exponents():
            return (sum(exp[:gn]), sum(exp[gn:]))
        return -1

    bj = [(0,0)]
    data = [bj]
    for k in range(1, len(mres)):
        bi = []
        ri = mres[k].matrix().sage_matrix(S)
        m, n = ri.dimensions()
        for j in range(n):
            for i in range(m):
                if ri[i,j]:
                    d = degree(ri[i,j])
                    e = bj[i]
                    bi.append((d[0] + e[0], d[1] + e[1]))
                    break
        data.append(bi)
        bj = bi

    Kpoly = 0
    sign = 1
    for j in range(len(data)):
        for v in data[j]:
            Kpoly += sign * L.monomial(*v)
        sign = -sign

    t1, t2 = L.gens()
    poly = Kpoly.substitute({t1: 1 - t1, t2: 1 - t2})


