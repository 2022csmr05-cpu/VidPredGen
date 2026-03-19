# ============================================================
# TASK 7.3 : ROBUST + DYNAMIC EVENT EXTRACTION (FIXED)
# ============================================================

import spacy
from collections import Counter
from nltk.corpus import wordnet as wn

# Load spaCy safely
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# ------------------------------------------------------------
# CHECK IF REAL VERB
# ------------------------------------------------------------
def is_real_verb(word):
    return len(wn.synsets(word, pos=wn.VERB)) > 0


# ------------------------------------------------------------
# EXTRACT ACTIONS WITH STRUCTURAL VALIDATION
# ------------------------------------------------------------
def extract_actions_with_scores(doc):

    actions = []

    for token in doc:

        # Must be verb
        if token.pos_ != "VERB":
            continue

        # Ignore auxiliaries / weak connectors
        if token.dep_ in {"aux", "auxpass", "cop"}:
            continue

        lemma = token.lemma_.lower()

        # Must be real verb
        if not is_real_verb(lemma):
            continue

        # Ignore non-alphabetic noise
        if not lemma.isalpha():
            continue

        # ----------------------------------------------------
        # SCORING SYSTEM (KEY FIX)
        # ----------------------------------------------------
        score = 1

        # ROOT verbs are important
        if token.dep_ == "ROOT":
            score += 3

        # Has subject → stronger action
        if any(child.dep_ in {"nsubj", "nsubjpass"} for child in token.children):
            score += 2

        # Has object → meaningful interaction
        if any(child.dep_ in {"dobj", "pobj"} for child in token.children):
            score += 1

        actions.append((lemma, score))

    return actions


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------
def event_extraction(scenes):

    print("\n[Task 7.3] Event Extraction Starting...")

    events = []
    action_scores = []

    for scene in scenes:

        doc = nlp(scene)
        scored_actions = extract_actions_with_scores(doc)

        if scored_actions:

            actions_only = [a for a, _ in scored_actions]

            events.append({
                "scene": scene,
                "actions": actions_only
            })

            action_scores.extend(scored_actions)

    # --------------------------------------------------------
    # AGGREGATE SCORES + FREQUENCY
    # --------------------------------------------------------
    score_map = {}
    freq_map = Counter([a for a, _ in action_scores])

    for action, score in action_scores:

        # combine score + frequency (balanced, not rigid)
        combined_score = score + freq_map[action]

        score_map[action] = score_map.get(action, 0) + combined_score

    # --------------------------------------------------------
    # FINAL SELECTION (TOP ACTIONS)
    # --------------------------------------------------------
    sorted_actions = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

    final_actions = [a for a, _ in sorted_actions[:5]]  # top 5 dynamic

    print(f"[Task 7.3] Events extracted: {len(events)}")

    # Debug logs
    print("\n[DEBUG] Action scores:")
    print(score_map)

    print("\n[DEBUG] Final ranked actions:")
    print(final_actions)

    return {
        "events": events,
        "action_scores": score_map,
        "all_actions": [a for a, _ in action_scores],
        "final_actions": final_actions
    }