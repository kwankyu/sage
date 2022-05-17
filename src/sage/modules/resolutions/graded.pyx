"""
Graded free resolutions

This module defines :class:`GradedFreeResolution` which computes a
graded free resolution of an ideal `I` with respect to a grading given to
the multi-variate polynomial ring `S`, of which `I` is a homogeneous ideal. The
output free resolution is always minimal.

The degrees given to the variables of `S` are integers or integer vectors of
the same length. In the latter case, the resolution is also called multigraded
free resolution. The standard grading where all variables have degree `1` is
used if the degrees are not specified.

The computation of the resolution is done by the libSingular behind. Different
Singular algorithms can be chosen for best performance.

EXAMPLES::

    sage: from sage.modules.resolutions.graded import GradedFreeResolution
    sage: P.<x,y,z,w> = PolynomialRing(QQ)
    sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
    sage: r = GradedFreeResolution(I, algorithm='minimal')
"""

from sage.libs.singular.decl cimport *
from sage.libs.singular.decl cimport ring
from sage.libs.singular.function cimport Resolution, new_sage_polynomial, access_singular_ring
from sage.structure.sequence import Sequence, Sequence_generic
from sage.libs.singular.function import singular_function
from sage.matrix.constructor import matrix as Matrix
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing

from .free import FreeResolution


class GradedFreeResolution(FreeResolution):
    """
    Graded free resolutions of ideals of multi-variate polynomial rings.

    INPUT:

    - ``ideal`` -- a homogeneous ideal of a multi-variate polynomial ring

    - ``degree`` -- list of integers or integer vectors

    - ``algorithm`` -- Singular algorithm to compute a resolution of ``ideal``

    OUTPUT: a graded minimal free resolution of the ideal

    The ``degrees`` specify degrees of the variables of the multi-variate
    polynomial ring `S` of which ``ideal`` is a homogeneous ideal.

    The available algorithms and the corresponding Singular commands are shown
    below:

    ============= ============================
    algorithm     Singular commands
    ============= ============================
    ``minimal``   ``mres(ideal)``
    ``shreyer``   ``minres(sres(std(ideal)))``
    ``standard``  ``minres(nres(std(ideal)))``
    ``heuristic`` ``minres(res(std(ideal)))``
    ============= ============================

    EXAMPLES::

        sage: from sage.modules.resolutions.graded import GradedFreeResolution
        sage: P.<x,y,z,w> = PolynomialRing(QQ)
        sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
        sage: r = GradedFreeResolution(I)
        sage: r
        S(-(0)) <- S(-(2))⊕S(-(2))⊕S(-(2)) <- S(-(3))⊕S(-(3))
    """
    def __init__(self, ideal, degrees=None, algorithm='shreyer'):
        cdef int i, j, k, ncols, nrows
        cdef list res_betti, prev_grade, grade

        S = ideal.ring()
        ng = S.ngens()

        if degrees is None:
            degrees = ng*[vector([1])]  # standard grading

        if len(degrees) != ng:
            raise ValueError('the length of degrees does not match the number of generators')

        if degrees[0] in ZZ:
            zero_deg = 0
        else:  # degrees are integer vectors
            zero_deg = degrees[0].parent().zero()

        # This ensures the first component of the Singular resolution to be a
        # module, like the later components. This is important when the
        # components are converted to Sage modules.
        module = singular_function("module")
        mod = module(ideal)

        if algorithm == 'minimal':
            mres = singular_function('mres')  # syzygy method
            r = mres(mod, 0)
        elif algorithm == 'shreyer':
            std = singular_function('std')
            sres = singular_function('sres')  # Shreyer method
            minres = singular_function('minres')
            r = minres(sres(std(mod), 0))
        elif algorithm == 'standard':
            nres = singular_function('nres')  # standard basis method
            minres = singular_function('minres')
            r = minres(nres(mod, 0))
        elif algorithm == 'heuristic':
            std = singular_function('std')
            res = singular_function('res')    # heuristic method
            minres = singular_function('minres')
            r = minres(res(std(mod), 0))

        res_mats, res_degs = to_sage_resolution(r, degrees)

        # compute graded Betti numbers
        res_betti = []
        prev_grade = [zero_deg]
        for k in range(len(res_degs)):
            grade = []
            degs = res_degs[k]
            ncols = len(degs)
            for j in range(ncols):
                col = degs[j]
                nrows = len(col)
                # should be enough to compute the graded Betti number
                # from any one entry of the column vector
                for i in range(nrows):
                    d = col[i]
                    if d is not None:
                        e = prev_grade[i]
                        grade.append(d + e)
                        break
            res_betti.append(grade)
            prev_grade = grade

        self.base = (S, zero_deg)
        self.ideal = ideal
        self.degrees = degrees
        self.length = len(res_mats)
        self.res_mats = res_mats
        self.res_degs = res_degs
        self.res_betti = res_betti

    def __repr__(self):
        S, shift = self.base
        s = f'S(-{shift})'
        for i in range(self.length):
            shifts = self.res_betti[i]
            if len(shifts) > 0:
                for j in range(len(shifts)):
                    shift = shifts[j]
                    if j == 0:
                        m = f'S(-{shift})'
                    else:
                        m += f'\u2295S(-{shift})'
            else:
                m = '0'
            s += ' <- ' + m
        return s

    def __len__(self):
        """
        EXAMPLES::

            sage: from sage.modules.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
            sage: len(r)
            2
        """
        return self.length

    def __getitem__(self, i):
        """
        EXAMPLES::

            sage: from sage.modules.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
            sage: r[0]
            (Ambient free module of rank 1 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field,
             [(0)])
            sage: r[1]
            (Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field,
             [(2), (2), (2)])
            sage: r[2]
            (Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field,
             [(3), (3)])
            sage: r[3]
            (Ambient free module of rank 0 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field,
             [])
        """
        S, zero_deg = self.base
        if i == 0:
            shifts = [zero_deg]
        elif i > 0:
            if i > self.length:
                shifts = []
            else:
                shifts = self.res_betti[i - 1]
        else:
            raise IndexError('invalid index')

        return S**len(shifts), shifts

    def matrix(self, i):
        """
        EXAMPLES::

            sage: from sage.modules.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
        """
        if i <= 0 or i > self.length:
            raise IndexError(f'valid indices are from 0 to {self.length}')

        return self.res_mats[i - 1]

    def map(self, i):
        """
        EXAMPLES::

            sage: from sage.modules.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
            sage: r.map(1)
            Free module morphism defined by the matrix
            [z^2 - y*w]
            [y*z - x*w]
            [y^2 - x*z]
            Domain: Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Codomain: Ambient free module of rank 1 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            sage: r.map(2)
            Free module morphism defined by the matrix
            [-y  z -w]
            [ x -y  z]
            Domain: Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Codomain: Ambient free module of rank 3 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            sage: r.map(3)
            Free module morphism defined by the matrix
            []
            Domain: Ambient free module of rank 0 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
            Codomain: Ambient free module of rank 2 over the integral domain Multivariate Polynomial Ring in x, y, z, w over Rational Field
        """
        source, _ = self[i]
        target, _ = self[i - 1]
        if i <= 0:
            raise IndexError('invalid index')
        elif i <= self.length:
            return source.hom(self.matrix(i).transpose(), target)
        else:
            return source.hom(0, target)

    def K_polynomial(self):
        """
        EXAMPLES::

            sage: from sage.modules.resolutions.graded import GradedFreeResolution
            sage: P.<x,y,z,w> = PolynomialRing(QQ)
            sage: I = P.ideal([y*w - z^2, -x*w + y*z, x*z - y^2])
            sage: r = GradedFreeResolution(I)
        """
        n = self.degrees[0].degree()
        L = LaurentPolynomialRing(ZZ, 't', n)

        Kpoly = 1
        sign = -1
        for j in range(self.length):
            for v in self.res_betti[j]:
                Kpoly += sign * L.monomial(*list(v))
            sign = -sign

        return Kpoly


cdef to_sage_resolution(Resolution res, degrees):
    """
    Pull from Singular resolution ``res`` the data to construct Sage
    resolution.

    INPUT:

    - ``res`` -- Singular resolution

    - ``degrees`` -- list of integers or integer vectors

    The procedure is destructive, and ``res`` is not usable afterward.
    """
    cdef ring *singular_ring
    cdef syStrategy singular_res
    cdef poly *p
    cdef poly *p_iter
    cdef poly *first
    cdef poly *previous
    cdef poly *acc
    cdef resolvente mods
    cdef ideal *mod
    cdef int i, j, k, idx, rank, nrows, ncols
    cdef int ngens = len(degrees)
    cdef bint zero_mat

    singular_res = res._resolution[0]
    sage_ring = res.base_ring
    singular_ring = access_singular_ring(res.base_ring)

    if singular_res.minres != NULL:
        mods = singular_res.minres
    elif singular_res.fullres != NULL:
        mods = singular_res.fullres
    else:
        raise ValueError('Singular resolution is not usable')

    res_mats = []
    res_degs = []

    # length is the length of fullres. The length of minres
    # can be shorter. Hence we avoid SEGFAULT by stopping
    # at NULL pointer.
    for idx in range(singular_res.length):
        mod = <ideal *> mods[idx]
        if mod == NULL:
            break
        rank = mod.rank
        free_module = sage_ring ** rank
        l = []

        nrows = rank
        ncols = IDELEMS(mod)

        mat = Matrix(sage_ring, nrows, ncols)
        matdegs = []
        zero_mat = True
        for j in range(ncols):
            p = <poly *> mod.m[j]
            degs = []
            # code below copied and modified from to_sage_vector_destructive
            # in sage.libs.singular.function.Converter
            for i in range(1, rank + 1):
                previous = NULL
                acc = NULL
                first = NULL
                p_iter = p
                while p_iter != NULL:
                    if p_GetComp(p_iter, singular_ring) == i:
                        p_SetComp(p_iter, 0, singular_ring)
                        p_Setm(p_iter, singular_ring)
                        if acc == NULL:
                            first = p_iter
                        else:
                            acc.next = p_iter
                        acc = p_iter
                        if p_iter == p:
                            p = pNext(p_iter)
                        if previous != NULL:
                            previous.next = pNext(p_iter)
                        p_iter = pNext(p_iter)
                        acc.next = NULL
                    else:
                        previous = p_iter
                        p_iter = pNext(p_iter)

                # degree of a homogeneous polynomial can be computed from the
                # first monomial
                if first != NULL:
                    exps = singular_monomial_exponents(first, singular_ring)
                    deg = 0
                    for k in range(ngens):
                        deg += exps[k] * degrees[k]
                    degs.append(deg)
                else:
                    degs.append(None)

                mat[i - 1, j] = new_sage_polynomial(sage_ring, first)

            matdegs.append(degs)

            if zero_mat:
                zero_mat = all(d is None for d in degs)

        # Singular sometimes leaves zero matrix in the resolution. We can finish
        # when one is seen.
        if zero_mat:
            break

        res_mats.append(mat)
        res_degs.append(matdegs)

    return res_mats, res_degs


cdef singular_monomial_exponents(poly *p, ring *r):
    """
    Return the list of exponents of monomial ``p``.
    """
    cdef int v
    cdef list ml = list()

    for v in range(1, r.N + 1):
        ml.append(p_GetExp(p, v, r))
    return ml
