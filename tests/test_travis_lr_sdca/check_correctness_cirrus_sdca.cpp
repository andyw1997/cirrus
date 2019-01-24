#include <unistd.h>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include <Configuration.h>
#include <InputReader.h>
#include <SparseLRSDCAModel.h>
#include "SDCA.h"

using namespace cirrus;

void print_info(const auto& samples) {
  std::cout << "Number of samples: " << samples.size() << std::endl;
  std::cout << "Number of cols: " << samples[0].size() << std::endl;
}

double check_error(SparseLRSDCAModel* model, SparseDataset& dataset) {
  auto ret = model->calc_loss(dataset, 0);
  auto loss = ret.first;
  auto avg_loss = loss / dataset.num_samples();
  std::cout << "total loss: " << loss << " avg loss: " << avg_loss << std::endl;
  return avg_loss;
}

cirrus::Configuration config =
    cirrus::Configuration("configs/criteo_kaggle_sdca.cfg");
std::mutex model_lock;
std::unique_ptr<SparseLRSDCAModel> model;
double learning_rate = 0.00001;
std::unique_ptr<SDCA> opt_method = std::make_unique<SDCA>(learning_rate);

void learning_function(const SparseDataset& dataset) {
  for (uint64_t i = 0; 20; ++i) {
    int index = (rand() % (dataset.num_samples() / 20)) * 20;
    SparseDataset ds = dataset.sample_from(index, config.get_minibatch_size());

    auto gradient =
        model->minibatch_grad_indexed(index, learning_rate, ds, config);

    model_lock.lock();
    opt_method->sdca_update(model, gradient.release());
    model_lock.unlock();
  }
}

int main() {
  InputReader input;
  SparseDataset dataset = input.read_input_criteo_kaggle_sparse(
      "tests/test_data/train_lr.csv", ",", config);  // normalize=true
  SparseDataset test_dataset = input.read_input_criteo_kaggle_sparse(
      "tests/test_data/test_lr.csv", ",", config);
  dataset.check();
  test_dataset.check();
  dataset.print_info();

  model.reset(new SparseLRSDCAModel((1 << config.get_model_bits()) + 1,
                                    config.get_limit_samples()));

  uint64_t num_threads = 20;
  std::vector<std::shared_ptr<std::thread>> threads;
  for (uint64_t i = 0; i < num_threads; ++i) {
    threads.push_back(
        std::make_shared<std::thread>(learning_function, dataset));
  }
  int iterations = 0;
  bool success = false;
  while (1) {
    usleep(100000);  // 100ms
    if (iterations == 300) {
      break;
    }
    model_lock.lock();
    auto avg_loss = check_error(model.get(), test_dataset);
    model_lock.unlock();
    if (avg_loss <= 0.54) {
      success = true;
      break;
    }
  }
  for (uint64_t i = 0; i < num_threads; ++i) {
    (*threads[i]).detach();
  }
  if (success) {
    return 0;
  }
  throw std::runtime_error("Logistic Regression SDCA test failed.");
}