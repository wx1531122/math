import sys
import os

# Import from other modules
try:
    from problem_manager import add_problem, get_problem_by_id, update_problem_solution, load_problems
    from gemini_integration import generate_solution_steps, MOCK_SOLUTION_TEXT, API_KEY_ENV_VAR
    from exporter import export_problems_to_html
except ModuleNotFoundError as e:
    print(f"CRITICAL ERROR: A required module was not found. Ensure all project files are in the same directory or PYTHONPATH is set correctly. Details: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"CRITICAL ERROR: Failed to import a required component. Details: {e}")
    sys.exit(1)

PROBLEMS_CSV_PATH = "data/problems.csv"

# Optional: Clear screen function for better UX
def clear_screen():
    """Clears the terminal screen."""
    # os.system('cls' if os.name == 'nt' else 'clear')
    # Disabled by default as it can be jarring. Uncomment if desired.
    pass

def print_header(title):
    """Prints a formatted header."""
    clear_screen()
    print("\n" + "=" * 50)
    print(f"=== {title.upper()} ===")
    print("=" * 50)

def get_user_input(prompt, validate_non_empty=False, to_lower=False, default=None):
    """Gets user input, optionally validates, converts to lowercase, and handles default values."""
    while True:
        if default is not None:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            if not user_input: # User pressed Enter for default
                return default
        else:
            user_input = input(prompt).strip()

        if validate_non_empty and not user_input:
            print("Error: This field cannot be empty. Please try again.")
        else:
            return user_input.lower() if to_lower else user_input

def handle_add_problem():
    """Handles the workflow for adding a new problem."""
    print_header("Add New Math Problem")

    problem_text = get_user_input("Enter the problem text: ", validate_non_empty=True)
    print("Common problem types: Arithmetic, Algebra, Geometry, Word Problem, Logic, etc.")
    problem_type = get_user_input("Enter the problem type: ", validate_non_empty=True)
    answer = get_user_input("Enter the correct answer: ", validate_non_empty=True)
    source = get_user_input("Enter the source (optional, press Enter to skip): ")

    try:
        new_problem = add_problem(
            problem_text=problem_text,
            problem_type=problem_type,
            answer=answer,
            source=source,
            filepath=PROBLEMS_CSV_PATH
        )
        if new_problem:
            print(f"\nSuccess! Problem added with ID: {new_problem['problem_id']}")
        else:
            print("\nError: Failed to add problem. Unknown error in problem_manager.")
    except Exception as e:
        print(f"\nError adding problem: {e}")
    input("\nPress Enter to return to the menu...")

def handle_generate_solution():
    """Handles the workflow for generating solution steps for a problem."""
    print_header("Generate Solution Steps (via Gemini API)")

    problem_id = get_user_input("Enter the Problem ID to generate solution for: ", validate_non_empty=True)

    try:
        problem = get_problem_by_id(problem_id, filepath=PROBLEMS_CSV_PATH)
    except Exception as e:
        print(f"Error retrieving problem: {e}")
        input("\nPress Enter to return to the menu...")
        return

    if not problem:
        print(f"Error: Problem with ID '{problem_id}' not found.")
        input("\nPress Enter to return to the menu...")
        return

    print("\n--- Problem Found ---")
    print(f"ID: {_escape_display(problem.get('problem_id'))}")
    print(f"Text: {_escape_display(problem.get('problem_text'))}")
    print(f"Type: {_escape_display(problem.get('problem_type'))}")
    print(f"Answer: {_escape_display(problem.get('answer'))}")
    print("--------------------")

    if not os.getenv(API_KEY_ENV_VAR):
        print(f"\nWarning: Gemini API key ({API_KEY_ENV_VAR}) is not set.")
        print("The system will return a mock/placeholder solution.")
        if get_user_input("Continue to get a mock response? (yes/no): ", to_lower=True, default="yes") != "yes":
            print("Solution generation cancelled.")
            input("\nPress Enter to return to the menu...")
            return

    print("\nAttempting to generate solution steps with Gemini API...")
    generated_steps = generate_solution_steps(
        problem_text=problem.get('problem_text'),
        problem_type=problem.get('problem_type'),
        answer=problem.get('answer')
    )

    if not generated_steps:
        print("\nError: Received no solution steps from the generation module.")
        input("\nPress Enter to return to the menu...")
        return

    print("\n--- Generated Solution Steps ---")
    print(_escape_display(generated_steps)) # Escape for display, just in case
    print("------------------------------")

    if "Error:" in generated_steps or generated_steps == MOCK_SOLUTION_TEXT:
        print("\nThe returned text appears to be an error or a mock response. It will not be saved.")
        input("\nPress Enter to return to the menu...")
        return

    save_confirmation = get_user_input("Save these solution steps? (yes/no): ", validate_non_empty=True, to_lower=True, default="yes")
    if save_confirmation == 'yes':
        try:
            success = update_problem_solution(problem_id, generated_steps, filepath=PROBLEMS_CSV_PATH)
            if success:
                print(f"\nSuccessfully saved solution steps for problem ID '{problem_id}'.")
            else:
                print(f"\nError: Failed to save solution steps for problem ID '{problem_id}'.")
        except Exception as e:
            print(f"\nError saving solution steps: {e}")
    else:
        print("\nSolution steps were not saved.")
    input("\nPress Enter to return to the menu...")

def _escape_display(text):
    """Basic escaping for console display if needed, primarily for newlines or tabs."""
    if text is None: return "N/A"
    return str(text).replace('\n', '\n  ') # Indent newlines for readability

def display_all_problems():
    """Displays all problems currently stored."""
    print_header("View All Problems")
    try:
        problems = load_problems(filepath=PROBLEMS_CSV_PATH)
        if not problems:
            print("No problems found.")
            input("\nPress Enter to return to the menu...")
            return

        print(f"Found {len(problems)} problem(s):\n")
        for idx, problem in enumerate(problems):
            print(f"--- Problem {idx + 1} ---")
            print(f"  ID: {_escape_display(problem.get('problem_id'))}")
            print(f"  Text: {_escape_display(problem.get('problem_text'))}")
            print(f"  Type: {_escape_display(problem.get('problem_type'))}")
            print(f"  Answer: {_escape_display(problem.get('answer'))}")
            solution_status = "Available" if problem.get('solution_steps_gemini') else "Not generated"
            if problem.get('solution_steps_gemini') == MOCK_SOLUTION_TEXT:
                solution_status = "Mock/Placeholder"
            print(f"  Solution: {solution_status}")
            print("-" * 25)
    except Exception as e:
        print(f"Error loading problems: {e}")
    input("\nPress Enter to return to the menu...")

def handle_export_problems():
    """Handles the workflow for exporting problems to HTML."""
    print_header("Export Problems to HTML")

    try:
        all_problems = load_problems(filepath=PROBLEMS_CSV_PATH)
        if not all_problems:
            print("No problems available to export.")
            input("\nPress Enter to return to the menu...")
            return
    except Exception as e:
        print(f"Error loading problems: {e}")
        input("\nPress Enter to return to the menu...")
        return

    problems_to_export = all_problems
    filter_choice = get_user_input("Export all problems or filter by type? (all/type): ", to_lower=True, default="all")

    if filter_choice == 'type':
        filter_type = get_user_input("Enter problem type to filter by: ", validate_non_empty=True)
        problems_to_export = [p for p in all_problems if p.get('problem_type', '').lower() == filter_type.lower()]
        if not problems_to_export:
            print(f"No problems found with type '{filter_type}'.")
            input("\nPress Enter to return to the menu...")
            return
        print(f"Found {len(problems_to_export)} problem(s) of type '{filter_type}'.")

    export_full_choice = get_user_input("Include answers and solution steps? (yes/no): ", to_lower=True, default="yes")
    export_full_flag = export_full_choice == 'yes'

    default_filename = "problems_export.html"
    output_filename = get_user_input("Enter output HTML filename: ", default=default_filename)
    if not output_filename.lower().endswith(".html"):
        output_filename += ".html"
        print(f"Filename adjusted to: {output_filename}")

    try:
        success = export_problems_to_html(problems_to_export, output_filename, export_full_flag)
        if success:
            print(f"\nSuccessfully exported {len(problems_to_export)} problem(s) to '{os.path.abspath(output_filename)}'.")
        else:
            print("\nError: Export failed. Check console for details from exporter module.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during export: {e}")
    input("\nPress Enter to return to the menu...")

def main_menu():
    """Displays the main menu and handles user choices."""
    # Initial check for CSV file, problem_manager's load/save will handle actual creation/header writing
    try:
        if not os.path.exists(PROBLEMS_CSV_PATH) or os.path.getsize(PROBLEMS_CSV_PATH) == 0:
            print(f"Note: Problems data file '{PROBLEMS_CSV_PATH}' is missing or empty.")
            print("It will be initialized when you add or attempt to load problems.")
    except Exception: # Catch potential permission errors etc.
        pass

    while True:
        print_header("Elementary Math Problem Assistant")
        print("1. Add New Problem")
        print("2. Generate Solution Steps")
        print("3. View All Problems")
        print("4. Export Problems to HTML")
        print("5. Exit")
        print("-" * 50)

        choice = get_user_input("Enter your choice (1-5): ")

        if choice == '1':
            handle_add_problem()
        elif choice == '2':
            handle_generate_solution()
        elif choice == '3':
            display_all_problems()
        elif choice == '4':
            handle_export_problems()
        elif choice == '5':
            print("\nExiting program. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}")
        print("Please report this issue.")
        sys.exit(1)
