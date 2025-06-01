// frontend/components/ProblemDetail.tsx
    import React from 'react';

    interface ProblemData {
        problem_id: string;
        problem_text: string;
        problem_type: string;
        answer: string;
        source?: string;
        solution_steps_gemini?: string;
        created_time?: string;
        updated_time?: string;
    }

    interface ProblemDetailProps {
        problem: ProblemData | null;
        onGenerateSolution: (problemId: string, studentLevel: string) => void; // Added studentLevel
        generatingSolution: boolean; // To disable button while generating
    }

    const ProblemDetail: React.FC<ProblemDetailProps> = ({ problem, onGenerateSolution, generatingSolution }) => {
        const [studentLevel, setStudentLevel] = React.useState('Elementary'); // Default student level

        if (!problem) {
            return <p>Problem not found or loading...</p>;
        }

        const handleGenerateClick = () => {
            if (problem && !generatingSolution) {
                onGenerateSolution(problem.problem_id, studentLevel);
            }
        };

        return (
            <div>
                <h2>Problem Details</h2>
                <p><strong>ID:</strong> {problem.problem_id}</p>
                <p><strong>Text:</strong> {problem.problem_text}</p>
                <p><strong>Type:</strong> {problem.problem_type}</p>
                <p><strong>Answer:</strong> {problem.answer}</p>
                {problem.source && <p><strong>Source:</strong> {problem.source}</p>}

                <h3>Solution Steps (Gemini)</h3>
                {problem.solution_steps_gemini ? (
                    <div dangerouslySetInnerHTML={{ __html: problem.solution_steps_gemini.replace(/\n/g, '<br />') }} />
                ) : (
                    <p>No solution steps generated yet.</p>
                )}

                <div>
                    <label htmlFor="studentLevel">Student Level for Solution:</label>
                    <select
                        id="studentLevel"
                        value={studentLevel}
                        onChange={(e) => setStudentLevel(e.target.value)}
                        disabled={generatingSolution}
                    >
                        <option value="Elementary">Elementary</option>
                        <option value="Middle School">Middle School</option>
                        <option value="High School">High School</option>
                    </select>
                    <button
                        onClick={handleGenerateClick}
                        disabled={generatingSolution || !!problem.solution_steps_gemini}
                    >
                        {generatingSolution ? 'Generating...' : (problem.solution_steps_gemini ? 'Solution Generated' : 'Generate Solution Steps')}
                    </button>
                </div>

                {problem.created_time && <p><small>Created: {new Date(problem.created_time).toLocaleString()}</small></p>}
                {problem.updated_time && <p><small>Last Updated: {new Date(problem.updated_time).toLocaleString()}</small></p>}
            </div>
        );
    };

    export default ProblemDetail;
