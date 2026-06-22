# LaTeX Mathematical Notation Guide

Quick reference for mathematical expressions in LaTeX.

## Basic Math

### Inline Math
```latex
The formula is $E = mc^2$.
The sum is $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$.
```

### Display Equations
```latex
$$
\int_0^\infty e^{-x} dx = 1
$$
```

### Numbered Equations
```latex
\begin{equation}
    f(x) = ax^2 + bx + c
    \label{eq:quadratic}
\end{equation}

Equation \ref{eq:quadratic} shows a quadratic function.
```

## Greek Letters

| Letter | LaTeX | Letter | LaTeX |
|--------|-------|--------|-------|
| α | `\alpha` | Α | `A` |
| β | `\beta` | Β | `B` |
| γ | `\gamma` | Γ | `\Gamma` |
| δ | `\delta` | Δ | `\Delta` |
| ε | `\epsilon` | Ε | `E` |
| θ | `\theta` | Θ | `\Theta` |
| λ | `\lambda` | Λ | `\Lambda` |
| μ | `\mu` | Μ | `M` |
| π | `\pi` | Π | `\Pi` |
| σ | `\sigma` | Σ | `\Sigma` |
| φ | `\phi` | Φ | `\Phi` |
| ω | `\omega` | Ω | `\Omega` |

## Superscripts & Subscripts

```latex
$x^2$          % superscript
$x_i$           % subscript
$x_i^2$         % both
$x^{2n}$        % curly braces for multi-char
```

## Fractions & Roots

```latex
\frac{a}{b}     % fraction
\sqrt{x}        % square root
\sqrt[n]{x}     % nth root
```

## Summations & Integrals

```latex
\sum_{i=1}^{n} i          % summation
\prod_{i=1}^{n} i         % product
\int_{a}^{b} f(x) dx      % definite integral
\oint_{C} F \cdot dr      % line integral
\infty                     % infinity
```

## Matrices

```latex
\begin matrix}
a & b \\
c & d
\end{matrix}

\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}

\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
```

## Common Symbols

```latex
\pm        % ±
\times     % ×
\div       % ÷
\leq       % ≤
\geq       % ≥
\neq       % ≠
\approx    % ≈
\equiv     % ≡
\subset    % ⊂
\subset    % ⊂
\in        % ∈
\cup       % ∪
\cap       % ∩
\forall    % ∀
\exists    % ∃
\rightarrow % →
\Rightarrow % ⇒
\leftrightarrow % ↔
\Leftarrow % ⇐
```

## Brackets

```latex
\left( ... \right)      % parentheses
\left[ ... \right]       % brackets
\left\{ ... \right\}     % braces
\left| ... \right|      % absolute value
```

## Functions

```latex
\sin(x)      \cos(x)      \tan(x)
\arcsin(x)   \arccos(x)   \arctan(x)
\log(x)      \ln(x)       \exp(x)
\lim_{x\to 0} f(x)        % limit
\max(x)      \min(x)
```

## Cases / Piecewise

```latex
f(x) = 
\begin{cases}
x & \text{if } x \geq 0 \\
-x & \text{if } x < 0
\end{cases}
```
