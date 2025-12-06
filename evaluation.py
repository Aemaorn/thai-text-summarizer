from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def evaluate_summary(reference, candidate):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    rouge_scores = scorer.score(reference, candidate)

    reference_tokens = [reference.split()]
    candidate_tokens = candidate.split()
    smoothie = SmoothingFunction().method4
    bleu = sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=smoothie)

    results = {
        'ROUGE-1': round(rouge_scores['rouge1'].fmeasure, 4),
        'ROUGE-L': round(rouge_scores['rougeL'].fmeasure, 4),
        'BLEU': round(bleu, 4)
    }
    return results
