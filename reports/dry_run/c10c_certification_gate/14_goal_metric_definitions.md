# GOAL-ENVIRONMENT METRIC DEFINITIONS & SPECIFICATIONS

## 1. Goals MAE (Mean Absolute Error)
\[
	ext{Goals MAE} = rac{1}{2N} \sum_{i=1}^N \left( |\hat{\lambda}_{H,i} - y_{H,i}| + |\hat{\lambda}_{A,i} - y_{A,i}| ight)
\]
Measures the average error in team-level expected goal predictions across all fixtures.

## 2. Clean Sheet Brier Score
\[
	ext{CS Brier} = rac{1}{2N} \sum_{i=1}^N \left( (\hat{P}(	ext{CS}_{H,i}) - \mathbb{I}(y_{A,i} = 0))^2 + (\hat{P}(	ext{CS}_{A,i}) - \mathbb{I}(y_{H,i} = 0))^2 ight)
\]
Measures probability calibration of clean-sheet forecasts for both home and away defences.

## 3. Both Teams To Score (BTTS) Brier Score
\[
	ext{BTTS Brier} = rac{1}{N} \sum_{i=1}^N \left( \hat{P}(	ext{BTTS}_i) - \mathbb{I}(y_{H,i} > 0 \land y_{A,i} > 0) ight)^2
\]
Measures match-level scoring environment forecast calibration.
