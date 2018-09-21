# Preprocessing module for Cirrus

from enum import Enum
import sklearn.datasets
import time
import MinMaxScaler
import NormalScaler
from serialization import serialize_data

class NormalizationType(Enum):
    MIN_MAX = 1,
    NORMAL = 2

def normalize(s3_bucket_input, s3_bucket_output, normalization_type, *args):
    if normalization_type == NormalizationType.MIN_MAX:
        assert len(args) >= 2 and len(args) <= 4, "Must specify min and max."
        MinMaxScaler.MinMaxScaler(s3_bucket_input, s3_bucket_output, *args)
    elif normalization_type == NormalizationType.NORMAL:
        NormalScaler.NormalScaler(s3_bucket_input, s3_bucket_output, *args)

def load_libsvm(path, s3_bucket):
    """ Load a libsvm file into S3 in the specified bucket. """
    start = time.time()
    path = "../../tests/test_data/criteo.train.min.svm"
    print("[{0} s] Reading file...".format(time.time() - start))
    X, y = sklearn.datasets.load_svmlight_file(path)
    print("[{0} s] Finished reading file...".format(time.time() - start))
    batch = []
    batch_num = 1
    batch_size = 0
    for r in range(X.shape[0]):
        if r % 10000 == 0:
            print("[{0} s] On row {1}...".format(time.time() - start, r))
        rows, cols = X[r, :].nonzero()
        curr_row = []
        for c in cols:
            curr_row.append((c, X[r, c]))
        batch.append(curr_row)
        batch_size += 1
        if batch_size == 50000:
            print("[{0} s] Writing batch {1}...".format(time.time() - start, batch_num))
            s = serialize_data(batch)
            client.put_object(Bucket=event["s3_bucket"], Key=str(batch_num, Body=serialized))
            batch = []
            batch_num += 1
            batch_size = 0

    if batch_size > 0:
        print("[{0} s] Writing final batch {1}...".format(time.time() - start, batch_num))
        s = serialize_data(batch)
        client.put_object(Bucket=event["s3_bucket"], Key=str(batch_num, Body=serialized))

    print("[{0} s] Finished writing to S3.".format(time.time() - start))
