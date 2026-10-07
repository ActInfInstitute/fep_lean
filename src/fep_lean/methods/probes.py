"""Deterministic mathematical boundary probes; explanatory non-proof evidence."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any


class BoundaryProbeError(ValueError):
    """A probability, support, or floating-point range contract failed."""


def bernoulli_fisher(parameter: float) -> float:
    """Evaluate the regular interior Bernoulli Fisher weight; reject singular endpoints."""
    if not math.isfinite(parameter) or not 0 < parameter < 1:
        raise BoundaryProbeError("Bernoulli Fisher needs 0 < p < 1")
    information = 1 / (parameter * (1 - parameter))
    if not math.isfinite(information):
        raise BoundaryProbeError(
            "interior Bernoulli Fisher exceeds the representable float range"
        )
    return information


def _law_pair(p: Sequence[float], q: Sequence[float]) -> None:
    if not p or len(p) != len(q):
        raise BoundaryProbeError("law comparison needs equal nonempty supports")
    for law in (p, q):
        if any(not math.isfinite(x) or x < 0 for x in law) or not math.isclose(
            math.fsum(law), 1, rel_tol=0, abs_tol=1e-12
        ):
            raise BoundaryProbeError("numeric law must be normalized and nonnegative")


def finite_kl_totalized(p: Sequence[float], q: Sequence[float]) -> float:
    """Mirror q*klFun(p/q), with totalized division, for an explanatory probe."""
    _law_pair(p, q)
    terms = []
    for source, reference in zip(p, q, strict=True):
        if reference == 0:
            terms.append(0.0)
        elif source == 0:
            terms.append(reference)
        else:
            # Algebraically the same supported integrand without ratio overflow.
            log_ratio = math.log(source) - math.log(reference)
            terms.append(math.fsum((source * log_ratio, -source, reference)))
    return math.fsum(terms)


def extended_kl(p: Sequence[float], q: Sequence[float]) -> float:
    """Conventional extended-real discrete KL with its support-failure boundary."""
    _law_pair(p, q)
    if any(
        source > 0 and reference == 0 for source, reference in zip(p, q, strict=True)
    ):
        return math.inf
    return math.fsum(
        source * (math.log(source) - math.log(reference))
        for source, reference in zip(p, q, strict=True)
        if source > 0
    )


def evaluate_boundary_probes() -> list[dict[str, Any]]:
    """Expose four finite diagnostic examples without claiming native verification."""
    extended_boundary = extended_kl((1.0, 0.0), (0.0, 1.0))
    law = [1 / 3, 1 / 3, 1 / 3]
    tangent = [1, -1, 0]
    return [
        {
            "id": "bernoulli-interior",
            "parameters": [0.5, 0.25, 0.01],
            "fisher": [bernoulli_fisher(p) for p in (0.5, 0.25, 0.01)],
            "boundary": "p=0 and p=1 rejected; no regular Fisher endpoint is inferred",
            "reading_anchor": "fep_fep038.FEP038.fep038_fisherMetric",
        },
        {
            "id": "kl-support-boundary",
            "source": [1.0, 0.0],
            "reference": [0.0, 1.0],
            "totalized_finite_kl": finite_kl_totalized((1.0, 0.0), (0.0, 1.0)),
            "extended_discrete_kl": "infinity"
            if math.isinf(extended_boundary)
            else extended_boundary,
            "interpretation": "Finite totalized KL cannot be substituted for native KL at disjoint support.",
            "reading_anchor": "FEP.FiniteInformation.finiteKL_disjoint_pointMass_totalized",
        },
        {
            "id": "fisher-chart-degeneracy",
            "law": law,
            "redundant_logit_information": [
                [2 / 9 if i == j else -1 / 9 for j in range(3)] for i in range(3)
            ],
            "logit_null_direction": [1, 1, 1],
            "simplex_tangent": tangent,
            "law_coordinate_tangent_norm_squared": sum(
                v * v / p for v, p in zip(tangent, law, strict=True)
            ),
            "interpretation": (
                "The redundant common-logit offset is null; the law-coordinate "
                "metric sum(v_i^2/p_i) is positive on this nonzero mass-zero tangent. "
                "These are different coordinate representations of the same family."
            ),
            "reading_anchor": "src/fep_lean/formal/geometric_optimization.lean",
        },
        {
            "id": "descent-does-not-identify",
            "objective": "f(x,y)=x^2",
            "update": "(x,y) -> (x/2,y)",
            "initial_states": [[1, 0], [1, 9]],
            "energy_sequence": [4.0 ** (-step) for step in range(6)],
            "distinct_limit_states": [[0, 0], [0, 9]],
            "interpretation": (
                "Both trajectories decrease the same objective but retain distinct "
                "unobserved coordinates. Descent alone does not establish "
                "identifiability or a unique state."
            ),
            "reading_anchor": "fep-032 exact scalar convergence versus additional latent coordinates",
        },
    ]


def classical_mds(vectors: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Deterministic two-dimensional classical MDS of binary feature assignments.

    Integer squared distances are authoritative. All derived arithmetic uses an
    80-digit Decimal context, a fixed largest-pivot Jacobi algorithm, and an
    explicit residual gate. Publication values are quantized to 24 decimal
    places with half-even rounding. Neither LAPACK nor platform libm determines
    these artifact bytes. Repeated axes remain interpretation-ambiguous.
    """
    from decimal import (
        ROUND_HALF_EVEN,
        Context,
        Decimal,
        DivisionByZero,
        InvalidOperation,
        Overflow,
        localcontext,
    )

    if not vectors or not vectors[0]:
        raise BoundaryProbeError("MDS requires nonempty rows and coordinates")
    width = len(vectors[0])
    if any(
        len(row) != width
        or any(type(value) is not int or value not in (0, 1) for value in row)
        for row in vectors
    ):
        raise BoundaryProbeError("MDS needs equal-width binary integer vectors")
    count = len(vectors)
    squared = [
        [sum(a != b for a, b in zip(left, right, strict=True)) for right in vectors]
        for left in vectors
    ]
    arithmetic = Context(
        prec=80,
        rounding=ROUND_HALF_EVEN,
        Emin=-999999,
        Emax=999999,
        capitals=1,
        clamp=0,
        traps=[InvalidOperation, DivisionByZero, Overflow],
    )
    with localcontext(arithmetic):
        zero, one = Decimal(0), Decimal(1)
        divisor = Decimal(count)
        means = [
            sum((Decimal(value) for value in row), zero) / divisor for row in squared
        ]
        grand_mean = sum(means, zero) / divisor
        gram = [
            [
                -(Decimal(squared[i][j]) - means[i] - means[j] + grand_mean) / 2
                for j in range(count)
            ]
            for i in range(count)
        ]
        norm_bound = max(sum((abs(value) for value in row), zero) for row in gram)
        residual_limit = Decimal("1e-60") * max(norm_bound, one)
        matrix = [row[:] for row in gram]
        basis = [[one if i == j else zero for j in range(count)] for i in range(count)]
        iteration_limit = max(1, 100 * count * count)
        residual = zero
        iterations = 0
        for iteration in range(iteration_limit):
            candidates = [
                (abs(matrix[i][j]), i, j)
                for i in range(count)
                for j in range(i + 1, count)
            ]
            residual, p, q = (
                max(candidates, key=lambda item: (item[0], -item[1], -item[2]))
                if candidates
                else (zero, 0, 0)
            )
            if residual <= residual_limit:
                iterations = iteration
                break
            off = matrix[p][q]
            theta = (matrix[q][q] - matrix[p][p]) / (2 * off)
            tangent = (one if theta >= 0 else -one) / (
                abs(theta) + (one + theta * theta).sqrt()
            )
            cosine = one / (one + tangent * tangent).sqrt()
            sine = tangent * cosine
            matrix[p][p] -= tangent * off
            matrix[q][q] += tangent * off
            matrix[p][q] = matrix[q][p] = zero
            for row in range(count):
                if row not in (p, q):
                    left, right = matrix[row][p], matrix[row][q]
                    matrix[row][p] = matrix[p][row] = cosine * left - sine * right
                    matrix[row][q] = matrix[q][row] = sine * left + cosine * right
                left, right = basis[row][p], basis[row][q]
                basis[row][p] = cosine * left - sine * right
                basis[row][q] = sine * left + cosine * right
        else:
            raise BoundaryProbeError(
                "deterministic MDS Jacobi residual did not converge within its fixed cap"
            )
        order = sorted(range(count), key=lambda index: (-matrix[index][index], index))
        values = [matrix[index][index] for index in order]
        basis = [[row[index] for index in order] for row in basis]
        # A symmetric residual with every off-diagonal <= r has spectral norm
        # <= (n-1)*r. This conservative diagnostic adds an explicit factor64;
        # it classifies numerical zero/repetition, never scientific acceptance.
        threshold = 64 * count * residual_limit
        if any(value < -threshold for value in values):
            raise BoundaryProbeError(
                "binary Euclidean MDS has a materially negative eigenvalue"
            )
        positive = [index for index, value in enumerate(values) if value > threshold]
        clusters: list[list[int]] = []
        for index in positive:
            if clusters and abs(values[index] - values[clusters[-1][0]]) <= threshold:
                clusters[-1].append(index)
            else:
                clusters.append([index])
        oriented: list[tuple[Decimal, list[Decimal]]] = []
        ambiguity = []
        orientation_threshold = 64 * count * Decimal("1e-60")
        quantum = Decimal("1e-24")

        def serialized(value: Decimal) -> float:
            rounded = value.quantize(quantum)
            return float(rounded) if rounded else 0.0

        for cluster in clusters:
            projector = [
                [
                    sum((basis[i][axis] * basis[j][axis] for axis in cluster), zero)
                    for j in range(count)
                ]
                for i in range(count)
            ]
            canonical: list[list[Decimal]] = []
            for row_index in range(count):
                candidate = [projector[row][row_index] for row in range(count)]
                for _pass in range(2):
                    for previous in canonical:
                        dot = sum(
                            (
                                left_value * right_value
                                for left_value, right_value in zip(
                                    previous, candidate, strict=True
                                )
                            ),
                            zero,
                        )
                        candidate = [
                            value - dot * previous_value
                            for value, previous_value in zip(
                                candidate, previous, strict=True
                            )
                        ]
                norm = sum((value * value for value in candidate), zero).sqrt()
                if norm <= orientation_threshold:
                    continue
                candidate = [value / norm for value in candidate]
                pivot = max(
                    range(count), key=lambda index: (abs(candidate[index]), -index)
                )
                if candidate[pivot] < 0:
                    candidate = [-value for value in candidate]
                canonical.append(candidate)
                if len(canonical) == len(cluster):
                    break
            if len(canonical) != len(cluster):
                raise BoundaryProbeError(
                    "cannot orient the MDS eigenspace at numeric precision"
                )
            representative = sum((values[index] for index in cluster), zero) / len(
                cluster
            )
            oriented.extend((representative, vector) for vector in canonical)
            if len(cluster) > 1:
                ambiguity.append(
                    {
                        "axis_indices": [index + 1 for index in cluster],
                        "multiplicity": len(cluster),
                        "eigenvalue_representative": serialized(representative),
                        "interpretation": "Rotationally ambiguous eigenspace; row-order projector basis is a display convention.",
                    }
                )
        points = [[zero, zero] for _row in vectors]
        for axis, (value, vector) in enumerate(oriented[:2]):
            for index in range(count):
                points[index][axis] = vector[index] * value.sqrt()
        residuals: list[Decimal] = []
        total: list[int] = []
        for left_index in range(count):
            for right_index in range(left_index + 1, count):
                distance = Decimal(squared[left_index][right_index]).sqrt()
                projected = sum(
                    (
                        (points[left_index][axis] - points[right_index][axis]) ** 2
                        for axis in range(2)
                    ),
                    zero,
                ).sqrt()
                residuals.append((distance - projected) ** 2)
                total.append(squared[left_index][right_index])
        denominator = sum(total)
        stress = (sum(residuals, zero) / denominator).sqrt() if denominator else zero
        positive_sum = sum((value for value, _vector in oriented), zero)
        return {
            "method": "classical MDS on explicit binary feature Euclidean distances",
            "distance_formula": "d(i,j)^2 = sum_k (z_ik - z_jk)^2 = Hamming mismatch count",
            "gram_formula": "B = -H D^2 H / 2; H = I - 11^T/n",
            "squared_distances": squared,
            "coordinates": [[serialized(value) for value in row] for row in points],
            "distances": [
                [serialized(Decimal(value).sqrt()) for value in row] for row in squared
            ],
            "eigenvalues": [serialized(value) for value in values],
            "eigenvalues_decimal": [format(value, ".60E") for value in values],
            "positive_rank": len(positive),
            "display_axis_eigenvalues": [
                serialized(value) for value, _vector in oriented[:2]
            ]
            + [0.0] * max(0, 2 - len(oriented)),
            "explained_positive_inertia": serialized(
                sum((value for value, _vector in oriented[:2]), zero) / positive_sum
            )
            if positive_sum
            else 0.0,
            "normalized_stress": serialized(stress),
            "stress_formula": "sqrt(sum_{i<j}(d_ij-dhat_ij)^2 / sum_{i<j}d_ij^2); zero denominator => 0",
            "numerical_zero_threshold": format(threshold, ".60E"),
            "threshold_scope": "64*n*Jacobi residual limit; spectral residual bound <=(n-1)*limit. Numerical rank/repetition diagnostic, not scientific/proof acceptance.",
            "eigensolver": {
                "algorithm": "80-digit Decimal largest-offdiagonal-pivot Jacobi; first row/column break exact ties",
                "iterations": iterations,
                "iteration_limit": iteration_limit,
                "offdiagonal_residual": format(residual, ".60E"),
                "residual_limit": format(residual_limit, ".60E"),
                "gram_norm_upper_bound": format(norm_bound, ".60E"),
                "converged": residual <= residual_limit,
            },
            "numerical_serialization": "Derived publication values: Decimal quantization to 24 decimal places, ROUND_HALF_EVEN, then IEEE float/JSON; full 60-decimal-exponent eigenspectrum retained separately. Exact binary vectors and integer squared distances are authoritative.",
            "eigenambiguity": ambiguity,
            "axis_convention": "Repeated-eigenspace projector columns, retained row order, reorthogonalized; greatest-absolute coordinate positive. Signs/orientations have no semantic meaning.",
            "zero_axis_policy": "Missing positive axes are identically zero; identical rows coincide. No fabricated spread or jitter.",
            "interpretation": "Distances compare authored feature assignments. They do not establish theorem equivalence, proof transfer, empirical similarity, or learned semantic embedding.",
        }
