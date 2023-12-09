# Copyright (c) 2023-present, SUSTech-ML.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from deepcp.classification.scores.base import DaseScoreFunction


class THR(DaseScoreFunction):
    def __init__(self) -> None:
        pass

    def __call__(self, probs, y):
        return 1 - probs[y]

    def predict(self, probs):
        return 1 - probs
