import os
import google.generativeai as genai
# To handle potential API errors specifically, though a general Exception is also used.
from google.api_core import exceptions as google_exceptions

# Environment variable for the API key
API_KEY_ENV_VAR = "GEMINI_API_KEY"

# Placeholder for when API key is not available
MOCK_SOLUTION_ENABLED = True # Set to False to disable mock response when API key is missing
MOCK_SOLUTION_TEXT = "Solution steps would be generated here by Gemini API. (Mock Response)"

def generate_solution_steps(problem_text, problem_type, answer=None):
    """
    Generates step-by-step solution for a given problem using the Gemini API.

    Args:
        problem_text (str): The text of the problem.
        problem_type (str): The type of the problem (e.g., "arithmetic", "algebra").
        answer (str, optional): The correct answer to the problem. Defaults to None.

    Returns:
        str: The generated solution steps as a string,
             a mock solution if API key is missing and MOCK_SOLUTION_ENABLED is True,
             or an error message string if an error occurs.
    """
    api_key = os.getenv(API_KEY_ENV_VAR)

    if not api_key:
        if MOCK_SOLUTION_ENABLED:
            print(f"Warning: Environment variable {API_KEY_ENV_VAR} not set. Returning mock solution.")
            return MOCK_SOLUTION_TEXT
        else:
            error_msg = f"Error: Gemini API key not found. Set the environment variable {API_KEY_ENV_VAR}."
            print(error_msg)
            # Depending on desired behavior, could raise ValueError(error_msg)
            return error_msg

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        error_msg = f"Error configuring Gemini API: {e}"
        print(error_msg)
        return error_msg

    # Construct the prompt
    prompt_lines = [
        "You are a friendly math tutor for elementary school students. Explain how to solve the following math problem step-by-step so a child can easily understand.",
        f"Problem Type: {problem_type}",
        f"Problem: \"{problem_text}\""
    ]
    if answer:
        prompt_lines.append(f"Correct Answer: {answer}")
    prompt_lines.append("Provide the solution steps:")

    prompt = "\n".join(prompt_lines)

    try:
        # Initialize the generative model
        # Using 'gemini-1.0-pro' as 'gemini-pro' might be an alias that changes.
        # Check documentation for the latest recommended model names.
        model = genai.GenerativeModel('gemini-1.0-pro')

        # Generate content
        response = model.generate_content(prompt)

        if response and response.parts:
            # Assuming the response structure contains text in `response.text`
            # or assembled from parts. For simple text, response.text is common.
            # If the response is streamed or complex, this part might need adjustment.
            # Based on Gemini API, `response.text` should be available.
            solution_text = response.text
            if solution_text:
                return solution_text.strip()
            else:
                # This case might occur if the response was successful but contained no text,
                # or if the model refused to answer (e.g. safety settings).
                print("Warning: Gemini API returned an empty response.")
                return "Error: Gemini API returned an empty response."
        else:
            # Handle cases where the response object itself is not as expected or parts are missing.
            print("Warning: Gemini API response structure was not as expected or was empty.")
            return "Error: Gemini API returned an invalid or empty response structure."

    except google_exceptions.GoogleAPIError as e:
        error_msg = f"Gemini API Error: {e}"
        print(error_msg)
        return error_msg
    except Exception as e:
        # Catch any other exceptions during API call or response processing
        error_msg = f"An unexpected error occurred during Gemini API interaction: {e}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    print("Testing Gemini Integration Module...")

    # Test case 1: API Key potentially missing (will use mock if enabled)
    print("\n--- Test Case 1: API Key Not Set (or mock response) ---")
    # To ensure this test runs as intended, we might temporarily unset the API key
    # if it's already set in the environment for this run.
    # However, for automated testing, relying on MOCK_SOLUTION_ENABLED is safer.
    original_mock_setting = MOCK_SOLUTION_ENABLED
    MOCK_SOLUTION_ENABLED = True # Ensure mock is on for this test

    problem1_text = "What is 5 + 3?"
    problem1_type = "Addition"
    problem1_answer = "8"

    solution1 = generate_solution_steps(problem1_text, problem1_type, problem1_answer)
    print(f"Problem: {problem1_text}")
    print(f"Solution:\n{solution1}")

    # Check if it's a mock response or an actual API key error message
    if os.getenv(API_KEY_ENV_VAR):
        print("(Note: API key IS set, so this might be an actual API call if mock was off)")
    else:
        assert solution1 == MOCK_SOLUTION_TEXT or API_KEY_ENV_VAR in solution1 # Checks if it's mock or the specific error message
        print("(API key not set, mock response or error message expected)")

    MOCK_SOLUTION_ENABLED = original_mock_setting # Restore mock setting

    # Test case 2: Example with a (potentially) valid API key
    # This test will only work if GEMINI_API_KEY is actually set in the environment
    # and the API call is successful.
    if os.getenv(API_KEY_ENV_VAR):
        print("\n--- Test Case 2: API Key IS Set (Actual API Call) ---")
        MOCK_SOLUTION_ENABLED = False # Turn off mock to force API call or key error

        problem2_text = "A farmer has 10 apples. He gives away 3 apples. How many apples does he have left?"
        problem2_type = "Subtraction"
        problem2_answer = "7"

        solution2 = generate_solution_steps(problem2_text, problem2_type, problem2_answer)
        print(f"Problem: {problem2_text}")
        print(f"Solution:\n{solution2}")
        assert solution2 is not None
        assert "Error" not in solution2 # Basic check that it's not an error message
        assert MOCK_SOLUTION_TEXT not in solution2 # Ensure it's not a mock response

        # Test case 3: Problem without a pre-defined answer
        print("\n--- Test Case 3: API Key IS Set, No Answer Provided (Actual API Call) ---")
        problem3_text = "What is 4 multiplied by 6?"
        problem3_type = "Multiplication"
        solution3 = generate_solution_steps(problem3_text, problem3_type)
        print(f"Problem: {problem3_text}")
        print(f"Solution:\n{solution3}")
        assert solution3 is not None
        assert "Error" not in solution3
        assert MOCK_SOLUTION_TEXT not in solution3

        MOCK_SOLUTION_ENABLED = original_mock_setting # Restore
    else:
        print("\n--- Test Case 2 & 3 Skipped: GEMINI_API_KEY environment variable not set. ---")
        print("Set the GEMINI_API_KEY to run live API tests.")

    print("\nGemini Integration Module testing finished.")
    # Example of how to set the API key for testing if needed, though it's best done in the environment:
    # os.environ[API_KEY_ENV_VAR] = "YOUR_ACTUAL_API_KEY_HERE"
    # And then call the function. Remember to not commit actual keys.
    # For this script, it relies on the environment variable being pre-set.
    # Or it uses the mock response if MOCK_SOLUTION_ENABLED is True.
    # The test cases try to handle both scenarios.
    # If you have the key, you can run:
    # GEMINI_API_KEY="your_key_here" python gemini_integration.py
    # to see live results for test cases 2 and 3.
