# Literature Review — Prompt Pack (MS-GARCH thesis)

**Updated for the current thesis plan.** The standing rules (thesis framing, structure, notation, source and writing rules) now live in the **Project instructions**, so this pack no longer repeats them. It contains only what is specific to the literature review: the brief (Part A), the working bibliography (Part B), and the sub-prompts (Part C).

Run this inside the thesis Project, with the PDFs, `notation.md` and `decisions.md` in the project context. Paste **Part A** first, then **Part B**, then fire the sub-prompts one at a time.

---

## WHAT CHANGED SINCE THE LAST VERSION

- The review is now **Chapters 2 and 3 of the thesis, ~20 pages (~7,000 words)**, not 10–14 pages spread across two chapters.
- Chapter 3 is organised around **four branches** (avoid / collapse / confront / remove), which is the review's analytical spine.
- **Theory, regime testing, forecasting evidence and the multivariate work have moved out** of the review and into Chapters 4, 5 and 7. The review sets them up; it does not cover them.
- The **Confront branch is conceptual only** — not estimated in the thesis.
- Notation is now **binding and file-based** (`notation.md`), not negotiated per chat.
- The application chapter is **hedging** (Chapter 6). VaR/ES backtesting is optional, not core.
- Papers held has risen from 6 to **24**; the bibliography below is re-marked accordingly.

---

## PART A — LITERATURE-REVIEW BRIEF (paste first)

> You are acting as my research assistant and supervisor for the literature review of my Master's thesis. The Project instructions, `notation.md` and `decisions.md` govern everything; this brief adds what is specific to the review. Read it fully before responding; do not write prose until I give you a specific sub-prompt.
>
> **WHAT THE REVIEW IS**
>
> The literature review is **Chapters 2 and 3** of the thesis, about **20 pages (~7,000 words)**:
>
> - **Chapter 2 — From ARCH to the persistence puzzle (~8 pp, ~2,800 words).** Brisk. Its only job is to make regime switching feel inevitable: ARCH, GARCH, IGARCH, the near-integrated persistence estimate, the argument that it is an artefact of neglected structural change, and Hamilton's filter as the natural fix.
> - **Chapter 3 — The models and the path dependence problem (~12 pp, ~4,200 words).** The analytical core.
>
> This is not an annotated bibliography and not a chronological march through papers. Chapter 3 is an **argumentative review organised around one problem**: path dependence in Markov-switching GARCH, and the competing solutions to it.
>
> **THE FOUR BRANCHES** (the spine of Chapter 3)
>
> Open by deriving path dependence explicitly — why the literal MS-GARCH likelihood requires K^t regime paths — then take each branch in turn. For every branch: specification, how it handles path dependence, what it gains, what it costs, and key empirical findings.
>
> 1. **Avoid it** (MS-ARCH) — Cai (1994); Hamilton and Susmel (1994). Finite ARCH memory keeps the filter tractable; GARCH parsimony is lost.
> 2. **Collapse it** — Gray (1996); Klaassen (2002). Aggregate the regime variances each period; full switching GARCH at the cost of an approximation and weak theory.
> 3. **Confront it** — Francq and Zakoïan; Bauwens, Preminger and Rombouts (2010); Augustyniak (2014). Keep the literal model and estimate it by simulation. **About 1 page, conceptual only — not estimated in my thesis.** Its job is to show that choosing branch 4 is a choice for tractability, not the only feasible option.
> 4. **Remove it** (IS-GARCH) — Haas, Mittnik and Paolella (2004); Haas and Liu. Parallel regime recursions; path dependence never arises.
>
> Close Chapter 3 with **(a)** a comparison table across branches (specification; path-dependence treatment; stationarity theory; forecast tractability; estimation feasibility) and **(b)** a justification of IS-GARCH as the focal model on tractability and theory grounds — not on fit, which is the empirical chapters' job.
>
> **WHAT THE REVIEW MUST SET UP BUT NOT COVER**
>
> These belong to later chapters. Flag them where relevant, in a sentence, and move on:
>
> - Stationarity, ergodicity, moments, QMLE asymptotics → Chapter 4
> - The Davies problem and testing the number of regimes → Chapter 4
> - Forecasting and risk evidence → Chapter 5
> - Multivariate and regime-dependent correlations → Chapter 7 coda
>
> If you find yourself writing more than a paragraph on any of these, stop and tell me — it means material is in the wrong chapter.
>
> **PAPERS I HAVE IN FULL** (the spine; everything specific must come from these)
>
> - **Engle (1982)**, *Econometrica* 50, 987–1008 — ARCH; conditional vs unconditional variance; stationarity; the TR² LM test.
> - **Bollerslev (1986)**, *J. Econometrics* 31, 307–327 — GARCH; A(1)+B(1)<1; ARMA representation of squares; the singular LM test.
> - **Cai (1994)**, *JBES* 12(3), 309–316 — MS-ARCH with a switching variance intercept; monthly T-bill excess returns; ARCH persistence largely spurious once regime shifts are allowed; Monte Carlo LR critical values.
> - **Hamilton and Susmel (1994)**, *J. Econometrics* 64, 307–333 — SWARCH: ARCH(q) scaled by a regime factor; 2–4 regimes; Gaussian and Student-t; weekly NYSE returns; persistence falls from 0.96 to 0.48.
> - **Gray (1996)**, *JFE* 42, 27–62 — breaks path dependence by collapsing the lagged conditional variance via regime probabilities; state-dependent transition probabilities; short-rate application.
> - **Klaassen (2002)**, *Empirical Economics* 27, 363–394 — modifies Gray's collapse to use t−1 information conditional on the current regime; easy multi-step recursion; argues Student-t stabilises the regimes; daily FX.
> - **Haas, Mittnik and Paolella (2004)**, *J. Financial Econometrics* 2(4), 493–530 — IS-GARCH: k parallel recursions, path dependence removed exactly; ρ(M)<1, moments, ACF of squares; individually nonstationary regimes; persistence does **not** always migrate to the Markov chain.
> - **Haas and Liu** — my file is the **2015 conference version**; cite the published article, **Haas and Liu (2018)**, *Studies in Nonlinear Dynamics & Econometrics* 22(3). Strict stationarity, MLE consistency under Gaussian innovations, LM test for correlation dynamics, multi-step covariance recursion; higher correlations in the turbulent regime.
>
> I also hold the Chapter 4 theory papers (see Part B). They are available for you to check, but they belong to Chapter 4, not the review.
>
> **REVIEW-SPECIFIC RULES** (in addition to the Project instructions)
>
> - Distinguish always: what a paper **proves**, what it **asserts**, what it **finds empirically on its own data**, and what later work **contests**.
> - Mark each paper's contribution type: theoretical, methodological, computational, empirical, or survey.
> - Where the literature disagrees, present the disagreement. Do not smooth it into a false consensus — the Haas et al. finding that persistence did not migrate for the yen and pound must not be suppressed.
> - Be blunt about limitations, including of the papers I hold. A review that praises everything is worthless to an examiner.
> - Treat the branches evenly. Chapter 3 justifies studying IS-GARCH closely; it does not argue that IS-GARCH wins.
>
> **WORKING ARTEFACTS** (besides the prose)
>
> (i) an evidence table, one row per paper; (ii) the branch comparison table for §3.6; (iii) a verification worklist.
>
> Confirm in under 120 words that you have this, then wait.

---

## PART B — WORKING BIBLIOGRAPHY (paste as the second message)

> Here is the working bibliography for the whole thesis, with the chapter each cluster serves. **[have]** = PDF in the project. **[checked]** = citation details verified. **[verify]** = provisional, flag if you rely on it. **[to collect]** = I do not have it yet; describe only its well-established main contribution and mark anything specific with [VERIFY].
>
> Do not silently drop papers, and tell me if a cluster is missing something important.
>
> **1. The persistence puzzle — Chapter 2**
> - Engle (1982), *Econometrica* 50, 987–1008. [have]
> - Bollerslev (1986), *J. Econometrics* 31, 307–327. [have]
> - Engle and Bollerslev (1986), "Modelling the persistence of conditional variances", *Econometric Reviews* 5, 1–50. [have]
> - Diebold (1986), "Modeling the persistence of conditional variances: A comment", *Econometric Reviews* 5, 51–56. [have]
> - Lamoureux and Lastrapes (1990), "Persistence in variance, structural change, and the GARCH model", *JBES* 8(2), 225–234. [have]
> - Mikosch and Stărică (2004), *Review of Economics and Statistics* 86(1), 378–390. [to collect]
> - Hillebrand (2005), "Neglecting parameter changes in GARCH models", *J. Econometrics* 129, 121–138. [to collect]
>
> **2. Markov-switching foundations — Chapter 2**
> - Hamilton (1989), *Econometrica* 57, 357–384. [have]
> - Hamilton (1994), *Time Series Analysis*, Princeton UP, ch. 22 — cite only for standard filtering results. [not in project]
> - Kim (1994), "Dynamic linear models with Markov-switching", *J. Econometrics* 60, 1–22. [have]
> - Hamilton (1990), *J. Econometrics* 45, 39–70. [to collect]
> - Timmermann (2000), "Moments of Markov switching models", *J. Econometrics* 96, 75–111. [to collect]
>
> **3. The path-dependence branches — Chapter 3 (the core)**
> - *Avoid:* Cai (1994), *JBES* 12(3), 309–316 [have]; Hamilton and Susmel (1994), *J. Econometrics* 64, 307–333 [have].
> - *Collapse:* Gray (1996), *JFE* 42, 27–62 [have]; Klaassen (2002), *Empirical Economics* 27, 363–394 [have]; Dueker (1997), *JBES* 15(1), 26–34 [to collect, cite only].
> - *Confront:* Francq, Roussignol and Zakoïan (2001), *JTSA* 22(2), 197–220 [to collect]; Francq and Zakoïan (2005), *SPA* 115, 1557–1582 [have]; Bauwens, Preminger and Rombouts (2010), *Econometrics Journal* 13(2), 218–244 [have, checked]; Augustyniak (2014), *CSDA* 76, 61–75 [have, checked].
> - *Remove:* Haas, Mittnik and Paolella (2004), *J. Financial Econometrics* 2(4), 493–530 [have]; Haas and Liu (2018), *SNDE* 22(3) [have, 2015 working version].
> - *Related:* Haas, Mittnik and Paolella (2004b), "Mixed normal conditional heteroskedasticity", *J. Financial Econometrics* 2(2), 211–250 — the i.i.d.-regime sibling of IS-GARCH [to collect, one sentence]; Alexander and Lazar (2006), *JAE* 21, 307–336 [to collect, optional]; Haas and Paolella (2012), in *Handbook of Volatility Models*, Wiley [to collect, optional survey].
>
> **4. Probabilistic theory — Chapter 4, not the review**
> - Nelson (1990), "Stationarity and persistence in the GARCH(1,1) model", *Econometric Theory* 6(3), 318–334. [have]
> - Bougerol and Picard (1992), *J. Econometrics* 52, 115–127. [have]
> - Liu (2006), "Stationarity of a Markov-switching GARCH model", *J. Financial Econometrics* 4(4), 573–593. [have]
> - Francq and Zakoïan (2004), "Maximum likelihood estimation of pure GARCH and ARMA-GARCH processes", *Bernoulli* 10(4), 605–637. [have]
> - Newey and Steigerwald (1997), *Econometrica* 65(3), 587–599. [have]
> - Bollerslev (1987), *REStat* 69(3), 542–547 — Student-t GARCH. [have]
> - Abramson and Cohen (2007), *Econometric Theory* 23(3), 485–500. [to collect, optional]
> - Francq and Zakoïan, *GARCH Models*, Wiley — the QML asymptotics reference. [to collect, optional] [verify edition/year]
>
> **5. Testing the number of regimes — Chapter 4, not the review**
> - Davies (1977), *Biometrika* 64, 247–254. [have]
> - Cho and White (2007), "Testing for regime switching", *Econometrica* 75(6), 1671–1720. [have]
> - Hansen (1992), *JAE* 7, S61–S82. [to collect]
> - Garcia (1998), *IER* 39, 763–788. [to collect]
> - Carrasco, Hu and Ploberger (2014), *Econometrica* 82(2). [to collect, optional] [checked]
> - Psaradakis and Spagnolo (2003), *JTSA* 24, 237–252. [to collect, optional]
>
> **6. Estimation and computation — Chapters 3 and 5**
> - Ardia, Bluteau, Boudt, Catania and Trottier (2019), "Markov-switching GARCH models in R: The MSGARCH package", *JSS* 91(4). [to collect] [checked]
> - Bauwens, Preminger and Rombouts (2010) — see cluster 3. [have]
> - Augustyniak (2014) — see cluster 3. [have]
> - Billio, Casarin and Osuntuyi (2016), *CSDA* 100, 37–57. [to collect, optional] [checked]
> - Kaufmann and Frühwirth-Schnatter (2002), *JTSA* 23, 425–458. [to collect, optional]
>
> **7. Forecasting and evaluation — Chapter 5, not the review**
> - Marcucci (2005), *SNDE* 9(4). [to collect] [checked]
> - Ardia, Bluteau, Boudt and Catania (2018), *IJF* 34(4), 733–747. [to collect] [checked]
> - Patton (2011), *J. Econometrics* 160, 246–256. [to collect]
> - Diebold and Mariano (1995), *JBES* 13, 253–263. [to collect]
> - Andersen and Bollerslev (1998), *IER* 39, 885–905. [to collect]
> - Hansen and Lunde (2005), *JAE* 20, 873–889. [to collect, optional]
> - Hansen, Lunde and Nason (2011), "The model confidence set", *Econometrica* 79(2), 453–497. [to collect, optional]
> - Kupiec (1995), *Journal of Derivatives* 3, 73–84; Christoffersen (1998), *IER* 39, 841–862 — only if I report VaR. [to collect, optional]
>
> **8. Hedging — Chapter 6, not the review**
> - Kroner and Sultan (1993), *JFQA* 28(4), 535–551. [to collect]
> - Lee and Yoder (2007), *Applied Economics* 39(10), 1253–1265. [to collect]
> - Alizadeh, Nomikos and Pouliasis (2008), *JBF*. [to collect, optional]
>
> **9. Multivariate — Chapter 7 coda, not the review**
> - Haas and Liu (2018) — see cluster 3. [have]
> - Bollerslev (1990), CCC, *REStat* 72, 498–505. [to collect]
> - Pelletier (2006), "Regime switching for dynamic correlations", *J. Econometrics* 131, 445–473. [to collect, optional]

---

## PART C — SUB-PROMPTS

Run C0 first if `notation.md` does not yet exist. C1 is optional now that the papers are collected; run it only if you want a search protocol for the appendix.

### C0 — Notation reconciliation (run before any writing)

> Read the papers I hold and reconcile their notation against `notation.md`. List every conflict you find — for example h_t vs σ²_t for the conditional variance, the row-vs-column convention for the transition matrix, ξ vs δ for leverage, and the different symbols for the information set — and say how each paper's notation maps onto ours. Flag any symbol the review will need that `notation.md` does not yet define as **NEW SYMBOL**, with a proposal and a reason. Do not write prose yet.

### C1 — Search strategy (optional, for the appendix)

> Produce a reproducible search protocol I can put in an appendix: databases and indices (Google Scholar, Scopus, Web of Science, RePEc/IDEAS, EconLit, SSRN, arXiv q-fin), Boolean query strings per branch, inclusion and exclusion criteria, and a citation-chasing plan. Name the five papers most worth forward-chasing and what I am looking for in each. Flag post-2018 territory I should check: large-scale forecast comparisons, Bayesian estimation, and the interaction of regime switching with realized-volatility and HAR models.

### C2 — Gap-and-triage pass

> Using the bibliography, do three things. (a) Identify what is missing for **Chapters 2 and 3 specifically** — thin clusters and named papers I should add, each with one line on why it matters and a [VERIFY] flag on anything you are not certain exists. (b) Triage into "must read in full" (about 10 for the review), "read the abstract and results" (about 8), and "cite only". (c) Give the reading order, sequenced so each paper makes the next easier. Do not pull Chapter 4–7 papers into this triage.

### C3 — Evidence extraction table

> Build the evidence table, one row per paper in the must-read tier. Columns: citation; contribution type; the model or result in one line; **branch** (avoid / collapse / confront / remove / not applicable); path-dependence treatment (exact / collapsed / truncated / n.a.); data and sample; headline finding; stated limitation; how it relates to the papers I hold (extends / contests / applies / supersedes). Markdown table. Flag every cell you are not certain about rather than filling it in plausibly.

### C4 — Branch syntheses (the analytic work)

> Write a synthesis of 500–700 words for each of the four branches: what that branch's papers collectively establish, the precise trick each uses on path dependence, what it costs, where the branch's own authors concede limitations, and what the branch leaves unresolved for the next one. Cite specific papers for every claim, using our notation throughout. No generic transitions — every sentence should carry content. End each synthesis with the sentence that will lead into the next branch.

### C5 — Chapter 2 draft

> Draft Chapter 2 (~2,800 words), following the outline you gave me. It must be an argument about intellectual pressure — each step solving a problem left by the previous one — not a timeline. It ends by making regime switching feel like the obvious next move, and hands over to Chapter 3 by naming path dependence as the obstacle. Include the placeholder for my motivating figure: a GARCH(1,1) fit to the S&P 500 sample with rolling persistence estimates.

### C6 — Chapter 3 draft

> Draft Chapter 3 (~4,200 words) using the C4 syntheses. Structure: 3.1 deriving path dependence; 3.2 avoid; 3.3 collapse; 3.4 confront (about 1 page); 3.5 remove; 3.6 comparison table and the case for IS-GARCH as the focal model. Keep 3.6's justification to tractability and theory — the empirical case is Chapter 5's job, so do not pre-empt it. End with the verification list and every reference cited.

### C7 — Verification pass (mandatory before I use anything)

> Produce a verification worklist: every citation in the draft with full bibliographic details as you have them, a confidence rating (certain / likely / uncertain), and what specifically I should check. Separately list every empirical claim attributed to a source, with the section of that source where I should find it. Then list any claim you generated from general knowledge rather than from a paper in the project — I will either source it or cut it. Flag every number taken from a paper I do not hold.

### C8 — Adversarial pass

> Critique Chapters 2 and 3 as a hostile examiner. Where is it thin? Which papers are cited but clearly not read? Where does it accept a claim uncritically? Is the branch taxonomy doing analytical work, or is it just a filing system? Does §3.6 read as a justification or as advocacy? What obvious counter-literature is missing? Give me the five most damaging questions and how I should handle each.

### C9 — Handover to Chapter 4

> List what Chapters 2 and 3 have promised but not delivered: every forward reference to theory, regime testing, forecasting or the multivariate work. For each, say which later chapter must honour it. Then list any NEW SYMBOLs and decisions I should add to `notation.md` and `decisions.md` before I start Chapter 4.

---

## NOTES

- **Verify before you cite, always.** Nothing an AI writes about a paper it has not read is trustworthy, including in the list above — the `[verify]` and `[to collect]` markers are real risks, not a formality. Check each against the publisher page or the PDF and keep everything in Zotero/BibTeX as you go.
- The Haas and Liu file in the project is the **2015 conference version**; cite the published article, **SNDE 22(3), 2018**.
- Two files are misnamed at source: "Hamilton 1993" is **Hamilton and Susmel (1994)**, and "Klassen 2000" is **Klaassen (2002)**, two a's. Rename the PDFs in the project so the model does not inherit the error.
- The **Ardia et al. (2019) MSGARCH paper is still uncollected** and is the highest-priority gap, since your code depends on it and you need to state exactly which specification the package estimates.
- The most useful thing C2 gives you is permission *not* to read thirty papers in full. Ten read properly beats fifty skimmed, and the examiner can tell the difference.
