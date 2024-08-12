"""
LagrangePolynomial class
"""
from __future__ import annotations

from copy import deepcopy

import numpy as np

from typing import Optional

import minterpy as mp

from minterpy.core import Grid, MultiIndexSet
from minterpy.core.ABC import MultivariatePolynomialSingleABC
from minterpy.utils.polynomials.lagrange import integrate_monomials_lagrange
from minterpy.utils.verification import dummy, verify_domain
from minterpy.global_settings import ARRAY

__all__ = ["LagrangePolynomial"]


# TODO : poly2 can be of a different basis?
def _lagrange_add(
    poly1: MultivariatePolynomialSingleABC, poly2: MultivariatePolynomialSingleABC
) -> MultivariatePolynomialSingleABC:
    """Addition of two polynomials in Lagrange basis.


    :param poly1: First polynomial to be added.
    :type poly1: LagrangePolynomial
    :param poly2: Second polynomial to be added.
    :type poly2: LagrangePolynomial

    :return: The result of ``poly1 + poly2``
    :rtype: LagrangePolynomial

    """
    p1, p2 = _match_dims(poly1, poly2)
    if p1.has_matching_domain(p2):
        l2n_p1 = mp.LagrangeToNewton(p1)
        newt_p1 = l2n_p1()
        l2n_p2 = mp.LagrangeToNewton(p2)
        newt_p2 = l2n_p2()

        max_poly_degree = np.max(
            np.array([p1.multi_index.poly_degree, p2.multi_index.poly_degree])
        )
        max_lp_degree = np.max(
            np.array([p1.multi_index.lp_degree, p2.multi_index.lp_degree])
        )

        dim = p1.spatial_dimension  # must be the same for p2

        res_mi = MultiIndexSet.from_degree(dim, int(max_poly_degree), max_lp_degree)
        res_grid = Grid(res_mi)

        un = res_grid.unisolvent_nodes

        eval_p1 = newt_p1(un)
        eval_p2 = newt_p2(un)

        res_coeffs = eval_p1 + eval_p2

        return LagrangePolynomial(
            res_mi,
            res_coeffs,
            grid=res_grid,
            internal_domain=p1.internal_domain,
            user_domain=p1.user_domain,
        )
    else:
        raise NotImplementedError(
            "Addition is not implemented for lagrange polynomials with different domains"
        )


def _lagrange_sub(
    poly1: MultivariatePolynomialSingleABC, poly2: MultivariatePolynomialSingleABC
) -> MultivariatePolynomialSingleABC:
    """Subtraction of two polynomials in Lagrange basis.


    :param poly1: First polynomial from which will be substracted.
    :type poly1: LagrangePolynomial
    :param poly2: Second polynomial which is substracted.
    :type poly2: LagrangePolynomial

    :return: The result of ``poly1 - poly2``
    :rtype: LagrangePolynomial
    """
    p1, p2 = _match_dims(poly1, poly2)
    if p1.has_matching_domain(p2):
        l2n_p1 = mp.LagrangeToNewton(p1)
        newt_p1 = l2n_p1()
        l2n_p2 = mp.LagrangeToNewton(p2)
        newt_p2 = l2n_p2()

        max_poly_degree = np.max(
            np.array([p1.multi_index.poly_degree, p2.multi_index.poly_degree])
        )
        max_lp_degree = np.max(
            np.array([p1.multi_index.lp_degree, p2.multi_index.lp_degree])
        )

        dim = p1.spatial_dimension  # must be the same for p2

        res_mi = MultiIndexSet.from_degree(dim, int(max_poly_degree), max_lp_degree)
        res_grid = Grid(res_mi)

        un = res_grid.unisolvent_nodes

        eval_p1 = newt_p1(un)
        eval_p2 = newt_p2(un)

        res_coeffs = eval_p1 - eval_p2

        return LagrangePolynomial(
            res_mi,
            res_coeffs,
            grid=res_grid,
            internal_domain=p1.internal_domain,
            user_domain=p1.user_domain,
        )
    else:
        raise NotImplementedError(
            "Subtraction is not implemented for lagrange polynomials with different domains"
        )


def _lagrange_mul(
    poly1: MultivariatePolynomialSingleABC, poly2: MultivariatePolynomialSingleABC
) -> MultivariatePolynomialSingleABC:
    """Multiplication of two polynomials in Lagrange basis.


    :param poly1: First polynomial to be multiplied.
    :type poly1: LagrangePolynomial
    :param poly2: Second polynomial to be multiplied.
    :type poly2: LagrangePolynomial

    :return: The result of ``poly1 * poly2``
    :rtype: LagrangePolynomial
    """
    p1, p2 = _match_dims(poly1, poly2)
    if p1.has_matching_domain(p2):
        l2n_p1 = mp.LagrangeToNewton(p1)
        newt_p1 = l2n_p1()
        l2n_p2 = mp.LagrangeToNewton(p2)
        newt_p2 = l2n_p2()

        degree_poly1 = p1.multi_index.poly_degree
        degree_poly2 = p2.multi_index.poly_degree
        lpdegree_poly1 = p1.multi_index.lp_degree
        lpdegree_poly2 = p2.multi_index.lp_degree

        res_degree = int(degree_poly1 + degree_poly2)
        res_lpdegree = lpdegree_poly1 + lpdegree_poly2

        res_mi = MultiIndexSet.from_degree(
            p1.spatial_dimension, res_degree, res_lpdegree
        )
        res_grid = Grid(res_mi)

        un = res_grid.unisolvent_nodes

        eval_p1 = newt_p1(un)
        eval_p2 = newt_p2(un)

        res_coeffs = eval_p1 * eval_p2

        return LagrangePolynomial(
            res_mi,
            res_coeffs,
            grid=res_grid,
            internal_domain=p1.internal_domain,
            user_domain=p1.user_domain,
        )
    else:
        raise NotImplementedError(
            "Multiplication is not implemented for Lagrange polynomials with different domains"
        )


def _lagrange_integrate_over(
    poly: "LagrangePolynomial", bounds: np.ndarray
) -> np.ndarray:
    """Compute the definite integral of a polynomial in the Lagrange basis.

    Parameters
    ----------
    poly : LagrangePolynomial
        The polynomial of which the integration is carried out.
    bounds : :class:`numpy:numpy.ndarray`
        The bounds (lower and upper) of the definite integration, an ``(M, 2)``
        array, where ``M`` is the number of spatial dimensions.

    Returns
    -------
    :class:`numpy:numpy.ndarray`
        The integral value of the polynomial over the given domain.
    """
    quad_weights = compute_quad_weights_lagrange(poly, bounds)

    return quad_weights @ poly.coeffs


# TODO redundant
lagrange_generate_internal_domain = verify_domain
lagrange_generate_user_domain = verify_domain


class LagrangePolynomial(MultivariatePolynomialSingleABC):
    """Datatype to discribe polynomials in Lagrange base.

    A polynomial in Lagrange basis is the sum of so called Lagrange polynomials (each multiplied with a coefficient).
    A `single` Lagrange monomial is per definition 1 on one of the grid points and 0 on all others.

    Notes
    -----
    A polynomial in Lagrange basis is well defined also for multi indices which are lexicographically incomplete. This means that the corresponding Lagrange polynomials also form a basis in such cases. These Lagrange polynomials however will possess their special property of being 1 on a single grid point and 0 on all others, with respect to the given grid! This allows defining very "sparse" polynomials (few multi indices -> few coefficients), but which still fulfill additional constraints (vanish on additional grid points). Practically this can be achieved by storing a "larger" grid (defined on a larger set of multi indices). In this case the transformation matrices become non-square, since there are fewer Lagrange polynomials than there are grid points (<-> only some of the Lagrange polynomials of this basis are "active"). Conceptually this is equal to fix the "inactivate" coefficients to always be 0.

    .. todo::
        - provide a short definition of this base here.
    """

    _newt_coeffs_lagr_monomials: Optional[ARRAY] = None

    # Virtual Functions
    _add = staticmethod(_lagrange_add)
    _sub = staticmethod(_lagrange_sub)
    _mul = staticmethod(dummy)
    _div = staticmethod(dummy)  # type: ignore
    _pow = staticmethod(dummy)  # type: ignore
    _eval = staticmethod(dummy)  # type: ignore
    _iadd = staticmethod(dummy)

    _partial_diff = staticmethod(dummy)
    _diff = staticmethod(dummy)

    _integrate_over = staticmethod(_lagrange_integrate_over)

    generate_internal_domain = staticmethod(lagrange_generate_internal_domain)
    generate_user_domain = staticmethod(lagrange_generate_user_domain)


def _match_dims(poly1, poly2, copy=None):
    """Dimensional expansion of two polynomial in order to match their spatial_dimensions.

    Parameters
    ----------
    poly1 : CanonicalPolynomial
        First polynomial in canonical basis
    poly2 : CanonicalPolynomial
        Second polynomial in canonical basis
    copy : bool
        If True, work on deepcopies of the passed polynomials (doesn't change the input).
        If False, inplace expansion of the passed polynomials

    Returns
    -------
    (poly1,poly2) : (CanonicalPolynomial,CanonicalPolynomial)
        Dimensionally matched polynomials in the same order as input.

    Notes
    -----
    - Maybe move this to the MultivariatePolynomialSingleABC since it shall be avialable for all poly bases
    """
    if copy is None:
        copy = True

    if copy:
        p1 = deepcopy(poly1)
        p2 = deepcopy(poly2)
    else:
        p1 = poly1
        p2 = poly2

    dim1 = p1.multi_index.spatial_dimension
    dim2 = p2.multi_index.spatial_dimension
    if dim1 >= dim2:
        p2 = p2.expand_dim(dim1)
    else:
        p1 = p1.expand_dim(dim2)
    return p1, p2


def compute_quad_weights_lagrange(
    poly: LagrangePolynomial,
    bounds: np.ndarray,
) -> np.ndarray:
    """Compute the quadrature weights of a polynomial in the Lagrange basis.
    """
    # Get the relevant data from the polynomial instance
    exponents = poly.multi_index.exponents
    generating_points = poly.grid.generating_points
    # ...from the MultiIndexTree
    tree = poly.grid.tree
    split_positions = tree.split_positions
    subtree_sizes = tree.subtree_sizes
    masks = tree.stored_masks

    quad_weights = integrate_monomials_lagrange(
        exponents,
        generating_points,
        split_positions,
        subtree_sizes,
        masks,
        bounds,
    )

    return quad_weights
