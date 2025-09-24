import { Outlet, Link } from 'react-router-dom';

export default function Layout() {
  return (
    <div>
      <h1>HR Management System</h1>
      <nav>
        <Link to="/jobs" style={{ marginRight: '10px' }}>Jobs</Link>
        <Link to="/candidates">Candidates</Link>
        <Link to="/interviewers" style={{ margin: '0 10px' }}>Interviewers</Link>
        <Link to="/hiring-classes">Hiring Classes</Link>
      </nav>
      <hr />
      <main>
        <Outlet /> {/* Child pages will be rendered here */}
      </main>
    </div>
  );
}