"""
@author: Shwet Prakash
@Purpose - Re-usable code in Python 3 for cross-validation and regression task in modeling process
"""

## Importing required libraries
import pandas as pd ## For DataFrame operation
import numpy as np ## Numerical python for matrix operations
from sklearn.model_selection import KFold, train_test_split ## Creating cross validation sets
from sklearn import metrics ## For loss functions
import matplotlib.pyplot as plt

## Libraries for Regressiion algorithms
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
import xgboost as xgb
import lightgbm as lgb 
from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor

########### Cross Validation ###########
### 1) Train test split
def holdout_cv(X,y,size = 0.3, seed = 1):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = size, random_state = seed)
    return X_train, X_test, y_train, y_test

### 2) Cross-Validation (K-Fold)
def kfold_cv(X,n_folds = 5, seed = 1):
    cv = KFold(n_splits = n_folds, random_state = seed, shuffle = True)
    return cv.split(X)

########### Model Explanation ###########
## Variable Importance plot
def feature_importance(model,X):
    feature_importance = model.feature_importances_
    feature_importance = 100.0 * (feature_importance / feature_importance.max())
    sorted_idx = np.argsort(feature_importance)
    pos = np.arange(sorted_idx.shape[0]) + .5
    plt.figure(figsize=(15, 15))
    plt.subplot(1, 2, 2)
    plt.barh(pos, feature_importance[sorted_idx], align='center')
    plt.yticks(pos, X.columns[sorted_idx])
    plt.xlabel('Relative Importance')
    plt.title('Variable Importance')
    plt.show()
    
########### Algorithms For Regression ###########

### Running Xgboost
def runXGB(train_X, train_y, test_X, test_y=None, test_X2=None, seed_val=0, rounds=500, dep=8, eta=0.05):
    params = {}
    params["objective"] = "reg:linear"
    params['eval_metric'] = 'rmse'
    params["eta"] = eta
    params["subsample"] = 0.7
    params["min_child_weight"] = 1
    params["colsample_bytree"] = 0.7
    params["max_depth"] = dep
    params["silent"] = 1
    params["seed"] = seed_val
    #params["max_delta_step"] = 2
    #params["gamma"] = 0.5
    num_rounds = rounds

    plst = list(params.items())
    xgtrain = xgb.DMatrix(train_X, label=train_y)

    if test_y is not None:
        xgtest = xgb.DMatrix(test_X, label=test_y)
        watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]
        model = xgb.train(plst, xgtrain, num_rounds, watchlist, early_stopping_rounds=100, verbose_eval=20)
    else:
        xgtest = xgb.DMatrix(test_X)
        model = xgb.train(plst, xgtrain, num_rounds)
    
    pred_test_y = model.predict(xgtest, ntree_limit=model.best_ntree_limit)
    
    pred_test_y2 = 0
    if test_X2 is not None:
        pred_test_y2 = model.predict(xgb.DMatrix(test_X2), ntree_limit=model.best_ntree_limit)
    
    loss = 0
    if test_y is not None:
        loss = metrics.mean_squared_error(test_y, pred_test_y)
        return pred_test_y, loss, pred_test_y2, model
    else:
        return pred_test_y, loss, pred_test_y2, model
        
### Running LightGBM
def runLGB(train_X, train_y, test_X, test_y=None, test_X2=None, feature_names=None, seed_val=0, rounds=500, dep=8, eta=0.05):
    params = {}
    params["objective"] = "regression"
    params['metric'] = 'rmse'
    params["max_depth"] = dep
    params["min_data_in_leaf"] = 20
    params["learning_rate"] = eta
    params["bagging_fraction"] = 0.7
    params["feature_fraction"] = 0.7
    params["bagging_freq"] = 5
    params["bagging_seed"] = seed_val
    params["verbosity"] = 0
    num_rounds = rounds
    
    lgtrain = lgb.Dataset(train_X, label=train_y)
    
    if test_y is not None:
        lgtest = lgb.Dataset(test_X, label=test_y)
        model = lgb.train(params, lgtrain, num_rounds, valid_sets=[lgtest], early_stopping_rounds=100, verbose_eval=20)
    else:
        lgtest = lgb.DMatrix(test_X)
        model = lgb.train(params, lgtrain, num_rounds)
        
    pred_test_y = model.predict(test_X, num_iteration=model.best_iteration)
    
    pred_test_y2 = 0
    if test_X2 is not None:
        pred_test_y2 = model.predict(test_X2, num_iteration=model.best_iteration)
    
    loss = 0
    if test_y is not None:
        loss = metrics.mean_squared_error(test_y, pred_test_y)
        print(loss)
        return pred_test_y, loss, pred_test_y2, model
    else:
        return pred_test_y, loss, pred_test_y2, model
        
### Running Extra Trees  
def runET(train_X, train_y, test_X, test_y=None, test_X2=None, depth=20, leaf=10, feat=0.2):
	model = ExtraTreesRegressor(
			n_estimators = 100,
					max_depth = depth,
					min_samples_split = 2,
					min_samples_leaf = leaf,
					max_features =  feat,
					n_jobs = 8,
					random_state = 0)
	model.fit(train_X, train_y)
	train_preds = model.predict(train_X)
	test_preds = model.predict(test_X)
	
	test_preds2 = 0
	if test_X2 is not None:
		test_preds2 = model.predict(test_X2)
	
	test_loss = 0
	if test_y is not None:
		train_loss = metrics.mean_squared_error(train_y, train_preds)
		test_loss = metrics.mean_squared_error(test_y, test_preds)
		print("Depth, leaf, feat : ", depth, leaf, feat)
		print("Train and Test loss : ", train_loss, test_loss)
	return test_preds, test_loss, test_preds2, model
 
### Running Random Forest
def runRF(train_X, train_y, test_X, test_y=None, test_X2=None, depth=20, leaf=10, feat=0.2):
    model = RandomForestRegressor(
            n_estimators = 1000,
                    max_depth = depth,
                    min_samples_split = 2,
                    min_samples_leaf = leaf,
                    max_features =  feat,
                    n_jobs = 4,
                    random_state = 0)
    model.fit(train_X, train_y)
    train_preds = model.predict(train_X)
    test_preds = model.predict(test_X)
    
    test_preds2 = 0
    if test_X2 is not None:
        test_preds2 = model.predict(test_X2)
    
    test_loss = 0
    
    train_loss = metrics.mean_squared_error(train_y, train_preds)
    test_loss = metrics.mean_squared_error(test_y, test_preds)
    print("Train and Test loss : ", train_loss, test_loss)
    return test_preds, test_loss, test_preds2, model

### Running Linear regression
def runLR(train_X, train_y, test_X, test_y=None, test_X2=None):
    model = LinearRegression()
    model.fit(train_X, train_y)
    train_preds = model.predict(train_X)
    test_preds = model.predict(test_X)

    test_preds2 = 0
    if test_X2 is not None:
        test_preds2 = model.predict(test_X2)
    test_loss = 0
    
    train_loss = metrics.mean_squared_error(train_y, train_preds)
    test_loss = metrics.mean_squared_error(test_y, test_preds)
    print("Train and Test loss : ", train_loss, test_loss)
    return test_preds, test_loss, test_preds2, model

### Running Decision Tree
def runDT(train_X, train_y, test_X, test_y=None, test_X2=None, criterion='mse', depth=None, min_split=2, min_leaf=1):
    model = DecisionTreeRegressor(criterion = criterion, max_depth = depth, min_samples_split = min_split, min_samples_leaf=min_leaf)
    model.fit(train_X, train_y)
    train_preds = model.predict(train_X)
    test_preds = model.predict(test_X)

    test_preds2 = 0
    if test_X2 is not None:
        test_preds2 = model.predict(test_X2)
    
    test_loss = 0
    
    train_loss = metrics.mean_squared_error(train_y, train_preds)
    test_loss = metrics.mean_squared_error(test_y, test_preds)
    print("Train and Test loss : ", train_loss, test_loss)
    return test_preds, test_loss, test_preds2, model
    
### Running K-Nearest Neighbour
def runKNN(train_X, train_y, test_X, test_y=None, test_X2=None, neighbors=5):
    model = KNeighborsRegressor(n_neighbors=neighbors, n_jobs=-1)
    model.fit(train_X, train_y)
    train_preds = model.predict(train_X)
    test_preds = model.predict(test_X)

    test_preds2 = 0
    if test_X2 is not None:
        test_preds2 = model.predict(test_X2)
    
    test_loss = 0
    
    train_loss = metrics.mean_squared_error(train_y, train_preds)
    test_loss = metrics.mean_squared_error(test_y, test_preds)
    print("Train and Test loss : ", train_loss, test_loss)
    return test_preds, test_loss, test_preds2, model

### Running SVM
def runSVC(train_X, train_y, test_X, test_y=None, test_X2=None, C=1.0, eps=0.1, kernel_choice = 'rbf'):
    model = SVR(C=C, kernel=kernel_choice,  epsilon=eps)
    model.fit(train_X, train_y)
    train_preds = model.predict(train_X)
    test_preds = model.predict(test_X)

    test_preds2 = 0
    if test_X2 is not None:
        test_preds2 = model.predict(test_X2)
    
    test_loss = 0
    
    train_loss = metrics.mean_squared_error(train_y, train_preds)
    test_loss = metrics.mean_squared_error(test_y, test_preds)
    print("Train and Test loss : ", train_loss, test_loss)
    return test_preds, test_loss, test_preds2, model
