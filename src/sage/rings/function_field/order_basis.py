# sage.doctest:           optional - sage.modules           (because __init__ constructs a vector space)
# some tests are marked # optional - sage.libs.pari         (because they use finite fields)
r"""
Orders of function fields given by a basis over the maximal order of the base field
"""

#*****************************************************************************
#       Copyright (C) 2023 Kwankyu Lee <ekwankyu@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from .ideal import FunctionFieldIdeal, FunctionFieldIdeal_module, FunctionFieldIdealInfinite_module
from .order import FunctionFieldOrder, FunctionFieldOrderInfinite


class FunctionFieldOrder_basis(FunctionFieldOrder):
    """
    Order given by a basis over the maximal order of the base field.

    INPUT:

    - ``basis`` -- list of elements of the function field

    - ``check`` -- (default: ``True``) if ``True``, check whether the module
      that ``basis`` generates forms an order

    EXAMPLES::

        sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                             # optional - sage.libs.pari
        sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                              # optional - sage.libs.pari
        sage: O = L.equation_order(); O                                                             # optional - sage.libs.pari
        Order in Function field in y defined by y^4 + x*y + 4*x + 1

    The basis only defines an order if the module it generates is closed under
    multiplication and contains the identity element::

        sage: K.<x> = FunctionField(QQ)
        sage: R.<y> = K[]
        sage: L.<y> = K.extension(y^5 - (x^3 + 2*x*y + 1/x))                                        # optional - sage.libs.singular
        sage: y.is_integral()                                                                       # optional - sage.libs.singular
        False
        sage: L.order(y)                                                                            # optional - sage.libs.singular
        Traceback (most recent call last):
        ...
        ValueError: the module generated by basis (1, y, y^2, y^3, y^4) must be closed under multiplication

    The basis also has to be linearly independent and of the same rank as the
    degree of the function field of its elements (only checked when ``check``
    is ``True``)::

        sage: L.order(L(x))                                                                         # optional - sage.libs.singular
        Traceback (most recent call last):
        ...
        ValueError: basis (1, x, x^2, x^3, x^4) is not linearly independent
        sage: sage.rings.function_field.order.FunctionFieldOrder_basis((y,y,y^3,y^4,y^5))           # optional - sage.libs.singular
        Traceback (most recent call last):
        ...
        ValueError: basis (y, y, y^3, y^4, 2*x*y + (x^4 + 1)/x) is not linearly independent
    """
    def __init__(self, basis, check=True):
        """
        Initialize.

        TESTS::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: TestSuite(O).run()                                                                # optional - sage.libs.pari
        """
        if len(basis) == 0:
            raise ValueError("basis must have positive length")

        field = basis[0].parent()
        if len(basis) != field.degree():
            raise ValueError("length of basis must equal degree of field")

        FunctionFieldOrder.__init__(self, field, ideal_class=FunctionFieldIdeal_module)

        V, from_V, to_V = field.vector_space()

        R = V.base_field().maximal_order()
        self._module = V.span([to_V(b) for b in basis], base_ring=R)

        self._from_module= from_V
        self._to_module = to_V
        self._basis = tuple(basis)
        self._ring = field.polynomial_ring()
        self._populate_coercion_lists_(coerce_list=[self._ring])

        if check:
            if self._module.rank() != field.degree():
                raise ValueError("basis {} is not linearly independent".format(basis))
            if not to_V(field(1)) in self._module:
                raise ValueError("the identity element must be in the module spanned by basis {}".format(basis))
            if not all(to_V(a*b) in self._module for a in basis for b in basis):
                raise ValueError("the module generated by basis {} must be closed under multiplication".format(basis))

    def _element_constructor_(self, f):
        """
        Construct an element of this order from ``f``.

        INPUT:

        - ``f`` -- element

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: K.maximal_order()._element_constructor_(x)
            x
        """
        F = self.function_field()

        try:
            f = F(f)
        except TypeError:
            raise TypeError("unable to convert to an element of {}".format(F))

        V, fr_V, to_V = F.vector_space()
        f_vector = to_V(f)
        if f_vector not in self._module:
            raise TypeError("{} is not an element of {}".format(f_vector, self))

        return f

    def ideal_with_gens_over_base(self, gens):
        """
        Return the fractional ideal with basis ``gens`` over the
        maximal order of the base field.

        It is not checked that the ``gens`` really generates an ideal.

        INPUT:

        - ``gens`` -- list of elements of the function field

        EXAMPLES:

        We construct an ideal in a rational function field::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: I = O.ideal([y]); I
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: I * I
            Ideal (y^2) of Maximal order of Rational function field in y over Rational Field

        We construct some ideals in a nontrivial function field::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^2 - x^3 - 1)                                                # optional - sage.libs.pari
            sage: O = L.equation_order(); O                                                         # optional - sage.libs.pari
            Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I = O.ideal_with_gens_over_base([1, y]);  I                                       # optional - sage.libs.pari
            Ideal (1) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I.module()                                                                        # optional - sage.libs.pari
            Free module of degree 2 and rank 2 over
             Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0]
            [0 1]

        There is no check if the resulting object is really an ideal::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^2 - x^3 - 1)                                                # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: I = O.ideal_with_gens_over_base([y]); I                                           # optional - sage.libs.pari
            Ideal (y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: y in I                                                                            # optional - sage.libs.pari
            True
            sage: y^2 in I                                                                          # optional - sage.libs.pari
            False
        """
        F = self.function_field()
        S = F.base_field().maximal_order()

        gens = [F(a) for a in gens]

        V, from_V, to_V = F.vector_space()
        M = V.span([to_V(b) for b in gens], base_ring=S)

        return self.ideal_monoid().element_class(self, M)

    def ideal(self, *gens):
        """
        Return the fractional ideal generated by the elements in ``gens``.

        INPUT:

        - ``gens`` -- list of generators or an ideal in a ring which
          coerces to this order

        EXAMPLES::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O.ideal(y)
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: O.ideal([y,1/y]) == O.ideal(y,1/y) # multiple generators may be given as a list
            True

        A fractional ideal of a nontrivial extension::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: O = K.maximal_order()                                                             # optional - sage.libs.pari
            sage: I = O.ideal(x^2 - 4)                                                              # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^2 - x^3 - 1)                                                # optional - sage.libs.pari
            sage: S = L.equation_order()                                                            # optional - sage.libs.pari
            sage: S.ideal(1/y)                                                                      # optional - sage.libs.pari
            Ideal (1, (6/(x^3 + 1))*y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I2 = S.ideal(x^2-4); I2                                                           # optional - sage.libs.pari
            Ideal (x^2 + 3) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I2 == S.ideal(I)                                                                  # optional - sage.libs.pari
            True
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if isinstance(gens, FunctionFieldIdeal):
                    gens = gens.gens()
                else:
                    gens = [gens]
        K = self.function_field()

        return self.ideal_with_gens_over_base([b*K(g) for b in self.basis() for g in gens])

    def polynomial(self):
        """
        Return the defining polynomial of the function field of which this is an order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: O.polynomial()                                                                    # optional - sage.libs.pari
            y^4 + x*y + 4*x + 1
        """
        return self._field.polynomial()

    def basis(self):
        """
        Return a basis of the order over the maximal order of the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: O.basis()                                                                         # optional - sage.libs.pari
            (1, y, y^2, y^3)
        """
        return self._basis

    def free_module(self):
        """
        Return the free module formed by the basis over the maximal order
        of the base function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: O.free_module()                                                                   # optional - sage.libs.pari
            Free module of degree 4 and rank 4 over Maximal order of Rational
            function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
        """
        return self._module

    def coordinate_vector(self, e):
        """
        Return the coordinates of ``e`` with respect to the basis of the order.

        INPUT:

        - ``e`` -- element of the order or the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: f = (x + y)^3                                                                     # optional - sage.libs.pari
            sage: O.coordinate_vector(f)                                                            # optional - sage.libs.pari
            (x^3, 3*x^2, 3*x, 1)
        """
        return self._module.coordinate_vector(self._to_module(e), check=False)


class FunctionFieldOrderInfinite_basis(FunctionFieldOrderInfinite):
    """
    Order given by a basis over the infinite maximal order of the base field.

    INPUT:

    - ``basis`` -- elements of the function field

    - ``check`` -- boolean (default: ``True``); if ``True``, check the basis generates
      an order

    EXAMPLES::

        sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                             # optional - sage.libs.pari
        sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                              # optional - sage.libs.pari
        sage: O = L.equation_order_infinite(); O                                                    # optional - sage.libs.pari
        Infinite order in Function field in y defined by y^4 + x*y + 4*x + 1

    The basis only defines an order if the module it generates is closed under
    multiplication and contains the identity element (only checked when
    ``check`` is ``True``)::

        sage: O = L.order_infinite_with_basis([1, y, 1/x^2*y^2, y^3]); O                            # optional - sage.libs.pari
        Traceback (most recent call last):
        ...
        ValueError: the module generated by basis (1, y, 1/x^2*y^2, y^3) must be closed under multiplication

    The basis also has to be linearly independent and of the same rank as the
    degree of the function field of its elements (only checked when ``check``
    is ``True``)::

        sage: O = L.order_infinite_with_basis([1, y, 1/x^2*y^2, 1 + y]); O                          # optional - sage.libs.pari
        Traceback (most recent call last):
        ...
        ValueError: The given basis vectors must be linearly independent.

    Note that 1 does not need to be an element of the basis, as long as it is
    in the module spanned by it::

        sage: O = L.order_infinite_with_basis([1 + 1/x*y, 1/x*y, 1/x^2*y^2, 1/x^3*y^3]); O          # optional - sage.libs.pari
        Infinite order in Function field in y defined by y^4 + x*y + 4*x + 1
        sage: O.basis()                                                                             # optional - sage.libs.pari
        (1/x*y + 1, 1/x*y, 1/x^2*y^2, 1/x^3*y^3)
    """
    def __init__(self, basis, check=True):
        """
        Initialize.

        TESTS::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order_infinite()                                                   # optional - sage.libs.pari
            sage: TestSuite(O).run()                                                                # optional - sage.libs.pari
        """
        if len(basis) == 0:
            raise ValueError("basis must have positive length")

        field = basis[0].parent()
        if len(basis) != field.degree():
            raise ValueError("length of basis must equal degree of field")

        FunctionFieldOrderInfinite.__init__(self, field, ideal_class=FunctionFieldIdealInfinite_module)

        # function field element f is in this order if and only if
        # W.coordinate_vector(to(f)) in M
        V, fr, to = field.vector_space()
        R = field.base_field().maximal_order_infinite()
        W = V.span_of_basis([to(v) for v in basis])
        from sage.modules.free_module import FreeModule
        M = FreeModule(R, W.dimension())
        self._basis = tuple(basis)
        self._ambient_space = W
        self._module = M

        self._ring = field.polynomial_ring()
        self._populate_coercion_lists_(coerce_list=[self._ring])

        if check:
            if self._module.rank() != field.degree():
                raise ValueError("basis {} is not linearly independent".format(basis))
            if not W.coordinate_vector(to(field(1))) in self._module:
                raise ValueError("the identity element must be in the module spanned by basis {}".format(basis))
            if not all(W.coordinate_vector(to(a*b)) in self._module for a in basis for b in basis):
                raise ValueError("the module generated by basis {} must be closed under multiplication".format(basis))

    def _element_constructor_(self, f):
        """
        Construct an element of this order.

        INPUT:

        - ``f`` -- element

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O(x)
            x
            sage: O(1/x)
            Traceback (most recent call last):
            ...
            TypeError: 1/x is not an element of Maximal order of Rational function field in x over Rational Field
        """
        F = self.function_field()
        try:
            f = F(f)
        except TypeError:
            raise TypeError("unable to convert to an element of {}".format(F))

        V, fr_V, to_V = F.vector_space()
        W = self._ambient_space
        if not W.coordinate_vector(to_V(f)) in self._module:
            raise TypeError("{} is not an element of {}".format(f, self))

        return f

    def ideal_with_gens_over_base(self, gens):
        """
        Return the fractional ideal with basis ``gens`` over the
        maximal order of the base field.

        It is not checked that ``gens`` really generates an ideal.

        INPUT:

        - ``gens`` -- list of elements that are a basis for the ideal over the
          maximal order of the base field

        EXAMPLES:

        We construct an ideal in a rational function field::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: I = O.ideal([y]); I
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: I*I
            Ideal (y^2) of Maximal order of Rational function field in y over Rational Field

        We construct some ideals in a nontrivial function field::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^2 - x^3 - 1)                                                # optional - sage.libs.pari
            sage: O = L.equation_order(); O                                                         # optional - sage.libs.pari
            Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I = O.ideal_with_gens_over_base([1, y]);  I                                       # optional - sage.libs.pari
            Ideal (1) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I.module()                                                                        # optional - sage.libs.pari
            Free module of degree 2 and rank 2 over Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0]
            [0 1]

        There is no check if the resulting object is really an ideal::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^2 - x^3 - 1)                                                # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: I = O.ideal_with_gens_over_base([y]); I                                           # optional - sage.libs.pari
            Ideal (y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: y in I                                                                            # optional - sage.libs.pari
            True
            sage: y^2 in I                                                                          # optional - sage.libs.pari
            False
        """
        F = self.function_field()
        S = F.base_field().maximal_order_infinite()

        gens = [F(a) for a in gens]

        V, from_V, to_V = F.vector_space()
        M = V.span([to_V(b) for b in gens], base_ring=S) # not work

        return self.ideal_monoid().element_class(self, M)

    def ideal(self, *gens):
        """
        Return the fractional ideal generated by the elements in ``gens``.

        INPUT:

        - ``gens`` -- list of generators or an ideal in a ring which coerces
          to this order

        EXAMPLES::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O.ideal(y)
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: O.ideal([y,1/y]) == O.ideal(y,1/y) # multiple generators may be given as a list
            True

        A fractional ideal of a nontrivial extension::

            sage: K.<x> = FunctionField(QQ); R.<y> = K[]
            sage: O = K.maximal_order_infinite()
            sage: I = O.ideal(x^2-4)
            sage: L.<y> = K.extension(y^2 - x^3 - 1)                                                # optional - sage.libs.singular
            sage: S = L.order_infinite_with_basis([1, 1/x^2*y])                                     # optional - sage.libs.singular
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if isinstance(gens, FunctionFieldIdeal):
                    gens = gens.gens()
                else:
                    gens = [gens]
        K = self.function_field()

        return self.ideal_with_gens_over_base([b*K(g) for b in self.basis() for g in gens])

    def polynomial(self):
        """
        Return the defining polynomial of the function field of which this is an order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: O.polynomial()                                                                    # optional - sage.libs.pari
            y^4 + x*y + 4*x + 1
        """
        return self._field.polynomial()

    def basis(self):
        """
        Return a basis of this order over the maximal order of the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: O.basis()                                                                         # optional - sage.libs.pari
            (1, y, y^2, y^3)
        """
        return self._basis

    def free_module(self):
        """
        Return the free module formed by the basis over the maximal order of
        the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]                                         # optional - sage.libs.pari
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)                                          # optional - sage.libs.pari
            sage: O = L.equation_order()                                                            # optional - sage.libs.pari
            sage: O.free_module()                                                                   # optional - sage.libs.pari
            Free module of degree 4 and rank 4 over Maximal order of Rational
            function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
        """
        return self._module
