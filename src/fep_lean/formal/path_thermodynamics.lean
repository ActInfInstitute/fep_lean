import FepSketches.finite_markov_dynamics
import FepSketches.variational_duality

/-!
# Finite path-space stochastic thermodynamics

This module keeps every thermodynamic statement on normalized finite laws.
The reverse law is stored in the same path coordinate as the forward law;
`reversal` records the involution used to align the physical reverse path.
Log-ratio identities require strict support.  At a zero reverse rate Lean's
totalized real logarithm is exposed as a boundary value, not interpreted as
an extended-real entropy production.
-/

namespace FEP.PathThermodynamics

open FEP FEP.FiniteInformation FEP.FiniteMarkovDynamics
  FEP.VariationalDuality Finset
open scoped BigOperators

variable {Path State : Type*} [Fintype Path] [Fintype State]

/-! ## Normalized forward and reverse path laws -/

/-- A pair of normalized finite path laws together with an involutive path
reversal.  `reverseAligned` is already expressed in forward-path coordinates,
so it can serve directly as the denominator of a likelihood ratio. -/
structure FinitePathProtocol (Path : Type*) [Fintype Path] where
  forward : FiniteLaw Path
  reverseAligned : FiniteLaw Path
  reversal : Path → Path
  reversal_involutive : Function.Involutive reversal

/-- Applying the protocol reversal twice recovers the original path. -/
theorem reverse_reverse (protocol : FinitePathProtocol Path) (path : Path) :
    protocol.reversal (protocol.reversal path) = path :=
  protocol.reversal_involutive path

/-- Both path laws carry unit mass by construction. -/
theorem pathLaw_normalization (protocol : FinitePathProtocol Path) :
    (∑ path, protocol.forward path = 1) ∧
      ∑ path, protocol.reverseAligned path = 1 :=
  ⟨protocol.forward.sum_one, protocol.reverseAligned.sum_one⟩

/-- Forward-to-reverse path likelihood ratio.  Its logarithmic use below is
restricted to full support. -/
noncomputable def pathRatio
    (protocol : FinitePathProtocol Path) (path : Path) : ℝ :=
  protocol.forward path / protocol.reverseAligned path

/-- Under reverse support, multiplying the ratio by its denominator
reconstructs the forward path mass. -/
theorem pathRatio_mul_reverse
    (protocol : FinitePathProtocol Path)
    (hReverse : ∀ path, 0 < protocol.reverseAligned path) (path : Path) :
    pathRatio protocol path * protocol.reverseAligned path =
      protocol.forward path := by
  exact div_mul_cancel₀ _ (ne_of_gt (hReverse path))

/-- The totalized ratio is zero at a zero reverse atom.  Downstream theorems
must not read this boundary as an infinite extended-real log ratio. -/
theorem pathRatio_zero_reverse_boundary
    (protocol : FinitePathProtocol Path) (path : Path)
    (hZero : protocol.reverseAligned path = 0) :
    pathRatio protocol path = 0 := by
  simp [pathRatio, hZero]

/-! ## Entropy production and fluctuation identities -/

/-- Pathwise stochastic entropy production as a supported log ratio. -/
noncomputable def pathwiseEntropyProduction
    (protocol : FinitePathProtocol Path) (path : Path) : ℝ :=
  Real.log (pathRatio protocol path)

/-- Mean path entropy production is the finite KL divergence between the
forward and aligned reverse laws. -/
noncomputable def entropyProduction
    (protocol : FinitePathProtocol Path) : ℝ :=
  finiteKL protocol.forward protocol.reverseAligned

/-- Entropy production is nonnegative on the normalized finite carrier. -/
theorem entropyProduction_nonneg (protocol : FinitePathProtocol Path) :
    0 ≤ entropyProduction protocol :=
  finiteKL_nonneg protocol.forward protocol.reverseAligned

/-- With full support, expected pathwise log ratio is exactly path KL. -/
theorem entropyProduction_eq_expected_logRatio
    (protocol : FinitePathProtocol Path)
    (hForward : ∀ path, 0 < protocol.forward path)
    (hReverse : ∀ path, 0 < protocol.reverseAligned path) :
    entropyProduction protocol =
      ∑ path, protocol.forward path * pathwiseEntropyProduction protocol path := by
  rw [entropyProduction,
    finiteKL_eq_crossEntropy_sub_entropy protocol.forward
      protocol.reverseAligned hReverse]
  simp only [crossEntropy, entropy, pathwiseEntropyProduction, pathRatio]
  simp_rw [Real.negMulLog_eq_neg,
    Real.log_div (ne_of_gt (hForward _)) (ne_of_gt (hReverse _))]
  rw [← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro path _
  ring

/-- Detailed pathwise fluctuation identity: reverse mass multiplied by the
exponential entropy production is the forward mass. -/
theorem detailedFluctuation_identity
    (protocol : FinitePathProtocol Path)
    (hForward : ∀ path, 0 < protocol.forward path)
    (hReverse : ∀ path, 0 < protocol.reverseAligned path) (path : Path) :
    protocol.reverseAligned path *
        Real.exp (pathwiseEntropyProduction protocol path) =
      protocol.forward path := by
  have hRatio : 0 < pathRatio protocol path :=
    div_pos (hForward path) (hReverse path)
  rw [pathwiseEntropyProduction, Real.exp_log hRatio]
  unfold pathRatio
  field_simp [ne_of_gt (hReverse path)]

/-- Integral fluctuation theorem on a supported finite path space. -/
theorem integralFluctuation_eq_one
    (protocol : FinitePathProtocol Path)
    (hForward : ∀ path, 0 < protocol.forward path)
    (hReverse : ∀ path, 0 < protocol.reverseAligned path) :
    ∑ path, protocol.forward path *
        Real.exp (-pathwiseEntropyProduction protocol path) = 1 := by
  calc
    (∑ path, protocol.forward path *
        Real.exp (-pathwiseEntropyProduction protocol path)) =
        ∑ path, protocol.reverseAligned path := by
      apply Finset.sum_congr rfl
      intro path _
      have hRatio : 0 < pathRatio protocol path :=
        div_pos (hForward path) (hReverse path)
      rw [pathwiseEntropyProduction, Real.exp_neg, Real.exp_log hRatio]
      unfold pathRatio
      field_simp [ne_of_gt (hForward path), ne_of_gt (hReverse path)]
    _ = 1 := protocol.reverseAligned.sum_one

/-- Under the usual reversal exchange law, entropy production changes sign
when the path is reversed. -/
theorem pathwiseEntropyProduction_reverse
    (protocol : FinitePathProtocol Path)
    (hForward : ∀ path, 0 < protocol.forward path)
    (hReverse : ∀ path, 0 < protocol.reverseAligned path)
    (hExchangeForward : ∀ path,
      protocol.forward (protocol.reversal path) =
        protocol.reverseAligned path)
    (hExchangeReverse : ∀ path,
      protocol.reverseAligned (protocol.reversal path) =
        protocol.forward path)
    (path : Path) :
    pathwiseEntropyProduction protocol (protocol.reversal path) =
      -pathwiseEntropyProduction protocol path := by
  simp only [pathwiseEntropyProduction, pathRatio, hExchangeForward,
    hExchangeReverse]
  rw [Real.log_div (ne_of_gt (hReverse path)) (ne_of_gt (hForward path)),
    Real.log_div (ne_of_gt (hForward path)) (ne_of_gt (hReverse path))]
  ring

/-! ## Finite Jarzynski equality -/

/-- Exponential work average for a finite protocol. -/
noncomputable def exponentialWorkAverage
    (law : FiniteLaw Path) (beta : ℝ) (work : Path → ℝ) : ℝ :=
  ∑ path, law path * Real.exp (-beta * work path)

/-- Explicit normalization premise for a finite Jarzynski protocol.  It is
the finite expectation of `exp (-β (W - ΔF))`, with positive inverse
temperature recorded separately. -/
def HasJarzynskiNormalization
    (law : FiniteLaw Path) (beta deltaFreeEnergy : ℝ)
    (work : Path → ℝ) : Prop :=
  0 < beta ∧
    ∑ path, law path *
      Real.exp (-beta * (work path - deltaFreeEnergy)) = 1

/-- Finite Jarzynski equality derived from the explicit exponential-work
normalization premise. -/
theorem finiteJarzynski_eq
    (law : FiniteLaw Path) (beta deltaFreeEnergy : ℝ)
    (work : Path → ℝ)
    (hNormalization :
      HasJarzynskiNormalization law beta deltaFreeEnergy work) :
    exponentialWorkAverage law beta work =
      Real.exp (-beta * deltaFreeEnergy) := by
  have hFactor :
      Real.exp (beta * deltaFreeEnergy) *
          exponentialWorkAverage law beta work = 1 := by
    calc
      Real.exp (beta * deltaFreeEnergy) *
          exponentialWorkAverage law beta work =
          ∑ path, law path *
            Real.exp (-beta * (work path - deltaFreeEnergy)) := by
        rw [exponentialWorkAverage, Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro path _
        calc
          Real.exp (beta * deltaFreeEnergy) *
              (law path * Real.exp (-beta * work path)) =
              law path *
                (Real.exp (beta * deltaFreeEnergy) *
                  Real.exp (-beta * work path)) := by ring
          _ = law path *
                Real.exp (beta * deltaFreeEnergy + -beta * work path) := by
              rw [← Real.exp_add]
          _ = law path *
                Real.exp (-beta * (work path - deltaFreeEnergy)) := by
              congr 2
              ring
      _ = 1 := hNormalization.2
  calc
    exponentialWorkAverage law beta work =
        Real.exp (-beta * deltaFreeEnergy) *
          (Real.exp (beta * deltaFreeEnergy) *
            exponentialWorkAverage law beta work) := by
      rw [← mul_assoc, ← Real.exp_add]
      simp
    _ = Real.exp (-beta * deltaFreeEnergy) := by rw [hFactor, mul_one]

/-! ## Crooks relation as the source of the Jarzynski premise -/

/-- Pathwise Crooks relation in forward-path coordinates: the aligned reverse
path mass, reweighted by the exponential dissipated work `β (W - ΔF)`, is the
forward path mass.  Unlike `HasJarzynskiNormalization`, it is a per-path
microscopic statement rather than the averaged conclusion. -/
def HasCrooksRelation
    (protocol : FinitePathProtocol Path) (beta deltaFreeEnergy : ℝ)
    (work : Path → ℝ) : Prop :=
  0 < beta ∧ ∀ path,
    protocol.reverseAligned path *
        Real.exp (beta * (work path - deltaFreeEnergy)) =
      protocol.forward path

/-- The pathwise Crooks relation implies the Jarzynski normalization premise:
weighting it by `exp (-β (W - ΔF))` returns the reverse law's unit mass.  No
support hypothesis is needed. -/
theorem hasJarzynskiNormalization_of_crooks
    (protocol : FinitePathProtocol Path) (beta deltaFreeEnergy : ℝ)
    (work : Path → ℝ)
    (hCrooks : HasCrooksRelation protocol beta deltaFreeEnergy work) :
    HasJarzynskiNormalization protocol.forward beta deltaFreeEnergy work := by
  refine ⟨hCrooks.1, ?_⟩
  calc
    (∑ path, protocol.forward path *
        Real.exp (-beta * (work path - deltaFreeEnergy))) =
        ∑ path, protocol.reverseAligned path := by
      apply Finset.sum_congr rfl
      intro path _
      rw [← hCrooks.2 path, mul_assoc, ← Real.exp_add]
      have hCancel : beta * (work path - deltaFreeEnergy) +
          -beta * (work path - deltaFreeEnergy) = 0 := by ring
      rw [hCancel, Real.exp_zero, mul_one]
    _ = 1 := protocol.reverseAligned.sum_one

/-- Finite Jarzynski equality derived from the pathwise Crooks relation rather
than from an assumed exponential-work normalization. -/
theorem finiteJarzynski_of_crooks
    (protocol : FinitePathProtocol Path) (beta deltaFreeEnergy : ℝ)
    (work : Path → ℝ)
    (hCrooks : HasCrooksRelation protocol beta deltaFreeEnergy work) :
    exponentialWorkAverage protocol.forward beta work =
      Real.exp (-beta * deltaFreeEnergy) :=
  finiteJarzynski_eq protocol.forward beta deltaFreeEnergy work
    (hasJarzynskiNormalization_of_crooks protocol beta deltaFreeEnergy work
      hCrooks)

/-- On a supported protocol the work `ΔF + σ / β`, with `σ` the pathwise
entropy production, satisfies the Crooks relation: the detailed fluctuation
identity is the Crooks relation with dissipated work `β (W - ΔF) = σ`. -/
theorem crooks_of_entropyProduction
    (protocol : FinitePathProtocol Path) (beta deltaFreeEnergy : ℝ)
    (hBeta : 0 < beta)
    (hForward : ∀ path, 0 < protocol.forward path)
    (hReverse : ∀ path, 0 < protocol.reverseAligned path) :
    HasCrooksRelation protocol beta deltaFreeEnergy
      (fun path =>
        deltaFreeEnergy + pathwiseEntropyProduction protocol path / beta) := by
  refine ⟨hBeta, fun path => ?_⟩
  have hDissipated :
      beta * (deltaFreeEnergy + pathwiseEntropyProduction protocol path / beta -
          deltaFreeEnergy) =
        pathwiseEntropyProduction protocol path := by
    field_simp
    ring
  rw [hDissipated]
  exact detailedFluctuation_identity protocol hForward hReverse path

/-! ## Local detailed balance and finite currents -/

/-- Oriented one-step probability current. -/
def probabilityCurrent (law : FiniteLaw State)
    (kernel : FiniteKernel State State) (source target : State) : ℝ :=
  law source * kernel source target - law target * kernel target source

/-- Probability current is antisymmetric under edge reversal. -/
theorem probabilityCurrent_antisymm
    (law : FiniteLaw State) (kernel : FiniteKernel State State)
    (source target : State) :
    probabilityCurrent law kernel source target =
      -probabilityCurrent law kernel target source := by
  simp [probabilityCurrent]

/-- Detailed balance cancels every local stationary current. -/
theorem localDetailedBalance_current_zero
    (law : FiniteLaw State) (kernel : FiniteKernel State State)
    (hReversible : IsReversible law kernel) (source target : State) :
    probabilityCurrent law kernel source target = 0 := by
  unfold probabilityCurrent
  rw [hReversible source target, sub_self]

/-- Supported local log affinity, kept separate from any physical heat
interpretation. -/
noncomputable def localAffinity (law : FiniteLaw State)
    (kernel : FiniteKernel State State) (source target : State) : ℝ :=
  Real.log ((law source * kernel source target) /
    (law target * kernel target source))

/-- A zero reverse edge rate is an explicit totalized-log boundary. -/
theorem localAffinity_zero_reverseRate_boundary
    (law : FiniteLaw State) (kernel : FiniteKernel State State)
    (source target : State) (hZero : kernel target source = 0) :
    localAffinity law kernel source target = 0 := by
  simp [localAffinity, hZero]

/-! ## Reversible one-step KL dissipation -/

/-- Detailed balance implies stationarity for a normalized finite kernel. -/
theorem isInvariant_of_isReversible
    (law : FiniteLaw State) (kernel : FiniteKernel State State)
    (hReversible : IsReversible law kernel) :
    FEP.FiniteMarkovDynamics.IsInvariant law kernel := by
  unfold FEP.FiniteMarkovDynamics.IsInvariant
  apply FiniteLaw.ext_mass
  funext target
  simp only [FiniteKernel.predictive_mass]
  calc
    (∑ source, law source * kernel source target) =
        ∑ source, law target * kernel target source := by
      apply Finset.sum_congr rfl
      intro source _
      exact hReversible source target
    _ = law target * ∑ source, kernel target source := by
      rw [Finset.mul_sum]
    _ = law target := by rw [kernel.sum_one, mul_one]

/-- One reversible Markov step cannot increase KL to its stationary law.
Strict support is explicit because this theorem reuses the finite logarithmic
data-processing proof rather than an extended-real divergence. -/
theorem reversibleKL_oneStep_dissipation [Nonempty State]
    (actual stationary : FiniteLaw State)
    (kernel : FiniteKernel State State)
    (hActual : ∀ state, 0 < actual state)
    (hStationary : ∀ state, 0 < stationary state)
    (hKernel : ∀ source target, 0 < kernel source target)
    (hReversible : IsReversible stationary kernel) :
    finiteKL (kernel.predictive actual) stationary ≤
      finiteKL actual stationary := by
  have hData := finiteChannel_dataProcessing actual stationary kernel
    hActual hStationary hKernel
  have hInvariant := isInvariant_of_isReversible stationary kernel hReversible
  change kernel.predictive stationary = stationary at hInvariant
  rw [hInvariant] at hData
  exact hData

/-- The identity kernel gives an exact reversible equality boundary. -/
theorem identityKernel_KL_equality [DecidableEq State]
    (actual stationary : FiniteLaw State) :
    finiteKL
        ((FiniteKernel.identity : FiniteKernel State State).predictive actual)
        stationary = finiteKL actual stationary := by
  rw [FiniteKernel.predictive_identity]

/-! ## Concrete irreversible positive-production witness -/

/-- Full-support Boolean forward path law with masses `3/4` and `1/4`. -/
noncomputable def irreversibleForward : FiniteLaw Bool where
  mass path := if path then 3 / 4 else 1 / 4
  nonneg path := by cases path <;> norm_num
  sum_one := by norm_num [Fintype.sum_bool]

/-- Full-support Boolean aligned reverse law with the masses exchanged. -/
noncomputable def irreversibleReverse : FiniteLaw Bool where
  mass path := if path then 1 / 4 else 3 / 4
  nonneg path := by cases path <;> norm_num
  sum_one := by norm_num [Fintype.sum_bool]

/-- Concrete two-path protocol with identity path reversal and unequal laws. -/
noncomputable def irreversibleBoolProtocol : FinitePathProtocol Bool where
  forward := irreversibleForward
  reverseAligned := irreversibleReverse
  reversal := id
  reversal_involutive := by intro path; rfl

/-- The forward and reverse Boolean path laws are genuinely distinct. -/
theorem irreversibleForward_ne_reverse :
    irreversibleForward ≠ irreversibleReverse := by
  intro hEqual
  have hTrue := congrFun (congrArg FiniteLaw.mass hEqual) true
  norm_num [irreversibleForward, irreversibleReverse] at hTrue

/-- The explicit irreversible Boolean witness has strictly positive mean
entropy production. -/
theorem irreversibleBool_entropyProduction_pos :
    0 < entropyProduction irreversibleBoolProtocol := by
  have hNonneg := finiteKL_nonneg irreversibleForward irreversibleReverse
  have hNe : finiteKL irreversibleForward irreversibleReverse ≠ 0 := by
    intro hZero
    exact irreversibleForward_ne_reverse
      ((finiteKL_eq_zero_iff irreversibleForward irreversibleReverse).mp hZero)
  exact lt_of_le_of_ne hNonneg (Ne.symm hNe)

/-! ## Crooks witness and the strictness of the Jarzynski premise -/

/-- Nonconstant Boolean work `± log 3` for the irreversible protocol. -/
noncomputable def irreversibleCrooksWork (path : Bool) : ℝ :=
  if path then Real.log 3 else -Real.log 3

/-- The irreversible Boolean protocol satisfies the Crooks relation at `β = 1`,
`ΔF = 0` with the nonconstant work `± log 3`. -/
theorem irreversibleBool_crooks :
    HasCrooksRelation irreversibleBoolProtocol 1 0 irreversibleCrooksWork := by
  have hLog : Real.exp (Real.log 3) = 3 := Real.exp_log (by norm_num)
  refine ⟨one_pos, fun path => ?_⟩
  cases path <;>
    norm_num [irreversibleBoolProtocol, irreversibleCrooksWork,
      irreversibleForward, irreversibleReverse, Real.exp_neg, hLog]

/-- The Crooks witness work genuinely varies across paths. -/
theorem irreversibleCrooksWork_nonconstant :
    irreversibleCrooksWork true ≠ irreversibleCrooksWork false := by
  have hPos : 0 < Real.log 3 := Real.log_pos (by norm_num)
  simp only [irreversibleCrooksWork, ↓reduceIte, Bool.false_eq_true]
  intro hEqual
  linarith

/-- The Jarzynski normalization is strictly weaker than Crooks: zero work
normalizes the irreversible forward law yet violates the pathwise relation. -/
theorem jarzynski_without_crooks :
    HasJarzynskiNormalization irreversibleBoolProtocol.forward 1 0
        (fun _ => 0) ∧
      ¬ HasCrooksRelation irreversibleBoolProtocol 1 0 (fun _ => 0) := by
  refine ⟨⟨one_pos, ?_⟩, ?_⟩
  · simp only [sub_self, mul_zero, Real.exp_zero, mul_one]
    exact irreversibleBoolProtocol.forward.sum_one
  · rintro ⟨_, hCrooks⟩
    have hTrue := hCrooks true
    simp only [irreversibleBoolProtocol, irreversibleForward,
      irreversibleReverse, ↓reduceIte, sub_self, mul_zero, Real.exp_zero,
      mul_one] at hTrue
    norm_num at hTrue

/-- The Jarzynski premise is substantive: constant unit work at `β = 1`,
`ΔF = 0` violates it on the irreversible forward law. -/
theorem irreversibleForward_unitWork_not_jarzynski :
    ¬ HasJarzynskiNormalization irreversibleBoolProtocol.forward 1 0
        (fun _ => 1) := by
  rintro ⟨_, hNormalization⟩
  have hSum : (∑ path, irreversibleBoolProtocol.forward path *
      Real.exp (-1 * ((1 : ℝ) - 0))) = Real.exp (-1) := by
    rw [← Finset.sum_mul, irreversibleBoolProtocol.forward.sum_one]
    norm_num
  have hLt : Real.exp (-1) < 1 := Real.exp_lt_one_iff.2 (by norm_num)
  rw [hSum] at hNormalization
  linarith

end FEP.PathThermodynamics
