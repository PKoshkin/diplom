#include <iostream>
#include <ctime>

#include "metric.h"
#include "model.h"
#include "counterfactural_model.h"
#include "active_learning_algo.h"
#include "al_utils.h"


int main() {
    std::srand(std::time(0));
    char pool_path[100] = "../../pool.json";
    Pool pool = get_pool(pool_path, 90000);
    auto pool_pair = train_test_split(pool, 0.75);
    Pool train_pool = pool_pair.first;
    Pool test_pool = pool_pair.second;
    PoolBasedUncertaintySamplingStrategy<LogisticRegression> strategy;
    test_pool_based_strategy<LogisticRegression>(&strategy, train_pool, test_pool, "al_test_results.txt");

    return 0;
}
