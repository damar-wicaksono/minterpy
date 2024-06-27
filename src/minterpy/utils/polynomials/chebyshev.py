"""
This module provides computational routines relevant to polynomials
in the Chebyshev basis.
"""

import numpy as np
from scipy.special import eval_chebyt


def evaluate_chebyshev_monomials(
    xx: np.ndarray,
    exponents: np.ndarray,
) -> np.ndarray:
    """Evaluate the Chebyshev monomials at all query points.

    Parameters
    ----------
    xx : np.ndarray
        The array of query points of shape ``(k, m)`` at which the monomials
        are evaluated. The values must be in :math:`[-1, 1]^m`.
    exponents : np.ndarray
        The non-negative integer array of polynomial exponents (i.e., as
        multi-indices) of shape ``(N, m)``.

    Returns
    -------
    np.ndarray
        The value of each Chebyshev basis evaluated at each given point.
        The array is of shape ``(k, N)``.
    """
    # One-dimensional monomials in each dimension
    monomials = eval_chebyt(exponents[None, :, :], xx[:, None, :])

    # Multi-dimensional monomials by tensor product
    monomials = np.prod(monomials, axis=-1)

    return monomials


def evaluate_chebyshev_polynomials(
    xx: np.ndarray,
    exponents: np.ndarray,
    coefficients: np.ndarray,
) -> np.ndarray:
    """Evaluate polynomial(s) in the Chebyshev bases.

    Parameters
    ----------
    xx : np.ndarray
        The array of query points of shape ``(k, m)`` at which the monomials
        are evaluated. The values must be in :math:`[-1, 1]^m`.
    exponents : np.ndarray
        The non-negative integer array of polynomial exponents (i.e., as
        multi-indices) of shape ``(N, m)``.
    coefficients : np.ndarray
        The array of coefficients of the polynomials of shape ``(N, Np)``.
        Multiple sets of coefficients (``Np > 1``) indicate multiple Chebyshev
        polynomials evaluated at the same time at the same query points.
    Notes
    -----
    The Chebyshev Polynomial has domain [-1,1]
    """
    # Evaluate the monomials
    monomials = evaluate_chebyshev_monomials(xx, exponents)

    # Multiply with the coefficients
    results = monomials @ coefficients

    return results
