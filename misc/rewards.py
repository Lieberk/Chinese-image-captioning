import numpy as np
from collections import OrderedDict
from evaluation.bleu.bleu import Bleu
from evaluation.cider.cider import Cider

cider_reward_weight = 1.0
bleu_reward_weight = 0.0


def array_to_str(arr):
    out = ''
    for i in range(len(arr)):
        out += str(arr[i]) + ' '
        if arr[i] == 0:
            break
    return out.strip()


def get_self_critical_reward(greedy_res, data_gts, sample_res):
    batch_size = len(data_gts)
    sample_res = sample_res.numpy()
    greedy_res = greedy_res.numpy()
    scores_greedy = get_scores(greedy_res, data_gts)
    scores_sample = get_scores(sample_res, data_gts)

    s_sample = scores_sample.reshape([batch_size, -1])
    b_greedy = scores_greedy.reshape([batch_size, -1])
    scores = s_sample - b_greedy

    scores = scores.reshape(-1)
    rewards = np.repeat(scores[:, np.newaxis], sample_res.shape[1], 1)
    return rewards


def get_scores(candidates, references):
    batch_size = len(references)
    candidates_size = candidates.shape[0]
    seq_per_img = candidates_size // batch_size  # gen_result_size  = batch_size * seq_per_img

    candidates_dict = OrderedDict()
    references_dict = OrderedDict()
    for i in range(candidates_size):
        candidates_dict[i] = [array_to_str(candidates[i])]

    for i in range(candidates_size):
        references_dict[i] = \
            [array_to_str(references[i // seq_per_img][j]) for j in range(len(references[i // seq_per_img]))]

    if cider_reward_weight > 0:
        _, cider_scores = Cider().compute_score(references_dict, candidates_dict)
    else:
        cider_scores = 0
    if bleu_reward_weight > 0:
        _, bleu_scores = Bleu().compute_score(references_dict, candidates_dict)
        bleu_scores = np.array(bleu_scores[0])
    else:
        bleu_scores = 0

    scores = cider_reward_weight * cider_scores + bleu_reward_weight * bleu_scores
    return scores
