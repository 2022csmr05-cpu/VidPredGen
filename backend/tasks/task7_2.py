# ============================================================
# TASK 7.2 : DYNAMIC SEMANTIC OBJECT ANALYSIS
# ============================================================

from nltk.corpus import wordnet as wn


def classify_category(hypernyms):

    if any(h in hypernyms for h in ["person", "human"]):
        return "human"

    if "animal" in hypernyms:
        return "animal"

    if any(h in hypernyms for h in ["vehicle", "conveyance", "transport"]):
        return "vehicle"

    if any(h in hypernyms for h in ["artifact", "instrumentality", "device"]):
        return "object"

    return "unknown"


def get_semantic_info(obj):

    obj = obj.lower().strip()

    synsets = wn.synsets(obj)

    if not synsets:
        return {
            "label": obj,
            "category": "unknown",
            "hypernyms": []
        }

    best_syn = synsets[0]

    hypernyms = []

    for path in best_syn.hypernym_paths():
        hypernyms.extend([h.name().split('.')[0] for h in path])

    hypernyms = list(set(hypernyms))

    category = classify_category(hypernyms)

    return {
        "label": obj,
        "category": category,
        "hypernyms": hypernyms
    }


def actor_object_analysis(detected_objects):

    print("\n[Task 7.2] Semantic Object Analysis...")

    structured = []
    grouped = {}

    for obj in detected_objects:

        info = get_semantic_info(obj)
        structured.append(info)

        grouped.setdefault(info["category"], []).append(info)

    print("[Task 7.2] Semantic classification complete")

    return {
        "structured": structured,
        "grouped": grouped
    }