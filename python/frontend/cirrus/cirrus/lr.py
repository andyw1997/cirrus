# Logistic Regression

from core import BaseTask


class LogisticRegressionTask(BaseTask):
    def __init__(self, *args, **kwargs):
        # pass all arguments of init to parent class
        super(LogisticRegressionTask, self).__init__(*args, **kwargs)

    def __del__(self):
        print("Logistic Regression Task Lost")

    def define_config(self):
        
        if self.use_grad_threshold:
            grad_t = 1
        else:
            grad_t = 0

        config = "load_input_path: /mnt/efs/criteo_kaggle/train.csv \n" + \
                 "load_input_type: csv\n" + \
                 "dataset_format: binary\n" + \
                 "num_classes: 2 \n" + \
                 "num_features: 13 \n" + \
                 "limit_cols: 14 \n" + \
                 "normalize: 0 \n" + \
                 "limit_samples: 10000 \n" + \
                 "s3_size: 10 \n" + \
                 "use_bias: 1 \n" + \
                 "model_type: LogisticRegression \n" + \
                 "minibatch_size: %d \n" % self.minibatch_size + \
                 "learning_rate: %f \n" % self.learning_rate + \
                 "epsilon: %lf \n" % self.epsilon + \
                 "model_bits: %d \n" % self.model_bits + \
                 "s3_bucket: %s \n" % self.dataset + \
                 "use_grad_threshold: %d \n" % grad_t + \
                 "grad_threshold: %lf \n" % self.grad_threshold + \
                 "train_set: %d-%d \n" % self.train_set + \
                 "test_set: %d-%d" % self.test_set
        return config


def LogisticRegression(
            n_workers,
            n_ps,
            lambda_size,
            dataset,
            learning_rate, epsilon,
            progress_callback,
            train_set,
            test_set,
            minibatch_size,
            model_bits,
            resume_model=0,
            ps=None,
            opt_method="sgd",
            checkpoint_model=0,
            use_grad_threshold=False,
            grad_threshold=0.001,
            timeout=60,
            threshold_loss=0
            ):
    return LogisticRegressionTask(
            n_workers=n_workers,
            lambda_size=lambda_size,
            n_ps=n_ps,
            dataset=dataset,
            learning_rate=learning_rate,
            epsilon=epsilon,
            ps=ps,
            opt_method=opt_method,
            checkpoint_model=checkpoint_model,
            train_set=train_set,
            test_set=test_set,
            minibatch_size=minibatch_size,
            model_bits=model_bits,
            use_grad_threshold=use_grad_threshold,
            grad_threshold=grad_threshold,
            timeout=timeout,
            threshold_loss=threshold_loss,
            progress_callback=progress_callback
           )


