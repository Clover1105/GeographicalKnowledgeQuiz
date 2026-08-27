def rrf(v_result, bm_result):
    scores = {}
    docs = {}
    for index,score in enumerate(v_result,start=0):
        scores[score.id] = scores.get(score.id,0) + round(1/(60+index),4)
        docs[score.id] = score
    for index,doc in enumerate(bm_result,start=1):
        scores[doc.id] = scores.get(doc.id,0)+round(1/(60+index),4)
        docs[doc.id] = doc
    # 分数排序
    sorted_scores = sorted(scores.items(),key=lambda x:x[1],reverse=True)
    # 返回排序后结果
    result = [docs[id] for id,score in sorted_scores]
    return result