import csv
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_FILEPATH = "data/problems.csv"
HEADERS = ["problem_id", "problem_text", "problem_type", "answer", "solution_steps_gemini", "source"]

def _initialize_csv(filepath):
    """Creates the CSV file with headers if it doesn't exist or is empty."""
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    write_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    if write_header:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(HEADERS)

def load_problems(filepath=DEFAULT_FILEPATH):
    """
    Loads problems from a CSV file.
    Returns a list of dictionaries, where each dictionary represents a problem.
    Handles FileNotFoundError by returning an empty list and printing a warning.
    """
    _initialize_csv(filepath) # Ensure file and headers exist
    problems = []
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if set(reader.fieldnames if reader.fieldnames else []) != set(HEADERS):
                # This case handles if the file exists but headers are incorrect or missing
                # Or if the file is empty after _initialize_csv (which shouldn't happen)
                # For simplicity, we could just rely on _initialize_csv to always fix it
                # but an explicit check can be useful for debugging.
                if not reader.fieldnames and os.path.getsize(filepath) > 0: # File has content but no headers DictReader could parse
                    logger.warning(f"CSV file {filepath} appears to be missing headers. Attempting to re-initialize.")
                    # This scenario is tricky, if there's data without headers, re-initializing might be destructive.
                    # For now, we'll proceed assuming _initialize_csv handles it, or it's empty.
                elif reader.fieldnames and set(reader.fieldnames) != set(HEADERS):
                     logger.warning(f"CSV file {filepath} has incorrect headers. Expected {HEADERS}, got {reader.fieldnames}")
                     # Decide on a recovery strategy: overwrite, error out, or attempt to map.
                     # For now, we'll return empty to avoid data corruption.
                     return []

            for row in reader:
                problems.append(row)
    except FileNotFoundError:
        logger.warning(f"File not found at {filepath}. Returning empty list.")
        # _initialize_csv should have created it, so this is unlikely unless there's a race condition or permission issue
    except Exception as e:
        logger.error(f"Error loading problems from {filepath}: {e}")
    return problems

def save_problems(problems, filepath=DEFAULT_FILEPATH):
    """
    Saves the list of problem dictionaries back to the CSV file.
    Ensures the header row is written correctly.
    """
    _initialize_csv(filepath) # Ensure directory exists, and file if it was somehow deleted
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(problems)
    except Exception as e:
        logger.error(f"Error saving problems to {filepath}: {e}")

def _generate_problem_id(existing_ids):
    """
    Generates a new unique problem ID (e.g., "P001", "P002").
    Starts from "P001" if no IDs exist.
    """
    if not existing_ids:
        return "P001"

    max_num = 0
    for problem_id in existing_ids:
        if problem_id.startswith("P") and problem_id[1:].isdigit():
            num = int(problem_id[1:])
            if num > max_num:
                max_num = num
    return f"P{max_num + 1:03d}"

def add_problem(problem_text, problem_type, answer, source="", filepath=DEFAULT_FILEPATH):
    """
    Adds a new problem to the CSV file.
    Generates a unique problem_id, creates a new problem dictionary,
    appends it to the list, and saves the updated list.
    Returns the newly added problem dictionary.
    """
    problems = load_problems(filepath=filepath)
    existing_ids = [p['problem_id'] for p in problems if 'problem_id' in p]

    new_id = _generate_problem_id(existing_ids)

    new_problem = {
        "problem_id": new_id,
        "problem_text": problem_text,
        "problem_type": problem_type,
        "answer": answer,
        "solution_steps_gemini": "",  # Initially empty
        "source": source
    }

    problems.append(new_problem)
    save_problems(problems, filepath=filepath)
    return new_problem

def get_problem_by_id(problem_id_to_find, filepath=DEFAULT_FILEPATH):
    """
    Loads problems and searches for a problem by its ID.
    Returns the problem dictionary if found, None otherwise.
    """
    problems = load_problems(filepath=filepath)
    for problem in problems:
        if problem.get('problem_id') == problem_id_to_find:
            return problem
    return None

def update_problem_solution(problem_id_to_update, solution_steps, filepath=DEFAULT_FILEPATH):
    """
    Updates the solution_steps_gemini field for a given problem_id.
    Loads problems, finds the problem, updates it, and saves the list.
    Returns True if successful, False otherwise.
    """
    problems = load_problems(filepath=filepath)
    problem_found = False
    for problem in problems:
        if problem.get('problem_id') == problem_id_to_update:
            problem['solution_steps_gemini'] = solution_steps
            problem_found = True
            break

    if problem_found:
        save_problems(problems, filepath=filepath)
        return True
    return False

if __name__ == '__main__':
    # Example Usage and Basic Tests
    print("Running basic tests for problem_manager...")

    # Ensure the CSV is clean for testing
    test_file = "data/test_problems.csv"
    if os.path.exists(test_file):
        os.remove(test_file)

    _initialize_csv(test_file) # Create it with headers

    # Test load_problems on an empty (or header-only) file
    initial_problems = load_problems(filepath=test_file)
    print(f"Initial problems: {initial_problems}")
    assert initial_problems == [], f"Expected empty list, got {initial_problems}"

    # Test add_problem
    print("\nTesting add_problem...")
    problem1 = add_problem("What is 2+2?", "arithmetic", "4", source="test_case", filepath=test_file)
    print(f"Added problem 1: {problem1}")
    assert problem1['problem_id'] == "P001"
    assert problem1['problem_text'] == "What is 2+2?"

    problem2 = add_problem("What is the capital of France?", "geography", "Paris", source="test_case", filepath=test_file)
    print(f"Added problem 2: {problem2}")
    assert problem2['problem_id'] == "P002"

    all_problems = load_problems(filepath=test_file)
    print(f"All problems after adding: {all_problems}")
    assert len(all_problems) == 2, f"Expected 2 problems, got {len(all_problems)}"

    # Test get_problem_by_id
    print("\nTesting get_problem_by_id...")
    retrieved_p1 = get_problem_by_id("P001", filepath=test_file)
    print(f"Retrieved P001: {retrieved_p1}")
    assert retrieved_p1 is not None and retrieved_p1['problem_text'] == "What is 2+2?"

    retrieved_p_non_existent = get_problem_by_id("P999", filepath=test_file)
    print(f"Retrieved P999: {retrieved_p_non_existent}")
    assert retrieved_p_non_existent is None

    # Test update_problem_solution
    print("\nTesting update_problem_solution...")
    update_success = update_problem_solution("P001", "Step 1: 2, Step 2: Add 2, Step 3: Equals 4", filepath=test_file)
    print(f"Update P001 success: {update_success}")
    assert update_success

    updated_p1 = get_problem_by_id("P001", filepath=test_file)
    print(f"Updated P001: {updated_p1}")
    assert updated_p1['solution_steps_gemini'] == "Step 1: 2, Step 2: Add 2, Step 3: Equals 4"

    update_fail = update_problem_solution("P999", "No steps", filepath=test_file)
    print(f"Update P999 success: {update_fail}")
    assert not update_fail

    # Test _generate_problem_id robustness
    print("\nTesting _generate_problem_id...")
    assert _generate_problem_id([]) == "P001"
    assert _generate_problem_id(["P001"]) == "P002"
    assert _generate_problem_id(["P001", "P003"]) == "P004"
    assert _generate_problem_id(["P010", "P002"]) == "P011"
    assert _generate_problem_id(["XYZ", "P001"]) == "P002" # Ignores malformed IDs
    assert _generate_problem_id(["P001", "P002", "P003", "P004", "P005", "P006", "P007", "P008", "P009"]) == "P010"
    assert _generate_problem_id(["P099"]) == "P100"


    # Test loading from default file (ensure it uses the default path correctly)
    # This requires `data/problems.csv` to be potentially modified by these tests if not careful
    # For now, we'll stick to test_file for explicit operations.
    # To truly test default file behavior, would need to setup/teardown `data/problems.csv`
    # or mock DEFAULT_FILEPATH.

    print("\nBasic tests for problem_manager completed.")
    print(f"Test data written to {test_file}")
    # Clean up test file by default, or inspect it manually
    # if os.path.exists(test_file):
    #     os.remove(test_file)

    # Re-run add_problem on the actual data file to ensure it's working
    # This will add problems to the main data/problems.csv
    # _initialize_csv(DEFAULT_FILEPATH) # Make sure it's there
    # print(f"\nAdding a sample problem to {DEFAULT_FILEPATH}...")
    # sample_problem = add_problem("What is 1+1?", "math", "2", source="initial_setup", filepath=DEFAULT_FILEPATH)
    # print(f"Added sample problem: {sample_problem}")
    # loaded_problems = load_problems(filepath=DEFAULT_FILEPATH)
    # print(f"Current problems in {DEFAULT_FILEPATH}: {loaded_problems}")

    # The example usage in __main__ now runs tests.
    # The original ProblemManager class is removed as per instructions focusing on functions.
    # If a class-based approach is desired later, these functions can be wrapped in a class.
    print("\nTo run example usage that modifies 'data/problems.csv', uncomment lines at the end of __main__")

    # For the actual run, we want problem_manager.py to define functions,
    # and main_cli.py or other scripts will call them.
    # The ProblemManager class from the original file is not used in this implementation.
    # The `manager = ProblemManager("data/problems.csv")` line in the original __main__
    # would not work directly with this functional approach unless refactored.
    # The new __main__ block provides test cases for the functions.

    # To use the default file path consistently in tests, we can set DEFAULT_FILEPATH to test_file
    # global DEFAULT_FILEPATH # This is not ideal in a module, better to pass filepath
    # DEFAULT_FILEPATH = test_file # This would make all calls use test_file
    # This is why functions explicitly take filepath and default to the real one.
    # The test cases explicitly use `test_file`.
    pass # End of __main__

# To ensure the main CSV file is initialized when the module is first imported or used.
# This is generally not recommended for module imports to have side effects like file creation.
# Better to call an init function from the main application entry point.
# However, given the subtask requirements, this ensures `data/problems.csv` has headers.
# _initialize_csv(DEFAULT_FILEPATH)
# This line above was moved into load_problems and save_problems to be more robust.

# _initialize_csv(DEFAULT_FILEPATH) # Ensure it exists with headers if module is just imported.
# This is a bit aggressive, usually an explicit setup step in your application is better.
# For this task, let's ensure it's always initialized by load/save.
# The `_initialize_csv` at the module level was removed.
# It's now called within load_problems and save_problems.
# The if __name__ == '__main__': block will not run on import, only when script is run directly.
# The print statement above will run on import.

# Final check on the requirements for _initialize_csv:
# "Initialize the data/problems.csv file with headers if it's empty or doesn't exist"
# This is handled by calling _initialize_csv at the start of load_problems and save_problems.
# The previous step should have created data/problems.csv with headers.
# _initialize_csv is idempotent and safe to call multiple times.
# It creates the directory if it doesn't exist.
# It writes headers only if the file doesn't exist or is empty.
# This should fulfill the requirement.

logger.info(f"problem_manager.py loaded. Main CSV: {DEFAULT_FILEPATH}")
