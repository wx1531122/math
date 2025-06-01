// frontend/pages/index.tsx
    import React, { useEffect, useState } from 'react';
    import ProblemList from '../components/ProblemList';
    import ProblemForm from '../components/ProblemForm';
    import Head from 'next/head';

    interface Problem {
        problem_id: string;
        problem_text: string;
        problem_type: string;
        // Add other fields if your ProblemList component expects them for linking or display
    }

    const HomePage: React.FC = () => {
        const [problems, setProblems] = useState<Problem[]>([]);
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState<string | null>(null);

        const fetchProblems = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await fetch('/api/problems'); // Assuming API is proxied or on same domain
                if (!response.ok) {
                    throw new Error(`Failed to fetch problems: ${response.statusText}`);
                }
                const data = await response.json();
                setProblems(data);
            } catch (err) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError('An unknown error occurred');
                }
                setProblems([]); // Clear problems on error
            } finally {
                setIsLoading(false);
            }
        };

        useEffect(() => {
            fetchProblems();
        }, []);

        // Callback to refresh problems after a new one is added
        const handleProblemAdded = () => {
            fetchProblems(); // Re-fetch the list of problems
        };

        // A simple export button
        const handleExport = () => {
            // Triggers download of all problems, full details
            window.location.href = '/api/export/problems?export_full=true';
        };


        return (
            <div>
                <Head>
                    <title>Math Problem Manager</title>
                    <meta name="description" content="Manage and generate math problems" />
                    <link rel="icon" href="/favicon.ico" /> {/* Placeholder, add favicon later */}
                </Head>

                <main>
                    <h1>Math Problem Manager</h1>

                    <ProblemForm /> {/* We can enhance ProblemForm to call handleProblemAdded */}

                    {/* Add a button or mechanism inside ProblemForm to call handleProblemAdded,
                        or pass handleProblemAdded as a prop to ProblemForm if it needs to trigger refresh from child.
                        For now, a manual refresh button could be an option or rely on user manually refreshing.
                        A better UX would be automatic refresh.
                    */}
                    <button onClick={fetchProblems} disabled={isLoading}>
                        {isLoading ? 'Refreshing Problems...' : 'Refresh Problem List'}
                    </button>
                     <button onClick={handleExport} style={{ marginLeft: '10px' }}>
                        Export All Problems (HTML)
                    </button>

                    {isLoading && <p>Loading problems...</p>}
                    {error && <p style={{ color: 'red' }}>Error fetching problems: {error}</p>}
                    {!isLoading && !error && <ProblemList problems={problems} />}
                </main>

                <footer>
                    {/* Basic footer */}
                    <p>© {new Date().getFullYear()} Math Problem Assistant</p>
                </footer>

                {/* Basic styling - consider moving to a global CSS file or using Tailwind */}
                <style jsx>{`
                    main {
                        padding: 2rem;
                        font-family: sans-serif;
                    }
                    h1 {
                        color: #333;
                    }
                    footer {
                        text-align: center;
                        padding: 1rem;
                        border-top: 1px solid #eee;
                    }
                `}</style>
            </div>
        );
    };

    export default HomePage;
