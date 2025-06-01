// frontend/pages/problems/[id].tsx
    import React, { useEffect, useState } from 'react';
    import { useRouter } from 'next/router';
    import Head from 'next/head';
    import Link from 'next/link';
    import ProblemDetail from '../../components/ProblemDetail'; // Adjusted path

    // TODO: Move ProblemData to a shared types file and import it here and in ProblemDetail.tsx
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

    const ProblemDetailPage: React.FC = () => { // Added React.FC type for consistency
        const [problem, setProblem] = useState<ProblemData | null>(null);
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState<string | null>(null);
        const [generatingSolution, setGeneratingSolution] = useState(false);
        const router = useRouter();
        const { id } = router.query; // Get problem_id from URL

        useEffect(() => {
            if (id && typeof id === 'string') { // Ensure id is a string
                setIsLoading(true);
                setError(null);
                fetch(`/api/problems/${id}`)
                    .then(res => {
                        if (!res.ok) {
                            if (res.status === 404) throw new Error('Problem not found');
                            throw new Error(`Failed to fetch problem: ${res.statusText}`);
                        }
                        return res.json();
                    })
                    .then(data => {
                        setProblem(data);
                    })
                    .catch(err => {
                         if (err instanceof Error) {
                            setError(err.message);
                        } else {
                            setError('An unknown error occurred');
                        }
                        setProblem(null);
                    })
                    .finally(() => setIsLoading(false));
            } else if (router.isReady && !id) { // Handle case where id might be undefined initially but router is ready
                setIsLoading(false);
                setError("Problem ID is missing in the URL.");
            }
        }, [id, router.isReady]); // Added router.isReady to dependencies

        const handleGenerateSolution = async (problemId: string, studentLevel: string) => {
            if (!problemId) return;
            setGeneratingSolution(true);
            setError(null);
            try {
                const response = await fetch(`/api/problems/${problemId}/generate_solution`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ student_level: studentLevel }),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `Failed to generate solution: ${response.statusText}`);
                }
                const updatedProblem = await response.json();
                setProblem(updatedProblem); // Update problem data with the new solution
            } catch (err) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError('An unknown error occurred while generating solution.');
                }
            } finally {
                setGeneratingSolution(false);
            }
        };

        // Display loading state until router.isReady and id is processed
        if (isLoading || !router.isReady) return <p>Loading problem details...</p>;
        if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
        // If id is definitely processed and still no problem, and no error, then it's likely not found.
        if (!problem) return <p>Problem data is not available or problem not found.</p>;

        return (
            <div>
                <Head>
                    <title>Problem: {problem?.problem_id || 'Detail'}</title>
                </Head>
                <main>
                    <Link href="/">Back to Problem List</Link>
                    <ProblemDetail
                        problem={problem}
                        onGenerateSolution={handleGenerateSolution}
                        generatingSolution={generatingSolution}
                    />
                </main>
                 <style jsx>{`
                    main {
                        padding: 2rem;
                        font-family: sans-serif;
                    }
                `}</style>
            </div>
        );
    };

    export default ProblemDetailPage;
