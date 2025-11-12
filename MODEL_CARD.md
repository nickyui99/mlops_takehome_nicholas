# Iris Classifier Model Card

## Overview
A Logistic Regression model trained on the Iris dataset to classify flower species.

## Intended Use
For MLOps technical test purposes only. Not for production decision-making.

## Dataset
- Source: `sklearn.datasets.load_iris()`
- Samples: 150
- Features: sepal length, sepal width, petal length, petal width (all in cm)
- Classes: setosa, versicolor, virginica

## Metrics
- Accuracy: ~96-100% (depending on train/test split)
- Evaluated on 20% holdout set

## Limitations
- Trained on a toy dataset; not representative of real-world variability.
- No uncertainty quantification.
- Assumes inputs are valid measurements in cm.

## Risks
- Misclassification possible with out-of-distribution inputs.
- Not validated for safety-critical applications.

## Version
- `iris-v1`

## Model Tracking
- Trained with MLflow
- Run ID: `d0a1a6c1c3254b4f982de13de8ff6308` 
- Registered as: `iris-classifier` (v1 in MLflow Model Registry)
- Metrics logged: accuracy
- Params logged: test_size, random_state, max_iter