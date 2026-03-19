# ============================================================
# TASK 7.1 : CLEAN + GENERIC SCENE SEGMENTATION
# ============================================================

import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    return (text or "").lower().replace("\n", " ")


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


def is_valid_scene(seg):

    if len(seg.split()) < 4:
        return False

    doc = nlp(seg)

    has_verb = any(t.pos_ == "VERB" for t in doc)
    has_noun = any(t.pos_ in {"NOUN", "PROPN"} for t in doc)

    return has_verb and has_noun


def scene_segmentation(context_summary, action_summary):

    print("\n[Task 7.1] Scene Segmentation Starting...")

    text = extract_pure_action_text(action_summary)
    text = clean_text(text)

    segments = [s.strip() for s in re.split(r"[.]", text) if s.strip()]

    scenes = [seg for seg in segments if is_valid_scene(seg)]

    unique_scenes = list(dict.fromkeys(scenes))

    print(f"[Task 7.1] Scenes identified: {len(unique_scenes)}")

    return unique_scenes