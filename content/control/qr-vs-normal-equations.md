---
title: The numerical view of least squares — why QR/orthogonal beats the normal equations
created: 2026-06-24
authorship: ai-generated
model: claude-opus-4-8
tags:
- robust-control
- least-squares
- qr
- orthogonal-matrices
related:
- '[[matrix_invertibility]]'
publish: true
description: Four questions, one story. Exercise 3.1 solves the same least-squares
  problem as Chapter 2, but with a method built for an actual computer instead of
  a formula built for a chalkboard.
---

> [!note] Drafted with an AI assistant (claude-opus-4-8)
> I wrote this note with model help and then read it, checked the
> math, and kept it because I agree with it. Errors are still mine.

# The numerical view of least squares — why QR/orthogonal beats the normal equations

Four questions, one story. Exercise 3.1 solves the *same* least-squares problem as Chapter 2, but with a method built for an actual computer instead of a formula built for a chalkboard.

## Numerical version

Chapter 2 hands you the **answer** to least squares: the normal equations

$$\hat{x}=(A^TA)^{-1}A^Ty.$$

That is a correct *formula* — a mathematician's answer. But a formula is not an algorithm. The moment you run it on a real machine (finite-precision floating point, ~16 decimal digits in double), the *way* you compute matters. "Numerical version" = same problem, but solved by an algorithm designed to keep rounding error under control, not just a symbolic identity.

The concrete trouble with the normal equations: forming $A^TA$ **squares the condition number**.

> [!warning] The condition-number squaring, with numbers
> The condition number $\kappa(A)$ measures how much $A$ amplifies relative error (think: how close to singular it is). Suppose $A$'s columns are *nearly* parallel, so $\kappa(A)=10^{6}$.
> - Work directly on $A$ (QR): you lose about 6 of your ~16 digits. Fine.
> - Form $A^TA$ first: $\kappa(A^TA)=\kappa(A)^2=10^{12}$. You've thrown away 12 of 16 digits *before you even start inverting*. The answer can be garbage.
>
> QR never forms $A^TA$. It works on $A$ itself, so it only ever "sees" $\kappa$, never $\kappa^2$. That is the entire point of doing the problem this "numerical" way.

This is what the textbook means at the end of 3.1: the normal-equation route implicitly evaluates $(R^TR)^{-1}R^T$ (note the $R^TR$ — there's the squaring), whereas Householder/Golub recognizes that product *is just* $R^{-1}$ and skips the error-prone middle.

## QR and orthogonal matrices

**QR factorization**: any full-column-rank $A$ ($m\times n$, $m\ge n$) splits as $A=QR$, with $Q$ orthogonal and $R$ upper triangular. The textbook writes the same fact "inside out":

$$UA=\begin{bmatrix}R\\0\end{bmatrix},\qquad U=Q^T.$$

(Multiply both sides by $U^T=Q$: $A=Q\begin{bmatrix}R\\0\end{bmatrix}$ — identical content. Matlab's `qr` gives you `Q`; the note's `U` is its transpose.)

**Orthogonal matrix** $U$: a square real matrix with orthonormal columns, equivalently $U^TU=I$, equivalently $U^{-1}=U^T$. Geometrically it is a **rigid motion** — a rotation or a reflection of the whole space. Nothing stretches, squishes, or shears.

## Nonsingular upper triangular

**Upper triangular**: every entry below the diagonal is zero. **Nonsingular**: invertible — and for a triangular matrix that's true iff every diagonal entry is nonzero (the determinant is just the product of the diagonal). Both matter here: nonsingular means $R\hat x=y_1$ has a unique solution; upper-triangular means you get it by back-substitution (solve the last row's one unknown, climb up) — no inverse needed.

## Why the zero block

This is the heart of it. The job of $U$ is to **rotate the problem into a frame where the answer is obvious**, without changing the answer (legal because $U$ preserves length — see §4).

Picture the geometry first. As $x$ ranges over all of $\mathbb{R}^n$, the vector $Ax$ sweeps out an $n$-dimensional subspace — the column space of $A$ — sitting at some awkward tilt inside the big $m$-dimensional space. Least squares = *find the point in that tilted subspace closest to the target $y$.*

$U$ grabs the whole space and **rotates it so that tilted subspace lies flat along the first $n$ coordinate axes.** That is exactly what $UA=\begin{bmatrix}R\\0\end{bmatrix}$ says: after the rotation, the bottom $m-n$ rows are *structurally zero*. So

$$UAx=\begin{bmatrix}R\\0\end{bmatrix}x=\begin{bmatrix}Rx\\0\end{bmatrix}.$$

No matter what $x$ you pick, the rotated $Ax$ can only put content in the **top $n$ slots** and is forced to be zero in the **bottom $m-n$ slots**. The reachable set is now axis-aligned and trivial to describe.

Rotate the target too: $Uy=\begin{bmatrix}y_1\\y_2\end{bmatrix}$. Now look at the error in the rotated frame:

$$Uy-UAx=\begin{bmatrix}y_1-Rx\\[2pt]y_2\end{bmatrix}.$$

It splits into two physically different pieces:

- **Top $n$ slots, $y_1-Rx$**: fully under your control. You can steer it to *anything*, including zero.
- **Bottom $m-n$ slots, $y_2$**: untouchable. No choice of $x$ moves it. This is the irreducible residual — the part of $y$ that simply does not live in the column space of $A$.

So the zero block is precisely **"the directions $y$ can point that $Ax$ can never reach."** The factorization's whole purpose is to *separate the controllable part of the error from the uncontrollable part* by lining the problem up with the axes. Then length is just slot-by-slot (Pythagoras):

$$\|y-Ax\|^2=\underbrace{\|y_1-Rx\|^2}_{\text{drive to }0}+\underbrace{\|y_2\|^2}_{\text{stuck}}.$$

Three wins, all from the $\begin{bmatrix}R\\0\end{bmatrix}$ shape:
1. **Splits** the error into reachable ($y_1$) vs. unreachable ($y_2$).
2. The reachable block $R$ is **square and nonsingular**, so $y_1-Rx=0$ is exactly solvable: $R\hat x=y_1$.
3. $R$ is **upper triangular**, so you solve $R\hat x=y_1$ by back-substitution (last row has one unknown, climb upward) — no matrix inverse, no $A^TA$.

## Why orthogonal matrices preserve length

An orthogonal matrix is a **rigid motion**: a rotation or reflection. Pick up the whole space and turn it (or flip it) — you haven't stretched the ruler. Length and angle are *the* invariants of rigid motion. A vector is an arrow; turning the arrow doesn't change how long the arrow is.

Concretely — take $v=(3,4)$, length $5$:

- Rotate $90°$ with $U=\begin{bmatrix}0&-1\\1&0\end{bmatrix}$: $Uv=(-4,3)$, length $\sqrt{16+9}=5$. ✓
- Reflect across $y=x$: $(3,4)\mapsto(4,3)$, length $\sqrt{16+9}=5$. ✓

Why orthonormal columns force this: the columns of $U$ are *where the standard basis vectors land*. If those landing spots are orthonormal (unit length, mutually perpendicular), then $U$ carries a perpendicular unit-grid to another perpendicular unit-grid — it's just a relabeling of perpendicular axes. A map that sends a unit square to a unit square (no shear, no scaling) can't change any length.

The one-line algebra, which is just that fact in symbols:

$$\|Uv\|^2=(Uv)^T(Uv)=v^T\underbrace{U^TU}_{=\,I}v=v^Tv=\|v\|^2.$$

The single identity $U^TU=I$ *is* "the new axes are still perpendicular unit vectors," so measuring a vector in the rotated frame returns the same number.

> [!tip] Why this is the linchpin of the whole proof
> Because $U$ doesn't change lengths, $\min_x\|y-Ax\|$ and $\min_x\|U(y-Ax)\|$ are the **same minimization with the same minimizer**. That equality is your *license* to rotate into the convenient $\begin{bmatrix}R\\0\end{bmatrix}$ frame, solve there, and keep the answer. Without length-preservation, the rotation would change the problem and the trick would be illegal.

## The one-sentence summary

Chapter 2 says *what* the least-squares answer is; Exercise 3.1 rotates the problem with a length-preserving $U$ until the column space lies on the first $n$ axes, which (a) cleanly separates the fixable error $y_1-Rx$ from the stuck error $y_2$, (b) leaves a square triangular system $R\hat x=y_1$, and (c) never forms $A^TA$ — so it keeps the digits the normal equations would have thrown away.
