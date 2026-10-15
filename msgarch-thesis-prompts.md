# MS-GARCH Master's Thesis — Prompt Pack

Two things live in here:

- **Part A — the Master Prompt.** Paste this at the top of every new session/chat before asking for anything. It carries the whole project spec.
- **Part B — Chapter sub-prompts.** Fire these one at a time, in order, in the same session (or a fresh one with Part A re-pasted). Never ask for "the whole thesis" in one go — you get 60 pages of mush.

Part C has the guardrails and the QA prompts for when drafts come back.

---

## PART A — MASTER PROMPT (paste first, every session)

> You are acting as my thesis supervisor and co-author for a Master's research project in financial econometrics. Read this entire brief before responding. Do not start writing prose until I give you a specific chapter prompt.
>
> **THE PROJECT**
>
> Title (working): *Markov-Switching GARCH Models: A Comparative Study of Path-Dependence Solutions, with an Application to S&P 500 Volatility.*
>
> This is **not** a paper claiming a new estimator. It is a rigorous comparative study: I take the four canonical solutions to the path-dependence problem in Markov-switching GARCH, present them in a single unified notation, derive/state their probabilistic properties, estimate all of them on the same data with the same protocol, and evaluate them on the same loss functions. A final chapter carries the best univariate specification into the multivariate setting.
>
> Target length: **55–60 pages max** of body text (excluding front matter, references, appendices). Density and correctness matter more than coverage — if something doesn't earn its page, cut it.
>
> **THE SIX SOURCE PAPERS** (these are the spine of the project; I have all six)
>
> 1. **Cai (1994)**, "A Markov Model of Switching-Regime ARCH", *JBES* 12(3), 309–316. Markov-switching ARCH(q) with a switching intercept in the variance. Path dependence is dodged by using **finite-memory ARCH**, so the likelihood requires integrating over only k^(q+1) regime paths. Application: monthly excess returns on the 3-month T-bill; finds two regime shifts (1974:2–1974:8, 1979:9–1982:8) and concludes that apparent ARCH persistence is largely spurious once shifts in the asymptotic variance are allowed.
> 2. **Hamilton and Susmel (1994)**, "Autoregressive conditional heteroskedasticity and changes in regime", *Journal of Econometrics* 64, 307–333. The **SWARCH** model: an ARCH(q) process whose scale is multiplied by a regime-dependent factor g_{s_t}. Two to four regimes, Gaussian and Student-t innovations, weekly CRSP value-weighted NYSE returns. Same finite-memory device as Cai; adds optimal forecasting and a richer regime structure.
> 3. **Gray (1996)**, "Modeling the conditional distribution of interest rates as a regime-switching process", *JFE* 42, 27–62. The **generalized regime-switching (GRS)** model. Breaks path dependence by *collapsing* the lagged conditional variance: at each step the regime is integrated out, and the recursion is fed the aggregated variance implied by the regime probabilities. Allows GARCH dynamics, state-dependent (time-varying) transition probabilities, and nests GARCH and square-root short-rate specifications.
> 4. **Klaassen (2002)** [working paper 2000], "Improving GARCH volatility forecasts with regime-switching GARCH", *Empirical Economics* 27, 363–394. Modifies Gray's collapsing step to condition on a **broader information set** — the expectation of the lagged variance is taken conditional on the *current* regime as well as on time t−1 information. This gives more flexible persistence and, crucially, a **simple recursion for multi-step-ahead forecasts**. Application: ~20 years of daily USD/GBP, USD/DEM, USD/JPY; shows single-regime GARCH forecasts are too high in volatile periods.
> 5. **Haas, Mittnik and Paolella (2004)**, "A New Approach to Markov-Switching GARCH Models", *Journal of Financial Econometrics* 2(4), 493–530. The **independent-switching (IS-GARCH)** model: k *parallel* GARCH recursions, one per regime, each updated with the observed shock, so path dependence disappears **exactly** rather than by approximation. They derive stationarity conditions, unconditional moments (including kurtosis) and the autocorrelation function of squares, and argue the "disaggregated" variance components are more interpretable. Exchange-rate application; best model is IS-GARCH with a skewed conditional mixture density.
> 6. **Haas and Liu (2015)**, "Theory for a Multivariate Markov-Switching GARCH Model with an Application to Stock Markets", conference paper, Verein für Socialpolitik / EconStor hdl:10419/112855. Multivariate MS-GARCH with regime-specific volatility dynamics, leverage effects and correlation structures. Contributions: stationarity conditions, **consistency of the MLE** under Gaussian innovations, an **LM test** for correct specification of the correlation dynamics, and a recursion for multi-step-ahead conditional covariance matrices. Application to global stock market and real estate equity returns; two-regime Student-t wins, with **higher correlations in the turbulent regime**.
>
> **THE INTELLECTUAL SPINE** (every chapter must serve this)
>
> The single organising problem is **path dependence**: in a GARCH recursion σ²_t depends on σ²_{t−1}, which depends on the entire history of regimes, so the exact likelihood requires summing over k^T paths. The literature offers exactly three escapes, and this thesis is the systematic comparison of them:
>
> - **(a) Truncate the memory** — Cai (1994), Hamilton and Susmel (1994): use ARCH(q) so only k^(q+1) paths matter. Exact, but no GARCH parsimony.
> - **(b) Collapse the state** — Gray (1996), Klaassen (2002): replace the path-dependent lagged variance with a conditional expectation. Approximate, but keeps GARCH; the two differ in *which* information set the collapse conditions on, and that difference has real consequences for persistence and for multi-step forecasting.
> - **(c) Remove the dependence by construction** — Haas, Mittnik and Paolella (2004): run k parallel recursions. Exact and tractable, and the only one with a clean analytical theory (stationarity, moments, ACF).
>
> The secondary thread running through all six papers: **regime switching absorbs the spurious near-integrated persistence (α+β → 1) of single-regime GARCH** (Diebold 1986; Lamoureux and Lastrapes 1990; Mikosch and Stărică 2004), which is why MS-GARCH forecasts are lower and better in turbulent periods.
>
> **NOTATION (use this everywhere, without deviation)**
>
> - ε_t = r_t − μ_{Δ_t}: demeaned return; Δ_t ∈ {1,…,k}: latent first-order Markov chain; P = (p_ij) transition matrix; π stationary distribution.
> - ξ_{t|t} = filtered regime probabilities, ξ_{t|t−1} = predicted, ξ_{t|T} = smoothed.
> - Ψ_{t−1} = the econometrician's information set.
> - Regime-specific variance: σ²_{j,t} for regime j. Aggregated/observable variance: h_t = E[ε²_t | Ψ_{t−1}].
> - Write each model as a *filter*: (i) the variance recursion, (ii) what is fed into it as the lagged variance, (iii) the log-likelihood contribution, (iv) the forecast recursion. That four-line template is how the models are compared throughout.
>
> **THE EMPIRICAL DESIGN**
>
> - Data: daily S&P 500 log returns, roughly 1990–2025 (state the exact sample and source when I give you the data chapter). Percentage returns (×100) for numerical stability.
> - Software: **R**. The `MSGARCH` package (Ardia, Bluteau, Boudt, Catania, Trottier) for the specifications it supports; my own hand-coded filters for the variants it does not (Gray's collapse, Klaassen's collapse, SWARCH). All estimation by ML/QML with numerical scores, multiple random starts, and a documented treatment of label switching.
> - Model set: GARCH(1,1) and GJR-GARCH(1,1) benchmarks (Normal and Student-t), SWARCH/MS-ARCH, Gray, Klaassen, and IS-GARCH; k = 2 and k = 3; Normal, Student-t and skewed-t innovations. Core specification for the deepest treatment: **two-regime IS-GARCH(1,1) with Student-t innovations**.
> - Evaluation: in-sample log-likelihood, AIC/BIC; rolling-window out-of-sample one-step and multi-step forecasts scored with MSE and **QLIKE** against a realized-variance proxy; **Diebold–Mariano** tests and the **Model Confidence Set** (Hansen, Lunde, Nason 2011); density forecasting via **VaR backtests** (Kupiec unconditional coverage, Christoffersen conditional coverage, Engle–Manganelli DQ) and an expected-shortfall test.
> - Application chapter: a decision-based evaluation (volatility-targeted position sizing or a variance-minimising hedge ratio) so the comparison is scored in economic and not only statistical terms.
> - Multivariate coda: Haas and Liu (2015) applied to a small system (S&P 500 plus one or two other indices / a REIT index), testing the "correlations rise in the turbulent regime" result.
>
> **THEORY I WANT TREATED PROPERLY** (this is what makes it a Master's thesis and not a survey)
>
> - Stationarity and ergodicity of MS-GARCH: the Lyapunov-exponent / spectral-radius condition on the matrix built from the regime-specific GARCH parameters and P (Haas et al. 2004; Francq and Zakoïan). Show why regime-wise stationarity is neither necessary nor sufficient for stationarity of the switching process.
> - Unconditional moments and the ACF of squares under IS-GARCH.
> - QML asymptotics: consistency and asymptotic normality, what is known and what is assumed; consistency of the MLE in the multivariate model (Haas and Liu 2015).
> - **The Davies problem**: testing k = 1 against k = 2 involves nuisance parameters unidentified under the null and a score that is identically zero in some directions, so standard LR asymptotics fail. State the problem honestly, describe the bootstrap and Hansen/Garcia-type alternatives, and say plainly what my own model selection can and cannot claim.
> - Identification and label switching; the practical estimation pathologies (unbounded likelihood, local optima, near-degenerate regimes).
>
> **HOW YOU MUST WORK**
>
> - **Never invent a citation, a theorem number, an equation number, a page number or an empirical result.** If you need a result from one of the six papers and are not certain of it, say "verify against [paper, section]" in a bracketed flag rather than asserting it. I will check every flag.
> - Distinguish always between (i) what a source proves, (ii) what a source claims without proof, and (iii) what I will show empirically.
> - Derivations get shown, not gestured at. When a step is standard, say which standard result is being used.
> - Write in formal academic English, third person or first-person plural, no bullet-point filler in the body text, LaTeX-ready. Equations numbered by chapter.
> - Every chapter draft ends with: (1) a list of the claims in it that need verification against sources, (2) the specific figures/tables it assumes will exist, (3) what the next chapter must pick up.
> - Push back on me. If a chapter's scope is unrealistic for the page budget or the design is weak, say so before writing.
>
> **PAGE BUDGET** (55–60 pages body)
>
> | Ch | Content | Pages |
> |----|---------|-------|
> | 1 | Introduction, research questions, contribution, roadmap | 5 |
> | 2 | Volatility modelling and the spurious-persistence problem; Markov-switching foundations (Hamilton filter, smoother, EM/ML) | 8 |
> | 3 | The path-dependence problem and the four solutions in unified notation (Cai; Hamilton–Susmel; Gray; Klaassen; Haas et al.) | 12 |
> | 4 | Probabilistic theory: stationarity, moments, ACF, QML asymptotics, the Davies problem | 10 |
> | 5 | Data, estimation protocol, in-sample results | 8 |
> | 6 | Out-of-sample forecasting and density/VaR evaluation | 8 |
> | 7 | Multivariate MS-GARCH (Haas and Liu 2015): theory and small application | 6 |
> | 8 | Conclusion, limitations, further research | 3 |
>
> Confirm you have absorbed this brief in **no more than 150 words**, flag anything you think is under-specified or over-ambitious, and then wait for my chapter prompt.

---

## PART B — SUB-PROMPTS (one at a time, in order)

### B0 — Planning (run this first)

> Before any writing: produce the full thesis plan. For each of the eight chapters give me (a) the section and subsection headings, (b) two or three sentences on the argument of each section, (c) the equations that must appear, (d) the tables and figures it needs with their exact intended content, (e) the page allocation, and (f) the source papers and any outside references each section leans on. Then give me a one-page "critical path": which analyses have to be run in R, and in what order, for the writing to be unblocked. End with the three biggest risks to finishing this at 60 pages and how to mitigate each.

### B1 — The comparison table (do this before Chapter 3)

> Build the central comparison table of the thesis. Rows: Cai (1994), Hamilton–Susmel (1994), Gray (1996), Klaassen (2002), Haas–Mittnik–Paolella (2004). Columns: variance recursion; what is substituted for the lagged variance; is path dependence removed exactly or by approximation; number of paths in the likelihood; can it do analytic multi-step forecasts; are stationarity conditions known; free parameters for k=2; original application and data. Then, in prose, explain what each cell of the "approximation" column actually costs — be precise about how Gray's collapse and Klaassen's collapse differ in the information set they condition on, and what that difference does to persistence and to forecasting. Flag anything you are not certain of for me to verify.

### B2 — Chapter 3 (the analytical core; write this before Chapters 1–2)

> Draft Chapter 3 in full, ~12 pages. Present all four solutions in the unified notation from the brief, each as the four-line filter template. Structure: 3.1 the path-dependence problem stated formally, with the k^T likelihood; 3.2 finite-memory solutions (Cai; Hamilton–Susmel's SWARCH scale factor); 3.3 collapsing solutions (Gray; then Klaassen's modification, with the difference made explicit); 3.4 independent switching (Haas et al.), including why the parallel recursions are exact; 3.5 the comparison table and a synthesis of the trade-offs. End with the three required lists.

### B3 — Chapter 4 (theory)

> Draft Chapter 4, ~10 pages: 4.1 stationarity and ergodicity of MS-GARCH — state the Lyapunov/spectral-radius condition and show why regime-wise stationarity is neither necessary nor sufficient; 4.2 unconditional variance, kurtosis and the ACF of squares under IS-GARCH; 4.3 QML/ML asymptotics — what is proved, under what conditions, and what remains assumed in practice; 4.4 the Davies problem and testing for the number of regimes, including the bootstrap alternative and an explicit statement of what my model selection can legitimately claim; 4.5 identification, label switching and estimation pathologies. Give proofs or proof sketches with the standard results named. Flag every result that must be checked against Haas et al. (2004), Haas and Liu (2015) or Francq–Zakoïan.

### B4 — The R work

> Write the R analysis plan and code skeleton: data ingestion and return construction; a reusable filter interface so Gray, Klaassen, SWARCH and IS-GARCH can all be estimated and compared through the same functions; likelihood implementations for the models `MSGARCH` doesn't cover; a multi-start optimiser with a label-switching normalisation; a rolling-window forecasting harness producing one-step and h-step forecasts for every model; scoring with MSE and QLIKE; Diebold–Mariano and Model Confidence Set; VaR/ES backtests. Include the numerical-stability details that actually bite here (log-sum-exp in the filter, variance-targeting or parameter transforms for constraints, sensible starting values). Then a Monte Carlo design: simulate from IS-GARCH, estimate under all four filters, and quantify the bias from Gray's and Klaassen's approximations — this is the strongest original-contribution-per-page in the project.

### B5 — Chapters 5 and 6 (empirics) — run only after you have results

> Here are my estimation results: [PASTE TABLES]. Draft Chapter 5 (~8 pages): data description and stylised facts; estimation protocol; in-sample results with regime interpretation, smoothed probabilities against known crisis periods, the persistence comparison against single-regime GARCH, and information criteria. Then Chapter 6 (~8 pages) from these forecast results: [PASTE]. Interpret, don't just narrate the tables: say what each result implies for the path-dependence trade-off from Chapter 3. Where a result contradicts the published papers, say so explicitly and offer the most likely reason.

### B6 — Chapter 7 (multivariate coda)

> Draft Chapter 7, ~6 pages, on Haas and Liu (2015): the model's structure (regime-specific dynamics, leverage, correlation structures); the stationarity conditions; the consistency result for the MLE; the LM test for correlation dynamics; the multi-step covariance recursion; then my small application [PASTE RESULTS]. Frame it as a bounded extension, not a second thesis: the question is whether the univariate ranking survives in the multivariate setting and whether the "correlations rise in the turbulent regime" finding replicates on my data. Be explicit about the curse of dimensionality and why the application stays small.

### B7 — Chapters 1, 2 and 8 (write these last)

> Now that Chapters 3–7 are drafted, write Chapter 1 (~5pp: motivation, the three research questions the thesis actually answers, contribution stated modestly and accurately, roadmap), Chapter 2 (~8pp: GARCH and the spurious-persistence literature; Hamilton's filter, the smoother and ML estimation of Markov-switching models — everything Chapter 3 assumes and nothing more), and Chapter 8 (~3pp: findings, limitations stated honestly, further research). The introduction must promise exactly what the later chapters deliver — check it against them line by line.

---

## PART C — QA AND REVISION PROMPTS

**Verification pass** (run on every chapter):

> Go through this chapter and produce a verification table: every factual claim, attribution, theorem, equation and numerical result, with the source it needs to be checked against and the page/section where I should look. Mark anything you generated from general knowledge rather than from the six papers. Do not defend the text — find its weak points.

**Consistency pass** (after all chapters exist):

> Check the full draft for: notation drift against the brief's notation block; equations that are stated in one chapter and used inconsistently in another; claims in the introduction not delivered later; duplicated material across Chapters 2, 3 and 4; and any place where I assert something the results don't support. Give a numbered list of fixes ordered by severity.

**Examiner pass** (before submission):

> Act as a critical external examiner in financial econometrics. Give me the ten hardest questions you would ask in the defence, the three weakest points of the thesis, and for each weak point whether it is best fixed, bounded by an explicit limitation, or defended.

**Trimming pass** (when it runs long):

> The body is [N] pages against a 60-page limit. Identify what to cut, in priority order, without weakening the argument. Prefer cutting duplicated exposition and standard textbook material over cutting derivations or results.

---

## NOTES ON USING THIS

- Write **Chapter 3 first**. It is the analytical core and everything else is scaffolding around it; the introduction cannot be written honestly until it exists.
- Feed results in, never ask for them. Any table an AI writes without your R output is fiction.
- The Monte Carlo in B4 is the cheapest genuine contribution available to you: it turns "these approximations differ" from a claim into a measurement, and it costs a few pages.
- Keep the verification flags in the drafts until you have actually checked them. They are the difference between a thesis and a plausible-sounding one.
