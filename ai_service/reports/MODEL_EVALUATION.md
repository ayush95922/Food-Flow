# Model evaluation report

## 1. Food classifier (Food-101 / MobileNetV2)
**Not trained in the delivery environment - no metrics exist yet.** After the Colab run, paste accuracy, top-3 accuracy, macro/weighted F1,
per-class table (`per_class_metrics.csv`) and confusion matrix here. Expect lower accuracy on real donation photos than on the Food-101 test set.
The export/inference pipeline was exercised on random synthetic images (1 epoch, untrained weights): plumbing OK, metrics meaningless.

## 2. Usable-time regression - SYNTHETIC data (6000 rows, seed 42)
Split {'train': 4200, 'validation': 900, 'test': 900}. Selected by validation RMSE: **gradient_boosting**. Hours.
| model | val MAE | val RMSE | val R2 | test MAE | test RMSE | test R2 |
|---|---|---|---|---|---|---|
| linear_regression | 4.37 | 6.61 | 0.911 | 4.00 | 5.97 | 0.922 |
| random_forest | 2.18 | 4.41 | 0.960 | 1.83 | 3.64 | 0.971 |
| gradient_boosting | 2.51 | 4.40 | 0.961 | 2.17 | 3.74 | 0.970 |

90 % interval half-width: 7.34 h. Because labels come from the assumption generator, these scores are *not* evidence about real food. Not a safety certification.

## 3. Forecasting
No real history available -> no real forecast. Pipeline demonstrated on a synthetic series in `notebooks/forecasting.ipynb`.

## 4. Algorithm experiments
See `reports/research_results.md` and PNG plots (synthetic scenarios, 30 seeds).

## 5. Software tests
`pytest -q`: unit/integration tests of software behaviour. They do **not** measure model accuracy (the food-classifier tests use an untrained random-weight model).
