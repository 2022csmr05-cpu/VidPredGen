# ============================================================
# TASK 8 : USER SELECTION
# ============================================================

def select_future_option(future_output):

    options = future_output.get("future_options", [])

    if not options:
        print("[Task 8] No options available.")
        return None

    print("\n========== SELECT AN OPTION ==========\n")

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