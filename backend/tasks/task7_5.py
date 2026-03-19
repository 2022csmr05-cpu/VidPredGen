# ============================================================
# TASK 7.5 : FINAL FUTURE PREDICTION ENGINE (ADVANCED + CLEAN)
# ============================================================

import random


# ------------------------------------------------------------
# CLEAN ACTIONS (REMOVE NOISE)
# ------------------------------------------------------------
def clean_actions(actions):

    banned = {"be", "have", "set", "appear", "seem", "create"}

    return [
        a for a in actions
        if a not in banned and len(a) > 3
    ]


# ------------------------------------------------------------
# EXTRACT ACTIONS FROM SUMMARY (BOOST)
# ------------------------------------------------------------
def extract_actions_from_summary(summary):

    keywords = [
        "run", "walk", "move", "jump", "chase", "collect",
        "talk", "speak", "look", "smile", "laugh",
        "drive", "ride", "climb", "fall", "dance",
        "eat", "drink", "gesture", "react"
    ]

    found = []

    for k in keywords:
        if k in summary.lower():
            found.append(k)

    return found


# ------------------------------------------------------------
# FILTER OBJECTS USING CONTEXT (REMOVE YOLO NOISE)
# ------------------------------------------------------------
def filter_objects(objects, summary):

    summary = summary.lower()

    valid = []

    for obj in objects:
        if obj.lower() in summary:
            valid.append(obj)

    return valid


# ------------------------------------------------------------
# SAFE PICK
# ------------------------------------------------------------
def pick(lst, default):
    return random.choice(lst) if lst else default


# ------------------------------------------------------------
# 🔥 ACTION DIVERSIFICATION (NEW FIX)
# ------------------------------------------------------------
def diversify_action(action):

    variations = {
        "collect": ["collect", "gather", "pick up"],
        "run": ["run", "move forward", "advance"],
        "move": ["move", "progress", "continue forward"],
        "walk": ["walk", "move steadily"],
        "jump": ["jump", "leap"],
        "talk": ["talk", "speak", "communicate"],
        "look": ["look", "observe"],
    }

    if action in variations:
        return random.choice(variations[action])

    return action


# ------------------------------------------------------------
# SCENE TYPE DETECTION
# ------------------------------------------------------------
def detect_scene_type(actions, objects, summary):

    text = summary.lower()

    motion_words = ["run", "move", "jump", "chase", "drive", "ride"]
    interaction_words = ["talk", "speak", "smile", "laugh", "react"]
    static_words = ["face", "expression", "close", "still"]
    object_words = ["screen", "ui", "display", "interface", "website"]

    scores = {
        "motion": 0,
        "interaction": 0,
        "static": 0,
        "object": 0
    }

    for word in motion_words:
        if word in text:
            scores["motion"] += 2

    for word in interaction_words:
        if word in text:
            scores["interaction"] += 2

    for word in static_words:
        if word in text:
            scores["static"] += 2

    for word in object_words:
        if word in text:
            scores["object"] += 2

    scene_type = max(scores, key=scores.get)

    if scores[scene_type] == 0:
        scene_type = "general"

    print("[Scene Type Scores]:", scores)
    print("[Detected Scene Type]:", scene_type)

    return scene_type


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------
def future_prediction_7_5(
    style_data,
    summary_6_3,
    scenes_7_1,
    object_data_7_2,
    event_data_7_3,
    intent_data_7_4,
    processor,
    model,
    last_frame=None,
    device="cpu"
):

    print("\n[Task 7.5] Future Prediction Starting...")

    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------
    raw_actions = event_data_7_3.get("final_actions", [])

    actions = list(set(
        clean_actions(raw_actions) +
        extract_actions_from_summary(summary_6_3)
    ))

    raw_objects = [obj["label"] for obj in object_data_7_2.get("structured", [])]
    objects = filter_objects(raw_objects, summary_6_3)

    main_action = diversify_action(pick(actions, "move"))
    alt_action = diversify_action(pick(actions[1:], "change direction"))
    main_object = pick(objects, "environment")

    scene_type = detect_scene_type(actions, objects, summary_6_3)

    options = []

    # ========================================================
    # GENERATION LOGIC
    # ========================================================

    if scene_type == "motion":

        options.extend([
            f"The subject continues to {main_action}, maintaining forward movement.",
            f"The subject adjusts direction while continuing to {alt_action}.",
            f"The subject interacts with the {main_object} during motion.",
            f"The subject speeds up, increasing intensity.",
            f"The subject slows slightly to regain control.",
            f"The subject briefly loses balance while moving.",
            f"The path ahead changes, requiring quick adaptation.",
        ])

    elif scene_type == "interaction":

        options.extend([
            f"The subject continues to {main_action}, maintaining interaction.",
            "The interaction receives a response that changes its direction.",
            "The subject pauses before continuing.",
            "The emotional tone shifts slightly.",
            "Another entity joins and affects the interaction.",
            "The interaction becomes more expressive.",
        ])

    elif scene_type == "static":

        options.extend([
            "A subtle change in expression occurs.",
            "The subject shifts gaze slightly.",
            "A blink or minor facial movement happens.",
            "The expression changes to reflect a different emotion.",
            "A small head movement alters the framing.",
        ])

    elif scene_type == "object":

        options.extend([
            f"The {main_object} updates or changes state.",
            f"A new element appears on the {main_object}.",
            "The display transitions to another view.",
            "An interaction modifies the current state.",
            "The system responds to an input.",
        ])

    else:

        options.extend([
            f"The subject continues to {main_action}.",
            f"The subject shifts from {main_action} to {alt_action}.",
            f"The subject interacts with the {main_object}.",
            "A variation occurs in the sequence.",
            "The situation evolves into a new phase.",
        ])

    # --------------------------------------------------------
    # CLEAN & LIMIT
    # --------------------------------------------------------
    options = list(dict.fromkeys(options))
    random.shuffle(options)
    options = options[:8]

    # --------------------------------------------------------
    # STRUCTURED OUTPUT + PRINT
    # --------------------------------------------------------
    structured_options = []

    print("\n========== FUTURE OPTIONS ==========\n")

    for i, opt in enumerate(options, 1):

        structured_options.append({
            "id": i,
            "text": opt
        })

        print(f"Option {i}: {opt}")

    print("\n[Task 7.5] Future options generated")

    return {
        "future_options": structured_options,
        "scene_type": scene_type
    }