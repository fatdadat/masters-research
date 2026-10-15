# Synthesis packet

Paste this into Claude after the master literature-review prompt. Everything below was extracted locally from the PDFs by a small model — it is a starting point for synthesis, not verified fact.

## Review questions

1. Why regimes at all â€” is GARCH's near-integrated persistence real or an artefact of neglected structural change in the unconditional variance?
2. How is the path-dependence problem solved â€” truncated memory, collapsing approximations, or independent switching â€” and what does each cost?
3. What is known theoretically â€” stationarity, ergodicity, moments, ACF of squares, QML consistency and asymptotic normality?
4. How do you test for the number of regimes, given the Davies problem and unidentified nuisance parameters under the null?
5. Does it pay off empirically â€” volatility forecasting, density forecasting, VaR and ES?
6. What happens in the multivariate case â€” regime-dependent correlations, dimensionality, estimation feasibility?

## Extracted papers

### Improving GARCH volatility forecasts with regime-switching GARCH (2002)
*Franc Klaassen* — Empirical Economics — doi:10.1007/s001810100100
- (not extracted) abstract: Many researchers use GARCH models to generate volatility forecasts. Using data on three major U.S. dollar exchange rates we show that such forecasts are too high in volatile periods. We argue that this is due to the high persistence of shocks in GARCH forecasts. To obtain more flexibility regarding volatility persistence, this paper generalizes the GARCH model by distinguishing two regimes [...]

### Theory and Inference for a Markov Switching GARCH Model (2007)
*Luc Bauwens, Arie Preminger, Jeroen V.K. Rombouts* — SSRN Electronic Journal — doi:10.2139/ssrn.1011623
- (not extracted) abstract: We develop a Markov-switching GARCH model (MS-GARCH) wherein the conditional mean and variance switch in time from one GARCH process to another. The switching is governed by a hidden Markov chain. We provide sufficient conditions for geometric ergodicity and existence of moments of the process. Because of path dependence, maximum likelihood estimation is not feasible. By enlarging the [...]

### A New Approach to Markov-Switching GARCH Models (2004)
*Markus Haas* — Journal of Financial Econometrics — doi:10.1093/jjfinec/nbh020
- (not extracted) abstract: The use of Markov-switching models to capture the volatility dynamics of financial time series has grown considerably during past years, in part because they give rise to a plausible interpretation of nonlinearities. Nevertheless, GARCH-type models remain ubiquitous in order to allow for nonlinearities associated with time-varying volatility. Existing methods of combining the two approaches [...]

### A multivariate regime-switching GARCH model with an application to global stock market and real estate equity returns (2018)
*Markus Haas, Ji‐Chun Liu* — Studies in Nonlinear Dynamics and Econometrics — doi:10.1515/snde-2016-0019
- (not extracted) abstract: Abstract We consider a multivariate Markov-switching GARCH model which allows for regime-specific volatility dynamics, leverage effects, and correlation structures. Conditions for stationarity and expressions for the moments of the process are derived. A Lagrange Multiplier test against misspecification of the within-regime correlation dynamics is proposed, and a simple recursion for multi- [...]

### Modeling the conditional distribution of interest rates as a regime-switching process (1996)
*Stephen Gray* — Journal of Financial Economics — doi:10.1016/0304-405x(96)00875-6
- (not extracted) abstract: 

### A Markov Model of Switching-Regime ARCH (1994)
*Jun Cai* — Journal of Business and Economic Statistics — doi:10.1080/07350015.1994.10524546
- (not extracted) abstract: In this article I present a new approach to model more realistically the variability of financial time series. I develop a Markov-ARCH model that incorporates the features of both Hamilton's switching-regime model and Engle's autoregressive conditional heteroscedasticity (ARCH) model to examine the issue of volatility persistence in the monthly excess returns of the three-month treasury [...]

### Autoregressive conditional heteroskedasticity and changes in regime (1994)
*James D. Hamilton, Raúl Susmel* — Journal of Econometrics — doi:10.1016/0304-4076(94)90067-1
- (not extracted) abstract: 

### MCMC-based estimation of Markov Switching ARMA–GARCH models (2009)
*Jan S. Henneke, Svetlozar T. Rachev, Frank J. Fabozzi, Metodi Nikolov* — Applied Economics — doi:10.1080/00036840802552379
- (not extracted) abstract: Regime switching models, especially Markov Switching (MS) models, are regarded as a promising way to capture nonlinearities in time series. Combining the elements of MS models with full Autoregressive Moving Average–Generalized Autoregressive Conditional Heteroskedasticity (ARMA–GARCH) models poses severe difficulties for the computation of parameter estimators. Existing methods can become [...]

### ON THE STATIONARITY OF MARKOV-SWITCHING GARCH PROCESSES (2007)
*Ari Abramson, Israel Cohen* — Econometric Theory — doi:10.1017/s0266466607070211
- (not extracted) abstract: Generalized autoregressive conditional heteroskedasticity (GARCH) models with Markov-switching regimes are often used for volatility analysis of financial time series. Such models imply less persistence in the conditional variance than the standard GARCH model and potentially provide a significant improvement in volatility forecast. Nevertheless, conditions for asymptotic wide-sense [...]

### Forecasting Stock Market Volatility with Regime-Switching GARCH Models (2005)
*Juri Marcucci* — Studies in Nonlinear Dynamics and Econometrics — doi:10.2202/1558-3708.1145
- (not extracted) abstract: In this paper we compare a set of different standard GARCH models with a group of Markov Regime-Switching GARCH (MRS-GARCH) in terms of their ability to forecast the US stock market volatility at horizons that range from one day to one month. To take into account the excessive persistence usually found in GARCH models that implies too smooth and too high volatility forecasts, in the MRS- [...]

### Forecasting risk with Markov-switching GARCH models:A large-scale performance study (2018)
*David Ardia, Keven Bluteau, Kris Boudt, Leopoldo Catania* — International Journal of Forecasting — doi:10.1016/j.ijforecast.2018.05.004
- (not extracted) abstract: We perform a large-scale empirical study in order to compare the forecasting performances of single-regime and Markov-switching GARCH (MSGARCH) models from a risk management perspective. We find that MSGARCH models yield more accurate Value-at-Risk, expected shortfall, and left-tail distribution forecasts than their single-regime counterparts for daily, weekly, and ten-day equity log- [...]

### Markov Switching Garch Models: Higher Order Moments, Kurtosis Measures, and Volatility Evaluation in Recessions and Pandemic (2021)
*Maddalena Cavicchioli* — Journal of Business and Economic Statistics — doi:10.1080/07350015.2021.1974459
- (not extracted) abstract: In this article, we derive neat matrix formulas in closed form for computing higher order moments and kurtosis of univariate Markov switching GARCH models. Then we provide asymptotic theory for sample estimators of higher order moments and kurtosis which can be used for testing normality. We also check our theory statements numerically via Monte Carlo simulations. Finally, we take advantage [...]

### Stationarity of a Markov-Switching GARCH Model (2006)
*Jiacheng Liu* — Journal of Financial Econometrics — doi:10.1093/jjfinec/nbl004
- (not extracted) abstract: This article investigates some structural properties of the Markov-switching GARCH process introduced by Haas, Mittnik, and Paolella. First, a sufficient and necessary condition for the existence of the weakly stationary solution of the process is presented. The solution is weakly stationary, and the causal expansion of the Markov-switching GARCH process is also established. Second, the [...]

### Maximum Likelihood Estimation and Forecasting for GARCH, Markov Switching, and Locally Stationary Wavelet Processes (2007)
*Yingfu Xie* — Epsilon Open Archive (Sveriges lantbruksuniversitet biblioteket (Swedish University of Agricultural Sciences))
- (not extracted) abstract: Financial time series are frequently met both in daily life and the scientific world. It is clearly of importance to study the financial time series, to understand the mechanism giving rise to the data, and/or predict the future values of a series. This thesis is dedicated to statistical inferences of a number of models for financial time series. Financial time series often exhibit time- [...]

### Stationarity and Persistence in the GARCH(1,1) Model (1990)
*Daniel B. Nelson* — Econometric Theory — doi:10.1017/s0266466600005296
- (not extracted) abstract: This paper establishes necessary and sufficient conditions for the stationarity and ergodicity of the GARCH(l.l) process. As a special case, it is shown that the IGARCH(1,1) process with no drift converges almost surely to zero, while IGARCH(1,1) with a positive drift is strictly stationary and ergodic. We examine the persistence of shocks to conditional variance in the GARCH(l.l) model, and [...]
