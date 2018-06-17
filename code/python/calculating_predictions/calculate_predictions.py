from __future__ import print_function
import os
import sys
import numpy as np
from catboost import Pool

sys.path.append("../utils")
from constants import POSITIONS_VARIANTS, DAYS_NUMBER
from json_tools import get_linear_stacked_features, get_labels
from pool_iterator import pool_iterator
from log import log


def calculate_predictions(args):
    """
    args contain:
        data_folder: str. Directory, containing files "day_i.json" where i in range(DAYS_NUMBER).
        out_folder: str. Directory, to save results. 1 file will be created.
        type: str. One of ["regression", "classification", "binary_classification", "binary_regression"]
        model_constructor: callable. Takes verbose param. If type == "classification" also takes max_clicks param.
        additional_features: list of additional features for train and test day or None.
        train_days: list of ints. Numbers of day to train on.
        test_day: int. Number of dat to test on.
        validation_day: int or None. Number of day to validate on.
    """
    log("preprocesing started")

    if args.type == "classification":
        model = args.model_constructor(args.verbose, args.max_clicks)
    else:
        model = args.model_constructor(args.verbose)

    json_filenames = [os.path.join(args.data_folder, "day_{}.json".format(day)) for day in range(DAYS_NUMBER)]

    need_position_feature = not args.type.startswith("binary")
    if args.additional_features is not None:
        features = np.array([
            get_linear_stacked_features(
                pool_iterator(json_filename),
                linear_prediction,
                args.first_feature,
                args.last_feature,
                need_position_feature
            ) for linear_prediction, json_filename in zip(args.additional_features, json_filenames)
        ])
    else:
        features = np.array([
            get_linear_stacked_features(
                pool_iterator(json_filename),
                first_feature=args.first_feature,
                last_feature=args.last_feature,
                add_positions=need_position_feature
            ) for json_filename in json_filenames
        ])

    labels = np.array([get_labels(pool_iterator(json_filename), args) for json_filename in json_filenames])

    train_features = np.concatenate(features[args.train_days], axis=0)
    train_labels = np.concatenate(labels[args.train_days], axis=0)

    log("train features shape: {}".format(np.shape(train_features)))

    test_features = features[args.test_day]

    if args.validation_day is not None:
        validation_features = features[args.validation_day]
        validation_labels = labels[args.validation_day]
        validation_pool = Pool(validation_features, validation_labels)

    log("preprocesing finished")
    log("start training on days {}".format(args.train_days))

    if args.validation_day is not None:
        log("using fit with validation")
        model.set_params(iterations=2000)
        model.fit(
            train_features,
            train_labels,
            eval_set=validation_pool,
            use_best_model=True
        )
    else:
        log("using fit without validation")
        model.fit(train_features, train_labels)

    log("built {} trees".format(model.tree_count_))

    log("start predicting on day {}".format(args.test_day))
    if args.type == "binary_classification":
        predictions = model.predict_proba(test_features)
    elif args.type == "binary_regression":
        predictions = model.predict(test_features)
    else:
        reshaped_positions = np.reshape(np.array(POSITIONS_VARIANTS), [-1, 1])
        predictions = []
        for feature in test_features:
            repeated_feature = np.repeat(np.array([feature[1:]]), len(POSITIONS_VARIANTS), axis=0)
            features_to_predict = np.concatenate([reshaped_positions, repeated_feature], axis=1)
            if args.type == "regression":
                current_predictions = model.predict(features_to_predict)
            else:
                current_predictions = model.predict_proba(features_to_predict)
            predictions.append(current_predictions)

    log("saveing results")
    np.save(
        os.path.join(args.out_folder, "train_{}_test_{}".format("_".join(map(str, args.train_days)), args.test_day)),
        np.array(predictions)
    )
    log("results saved")
