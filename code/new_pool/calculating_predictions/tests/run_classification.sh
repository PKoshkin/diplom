#/bin/bash

cd ..
python2 run.py --data_folder ../../../sorted_data/small_days_data --out_folder tests/res --model catboost --type classification --verbose --fast --max_clicks 5