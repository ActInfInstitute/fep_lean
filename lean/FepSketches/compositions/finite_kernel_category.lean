import FepSketches.finite_probability
import Mathlib.CategoryTheory.Category.Basic
import Mathlib.CategoryTheory.Functor.Basic

/-!
# Finite-kernel composition as a Mathlib CategoryTheory instance

This leaf packages the already-proved kernel-composition lemmas from
`FEP.FiniteKernel` — `comp_assoc`, `comp_identity_right`, and
`comp_identity_left` — as a legitimate `CategoryTheory.Category` instance
over a bundled object type, without hand-rolling any duplicates of Mathlib's
categorical infrastructure.

## Design

Objects of `FinKernCat` are finite types bundled with a `Fintype` instance and
a `DecidableEq` instance (required by `FiniteKernel.identity`).  Morphisms are
normalized finite Markov kernels (`FEP.FiniteKernel`).  Composition is
`FiniteKernel.comp` and the identity is `FiniteKernel.identity`; the category
axioms are witnessed by the three composition theorems already proved in
`finite_probability.lean`.

## Liskov amendment (functoriality as record fields)

`FiniteKernelFunctor` carries its coherence obligations — object map,
morphism map, preservation of identity, and preservation of composition — as
record **fields**, not as floating theorems over an opaque instance.  This
means any downstream term claiming functoriality must supply concrete proofs at
construction time; the class cannot be inhabited by a partial witness that
defers coherence to separate lemmas.
-/

namespace FEPComposed.FiniteKernelCategory

open CategoryTheory FEP FEP.FiniteKernel

/-! ## Bundled object type -/

/-- An object of the finite-kernel category: a finite type `α` equipped with
decidable equality (required to form the identity kernel) and a `Fintype`
instance (required by `FiniteKernel`). -/
structure FinKernCat : Type 1 where
  /-- The underlying type. -/
  α : Type
  /-- Fintype instance. -/
  [instFintype : Fintype α]
  /-- DecidableEq instance (needed for the identity kernel). -/
  [instDecEq : DecidableEq α]

attribute [instance] FinKernCat.instFintype FinKernCat.instDecEq

/-! ## CategoryStruct and Category instances -/

/-- The morphism type: a normalized finite Markov kernel between the underlying
types of two bundled objects. -/
instance : Quiver FinKernCat where
  Hom X Y := FiniteKernel X.α Y.α

/-- The identity morphism on a bundled object is `FiniteKernel.identity`. -/
instance : CategoryStruct FinKernCat where
  id X := FiniteKernel.identity (α := X.α)
  comp f g := FiniteKernel.comp g f

/-- The category of finite types and normalized finite Markov kernels.
The three axioms are witnessed by the already-proved theorems
`FiniteKernel.comp_identity_right`, `FiniteKernel.comp_identity_left`, and
`FiniteKernel.comp_assoc`. -/
instance : Category FinKernCat where
  id_comp f := FiniteKernel.comp_identity_right f
  comp_id f := FiniteKernel.comp_identity_left f
  assoc f g h := (FiniteKernel.comp_assoc h g f).symm

/-! ## Functoriality structure (Liskov amendment)

Any claim of functoriality between finite-kernel categories must inhabit this
structure, committing upfront to all four fields.  Coherence lives in the
record, not in separate floating lemmas. -/

/-- A functor from a finite-kernel source category to a finite-kernel target
category, with all coherence obligations carried as record fields. -/
structure FiniteKernelFunctor (C D : Type*)
    [Category C] [Category D]
    (obj_map : C → D) where
  /-- The action on morphisms. -/
  map : ∀ {X Y : C}, (X ⟶ Y) → (obj_map X ⟶ obj_map Y)
  /-- Preservation of identities. -/
  map_id : ∀ (X : C), map (𝟙 X) = 𝟙 (obj_map X)
  /-- Preservation of composition. -/
  map_comp : ∀ {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z),
      map (f ≫ g) = map f ≫ map g

/-- Every `FiniteKernelFunctor` bundle determines a Mathlib `Functor`. -/
def FiniteKernelFunctor.toFunctor {C D : Type*} [Category C] [Category D]
    (obj_map : C → D)
    (fkf : FiniteKernelFunctor C D obj_map) :
    C ⥤ D where
  obj := obj_map
  map := fkf.map
  map_id := fkf.map_id
  map_comp := fkf.map_comp

/-! ## Coherence witnesses using the existing composition lemmas

The three theorems below explicitly witness the category axioms from the
composition lemmas in `finite_probability.lean`, making the connection
between the raw algebraic proofs and their categorical packaging transparent.
-/

/-- The identity kernel composed on the left with any kernel yields that
kernel: `identity ≫ f = f`. -/
theorem finKernCat_id_comp (X Y : FinKernCat) (f : X ⟶ Y) :
    𝟙 X ≫ f = f :=
  FiniteKernel.comp_identity_right f

/-- Any kernel composed on the right with the identity kernel yields that
kernel: `f ≫ identity = f`. -/
theorem finKernCat_comp_id (X Y : FinKernCat) (f : X ⟶ Y) :
    f ≫ 𝟙 Y = f :=
  FiniteKernel.comp_identity_left f

/-- Composition of finite kernels is associative in the categorical sense. -/
theorem finKernCat_assoc (W X Y Z : FinKernCat)
    (f : W ⟶ X) (g : X ⟶ Y) (h : Y ⟶ Z) :
    (f ≫ g) ≫ h = f ≫ (g ≫ h) :=
  (FiniteKernel.comp_assoc h g f).symm

end FEPComposed.FiniteKernelCategory
