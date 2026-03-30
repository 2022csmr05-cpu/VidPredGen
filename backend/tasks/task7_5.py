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


def detect_subject_from_context(summary, objects):

    text = summary.lower()

    subject_keywords = [
        "waterfall", "river", "stream", "water", "ocean", "wave",
        "rain", "snow", "cloud", "sky", "forest", "tree",
        "mountain", "fire", "smoke", "road", "traffic"
    ]

    for keyword in subject_keywords:
        if keyword in text:
            return keyword

    for obj in objects:
        if obj and obj.lower() in text:
            return obj.lower()

    return "scene"


def has_human_presence(summary, object_data):

    text = summary.lower()

    human_words = [
        "person", "people", "man", "woman", "child",
        "face", "facial", "character", "subject"
    ]

    if any(word in text for word in human_words):
        return True

    for item in object_data.get("structured", []):
        if item.get("category") == "human":
            return True

    return False


# ------------------------------------------------------------
# SAFE PICK
# ------------------------------------------------------------
def pick(lst, default):
    return random.choice(lst) if lst else default


# ------------------------------------------------------------
# ACTION DIVERSIFICATION (NEW FIX)
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
def detect_scene_type(actions, objects, summary, object_data):

    text = summary.lower()

    motion_words = ["run", "move", "jump", "chase", "drive", "ride"]
    interaction_words = ["talk", "speak", "smile", "laugh", "react"]
    static_words = ["face", "expression", "close", "still"]
    object_words = ["screen", "ui", "display", "interface", "website"]
    nature_words = [
        "waterfall", "river", "stream", "water", "ocean", "wave",
        "rain", "snow", "cloud", "mist", "forest", "tree",
        "mountain", "nature", "landscape", "fire", "smoke"
    ]

    scores = {
        "motion": 0,
        "interaction": 0,
        "static": 0,
        "object": 0,
        "natural_flow": 0
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

    for word in nature_words:
        if word in text:
            scores["natural_flow"] += 3

    grouped_objects = object_data.get("grouped", {})
    if grouped_objects.get("human"):
        scores["interaction"] += 2
    else:
        scores["static"] = max(0, scores["static"] - 2)

    if any(obj.lower() in nature_words for obj in objects):
        scores["natural_flow"] += 2

    scene_type = max(scores, key=scores.get)

    if scores[scene_type] == 0:
        scene_type = "natural_flow" if not has_human_presence(summary, object_data) else "general"

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
    human_present = has_human_presence(summary_6_3, object_data_7_2)
    detected_subject = detect_subject_from_context(summary_6_3, objects)

    main_action = diversify_action(pick(actions, "move"))
    alt_action = diversify_action(pick(actions[1:], "change direction"))
    main_object = pick(objects, "environment")

    scene_type = detect_scene_type(actions, objects, summary_6_3, object_data_7_2)

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

        if human_present:
            options.extend([
                "A subtle change in expression occurs.",
                "The subject shifts gaze slightly.",
                "A blink or minor facial movement happens.",
                "The expression changes to reflect a different emotion.",
                "A small head movement alters the framing.",
            ])
        else:
            options.extend([
                f"The {detected_subject} remains steady while subtle visual changes emerge.",
                f"The framing around the {detected_subject} shifts slightly.",
                "Ambient motion becomes more noticeable in the scene.",
                "Lighting or texture changes gently over the moment.",
                "The scene stays calm, with a small environmental variation.",
            ])

    elif scene_type == "object":

        options.extend([
            f"The {main_object} updates or changes state.",
            f"A new element appears on the {main_object}.",
            "The display transitions to another view.",
            "An interaction modifies the current state.",
            "The system responds to an input.",
        ])

    elif scene_type == "natural_flow":

        if detected_subject == "waterfall":
            options.extend([
                "The waterfall continues cascading, with the flow becoming slightly stronger.",
                "More mist forms around the waterfall as the water crashes below.",
                "The waterfall maintains its flow while nearby ripples spread outward.",
                "The stream beneath the waterfall becomes more turbulent for a moment.",
                "The waterfall's movement stays steady as the surrounding spray thickens.",
                "The camera could follow the falling water downward toward the pool below.",
            ])
        elif detected_subject in {"river", "stream", "water", "ocean", "wave"}:
            options.extend([
                f"The {detected_subject} continues flowing with a slight change in intensity.",
                f"Small ripples build across the {detected_subject} as motion carries forward.",
                f"The movement of the {detected_subject} becomes briefly more turbulent.",
                f"The {detected_subject} keeps its rhythm while reflections shift across the surface.",
                "Spray, foam, or surface texture becomes more visible as the scene develops.",
            ])
        else:
            options.extend([
                f"The {detected_subject} continues naturally with a subtle shift in motion.",
                f"The scene around the {detected_subject} becomes slightly more dynamic.",
                "Ambient movement builds gradually in the environment.",
                "Natural textures and motion become more pronounced over time.",
                "The scene evolves gently while preserving the same setting.",
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
