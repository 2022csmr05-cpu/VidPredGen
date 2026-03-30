# ============================================================
# TASK 8 : USER SELECTION
# ============================================================


def select_future_option(future_output, choice_id=None):
    """Select a future option.

    If `choice_id` is provided, select that option directly (suitable for API-driven use).
    Otherwise, fall back to an interactive CLI prompt.
    """

    options = future_output.get("future_options", [])

    if not options:
        print("[Task 8] No options available.")
        return None

    # If an option id is provided, pick it directly (API-friendly)
    if choice_id is not None:
        selected = next(
            (opt for opt in options if opt["id"] == choice_id),
            None
        )

        if selected:
            print("\n[Task 8] Selected Option:")
            print(selected["text"])
        else:
            print(f"[Task 8] Invalid selection id: {choice_id}")

        return selected

    print("========== SELECT AN OPTION ==========")

    for opt in options:
        print(f"{opt['id']}: {opt['text']}")

    # --------------------------------------------------------
    # USER INPUT LOOP (SAFE)
    # --------------------------------------------------------
    while True:
        try:
            choice = int(input("\nEnter option number: "))

            selected = next(
                (opt for opt in options if opt["id"] == choice),
                None
            )

            if selected:
                print("\n[Task 8] Selected Option:")
                print(selected["text"])
                return selected

            else:
                print("Invalid choice. Try again.")

        except ValueError:
            print("Please enter a valid number.")
