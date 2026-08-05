import Lake
open Lake DSL

package «LeanEcon» where
  leanOptions := #[
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩
  ]

-- Pinned Mathlib dependency. The tag is part of the v4 reproducibility pin:
-- changing it changes the verification workspace identity and requires review.
require "leanprover-community" / "mathlib" @ git "v4.32.2"

@[default_target]
lean_lib «LeanEcon» where
