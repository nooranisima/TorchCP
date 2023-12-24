# Copyright (c) 2023-present, SUSTech-ML.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


import torch

from torchcp.classification.scores.aps import APS


class SAPS(APS):
    """
    Sorted Adaptive Prediction Sets (Huang et al., 2023)
    paper: https://arxiv.org/abs/2310.06430
    """

    def __init__(self, weight):
        """
        :param weight: the weigth of label ranking.
        """
        super(SAPS, self).__init__()
        if weight <= 0:
            raise ValueError("The parameter 'weight' must be a positive value.")
        self.__weight = weight

    def __call__(self, logits, y):
        assert len(logits.shape) <= 2, "The dimension of logits must be less than 2."
        if len(logits) == 1:
            logits = logits.unsqueeze(0)
        probs = torch.softmax(logits, dim=-1)
        # sorting probabilities
        indices, ordered, cumsum = self._sort_sum(probs)
        return self.__compute_score(indices, y, cumsum, ordered)

    def predict(self, logits):
        probs = torch.softmax(logits, dim=-1)
        I, ordered, _ = self._sort_sum(probs)
        if len(logits.shape) == 1:
            ordered[1:] = self.__weight
        else:
            ordered[...,1:] = self.__weight
        cumsum = torch.cumsum(ordered, dim=-1)
        U = torch.rand(probs.shape, device=logits.device)
        ordered_scores = cumsum - ordered * U
        _, sorted_indices = torch.sort(I, descending=False, dim=-1)
        scores = ordered_scores.gather(dim=-1, index=sorted_indices)
        return scores
    
    def __compute_score(self, indices, y, cumsum, ordered):
        
        U = torch.rand(indices.shape[0], device = indices.device)
        idx = torch.where(indices == y.view(-1, 1))
        scores_first_rank  = U * cumsum[idx] 
        scores_usual  = self.__weight * (idx[1] - U) + ordered[:,0]
        return torch.where(idx[1] == 0, scores_first_rank, scores_usual)

