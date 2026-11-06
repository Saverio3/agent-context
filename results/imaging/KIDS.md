# Children's chest X-rays with little data (pneumonia vs normal)

Train pool 5,232 child X-rays, test 624 (official split). Test AUC, mean of 20 random draws (range in brackets). 0.5 = coin flip, 1.0 = perfect.

Adult model, zero child images (its own 'Pneumonia' output): **0.583**

| Child X-rays used per class | Generic image model (ImageNet) | Adult chest X-ray model | Gain |
|---|---|---|---|
| 5 | 0.835 (0.78–0.91) | 0.920 (0.89–0.95) | +0.085 |
| 10 | 0.844 (0.71–0.88) | 0.916 (0.88–0.94) | +0.072 |
| 25 | 0.883 (0.84–0.92) | 0.931 (0.90–0.96) | +0.048 |
| 50 | 0.899 (0.82–0.92) | 0.941 (0.91–0.96) | +0.041 |
| 100 | 0.917 (0.88–0.94) | 0.950 (0.94–0.97) | +0.033 |
| 250 | 0.935 (0.92–0.94) | 0.956 (0.94–0.96) | +0.021 |
| all (5232) | 0.953 | 0.964 | +0.011 |
