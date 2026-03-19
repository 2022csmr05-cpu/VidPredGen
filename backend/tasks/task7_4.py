# ============================================================
# TASK 7.4 : FULLY DYNAMIC INTENT ANALYSIS
# ============================================================

import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


classifier = None


def get_classifier():

    global classifier

    if classifier is None:
        from transformers import pipeline

        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

    return classifier


def extract_pure_action_text(text):

    if not text:
        return ""

    stop_patterns = [
        "you are analyzing",
        "use the following sections",
        "scene overview",
        "environment:",
        "subjects:",
        "objects:",
        "actions:",
        "emotions",
        "motion:",
        "camera:",
        "temporal flow"
    ]

    cleaned_lines = []

    for line in text.split("."):
        line = line.strip().lower()

        if not any(p in line for p in stop_patterns):
            cleaned_lines.append(line)

    return ". ".join(cleaned_lines)


def generate_candidate_labels(text):

    doc = nlp(text)

    nouns = list({
        token.lemma_.lower()
        for token in doc
        if token.pos_ in {"NOUN", "PROPN"}
        and len(token.lemma_) > 2
    })

    verbs = list({
        token.lemma_.lower()
        for token in doc
        if token.pos_ == "VERB"
    })

    labels = []

    for n in nouns[:5]:
        labels.append(f"{n} activity")
        labels.append(f"{n} interaction")

    for v in verbs[:5]:
        labels.append(f"{v} action")

    labels.extend([
        "human activity",
        "object interaction",
        "movement"
    ])

    return list(set(labels))


def video_intent_analysis(context_summary, action_summary):

    print("\n[Task 7.4] Intent Analysis Starting...")

    clean_text_input = extract_pure_action_text(action_summary)

    if not clean_text_input or len(clean_text_input.split()) < 5:
        return {
            "predicted_activity": "insufficient_data",
            "confidence": 0.0,
            "top_3": []
        }

    clf = get_classifier()

    candidate_labels = generate_candidate_labels(clean_text_input)

    result = clf(clean_text_input, candidate_labels)

    intent = {
        "predicted_activity": result["labels"][0],
        "confidence": float(result["scores"][0]),
        "top_3": list(zip(result["labels"][:3], result["scores"][:3]))
    }

    print("[Task 7.4] Intent prediction complete")

    return intent