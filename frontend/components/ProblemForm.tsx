// frontend/components/ProblemForm.tsx
    import React, { useState } from 'react';

    const ProblemForm: React.FC = () => {
        const [problemText, setProblemText] = useState('');
        const [problemType, setProblemType] = useState('');
        const [answer, setAnswer] = useState('');
        const [source, setSource] = useState('');

        const handleSubmit = async (event: React.FormEvent) => {
            event.preventDefault();
            // Basic validation
            if (!problemText.trim() || !problemType.trim() || !answer.trim()) {
                alert('Problem text, type, and answer are required.');
                return;
            }
            try {
                const response = await fetch('/api/problems', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ problem_text: problemText, problem_type: problemType, answer, source }),
                });
                if (response.ok) {
                    alert('Problem added successfully!');
                    setProblemText('');
                    setProblemType('');
                    setAnswer('');
                    setSource('');
                    // Optionally, trigger a refresh of the problem list here
                } else {
                    const errorData = await response.json();
                    alert(`Failed to add problem: ${errorData.error || response.statusText}`);
                }
            } catch (error) {
                console.error('Error submitting problem:', error);
                alert('An error occurred while submitting the problem.');
            }
        };

        return (
            <form onSubmit={handleSubmit}>
                <h2>Add New Problem</h2>
                <div>
                    <label htmlFor="problemText">Problem Text:</label>
                    <textarea
                        id="problemText"
                        value={problemText}
                        onChange={(e) => setProblemText(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="problemType">Problem Type:</label>
                    <input
                        type="text"
                        id="problemType"
                        value={problemType}
                        onChange={(e) => setProblemType(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="answer">Answer:</label>
                    <input
                        type="text"
                        id="answer"
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="source">Source (Optional):</label>
                    <input
                        type="text"
                        id="source"
                        value={source}
                        onChange={(e) => setSource(e.target.value)}
                    />
                </div>
                <button type="submit">Add Problem</button>
            </form>
        );
    };

    export default ProblemForm;
