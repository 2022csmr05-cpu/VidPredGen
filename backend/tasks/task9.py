# ============================================================
# TASK 9 : PROMPT GENERATION
# ============================================================

def generate_prompt_from_selection(
    selected_option,
    summary_6_3,
    style_data,
    intent_data_7_4
):

    print("\n[Task 9] Generating prompt...")

    if not selected_option:
        print("[Task 9] No selected option provided.")
        return None

    selected_text = selected_option.get("text", "")

    style = style_data.get("style", "cinematic")
    motion = style_data.get("motion_level", "medium")
    intent = intent_data_7_4.get("predicted_activity", "")

    # --------------------------------------------------------
    # FINAL PROMPT
    # --------------------------------------------------------
    prompt = f"""
Generate a video scene based on the following:

Context:
{summary_6_3}

Selected Future Event:
{selected_text}

Style:
- Visual style: {style}
- Motion intensity: {motion}

Intent:
{intent}

Instructions:
- Maintain visual consistency with the original scene
- Keep characters and environment coherent
- Ensure smooth transition from previous scene
- Make the scene realistic and visually engaging
"""

    print("\n========== GENERATED PROMPT ==========\n")
    print(prompt.strip())

    return {
        "prompt": prompt.strip()
    }