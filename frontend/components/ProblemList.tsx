// frontend/components/ProblemList.tsx
    import React from 'react';

    interface Problem {
        problem_id: string;
        problem_text: string;
        problem_type: string;
    }

    interface ProblemListProps {
        problems: Problem[];
    }

    const ProblemList: React.FC<ProblemListProps> = ({ problems }) => {
        if (!problems || problems.length === 0) {
            return <p>No problems to display.</p>;
        }

        return (
            <div>
                <h2>Problem List</h2>
                <ul>
                    {problems.map((problem) => (
                        <li key={problem.problem_id}>
                            <a href={`/problems/${problem.problem_id}`}>
                                {problem.problem_text} ({problem.problem_type})
                            </a>
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    export default ProblemList;
