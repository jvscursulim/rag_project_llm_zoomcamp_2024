def calculate_hit_rate(relevance_total: list) -> float:
    """Calculates the hit rate retrieval metric

    Args:
        relevance_total (list): A list of boolean
        that tells the relevance of the search result.

    Returns:
        float: The hit rate value.
    """

    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)


def calculate_mrr(relevance_total: list) -> float:
    """Calculates the mrr retrieval metric.

    Args:
        relevance_total (list): A list of boolean
        that tells the relevance of the search result.

    Returns:
        float: The mrr value.
    """

    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)
