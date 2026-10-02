"""Native boundaries for the measure-Bayes and variational-duality families."""

from __future__ import annotations

import re
import runpy
import subprocess
from pathlib import Path

import pytest

from tests._support.lake import lake_executable
from tests._support.lean_runner import run_lean_compile_probe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = PROJECT_ROOT / "lean"
FORMAL_ROOT = PROJECT_ROOT / "src" / "fep_lean" / "formal"
BODIES_ROOT = PROJECT_ROOT / "src" / "fep_lean" / "catalogue" / "bodies"

pytestmark = pytest.mark.serial_lean


def _compile(source: Path) -> subprocess.CompletedProcess[str]:
    return run_lean_compile_probe(
        source,
        cwd=LEAN_ROOT,
        timeout_s=300,
        executable=lake_executable(),
    )


def _bodies(module_name: str) -> dict[str, str]:
    namespace = runpy.run_path(BODIES_ROOT / f"{module_name}.py")
    return namespace["BODIES"]


def _compile_with_foundation(
    tmp_path: Path, *, foundation: str, topic_id: str, body: str
) -> subprocess.CompletedProcess[str]:
    import_line = f"import FepSketches.{foundation}\n"
    assert body.startswith(import_line)
    combined = tmp_path / f"{topic_id}.lean"
    combined.write_text(
        (FORMAL_ROOT / f"{foundation}.lean").read_text(encoding="utf-8")
        + "\n"
        + body.removeprefix(import_line),
        encoding="utf-8",
    )
    return _compile(combined)


def test_measure_bayes_foundation_compiles_warning_free() -> None:
    result = _compile(FORMAL_ROOT / "measure_bayes.lean")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning:" not in (result.stdout + result.stderr).lower()


def test_variational_duality_foundation_compiles_warning_free() -> None:
    result = _compile(FORMAL_ROOT / "variational_duality.lean")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning:" not in (result.stdout + result.stderr).lower()


def test_measure_bayesian_inversion_family_owns_ordered_standalone_bodies() -> None:
    bodies = _bodies("measure_bayesian_inversion")

    assert tuple(bodies) == tuple(f"fep-{number:03d}" for number in range(51, 58))
    for number, body in zip(range(51, 58), bodies.values(), strict=True):
        assert body.startswith("import FepSketches.measure_bayes\n")
        assert f"namespace FEP{number:03d}\n" in body
        assert f"end FEP{number:03d}\n" in body
        assert f"theorem fep{number:03d}_" in body
        assert "sorry" not in body
        assert "axiom " not in body


def test_standard_borel_disintegration_topic_compiles_at_native_boundary(
    tmp_path: Path,
) -> None:
    body = _bodies("measure_bayesian_inversion")["fep-056"]
    result = _compile_with_foundation(
        tmp_path,
        foundation="measure_bayes",
        topic_id="fep-056",
        body=body,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning:" not in (result.stdout + result.stderr).lower()


def test_variational_duality_family_owns_ordered_standalone_bodies() -> None:
    bodies = _bodies("variational_duality")

    assert tuple(bodies) == tuple(f"fep-{number:03d}" for number in range(58, 65))
    for number, body in zip(range(58, 65), bodies.values(), strict=True):
        assert body.startswith("import FepSketches.variational_duality\n")
        assert f"namespace FEP{number:03d}\n" in body
        assert f"end FEP{number:03d}\n" in body
        assert f"theorem fep{number:03d}_" in body
        assert "sorry" not in body
        assert "axiom " not in body


def test_donsker_varadhan_topic_compiles_with_full_support_visible(
    tmp_path: Path,
) -> None:
    body = _bodies("variational_duality")["fep-059"]
    result = _compile_with_foundation(
        tmp_path,
        foundation="variational_duality",
        topic_id="fep-059",
        body=body,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning:" not in (result.stdout + result.stderr).lower()


def test_finite_channel_data_processing_compiles_with_support_boundary(
    tmp_path: Path,
) -> None:
    body = _bodies("variational_duality")["fep-063"]
    result = _compile_with_foundation(
        tmp_path,
        foundation="variational_duality",
        topic_id="fep-063",
        body=body,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning:" not in (result.stdout + result.stderr).lower()


@pytest.mark.parametrize(
    ("module_name", "foundation"),
    [
        ("measure_bayesian_inversion", "measure_bayes"),
        ("variational_duality", "variational_duality"),
    ],
)
def test_family_body_closure_compiles_warning_free(
    tmp_path: Path, module_name: str, foundation: str
) -> None:
    import_line = f"import FepSketches.{foundation}\n"
    combined = tmp_path / f"{module_name}.lean"
    bodies = _bodies(module_name)
    combined.write_text(
        (FORMAL_ROOT / f"{foundation}.lean").read_text(encoding="utf-8")
        + "\n"
        + "\n".join(body.removeprefix(import_line) for body in bodies.values()),
        encoding="utf-8",
    )

    result = _compile(combined)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning:" not in (result.stdout + result.stderr).lower()


def test_iwae_topic_fixes_a_positive_sample_count_and_iid_product_law() -> None:
    foundation = (FORMAL_ROOT / "variational_duality.lean").read_text(encoding="utf-8")
    body = _bodies("variational_duality")["fep-062"]

    assert "def iidProductLaw" in foundation
    assert "def sampleMeanWeight" in foundation
    assert "theorem fixedSampleImportanceJensen" in foundation
    assert "[NeZero sampleCount]" in foundation
    assert "theorem fep062_iidProduct_importanceJensen" in body


def test_gibbs_certificate_has_a_compiled_nonvacuity_witness() -> None:
    foundation = (FORMAL_ROOT / "variational_duality.lean").read_text(encoding="utf-8")
    body = _bodies("variational_duality")["fep-058"]

    assert "def uniformZeroPotentialGibbs" in foundation
    assert "theorem uniformZeroPotentialGibbs_objective" in foundation
    assert "theorem fep058_uniformGibbs_nonvacuity" in body


def test_family_declaration_names_are_unique_stable_and_topic_scoped() -> None:
    expected = {
        "fep-051": (
            "fep051_likelihoodRatio_reconstruction",
            "fep051_reconstruction_iff_absoluteContinuous",
        ),
        "fep-052": (
            "fep052_posterior_density_tilt",
            "fep052_countable_posterior_density_tilt",
        ),
        "fep-053": (
            "fep053_kernelBayes_joint_reconstruction",
            "fep053_finiteBayes_atom_reconstruction",
        ),
        "fep-054": (
            "fep054_bayes_involution",
            "fep054_posterior_reconstructs_prior",
        ),
        "fep-055": (
            "fep055_compositeKernel_bayesInversion",
            "fep055_compositePredictive_associativity",
        ),
        "fep-056": (
            "fep056_standardBorel_condKernel_reconstruction",
            "fep056_standardBorel_condKernel_mass_one",
        ),
        "fep-057": (
            "fep057_conditionalExpectation_tower",
            "fep057_conditionalLIntegral_tower",
        ),
        "fep-058": (
            "fep058_gibbsVariational_lower_bound",
            "fep058_gibbsVariational_optimizer",
            "fep058_uniformGibbs_nonvacuity",
        ),
        "fep-059": (
            "fep059_donskerVaradhan_upper_bound",
            "fep059_donskerVaradhan_optimizer",
            "fep059_donskerVaradhan_equality_iff",
        ),
        "fep-060": (
            "fep060_coordinateELBO_decomposition",
            "fep060_coordinateKL_nonnegative",
        ),
        "fep-061": (
            "fep061_meanFieldCoordinate_reduction",
            "fep061_meanFieldCoordinate_optimum_iff",
        ),
        "fep-062": (
            "fep062_iidProduct_importanceJensen",
            "fep062_fixedSample_importanceJensen",
            "fep062_expectedImportanceWeight_positive",
        ),
        "fep-063": (
            "fep063_finiteChannel_klDataProcessing",
            "fep063_referencePredictive_fullSupport",
            "fep063_identityChannel_preservesKL",
            "fep063_constantChannel_strict",
        ),
        "fep-064": (
            "fep064_rateDistortion_weakDuality",
            "fep064_zeroMultiplier_boundary",
            "fep064_rateDistortion_exists_minimizer",
            "fep064_rateDistortion_dual_lower_bound",
            "fep064_dual_zeroMultiplier",
            "fep064_negativeBudget_infeasible",
            "fep064_quarterBudget_informative_optimum",
            "fep064_halfBudget_nonunique",
            "fep064_zeroBudget_unique",
        ),
    }
    bodies = {
        **_bodies("measure_bayesian_inversion"),
        **_bodies("variational_duality"),
    }

    actual = {
        topic_id: tuple(
            re.findall(r"^theorem\s+([A-Za-z][A-Za-z0-9_]*)", body, re.MULTILINE)
        )
        for topic_id, body in bodies.items()
    }
    assert actual == expected
    names = [name for topic_names in actual.values() for name in topic_names]
    assert len(names) == len(set(names))


def test_rate_distortion_optimization_consumers_compile(tmp_path: Path) -> None:
    """Exercise informative, infeasible, unique, and nonunique budget faces."""
    consumer = tmp_path / "rate_distortion_consumers.lean"
    consumer.write_text(
        (FORMAL_ROOT / "variational_duality.lean").read_text(encoding="utf-8")
        + """
namespace RateDistortionConsumer
open FEP FEP.FiniteInformation FEP.VariationalDuality

example : ¬ ∃ joint, RateDistortionFeasible (FiniteLaw.uniform : FiniteLaw Bool)
    boolHammingDistortion (-1) joint :=
  rateDistortion_infeasible_of_negativeBudget _ _ _ boolHammingDistortion_nonneg (by norm_num)

example : RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion (1 / 4)
    boolQuarterDistortionJoint := boolQuarterDistortionJoint_feasible

example : ∃ optimizer : FiniteLaw (Bool × Bool),
    RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion (1 / 4) optimizer ∧
      0 < mutualInformation optimizer ∧
        ∀ candidate, RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion
          (1 / 4) candidate → mutualInformation optimizer ≤ mutualInformation candidate :=
  boolQuarterBudget_exists_positive_minimizer

example : rateDistortionDualValue (FiniteLaw.uniform : FiniteLaw Bool)
    boolHammingDistortion (1 / 4) 2 ≤ mutualInformation boolQuarterDistortionJoint :=
  rateDistortionDual_le_feasible_information _ _ _ _ boolHammingDistortion_nonneg
    (by norm_num) _ boolQuarterDistortionJoint_feasible

example : rateDistortionDualValue (FiniteLaw.uniform : FiniteLaw Bool)
    boolHammingDistortion (-1) 0 = 0 := rateDistortionDual_zeroMultiplier _ _ _

example (joint : FiniteLaw (Bool × Bool))
    (hjoint : RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion 0 joint) :
    joint = boolZeroDistortionJoint := boolZeroBudget_unique_feasible joint hjoint

example : ∃ left right : FiniteLaw (Bool × Bool), left ≠ right ∧
    (RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion (1 / 2) left ∧
      ∀ candidate, RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion
        (1 / 2) candidate → mutualInformation left ≤ mutualInformation candidate) ∧
    (RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion (1 / 2) right ∧
      ∀ candidate, RateDistortionFeasible FiniteLaw.uniform boolHammingDistortion
        (1 / 2) candidate → mutualInformation right ≤ mutualInformation candidate) :=
  boolHalfBudget_distinct_minimizers
end RateDistortionConsumer
""",
        encoding="utf-8",
    )
    result = _compile(consumer)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "warning:" not in output.lower()
