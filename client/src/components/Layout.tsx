import { Outlet, Link } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';

export default function Layout() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* AppBar is the main navigation bar */}
      <AppBar position="static">
        <Toolbar>
          {/* Typography is for styled text */}
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            HR Management System
          </Typography>

          {/* Use MUI Buttons that act as React Router Links */}
          <Button color="inherit" component={Link} to="/jobs">Jobs</Button>
          <Button color="inherit" component={Link} to="/candidates">Candidates</Button>
          <Button color="inherit" component={Link} to="/hiring-classes">Hiring Classes</Button>
          <Button color="inherit" component={Link} to="/interviewers">Interviewers</Button>
          <Button color="inherit" component={Link} to="/applicant-tracker">Applicant Tracker</Button>
        </Toolbar>
      </AppBar>

      {/* Container centers and adds padding to our main content */}
      <Container component="main" sx={{ mt: 4, mb: 4 }}>
        <Outlet /> {/* Child pages will be rendered here */}
      </Container>
    </Box>
  );
}