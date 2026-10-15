# decisions.md

Modelling and writing decisions already made. Follow them; propose changes explicitly rather than drifting.

Last updated: 23 September 2026.

## 1. Writing and format

- **Citation style:** APA 7th edition.
- **Compile target:** LaTeX, with `biblatex` (`style=apa`, backend `biber`). Required packages so far: `amsmath`, `amssymb`, `bm`, `bbm` (for `\mathbbm{1}`).
- **In-text citations in .tex files:** `\textcite{}` for narrative, `\parencite{}` for parenthetical. Avoid possessive citation forms ("Engle's (1982)"); rephrase instead.
- **Citation keys:** lowercase surname(s) + year. One author: `engle1982`. Two authors: both surnames, `hamiltonsusmel1994`. Three or more: first surname + `etal`, `haasetal2004`. Same authors and year: suffix a/b in APA title order.
- **Equations:** numbered by chapter via `\label{eq:...}`; (2.1), (2.2), ….
- **Prose only** in chapter text: no bullet or numbered lists inside the thesis.
- **Spelling:** Australian/British (-ise, -our, "per cent") — *provisional, confirm*.
- **Word budget:** about 350 words per page including equations. Each subsection is drafted separately and stopped for feedback.

## 2. Sources

- **Not being added:** Engle & Bollerslev (1986, *Econometric Reviews*) and Lamoureux & Lastrapes (1990b, *JBES*, "Persistence in variance, structural change, and the GARCH model"). Where needed, cite them as APA 7 secondary sources, e.g. "(Lamoureux & Lastrapes, 1990b, as cited in Cai, 1994)". Only the source actually read goes in the reference list. Attribute to them only what the citing paper reports.
- **Mislabelled file:** "Engle_and_Bollerslev_1986.pdf" is Bollerslev & Engle (1993), *Econometrica* 61(1), "Common persistence in conditional variances". Cite it as such (`bollerslevengle1993`).
- **Lamoureux & Lastrapes file:** this is the 1990 *Journal of Finance* paper on volume versus GARCH effects (`lamoureuxlastrapes1990a`). It supports "persistence can reflect omitted structure (volume)", not the structural-break argument.
- **Notes PDFs are not sources:** Hamilton_1993_Notes.pdf and Klassen_2000_notes.pdf are summaries containing errors (e.g. SWARCH scale written as γ_{s_t}·ũ_t instead of √g_{s_t}·ũ_t). Never cite them; verify everything against the papers.
- **File names vs. papers:** Hamilton_and_Susmel_1993.pdf is Hamilton & Susmel (1994), *Journal of Econometrics* 64. Klassen_2000_Improving….pdf is Klaassen (2002), *Empirical Economics* 27.
- **Bauwens et al.:** cite Bauwens, Preminger & Rombouts (2010, *Econometrics Journal*). Do not cite the 2006 CORE discussion paper, which has a different model with time-varying transition probabilities.
- **Branch 3:** add Francq, Roussignol & Zakoïan (2001) for strict stationarity of the path-dependent model and ML consistency for MS-ARCH.
- **Francq & Zakoïan (2005):** gives moments and ARMA representations only. It does not itself propose an estimator; the moment-based estimator is in a companion paper not in the files.
- **Haas & Liu (2015):** cite as a conference paper (Beiträge zur Jahrestagung des Vereins für Socialpolitik 2015).
- **Engle (1982):** image-only scan. OCR text has been verified against page images for the numbers used.
- **Hamilton (1994), *Time Series Analysis*:** standard filtering results only.

### Citation keys (current set)

| Key | Reference |
|---|---|
| `engle1982` | Engle (1982), *Econometrica* 50(4) |
| `bollerslev1986` | Bollerslev (1986), *Journal of Econometrics* 31 |
| `bollerslev1987` | Bollerslev (1987), *Review of Economics and Statistics* 69(3) |
| `bollerslevengle1993` | Bollerslev & Engle (1993), *Econometrica* 61(1) |
| `diebold1986` | Diebold (1986), *Econometric Reviews* 5(1) |
| `lamoureuxlastrapes1990a` | Lamoureux & Lastrapes (1990a), *Journal of Finance* 45(1) |
| `hamilton1989` | Hamilton (1989), *Econometrica* 57(2) |
| `hamilton1994` | Hamilton (1994), *Time Series Analysis* (textbook; filtering only) |
| `hamiltonsusmel1994` | Hamilton & Susmel (1994), *Journal of Econometrics* 64 |
| `cai1994` | Cai (1994), *JBES* 12(3) |
| `gray1996` | Gray (1996), *Journal of Financial Economics* 42 |
| `klaassen2002` | Klaassen (2002), *Empirical Economics* 27 |
| `kim1994` | Kim (1994), *Journal of Econometrics* 60 [VERIFY volume] |
| `francqetal2001` | Francq, Roussignol & Zakoïan (2001), *Journal of Time Series Analysis* [VERIFY volume] |
| `francqzakoian2004` | Francq & Zakoïan (2004), *Bernoulli* [VERIFY] |
| `francqzakoian2005` | Francq & Zakoïan (2005), *Stochastic Processes and their Applications* 115 |
| `bauwensetal2010` | Bauwens, Preminger & Rombouts (2010), *Econometrics Journal* 13(2) |
| `augustyniak2014` | Augustyniak (2014), *Computational Statistics & Data Analysis* 76 |
| `haasetal2004` | Haas, Mittnik & Paolella (2004), *Journal of Financial Econometrics* [VERIFY volume] |
| `haasliu2015` | Haas & Liu (2015), conference paper |
| `ardiaetal2019` | Ardia et al. (2019), MSGARCH package paper [VERIFY outlet] |
| `nelson1990`, `bougerolpicard1992`, `liu2006`, `neweysteigerwald1997`, `davies1977`, `chowhite2007` | Chapter 4 papers |

[VERIFY] items are resolved from the papers' own title pages when the bibliography is compiled.

## 3. Notation

- notation.md is binding and approved (23 Sep 2026).
- a_m = lag-m ARCH coefficient; α is reserved for the GARCH(1,1) ARCH coefficient. m is the lag index.
- p appears only inside model labels such as GARCH(p,q).
- δ is leverage only; Markov persistence is written p_11 + p_22 − 1 without a symbol.
- σ²_t = Var(ε_t | F_{t−1}) in every model, including regime-switching ones.

## 4. Scope and modelling (from project brief)

- Comparison and application thesis, not a new model. Focal model: two-regime IS-GARCH(1,1) with Student-t innovations (Haas, Mittnik & Paolella, 2004).
- Estimated models: GARCH(1,1), SWARCH, Klaassen, IS-GARCH, each with normal and Student-t innovations. Branch 3 (full path-dependent model) is conceptual only, not estimated.
- Empirics in R: MSGARCH package plus hand-coded filters for SWARCH and Klaassen.

## 5. Approved outline: Chapters 2 and 3

Total about 6,800 words (Ch. 2 ≈ 2,800; Ch. 3 ≈ 4,000 plus table).

### Chapter 2 — From ARCH to the persistence puzzle (8 pp, ~2,800 words)

| § | Title | Words | Content |
|---|---|---|---|
| 2.1 | Volatility clustering and ARCH | 450 | Engle (1982): ARCH(q), LM test, UK inflation; fixed declining weights → hand-off to GARCH |
| 2.2 | GARCH(1,1) and what persistence means | 600 | Bollerslev (1986): recursion, ARCH(∞) form, α+β<1, ACF and forecast decay; Student-t (Bollerslev, 1987) |
| 2.3 | The persistence puzzle | 700 | IGARCH via Bollerslev & Engle (1993) and Diebold (1986); Diebold's regime-dummy argument; Lamoureux & Lastrapes (1990a) volume result; Bollerslev (1987) daily-vs-monthly contrast; Hamilton & Susmel's t-GARCH-L persistence 0.96 and forecast MSE 815.6 vs 757.9 ("symptom" evidence) |
| 2.4 | Regime switching as the alternative account | 650 | Hamilton (1989): Markov chain, filter, smoother, durations; Haas et al. (2004) simulation (GARCH absorbs Markov persistence) as the bridge |
| 2.5 | Two sources of persistence | 400 | shock persistence (α_k+β_k) vs regime persistence (p_11+p_22−1); combining them creates path dependence → Ch. 3 |

### Chapter 3 — The models and the path dependence problem (12 pp, ~4,000 words + table)

| § | Title | Words | Content |
|---|---|---|---|
| 3.1 | Deriving path dependence | 500 | unroll σ²_t(S_{1:t}); K^t paths; finite-lag condition for the Hamilton filter; evaluation template |
| 3.2 | Avoid: MS-ARCH | 750 | Cai (1994); Hamilton & Susmel (1994) SWARCH results ("cure" evidence); Francq et al. (2001) MS-ARCH ML consistency |
| 3.3 | Collapse: Gray and Klaassen | 800 | Gray (1996); Klaassen (2002); Kim (1994) as antecedent; Haas et al. interpretation critique; Augustyniak (2014) bias evidence |
| 3.4 | Confront: full path-dependent model | 650 | Francq et al. (2001); Francq & Zakoïan (2005); Bauwens et al. (2010); Augustyniak (2014). Conceptual only |
| 3.5 | Remove: IS-GARCH | 750 | Haas et al. (2004); Haas & Liu (2015); gains and costs; derivations deferred to Ch. 4 |
| 3.6 | Comparison and choice of focal model | 550 + table | comparison table; justification framed as a combination of properties, not superiority |

**Cut order if Ch. 3 runs long:** Gray's time-varying transition probabilities → Cai's mean switching → Francq & Zakoïan (2005) ARMA-representation detail.

## 6. Open issues (decide before Chapter 4 unless noted)

1. **MSGARCH constraint:** the package imposes covariance stationarity in each regime (Ardia et al., 2019, fn. 8), which is stronger than Haas et al.'s ρ(M) < 1 and rules out a locally nonstationary regime. Accept it, or hand-code IS-GARCH with only ρ(M) < 1?
2. **Student-t theory gap:** Haas & Liu (2015) prove MLE consistency for Gaussian innovations only; nothing in the files covers Student-t IS-GARCH. Decide how Chapter 4 handles this.
3. **Hedging model (needed before §3.5):** does Chapter 6 require a bivariate model (e.g. Haas & Liu's multivariate specification)?
4. **Spelling convention:** confirm Australian/British.

## 7. Progress log

| Section | Status | Words | Note |
|---|---|---|---|
| 2.1 | drafted, saved in ch2_draft.tex | ~490 | 40 over target |
| 2.2 | drafted, saved in ch2_draft.tex | ~640 | 40 over target; Ch. 2 running ~80 over, to be recovered in §2.5 |
