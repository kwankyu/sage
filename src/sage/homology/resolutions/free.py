"""
Free resolutions

AUTHORS:

- Kwankyu Lee (2022-05-13): initial implementation
"""

from sage.structure.sage_object import SageObject
from sage.structure.element import Matrix

class FreeResolution(SageObject):
    """
    Base class of free resolutions.

    EXAMPLES::

        sage: from sage.homology.resolutions.free import FreeResolution
        sage: S.<x,y,z,w> = PolynomialRing(QQ)
        sage: I = S.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
        sage: M = S.quotient(I)
        sage: d0 = M.coerce_map_from(S)
        sage: m1 = matrix(S, 1, [z^2 - y*w, y*z - x*w, y^2 - x*z])
        sage: m2 = matrix(S, 3, [-y, x, z, -y, -w, z])
        sage: r = FreeResolution([d0, m1, m2], name='S')
        sage: r
        S^3 <-- S^1 <-- S^3 <-- 0
    """
    def __init__(self, maps, name='F'):
        self._base_ring = maps[1].base_ring()
        self._maps = maps
        self._name = name
        self._length = len(maps)

    def __repr__(self):
        s = self._repr_module(0)
        for i in range(1, self._length):
            s += ' <-- ' + self._repr_module(i)
        s += ' <-- 0'
        return s

    def _repr_module(self, i):
        if i == 0:
            r = self._maps[1].ncols()
            s = f'{self._name}^{r}'
            return s
        elif i >= self._length:
            s = '0'
        else:
            r = self._maps[i].nrows()
            if r > 0:
                s = f'{self._name}^{r}'
            else:
                s = '0'
        return s

    def __len__(self):
        return self._length - 1

    def __getitem__(self, i):
        if i < 0:
            raise IndexError('invalid index')
        elif i >= self._length:
            F = (self._base_ring)**0
        elif i == self._length - 1:
            F = (self._base_ring)**(self._maps[i].ncols())
        else:
            F = (self._base_ring)**(self._maps[i + 1].nrows())
        return F

    def target(self):
        return self._maps[0].codomain()

    def d(self, i):
        if i < 0:
            raise IndexError('invalid index')
        elif i == 0:
            m = self._maps[0]
        elif i == self._length:
            s = (self._base_ring)**0
            t = (self._base_ring)**(self._maps[i - 1].ncols())
            m = s.hom(0, t)
        elif i > self._length:
            s = (self._base_ring)**0
            t = (self._base_ring)**0
            m = s.hom(0, t)
        else:
            s = (self._base_ring)**(self._maps[i].ncols())
            t = (self._base_ring)**(self._maps[i].nrows())
            m = s.hom(self._maps[i].columns(), t)
        return m

    def matrix(self, i):
        """
        EXAMPLES::

            sage: from sage.homology.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
        """
        if i <= 0 or i >= self._length:
            raise IndexError(f'invalid index')
        return self._maps[i]

    def chain_complex(self):
        pass
