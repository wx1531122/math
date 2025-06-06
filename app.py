from flask import Flask, request, jsonify, make_response
import logging
import sys
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# For now, we'll just import the modules to ensure they can be imported
# Actual usage will come in later steps
try:
    from problem_manager import (
        add_problem, load_problems, get_problem_by_id,
        update_problem_solution, save_problems, delete_problem
    )
    import problem_manager # Keep this for now if other parts of problem_manager are needed directly
    from gemini_integration import generate_solution_steps
    from exporter import export_problems_to_html
except ImportError as e:
    logging.error(f"Error importing modules: {e}")
    # You might want to handle this more gracefully depending on your application's needs
    # For example, by exiting or disabling features that depend on these modules.

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Math Problems API!"

@app.route('/api/problems', methods=['POST'])
def create_problem():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        problem_text = data.get('problem_text')
        problem_type = data.get('problem_type')
        answer = data.get('answer')
        source = data.get('source') # Optional

        if not all([problem_text, problem_type, answer]):
            missing_fields = []
            if not problem_text: missing_fields.append('problem_text')
            if not problem_type: missing_fields.append('problem_type')
            if not answer: missing_fields.append('answer')
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        new_problem = add_problem(problem_text, problem_type, answer, source)
        return jsonify(new_problem), 201

    except Exception as e:
        # Log the exception e for debugging
        logging.exception("Error in create_problem")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/problems', methods=['GET'])
def get_problems():
    try:
        # Retrieve potential filter parameters from request.args
        filter_problem_type = request.args.get('problem_type', None)

        problems = load_problems()

        if filter_problem_type:
            # Perform case-insensitive filtering
            filter_problem_type_lower = filter_problem_type.lower()
            filtered_problems = [
                p for p in problems
                if p.get('problem_type', '').lower() == filter_problem_type_lower
            ]
            problems = filtered_problems # Replace original list with filtered list

        return jsonify(problems), 200
    except Exception as e:
        # Log the exception e for debugging
        logging.exception("Error in get_problems")
        return jsonify({"error": "An unexpected error occurred while retrieving problems"}), 500

@app.route('/api/problems/<problem_id>', methods=['GET'])
def get_problem(problem_id):
    try:
        problem = get_problem_by_id(problem_id)
        if problem:
            return jsonify(problem), 200
        else:
            return jsonify({"error": "Problem not found"}), 404
    except Exception as e:
        # Log the exception e for debugging
        logging.exception(f"Error in get_problem(problem_id={problem_id})")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/problems/<problem_id>/generate_solution', methods=['POST'])
def generate_solution_for_problem(problem_id):
    # 1. Get the problem
    try:
        problem = get_problem_by_id(problem_id)
        if not problem:
            return jsonify({"error": "Problem not found"}), 404
    except Exception as e:
        logging.exception(f"Error retrieving problem {problem_id}")
        return jsonify({"error": f"An error occurred while retrieving problem {problem_id}"}), 500

    problem_text = problem.get('problem_text')
    problem_type = problem.get('problem_type')
    answer = problem.get('answer')

    if not all([problem_text, problem_type, answer]):
        # Note: Answer might be optional for generation, but crucial for a good prompt.
        # Depending on requirements, might allow generation without an answer.
        # For now, keeping it as a required piece of info from the problem itself.
        return jsonify({"error": "Problem data (text, type, answer) is incomplete, cannot generate solution."}), 400

    # Get student_level from request JSON
    student_level = None
    request_data = request.get_json()
    if request_data:
        student_level = request_data.get('student_level')

    # 2. Generate solution steps via Gemini
    try:
        generated_steps = generate_solution_steps(problem_text, problem_type, answer, student_level=student_level)
        if not generated_steps or generated_steps.startswith("Error:"):
            error_detail = generated_steps if generated_steps else "No content from Gemini."
            logging.error(f"Gemini API error for problem {problem_id} (level: {student_level}): {error_detail}")
            return jsonify({
                "error": "Failed to generate solution from Gemini API",
                "details": error_detail
            }), 502 # Bad Gateway, as we depend on an upstream service
    except Exception as e:
        logging.exception(f"Exception calling Gemini API for problem {problem_id}")
        return jsonify({"error": "An unexpected error occurred while generating solution steps"}), 500

    # 3. Update the problem with the generated solution
    try:
        updated_problem_data = update_problem_solution(problem_id, generated_steps)
        if not updated_problem_data:
             # This case might occur if update_problem_solution itself can't find the problem again
             # or if the update operation fails silently (though it should raise an exception ideally)
            logging.error(f"Failed to update problem {problem_id} after generating solution.")
            return jsonify({"error": "Failed to update problem with solution, problem may have been deleted."}), 500
    except Exception as e:
        logging.exception(f"Error updating problem {problem_id} with solution")
        return jsonify({"error": f"An error occurred while updating problem {problem_id} with the solution"}), 500

    # 4. Return the updated problem
    # Re-fetch to ensure we have the absolute latest state, though update_problem_solution might return it.
    # For consistency and to adhere to the subtask (retrieve the updated problem).
    try:
        final_updated_problem = get_problem_by_id(problem_id)
        if not final_updated_problem:
            # Should ideally not happen if update was successful
            logging.error(f"Problem {problem_id} not found after successful update. This is unexpected.")
            return jsonify({"error": "Problem disappeared after update, please check system integrity."}), 500
        return jsonify(final_updated_problem), 200
    except Exception as e:
        logging.exception(f"Error re-retrieving problem {problem_id} after update")
        return jsonify({"error": f"An error occurred retrieving the updated problem {problem_id}"}), 500

@app.route('/api/problems/<problem_id>', methods=['PUT'])
def update_existing_problem(problem_id):
    try:
        all_problems = load_problems()
    except Exception as e:
        logging.exception("Error loading problems for update")
        return jsonify({"error": "Failed to load problem data for update."}), 500

    problem_to_update = None
    problem_idx = -1
    for i, p in enumerate(all_problems):
        if p.get('problem_id') == problem_id: # Corrected 'id' to 'problem_id'
            problem_to_update = p
            problem_idx = i
            break

    if not problem_to_update:
        return jsonify({"error": "Problem not found"}), 404

    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "Invalid JSON payload for update"}), 400
    except Exception as e:
        logging.exception(f"Error getting JSON for update problem {problem_id}")
        return jsonify({"error": "Invalid JSON payload for update"}), 400

    # Fields that can be updated
    updatable_fields = ['problem_text', 'problem_type', 'answer', 'source', 'solution_steps_gemini']
    updated_fields_count = 0

    for field in updatable_fields:
        if field in update_data:
            problem_to_update[field] = update_data[field]
            updated_fields_count +=1

    if updated_fields_count == 0:
        # If only timestamps are updated, this might be an issue.
        # However, the task is to *set* updated_time, implying other fields might not change.
        # For now, let's assume an update request should change at least one of the updatable_fields.
        # If the only change is intended to be 'updated_time', this logic might need adjustment.
        # Given the current structure, updated_time is added regardless.
        pass # No return here if only updated_time is the change.

    # Set/update the updated_time field
    current_time_iso = datetime.now(timezone.utc).isoformat()
    problem_to_update['updated_time'] = current_time_iso
    # Ensure created_time is preserved if it exists, or set if this is an old record format.
    if 'created_time' not in problem_to_update or not problem_to_update['created_time']:
        # This case handles records that might have existed before created_time was introduced
        # and are now being updated. It's a sensible default to set created_time to updated_time
        # if it's missing, assuming this update is the first time it's being "timestamped".
        problem_to_update['created_time'] = current_time_iso

    all_problems[problem_idx] = problem_to_update

    try:
        save_problems(all_problems)
    except Exception as e:
        logging.exception(f"Error saving problems after update for problem_id {problem_id}")
        return jsonify({"error": "Failed to save updated problem data."}), 500

    # Return the modified problem dictionary
    return jsonify(problem_to_update), 200

@app.route('/api/problems/<problem_id>', methods=['DELETE'])
def delete_problem_endpoint(problem_id):
    try:
        deleted_successfully = delete_problem(problem_id)
        if deleted_successfully:
            return jsonify({"message": "Problem deleted successfully"}), 200
        else:
            return jsonify({"error": "Problem not found"}), 404
    except Exception as e:
        logging.exception(f"Error in delete_problem_endpoint for problem_id {problem_id}")
        return jsonify({"error": "An unexpected error occurred during problem deletion"}), 500

@app.route('/api/export/problems', methods=['GET'])
def export_problems_route():
    try:
        # Retrieve query parameters
        filter_type = request.args.get('type', None)
        export_full_str = request.args.get('export_full', 'true').lower()
        export_full_flag = export_full_str == 'true'

        # Load problems
        try:
            all_problems = load_problems()
        except Exception as e:
            logging.exception("Error loading problems for export")
            return jsonify({"error": "Failed to load problem data for export."}), 500

        # Filter problems if type is specified
        problems_to_export = []
        if filter_type:
            for p in all_problems:
                if p.get('problem_type', '').lower() == filter_type.lower():
                    problems_to_export.append(p)
        else:
            problems_to_export = all_problems

        if not problems_to_export:
            return jsonify({"message": "No problems found matching the criteria for export."}), 404

        # Call exporter
        # ASSUMPTION: export_problems_to_html returns the HTML content as a string.
        # If it writes to a file, we'd need to use a temp file and send_file.
        # e.g., temp_filepath = f"/tmp/{uuid.uuid4()}.html"
        #       export_problems_to_html(problems_to_export, output_filename=temp_filepath, export_full=export_full_flag)
        #       return send_file(temp_filepath, as_attachment=True, download_name='problems_export.html', mimetype='text/html')
        #       # Remember to os.remove(temp_filepath) in a finally or after_this_request
        try:
            html_content = export_problems_to_html(problems_to_export, export_full=export_full_flag)
            if not html_content:
                logging.warning("Export function returned empty content.")
                return jsonify({"error": "Failed to generate HTML content for export."}), 500
        except Exception as e:
            logging.exception("Error during HTML export process")
            return jsonify({"error": "An unexpected error occurred during the export process."}), 500

        # Create and return response
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = 'attachment; filename="problems_export.html"'
        return response, 200

    except Exception as e:
        # Catch-all for any other unexpected errors
        logging.exception("Unexpected error in export_problems_route")
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    # Consider whether to run with debug=True in production or rely on logging
    logging.info("Starting Flask app")
    app.run(debug=True) # Set debug=False for production
