#include <algorithm>
#include <cmath>
#include <iostream>

#include "model.h"


std::vector<int> get_permutation(int size) {
    std::vector<int> result(size);
    for (int i = 0; i < size; ++i)
    result[i] = i;
    std::random_shuffle(result.begin(), result.end());
    return result;
}


std::vector<double> LinearRegression::predict(const Matrix& features) {
    std::vector<double> result(features.size(), 0);

    for (int i = 0; i < features.size(); ++i)
    for (int j = 0; j < features[i].size(); ++j)
        result[i] += weights[j] * features[i][j];

    return result;
}


void LinearRegression::fit(const Matrix& features, const std::vector<double>& scores) {
    weights.resize(features[0].size(), 0);

    for (int iter = 0; iter < iterations_number; ++iter) {
    std::vector<int> random_permutation = get_permutation(features.size());

    for (int batch_start = 0; batch_start < features.size(); batch_start += batch_size) {
        std::vector<double> gradient(weights.size(), 0);
        for (int index = batch_start; index < std::min(batch_start + batch_size, int(features.size())); ++index) {
        int pool_ind = random_permutation[index];
        std::vector<double> curr_grad = get_gradient(features[pool_ind], scores[pool_ind]);
        for (int feature_index = 0; feature_index < gradient.size(); ++feature_index)
            gradient[feature_index] += curr_grad[feature_index];
        }

        for (int feature_index = 0; feature_index < gradient.size(); ++feature_index)
        weights[feature_index] -= lr * gradient[feature_index];
    }
    std::cout << weights[255] << " " << weights[1052] << " " << weights[1053] << " " << weights[1054] << " " << weights[1058] << std::endl;
    std::cout << "loss: " << loss(features, scores) << std::endl;
    }
}


LinearRegression::LinearRegression(double lr, double reg_lambda, int batch_size, int iterations_number)
    : lr(lr), reg_lambda(reg_lambda), batch_size(batch_size), iterations_number(iterations_number) {}


std::vector<double> LinearRegression::get_gradient(const std::vector<double>& features, double score) {
    double prediction = 0;
    for (int i = 0; i < features.size(); ++i)
        prediction += features[i] * weights[i];
    std::vector<double> result = features;
    for (int i = 0; i < features.size(); ++i)
        result[i] *= 2 * (score - prediction);
    return result;
}


double LinearRegression::loss(const Matrix& features, std::vector<double> scores) {
    double loss = 0;

    for (int i = 0; i < features.size(); ++i) {
        double prediction = 0;
        for (int k = 0; k < features[i].size(); ++k)
            prediction += features[i][k] * weights[k];
        loss += (score[i] - prediction) * (scores[i] - prediction);
    }

    return loss / features.size();
}
