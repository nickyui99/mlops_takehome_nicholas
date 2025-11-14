# Titanic Survival Predictor Model Card

## Overview
A Logistic Regression model trained on the Titanic dataset to predict passenger survival.

## Intended Use
For MLOps technical test purposes only. Not for production decision-making.

## Dataset
- Source: `seaborn.load_dataset('titanic')`
- Samples: 891 passengers
- Features:
  - `pclass`: Passenger class (1, 2, or 3)
  - `sex`: Gender (male/female)
  - `age`: Age in years
  - `sibsp`: Number of siblings/spouses aboard
  - `parch`: Number of parents/children aboard
  - `fare`: Passenger fare
  - `embarked`: Port of embarkation (C=Cherbourg, Q=Queenstown, S=Southampton)
- Target: `survived` (0=died, 1=survived)
- Preprocessing: 
  - Categorical encoding (sex, embarked)
  - Median imputation for missing values
  - Standard scaling

## Metrics
- Accuracy: ~78-82% (depending on train/test split)
- Precision: ~75-85%
- Recall: ~70-80%
- F1 Score: ~75-80%
- Evaluated on 20% holdout set with stratification

## Limitations
- Historical dataset; not representative of modern maritime safety standards.
- Missing data imputed with median values, which may introduce bias.
- No uncertainty quantification.
- Binary classification only (survived/died).

## Risks
- Misclassification possible with out-of-distribution inputs.
- Not validated for safety-critical applications.
- Historical biases present in original dataset (gender, class-based survival rates).

## Version
- `titanic-v1`

## Model Tracking
- Trained with MLflow
- Registered as: `titanic-classifier` (v1 in MLflow Model Registry)
- Metrics logged: accuracy, precision, recall, f1_score
- Params logged: test_size, random_state, max_iter, class_weight