# notation.md

Binding notation for the thesis. Use these symbols even where a paper uses different ones; translate the paper's notation into ours (see the translation table at the end). Any symbol not listed here must be proposed and flagged as NEW SYMBOL before use.

Last updated: 23 September 2026.

## General

| Symbol | LaTeX | Meaning |
|---|---|---|
| T | `T` | sample size |
| t | `t` | time index |
| m | `m` | lag index in sums over past observations, e.g. `\sum_{m=1}^{q}` |
| q | `q` | ARCH order |
| p | `p` | GARCH order; used **only** inside model labels such as GARCH(p,q), never as a standalone symbol (avoids confusion with p_{ij}) |
| h | `h` | forecast horizon (h is free because h_t is no longer used for the variance) |
| f(·\|·) | `f(\cdot \mid \cdot)` | generic conditional density |
| 𝟙{·} | `\mathbbm{1}\{\cdot\}` (package `bbm`) | indicator function |

## Returns and innovations

| Symbol | LaTeX | Meaning |
|---|---|---|
| r_t | `r_t` | daily log return (percent) |
| μ | `\mu` | conditional mean |
| ε_t | `\varepsilon_t` | innovation, ε_t = r_t − μ |
| η_t | `\eta_t` | i.i.d. standardised innovation, mean 0, variance 1 |
| ν | `\nu` | Student-t degrees of freedom (t standardised to unit variance, ν > 2) |
| F_{t−1} | `\mathcal{F}_{t-1}` | information set of observed returns up to t−1 (replaces ψ, Ω, I, φ in the papers). Never includes regimes. |

## Single-regime models

| Symbol | LaTeX | Meaning |
|---|---|---|
| σ²_t | `\sigma_t^2` | conditional variance, σ²_t = Var(ε_t \| F_{t−1}) (replaces h_t in Engle, Bollerslev and others) |
| ω, α, β | `\omega, \alpha, \beta` | GARCH(1,1) intercept, ARCH and GARCH coefficients |
| a_m | `a_m` | lag-m coefficient of an ARCH(q) model, m = 1, …, q. α is reserved for the GARCH(1,1) ARCH coefficient, so α_1 can never mean "lag-1 ARCH coefficient" |
| α + β | `\alpha + \beta` | persistence |
| σ̄² | `\bar\sigma^2` | unconditional variance of the single-regime model, σ̄² = ω/(1 − α − β) |
| σ²_{t+h\|t} | `\sigma^2_{t+h\mid t}` | h-step-ahead variance forecast, E(ε²_{t+h} \| F_t); note σ²_{t+1\|t} = σ²_{t+1} |

## Regimes

| Symbol | LaTeX | Meaning |
|---|---|---|
| S_t | `S_t` | regime at time t, in {1, …, K}; K = 2 in the empirics |
| S_{1:t} | `S_{1:t}` | regime path (S_1, …, S_t) |
| K | `K` | number of regimes |
| i, j, k | `i, j, k` | regime indices |
| p_{ij} | `p_{ij}` | P(S_t = j \| S_{t−1} = i); rows of P sum to one |
| P | `P` | transition matrix (row-stochastic) |
| π_k | `\pi_k` | stationary probability of regime k |
| p_11 + p_22 − 1 | `p_{11} + p_{22} - 1` | Markov persistence (two regimes). **No symbol**; in particular do not use δ, which is the leverage coefficient |

## Regime-specific volatility

| Symbol | LaTeX | Meaning |
|---|---|---|
| σ²_{k,t} | `\sigma^2_{k,t}` | conditional variance in regime k (exact conditioning set is model-specific; state it when first used for each model) |
| **σ**²_t | `\boldsymbol{\sigma}^2_t` | vector (σ²_{1,t}, …, σ²_{K,t})′ of regime variances (IS-GARCH vector form) |
| ω_k, α_k, β_k | `\omega_k, \alpha_k, \beta_k` | regime-k GARCH parameters |
| δ | `\delta` | leverage coefficient (replaces ξ in Hamilton & Susmel) |

In regime-switching models σ²_t continues to mean Var(ε_t | F_{t−1}), i.e. the variance mixed over regimes. This is the object Gray (1996) collapses onto.

## SWARCH (Hamilton & Susmel, 1994)

| Symbol | LaTeX | Meaning |
|---|---|---|
| g_k | `g_k` | SWARCH **variance** scale factor, g_1 = 1: ε_t = √g_{S_t} · ε̃_t, so Var scales by g_k |
| ε̃_t | `\tilde\varepsilon_t` | latent unscaled ARCH process, ε̃_t = σ̃_t η_t |
| σ̃²_t | `\tilde\sigma^2_t` | conditional variance of ε̃_t, e.g. σ̃²_t = ω + Σ a_m ε̃²_{t−m} + δ 𝟙{ε̃_{t−1} ≤ 0} ε̃²_{t−1} |

## Filtering and estimation

| Symbol | LaTeX | Meaning |
|---|---|---|
| ξ_{k,t\|t−1} | `\xi_{k,t\mid t-1}` | predicted (ex ante) probability P(S_t = k \| F_{t−1}) |
| ξ_{k,t\|t} | `\xi_{k,t\mid t}` | filtered probability P(S_t = k \| F_t) |
| ξ_{k,t\|T} | `\xi_{k,t\mid T}` | smoothed probability P(S_t = k \| F_T) |
| θ | `\theta` | parameter vector |
| ℓ_T(θ) | `\ell_T(\theta)` | log-likelihood |

## Theory

| Symbol | LaTeX | Meaning |
|---|---|---|
| M | `M` | Haas et al. (2004) stationarity matrix (never Klaassen's transition matrix) |
| ρ(·) | `\rho(\cdot)` | spectral radius |
| γ | `\gamma` | top Lyapunov exponent |

## Translation table

| Paper | Their symbol | Ours |
|---|---|---|
| Engle (1982) | h_t; α_0; α_i, i = 1…p; p (order); ψ_{t−1} | σ²_t; ω; a_m; q; F_{t−1} |
| Bollerslev (1986) | h_t; α_0, α_i, β_i; ψ_{t−1}; δ_i (ARCH(∞) weights) | σ²_t; ω, α (or a_m), β; F_{t−1}; write weights explicitly (δ is taken) |
| Bollerslev (1987) | 1/ν | report as ν |
| Hamilton & Susmel (1994) | s_t; P (column-stochastic); u_t; ũ_t; h_t (a standard deviation: ũ_t = h_t v_t); v_t; a_0, a_i; ξ; d_{t−1}; λ (decay parameter) | S_t; P′ (transpose to ours); ε_t; ε̃_t; σ̃_t (h²_t → σ̃²_t); η_t; ω, a_m; δ; 𝟙{ε̃_{t−1} ≤ 0}; no symbol, write α + β (+ δ/2 with leverage) |
| Cai (1994) | S_t ∈ {0, 1}; p, q (staying probabilities); γ_0, γ_1 (switching intercept); α_i; Markov persistence parameter (symbol illegible in the scan) | S_t ∈ {1, 2}; p_11, p_22; ω_1, ω_2 as implied regime intercepts; a_m; p_11 + p_22 − 1 |
| Gray (1996) | S_t; φ_{t−1}; h_t; h_{it}; p_{1t} (ex ante probability) | S_t; F_{t−1}; σ²_t; σ²_{i,t}; ξ_{1,t\|t−1} |
| Klaassen (2002) | r_t (regime); r̃_t (regime path); I_{t−1}; V_{t−1}(e_t \| r̃_t); M (transition matrix, column-stochastic); h (horizon) | S_t; S_{1:t}; F_{t−1}; σ²_{k,t}; P′ (not our M); h |
| Haas, Mittnik & Paolella (2004) | Δ_t; a_0, a_1, b (vectors); σ^{(2)}_t; δ = p_11 + p_22 − 1 | S_t; (ω_k), (α_k), (β_k); **σ**²_t; write p_11 + p_22 − 1 (δ is leverage) |
| Francq & Zakoïan (2005); Francq, Roussignol & Zakoïan (2001) | Δ_t; h_t; ω(Δ_t), a_i(Δ_t), b_j(Δ_t) | S_t; σ²_t; ω_{S_t}, α_{S_t}, β_{S_t} (or a_m for ARCH lags) |
| Bauwens, Preminger & Rombouts (2010) | s_t; h_t | S_t; σ²_t |
| Haas & Liu (2015) | Δ_t; ξ_t (innovations); γ_C (Lyapunov exponent) | S_t; η_t; γ |
