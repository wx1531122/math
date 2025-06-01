# Frontend Application (Next.js)

This directory contains the Next.js frontend for the Math Problem Assistant.

## Prerequisites

*   Node.js (v16.x or later recommended)
*   npm or yarn

## Getting Started

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    Using npm:
    ```bash
    npm install
    ```
    Or using yarn:
    ```bash
    yarn install
    ```

3.  **Run the development server:**
    Using npm:
    ```bash
    npm run dev
    ```
    Or using yarn:
    ```bash
    yarn dev
    ```
    This will typically start the development server on `http://localhost:3000`.

4.  **Build for production:**
    Using npm:
    ```bash
    npm run build
    ```
    Or using yarn:
    ```bash
    yarn build
    ```
    And to start the production server:
    Using npm:
    ```bash
    npm start
    ```
    Or using yarn:
    ```bash
    yarn start
    ```

## Project Structure

*   `pages/`: Contains the application's pages.
    *   `index.tsx`: The main page, displaying the problem list and form to add new problems.
    *   `problems/[id].tsx`: The detail page for a single problem, including solution generation.
*   `components/`: Contains reusable React components.
    *   `ProblemList.tsx`: Component to display the list of problems.
    *   `ProblemForm.tsx`: Component for the new problem input form.
    *   `ProblemDetail.tsx`: Component to display the details of a specific problem.
*   `public/`: Static assets can be placed here.

## API Interaction

The frontend interacts with the Python Flask backend API (assumed to be running, typically on a different port like `http://localhost:5000` or `http://localhost:8000`).

-   Fetching problems: `GET /api/problems`
-   Adding a problem: `POST /api/problems`
-   Fetching a single problem: `GET /api/problems/<problem_id>`
-   Generating solution steps: `POST /api/problems/<problem_id>/generate_solution`
-   Exporting problems: `GET /api/export/problems`

Make sure the backend server is running and accessible by the frontend. If the backend is on a different port, you might need to configure proxying in `next.config.js` for local development to avoid CORS issues, or ensure the backend API has CORS enabled. For simplicity in this initial setup, the components use relative paths for API calls (e.g., `/api/problems`), assuming the Next.js app can proxy these requests to the backend or is served under the same domain in production.
