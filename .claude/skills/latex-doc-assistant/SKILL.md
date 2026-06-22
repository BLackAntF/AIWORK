---
name: latex-doc-assistant
description: "Generate professional documents with LaTeX formatting. Supports mathematical formulas, equations, and scientific notation. Converts LaTeX to Word/PDF with consistent formatting for software engineering documentation."
---

# LaTeX Document Assistant

Generate professional documents with LaTeX formatting for consistent, publication-quality output.

## Overview

Create documents with mathematical formulas, technical notation, and professional formatting using LaTeX syntax. Supports conversion to Word and PDF formats.

## Supported Features

### Mathematical Formulas
- Inline math: `$formula$`
- Display equations: `$$formula$$`
- Numbered equations: `\begin{equation}...\end{equation}`
- Equation arrays: `\begin{align}...\end{align}`
- Matrices and vectors
- Greek letters and symbols
- Fractions, summations, integrals

### Document Structure
- Chapters, sections, subsections
- Tables and figures
- Table of contents
- Bibliographies (BibTeX)
- Cross-references

### Technical Notation
- Code listings with syntax highlighting
- Algorithms and pseudocode
- Technical diagrams
- UML diagrams (via external tools)

## Workflow

1. **Write LaTeX source** - Create document with formulas
2. **Preview locally** - Use VS Code LaTeX Workshop
3. **Compile to PDF** - Using pdflatex/xelatex
4. **Convert to Word** - Using pandoc or tex4ht

## Conversion Pipeline

```
Markdown/LaTeX → PDF
        ↓
pandoc → Word (.docx)
        ↓
Word → Further editing
```

### Common Conversions

```bash
# LaTeX to PDF
pdflatex document.tex

# Markdown to Word
pandoc document.md -o document.docx

# LaTeX to Word
pandoc document.tex -o document.docx

# With formula support
pandoc document.md --mathml -o document.docx
```

## LaTeX Example

```latex
\documentclass{article}
\usepackage{amsmath}
\usepackage{graphicx}

\title{Software Architecture Document}
\author{Team Name}
\date{\today}

\begin{document}

\maketitle

\section{System Overview}
The system follows a layered architecture pattern.

\section{Mathematical Models}
The performance metric is defined as:

\begin{equation}
    P = \frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2
    \label{eq:mse}
\end{equation}

Where:
\begin{itemize}
    \item $N$ is the total number of samples
    \item $y_i$ is the actual value
    \item $\hat{y}_i$ is the predicted value
\end{itemize}

\section{Complexity Analysis}
The time complexity is $O(n^2)$ and space complexity is $O(n)$.

\end{document}
```

## Inline Formulas

Common mathematical expressions:

| Description | LaTeX | Rendered |
|-------------|-------|----------|
| Fraction | `\frac{a}{b}` | a/b |
| Square root | `\sqrt{x}` | √x |
| Sum | `\sum_{i=1}^{n}` | Σ |
| Integral | `\int_{0}^{1}` | ∫ |
| Greek letters | `\alpha, \beta, \gamma` | α, β, γ |
| Infinity | `\infty` | ∞ |
| Matrix | `\begin{matrix} a & b \\ c & d \end{matrix}` | matrix |

## Best Practices

1. **Use semantic markup** - `\section{Overview}` not raw formatting
2. **Number equations** - Enable cross-referencing with `\label{}` and `\ref{}`
3. **Consistent notation** - Define notation in a dedicated section
4. **Modular structure** - Use `\input{}` for large documents
5. **Version control** - Keep .tex files in Git

## Resources

### scripts/
- `compile.sh` - Compile LaTeX to PDF
- `convert-to-word.sh` - Convert to Word format
- `validate-latex.sh` - Validate LaTeX syntax

### templates/
- `article-template.tex` - Standard article
- `report-template.tex` - Technical report
- `slides-template.tex` - Presentation slides

### references/
- `math-guide.md` - Mathematical notation guide
- `symbols.md` - LaTeX symbols reference
