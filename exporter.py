import html
import os

def _escape(text):
    """Helper function to escape HTML characters. Returns empty string if text is None."""
    if text is None:
        return ""
    return html.escape(str(text))

def export_problems_to_html(problems_data, output_filename=None, export_full=True):
    """
    Exports a list of problem dictionaries to an HTML file or returns as an HTML string.

    Args:
        problems_data (list): A list of problem dictionaries. Each dictionary should have keys like
                              'problem_id', 'problem_text', 'problem_type', 'answer',
                              'solution_steps_gemini'.
        output_filename (str, optional): The name of the HTML file to create.
                                         If None, the HTML content is returned as a string.
                                         Defaults to None.
        export_full (bool): If True, exports problem, answer, and solution.
                            If False, exports only the problem text and type.

    Returns:
        str or bool: If output_filename is None, returns the HTML content as a string.
                     If output_filename is provided, returns True on successful file export, False on failure.
    """
    html_content = []

    # Start HTML5 boilerplate
    html_content.append("<!DOCTYPE html>")
    html_content.append("<html lang=\"en\">")
    html_content.append("<head>")
    html_content.append("    <meta charset=\"UTF-8\">")
    html_content.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
    html_content.append("    <title>Math Problems Export</title>")
    html_content.append("    <style>")
    html_content.append("        body { font-family: sans-serif; margin: 20px; line-height: 1.6; }")
    html_content.append("        .page-container { max-width: 800px; margin: auto; }") # For better A4 centering
    html_content.append("        .problem-container { page-break-inside: avoid; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #eee; }")
    html_content.append("        .problem-header { margin-bottom: 10px; }")
    html_content.append("        .problem-id { font-weight: bold; color: #333; font-size: 1.1em; }")
    html_content.append("        .problem-type { font-style: italic; color: #555; margin-left: 10px; font-size: 0.9em; }")
    html_content.append("        .problem-text { margin-top: 5px; margin-bottom: 10px; font-size: 1.2em; color: #000; }")
    html_content.append("        .answer-section { margin-left: 20px; margin-bottom: 10px; }")
    html_content.append("        .answer-label { font-weight: bold; color: #4CAF50; }") # Green for answer
    html_content.append("        .answer-text { margin-left: 5px; }")
    html_content.append("        .solution-steps-label { font-weight: bold; color: #007BFF; margin-top:10px }") # Blue for solution
    html_content.append("        .solution-steps { margin-left: 20px; white-space: pre-wrap; background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; border-radius: 4px; }")
    html_content.append("        h1 { text-align: center; color: #333; border-bottom: 2px solid #333; padding-bottom:10px; }")
    html_content.append("        @media print {") # Specific styles for printing
    html_content.append("            body { margin: 0.5in; font-size: 10pt; }") # Adjust margins for A4
    html_content.append("            .problem-container { border-bottom: 1px solid #ccc; }")
    html_content.append("            h1 { font-size: 18pt; }")
    html_content.append("            .page-container { max-width: 100%; margin: 0; }") # Use full width for print
    html_content.append("            .solution-steps { background-color: #fff; border: 1px solid #eee; }") # Lighter for print
    html_content.append("        }")
    html_content.append("    </style>")
    html_content.append("</head>")
    html_content.append("<body>")
    html_content.append("<div class=\"page-container\">")
    html_content.append("    <h1>Math Problems</h1>")

    if not problems_data:
        html_content.append("<p>No problems to display.</p>")

    for problem in problems_data:
        html_content.append("    <div class=\"problem-container\">")
        html_content.append("        <div class=\"problem-header\">")
        html_content.append(f"            <span class=\"problem-id\">Problem ID: {_escape(problem.get('problem_id', 'N/A'))}</span>")
        html_content.append(f"            <span class=\"problem-type\">Type: {_escape(problem.get('problem_type', 'N/A'))}</span>")
        html_content.append("        </div>")
        html_content.append(f"        <div class=\"problem-text\">{_escape(problem.get('problem_text', 'No problem text provided.'))}</div>")

        if export_full:
            html_content.append("        <div class=\"answer-section\">")
            html_content.append(f"            <span class=\"answer-label\">Answer:</span>")
            html_content.append(f"            <span class=\"answer-text\">{_escape(problem.get('answer', 'N/A'))}</span>")
            html_content.append("        </div>")

            solution_steps = problem.get('solution_steps_gemini')
            if solution_steps: # Only show solution section if steps are available
                html_content.append("        <div>") # Added div for better structure of label + steps
                html_content.append(f"            <div class=\"solution-steps-label\">Solution Steps:</div>")
                html_content.append(f"            <div class=\"solution-steps\">{_escape(solution_steps)}</div>")
                html_content.append("        </div>")
            else:
                html_content.append("        <div>")
                html_content.append(f"            <div class=\"solution-steps-label\">Solution Steps:</div>")
                html_content.append(f"            <div class=\"solution-steps\">No solution steps provided.</div>") # Placeholder if empty
                html_content.append("        </div>")


        html_content.append("    </div>") # End problem-container

    html_content.append("</div>") # End page-container
    html_content.append("</body>")
    html_content.append("</html>")

    final_html_string = "\n".join(html_content)

    if output_filename:
        try:
            # Ensure output directory exists if output_filename includes a path
            output_dir = os.path.dirname(output_filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(final_html_string)
            print(f"Successfully exported problems to {output_filename}")
            return True
        except IOError as e:
            print(f"Error writing HTML file {output_filename}: {e}")
            return False
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred during HTML export to file: {e}")
            return False
    else:
        # If output_filename is None, return the HTML string
        return final_html_string

if __name__ == '__main__':
    print("Testing Exporter Module...")

    # Sample problems data (mimicking what problem_manager would provide)
    sample_problems = [
        {
            "problem_id": "P001",
            "problem_text": "What is 2 + 2? Explain like I'm five.",
            "problem_type": "Arithmetic",
            "answer": "4",
            "solution_steps_gemini": "1. Imagine you have 2 apples.\n2. Now, someone gives you 2 more apples.\n3. Count all the apples: One, two, three, four!\nSo, 2 + 2 = 4.",
            "source": "Test Data"
        },
        {
            "problem_id": "P002",
            "problem_text": "If a cat has 4 legs, how many legs do 3 cats have in total?",
            "problem_type": "Multiplication",
            "answer": "12",
            "solution_steps_gemini": "Step 1: One cat has 4 legs.\nStep 2: For the second cat, add another 4 legs: 4 + 4 = 8 legs.\nStep 3: For the third cat, add another 4 legs: 8 + 4 = 12 legs.\nSo, 3 cats have 12 legs.",
            "source": "Test Data"
        },
        {
            "problem_id": "P003",
            "problem_text": "What is the capital of France?",
            "problem_type": "Geography",
            "answer": "Paris",
            "solution_steps_gemini": None, # No solution steps for this one
            "source": "Test Data"
        },
         {
            "problem_id": "P004",
            "problem_text": "This problem only has text and will be exported with export_full=False.",
            "problem_type": "Short Export",
            "answer": "This answer won't be shown.",
            "solution_steps_gemini": "These steps won't be shown.",
            "source": "Test Data"
        }
    ]

    # Test full export
    print("\n--- Test Case 1: Full Export (File) ---")
    full_export_filename = "test_problems_full_export.html"
    success_full_file = export_problems_to_html(sample_problems, output_filename=full_export_filename, export_full=True)
    if success_full_file: # This will print the success message from the function
        print(f"File export test generated: {os.path.abspath(full_export_filename)}")
    assert success_full_file

    # Test partial export (only problem text)
    print("\n--- Test Case 2: Partial Export (File) ---")
    partial_export_filename = "test_problems_partial_export.html"
    success_partial_file = export_problems_to_html(sample_problems, output_filename=partial_export_filename, export_full=False)
    if success_partial_file:
        print(f"File export test generated: {os.path.abspath(partial_export_filename)}")
    assert success_partial_file

    # Test with empty data (File)
    print("\n--- Test Case 3: Empty Data Export (File) ---")
    empty_export_filename = "test_problems_empty_export.html"
    success_empty_file = export_problems_to_html([], output_filename=empty_export_filename, export_full=True)
    if success_empty_file:
        print(f"File export test generated: {os.path.abspath(empty_export_filename)}")
    assert success_empty_file

    # Test export to subdirectory (File)
    print("\n--- Test Case 4: Export to Subdirectory (File) ---")
    subdir_export_filename = "exports/test_problems_subdir_export.html"
    if os.path.exists(subdir_export_filename): os.remove(subdir_export_filename)
    if os.path.exists(os.path.dirname(subdir_export_filename)) and not os.listdir(os.path.dirname(subdir_export_filename)):
        os.rmdir(os.path.dirname(subdir_export_filename))

    success_subdir_file = export_problems_to_html(sample_problems[:1], output_filename=subdir_export_filename, export_full=True)
    if success_subdir_file:
        print(f"File export test generated: {os.path.abspath(subdir_export_filename)}")
    assert success_subdir_file
    assert os.path.exists(subdir_export_filename)

    # Test string output
    print("\n--- Test Case 5: Full Export (String Output) ---")
    html_string_full = export_problems_to_html(sample_problems, output_filename=None, export_full=True)
    assert isinstance(html_string_full, str)
    assert "</html>" in html_string_full
    assert "Problem ID: P001" in html_string_full
    assert "What is 2 + 2?" in html_string_full
    assert "Solution Steps:" in html_string_full # Check if solution steps are included
    print("String output (full) test passed. Length:", len(html_string_full))

    print("\n--- Test Case 6: Partial Export (String Output) ---")
    html_string_partial = export_problems_to_html(sample_problems, output_filename=None, export_full=False)
    assert isinstance(html_string_partial, str)
    assert "</html>" in html_string_partial
    assert "Problem ID: P004" in html_string_partial
    assert "This problem only has text" in html_string_partial
    assert "Solution Steps:" not in html_string_partial # Check that solution steps are NOT included
    assert "Answer:" not in html_string_partial
    print("String output (partial) test passed. Length:", len(html_string_partial))

    print("\n--- Test Case 7: Empty Data (String Output) ---")
    html_string_empty = export_problems_to_html([], output_filename=None, export_full=True)
    assert isinstance(html_string_empty, str)
    assert "<p>No problems to display.</p>" in html_string_empty
    print("String output (empty) test passed.")

    print("\nExporter Module testing finished.")
    print("File-based tests can be visually inspected by opening the generated .html files.")
    # Example:
    # (These commands are for your local terminal, not for the run_in_bash_session here)

    # To check the `_escape` function (remains unchanged)
    assert _escape("<b>Bold</b>") == "&lt;b&gt;Bold&lt;/b&gt;"
    assert _escape(None) == ""
    assert _escape(123) == "123"
    print("\n_escape function tests passed (unchanged).")

    print("\nAll exporter tests completed.")
