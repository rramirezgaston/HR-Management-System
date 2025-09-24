import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Layout from './components/Layout';
import JobsPage from './pages/JobsPage';
import CandidatesPage from './pages/CandidatesPage';
import HiringClassesPage from './pages/HiringClassesPage';

// Define the application's routes
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />, // The Layout component is the parent for all pages
    children: [
      {
        path: 'jobs', // Renders at /jobs
        element: <JobsPage />,
      },
      {
        path: 'candidates', // Renders at /candidates
        element: <CandidatesPage />,
      },
      {
        path: 'hiring-classes', // Renders at /hiring-classes
        element: <HiringClassesPage />,
      }
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;