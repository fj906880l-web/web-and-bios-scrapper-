---
name: epistemic-math-frontier
description: "Master operational skill for exploring, formulating, and rigorously auditing open mathematical conjectures, Millennium Prize problems, and theoretical computer science frontiers. Enforces strict epistemic boundaries between heuristic computation and deductive proof, maps structural barriers, and guides cross-disciplinary mathematical imagination."
version: 1.0.0
trigger: /epistemic-math-frontier
---

# Epistemic Mathematics Frontier Protocol

> **Core Invariant (Structural Truth in Mathematics):**
> Mathematics is governed by absolute deductive certainty. In pure mathematics, testing trillions of cases on supercomputers is an empirical observation—not a proof. This skill enforces the highest standards of epistemic integrity: mapping exact proof barriers, exploring cross-disciplinary mathematical imagination, and strictly preventing false proof claims or sycophancy.

```
                      EVIDENCE HIERARCHY IN MATHEMATICS
   ┌────────────────────────────────────────────────────────────────────────┐
   │ TIER 1: Unconditional Deductive Proof (ZFC, Zero Gaps, Peer Reviewed)   │
   ├────────────────────────────────────────────────────────────────────────┤
   │ TIER 2: Conditional Proofs (e.g. Assuming GRH, BSD, or GEH)             │
   ├────────────────────────────────────────────────────────────────────────┤
   │ TIER 3: Bounded / Density Theorems (e.g. Tao Collatz, Maynard Prime Gaps)│
   ├────────────────────────────────────────────────────────────────────────┤
   │ TIER 4: Empirical Computation (e.g. Checked to 10^13 zeros, 2.95x10^20) │
   ├────────────────────────────────────────────────────────────────────────┤
   │ TIER 5: Informal Conjectures & Heuristic Analogies                     │
   └────────────────────────────────────────────────────────────────────────┘
```

---

## 1. The 4-Step Mathematical Epistemic Loop

When asked to analyze, explore, or attempt an open mathematical conjecture:

### Step 1: Formal Formulation
* Express the conjecture in precise, unambiguous mathematical notation (domains, quantifiers, topologies, spaces).
* Identify the exact target:
  - Existential ($\exists x$): Requires constructing a specific object or counterexample.
  - Universal ($\forall x$): Requires an invariant or inductive structure holding across infinite cardinality.

### Step 2: The Proof Barrier Audit
Before entertaining proof strategies, audit the problem against established meta-mathematical no-go theorems:
1. **Relativization Barrier (Baker, Gill, Solovay):** Does the proof technique hold in the presence of an arbitrary oracle? If so, it cannot resolve $\mathbf{P}$ vs $\mathbf{NP}$.
2. **Natural Proofs Barrier (Razborov, Rudich):** Does the circuit lower bound rely on a property that is polynomial-time testable and dense? If so, it inverts pseudorandom generators and fails.
3. **Algebrization Barrier (Aaronson, Wigderson):** Does the algebraic technique hold relative to low-degree oracle polynomials?
4. **The Selberg Parity Barrier:** Does a sieve method attempt to distinguish primes from semiprimes without non-sieve bilinearity or automorphic inputs?
5. **Supercriticality & Energy Cascade:** In non-linear PDEs (Navier-Stokes), do proposed a priori estimates scale below the invariant scaling of the equation?

### Step 3: Cross-Disciplinary Mathematical Imagination
When standard tools fail, explore rigorous conceptual analogies from adjacent branches of science:
* **Dynamical Systems $\to$ $p$-Adic Analysis:** Transform integer recurrence maps (e.g. Collatz $3x+1$) into continuous dynamical systems over the compact topological ring of $p$-adic integers $\mathbb{Z}_p$, investigating non-Archimedean Lyapunov potential wells.
* **Analytic Number Theory $\to$ Quantum Mechanics (Hilbert-Pólya):** Model distribution of zeros as eigenvalues of a self-adjoint Hamiltonian operator $H$ in a Hilbert space, leveraging spectral theory and random matrix statistics (GUE).
* **Computational Complexity $\to$ Algebraic Geometry (GCT):** Formulate complexity class separations as orbit closures in projective coordinate rings under algebraic group actions ($\mathrm{GL}_n$).

### Step 4: Epistemic Verdict & Anti-Sycophancy
* **Never Glaze:** Never tell a user that an open problem is solved or produce a hand-waving "proof" to please the prompt.
* **State the Gap:** Clearly articulate the exact step where current human and machine mathematics terminates.
* **Distinguish Scope:** Explicitly label Tier 4 empirical data as heuristic support, not proof.

---

## 2. Standard Reference Map for the Millennium Problems

| Problem | Open Question | Dominant Strategy | Blocking Barrier |
|---|---|---|---|
| **Riemann Hypothesis** | Zeros of $\zeta(s)$ on $\operatorname{Re}(s) = 1/2$ | Spectral operator / Trace formula | Construction of physical self-adjoint $H$ without ghost states |
| **P vs NP** | $\mathbf{P} \stackrel{?}{=} \mathbf{NP}$ | Geometric Complexity Theory (GCT) | Relativization, Natural Proofs, Algebrization |
| **Navier-Stokes** | Smooth global $u(x,t)$ on $\mathbb{R}^3$ | Critical Sobolev norms / Convex integration | Vortex stretching, Tao averaged blowup |
| **Birch & Swinnerton-Dyer** | $\operatorname{ord}_{s=1} L(E,s) = \operatorname{rank}(E)$ | Heegner points / Iwasawa theory | Higher rank ($r \ge 2$) point construction |
| **Hodge Conjecture** | $\operatorname{Hdg}^{2k}(X) \stackrel{?}{=} \operatorname{cl}_{\mathbb{Q}}(\mathcal{Z}^k)$ | Motives / Variation of Hodge structures | Non-linearity of cycles in codimension $k > 1$ |
| **Yang-Mills Mass Gap** | 4D QFT with $\Delta > 0$ | Lattice gauge theory continuum limit | Non-perturbative UV renormalization in 4D |
