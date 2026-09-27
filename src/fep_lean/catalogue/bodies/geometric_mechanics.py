"""Canonical Lean bodies for the geometric-mechanics-notation family."""

from __future__ import annotations

BODIES: dict[str, str] = {
    "fep-161": """import FepSketches.geometric_mechanics

namespace FEP161

open FEP.GeometricMechanics

/-- **The trace-term cancellation:** a skew matrix contracted against a
symmetric (Hessian-role) matrix has zero trace — the finite form of
`tr(Q ∇²F) = 0` under `Qᵀ = -Q`. -/
theorem fep161_skewTrace_eq_zero {n : ℕ} (Q H : Fin n → Fin n → ℝ)
    (hQ : SkewSymmetric Q) (hH : SymmetricOf H) : traceOf (mulOf Q H) = 0 :=
  FEP.GeometricMechanics.skewTrace_eq_zero Q H hQ hH

/-- **The quadratic-term cancellation:** a skew-symmetric matrix
annihilates its own quadratic form `gᵀ Q g = 0`. -/
theorem fep161_skewQuadratic_eq_zero {n : ℕ} (Q : Fin n → Fin n → ℝ)
    (g : Fin n → ℝ) (hQ : SkewSymmetric Q) : dot g (mulVec Q g) = 0 :=
  FEP.GeometricMechanics.skewQuadratic_eq_zero Q g hQ

end FEP161
""",
    "fep-162": """import FepSketches.geometric_mechanics

namespace FEP162

open FEP.GeometricMechanics

/-- **Discrete-Hessian symmetry (finite Clairaut):** the symmetrized
mixed-difference data is symmetric by construction, not by hypothesis. -/
theorem fep162_symmetrize_symmetric {n : ℕ} (H : Fin n → Fin n → ℝ) :
    SymmetricOf (symmetrize H) :=
  FEP.GeometricMechanics.symmetrize_symmetric H

/-- The trace cancellation holds against the constructed discrete Hessian
for arbitrary raw mixed-difference data. -/
theorem fep162_skewTrace_symmetrize_eq_zero {n : ℕ} (Q H : Fin n → Fin n → ℝ)
    (hQ : SkewSymmetric Q) : traceOf (mulOf Q (symmetrize H)) = 0 :=
  FEP.GeometricMechanics.skewTrace_symmetrize_eq_zero Q H hQ

/-- On already-symmetric data the symmetrization construction is the
identity: the discrete Hessian coincides with the given Hessian-role
matrix. -/
theorem fep162_symmetrize_of_symmetric {n : ℕ} (H : Fin n → Fin n → ℝ)
    (hH : SymmetricOf H) : symmetrize H = H :=
  FEP.GeometricMechanics.symmetrize_of_symmetric H hH

end FEP162
""",
    "fep-163": """import FepSketches.geometric_mechanics

namespace FEP163

open FEP.GeometricMechanics

/-- The finite `div(p* · Q g)/p*` from explicit directional derivative
data. -/
def fep163_weightedDivergence {n : ℕ} (Q H DQ : Fin n → Fin n → ℝ)
    (g dlogp : Fin n → ℝ) : ℝ :=
  FEP.GeometricMechanics.weightedDivergence Q H DQ g dlogp

/-- The raw Leibniz expansion: trace slot + `∇·Q` slot + `p*`-coupling
slot. -/
theorem fep163_weightedDivergence_eq {n : ℕ} (Q H DQ : Fin n → Fin n → ℝ)
    (g dlogp : Fin n → ℝ) :
    weightedDivergence Q H DQ g dlogp
      = traceOf (mulOf Q H) + dot (divQ DQ) g + dot (mulVec Q g) dlogp :=
  FEP.GeometricMechanics.weightedDivergence_eq Q H DQ g dlogp

/-- **The manuscript's three-term solenoidal identity** under the
stationary coupling `∇log p* = -∇F = -g`. -/
theorem fep163_solenoidal_expansion {n : ℕ} (Q H DQ : Fin n → Fin n → ℝ)
    (g dlogp : Fin n → ℝ) (hcoup : ∀ i, dlogp i = -g i) :
    weightedDivergence Q H DQ g dlogp
      = traceOf (mulOf Q H) - dot g (mulVec Q g) + dot (divQ DQ) g :=
  FEP.GeometricMechanics.solenoidal_expansion Q H DQ g dlogp hcoup

/-- The conditional solenoidal drop under the explicit orthogonality
hypothesis `g ⊥ (∇·Q)ᵀ`. -/
theorem fep163_solenoidal_drop_of_orthogonal {n : ℕ}
    (Q H DQ : Fin n → Fin n → ℝ) (g dlogp : Fin n → ℝ)
    (hQ : SkewSymmetric Q) (hH : SymmetricOf H)
    (hcoup : ∀ i, dlogp i = -g i) (horth : dot (divQ DQ) g = 0) :
    weightedDivergence Q H DQ g dlogp = 0 :=
  FEP.GeometricMechanics.solenoidal_drop_of_orthogonal Q H DQ g dlogp hQ hH hcoup horth

/-- The conditional solenoidal drop for spatially constant `Q`. -/
theorem fep163_solenoidal_drop_of_constantQ {n : ℕ}
    (Q H DQ : Fin n → Fin n → ℝ) (g dlogp : Fin n → ℝ)
    (hQ : SkewSymmetric Q) (hH : SymmetricOf H)
    (hcoup : ∀ i, dlogp i = -g i) (hconst : ∀ k l, DQ k l = 0) :
    weightedDivergence Q H DQ g dlogp = 0 :=
  FEP.GeometricMechanics.solenoidal_drop_of_constantQ Q H DQ g dlogp hQ hH hcoup hconst

/-- The concrete expansion remainder `(∇·Q)ᵀ g = 1 ≠ 0` on explicit
derivative data: without the extra hypothesis the drop genuinely fails. -/
theorem fep163_expansion_remainder_witness :
    dot (divQ remainderDQ) remainderG = 1 :=
  FEP.GeometricMechanics.expansion_remainder_witness

end FEP163
""",
    "fep-164": """import FepSketches.geometric_mechanics

namespace FEP164

open FEP.GeometricMechanics

/-- For skew `Q` the node divergence of the transport field is twice its
row sum: the discrete divergence slot is generically nonzero. -/
theorem fep164_nodeDiv_skew {n : ℕ} {Q : Fin n → Fin n → ℝ} (hQ : SkewSymmetric Q)
    (i : Fin n) : nodeDiv Q i = 2 * rowSum Q i :=
  FEP.GeometricMechanics.nodeDiv_skew hQ i

/-- **The graph decomposition** of the candidate current's node
divergence into the transport slot plus the discrete-divergence slot. -/
theorem fep164_graphDecomposition {n : ℕ} (Q : Fin n → Fin n → ℝ)
    (g : Fin n → ℝ) (hQ : SkewSymmetric Q) (i : Fin n) :
    nodeDiv (currentOf Q g) i = mulVec Q g i + g i * rowSum Q i :=
  FEP.GeometricMechanics.graphDecomposition Q g hQ i

/-- The exact finite Leibniz rule for the weighted node divergence. -/
theorem fep164_weightedNodeDiv_eq {n : ℕ} (W : Fin n → Fin n → ℝ)
    {p : Fin n → ℝ} (hp : ∀ i, 0 < p i) (i : Fin n) :
    weightedNodeDiv p W i =
      nodeDiv W i + ∑ j, (1 - p j / p i) * W j i :=
  FEP.GeometricMechanics.weightedNodeDiv_eq W hp i

/-- The three-term graph expansion of the weighted candidate current. -/
theorem fep164_weightedCurrent_div_eq {n : ℕ} (Q : Fin n → Fin n → ℝ)
    (g : Fin n → ℝ) {p : Fin n → ℝ} (hQ : SkewSymmetric Q)
    (hp : ∀ i, 0 < p i) (i : Fin n) :
    weightedNodeDiv p (currentOf Q g) i
      = mulVec Q g i + g i * rowSum Q i
        + g i * ∑ j, (1 - p j / p i) * Q j i :=
  FEP.GeometricMechanics.weightedCurrent_div_eq Q g hQ hp i

end FEP164
""",
    "fep-165": """import FepSketches.geometric_mechanics

namespace FEP165

open FEP.GeometricMechanics

/-- The manuscript honesty-guard transport matrix is skew. -/
theorem fep165_witnessQ_skew : SkewSymmetric witnessQ :=
  FEP.GeometricMechanics.witnessQ_skew

/-- The candidate current of the honesty guard: `Q g = (0, -1)`. -/
theorem fep165_witness_current :
    mulVec witnessQ witnessG = fun i => if i = 0 then 0 else -1 :=
  FEP.GeometricMechanics.witness_current

/-- The discrete divergence of the witness transport field is `(2, -2) ≠ 0`. -/
theorem fep165_witness_divQ :
    nodeDiv witnessQ = fun i => if i = 0 then 2 else -2 :=
  FEP.GeometricMechanics.witness_divQ

/-- The node divergence of the witness current is `(1, -1) ≠ 0`. -/
theorem fep165_witness_divergence :
    nodeDiv (currentOf witnessQ witnessG) = fun i => if i = 0 then 1 else -1 :=
  FEP.GeometricMechanics.witness_divergence

/-- **The unconditional solenoidal drop is FALSE:** on the exact 2-node
counterexample the node divergence of the candidate current is `1 ≠ 0`
at node `0`. -/
theorem fep165_witness_drop_fails : nodeDiv (currentOf witnessQ witnessG) 0 = 1 :=
  FEP.GeometricMechanics.witness_drop_fails

end FEP165
""",
}
