#/bin/bash

cd ..
python2 run.py --data_folder ../../../sorted_data/small_days_data --out_folder tests/res --model catboost --type binary_classification --verbose --fast --threshold 1