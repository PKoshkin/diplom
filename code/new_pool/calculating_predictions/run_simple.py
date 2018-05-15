import argparse
from simple_regression import calculate_simple_regression_predictions
from simple_classification import calculate_simple_classification_predictions
import xgboost as xgb
from catboost import CatBoostRegressor, CatBoostClassifier


class ArgumentException(Exception):
    pass


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", type=str, required=True)
    parser.add_argument("--out_folder", type=str, required=True)
    parser.add_argument("--model", type=str, required=True, help="catboost of xgboost")
    parser.add_argument("--type", type=str, required=True, help="classification of regression")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.type == "regression":
        if args.model.lower() == "catboost":
            model_constructor = lambda: CatBoostRegressor(verbose=args.verbose)
        elif args.model.lower() in ["xgb", "xgboost"]:
            model_constructor = lambda: xgb.XGBRegressor(silent=not args.verbose)
        else:
            raise ArgumentException("Wrong model \"{}\".".format(args.model))
        calculate_simple_regression_predictions(model_constructor, args.data_folder, args.out_folder)
    elif args.type == "classification":
        if args.model.lower() == "catboost":
            model_constructor = lambda: CatBoostClassifier(verbose=args.verbose,
                                                           loss_function='MultiClass',
                                                           classes_count=15)
        elif args.model.lower() in ["xgb", "xgboost"]:
            model_constructor = lambda: xgb.XGBClassifier(silent=not args.verbose)
        else:
            raise ArgumentException("Wrong model \"{}\".".format(args.model))
        calculate_simple_classification_predictions(model_constructor, args.data_folder, args.out_folder)
    else:
        raise ArgumentException("Wrong model type \"{}\".".format(args.type))


if __name__ == "__main__":
    run()