// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link as RouterLink, Navigate } from 'react-router-dom';
// Import the necessary MUI components
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';

import JobList from './JobList';
import Login from './Login';
import Registration from './Registration';
import JobCreate from './JobCreate';
import JobDetail from './JobDetail';
import './App.css';

function App() {
    const token = localStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user'));

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login'; // Redirect cleanly after logout
    };

    return (
        <Router>
            {/* The AppBar provides the main navigation header */}
            <AppBar position="static">
                {/* Toolbar handles the horizontal layout of items */}
                <Toolbar>
                    {/* Typography for the site title. The sx prop is for custom styling. */}
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        <RouterLink to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                            4kara
                        </RouterLink>
                    </Typography>
                    
                    {/* We use MUI Buttons that act as Links */}
                    <Button color="inherit" component={RouterLink} to="/jobs">Jobs</Button>
                    
                    {user && !user.is_pro && (
                         <Button color="inherit" component={RouterLink} to="/jobs/create">Post Job</Button>
                    )}

                    {token ? (
                        <Button color="inherit" onClick={handleLogout}>Logout</Button>
                    ) : (
                        <>
                            <Button color="inherit" component={RouterLink} to="/register">Register</Button>
                            <Button color="inherit" component={RouterLink} to="/login">Login</Button>
                        </>
                    )}
                </Toolbar>
            </AppBar>

            {/* Container provides consistent padding and centering for the page content. */}
            <Container component="main" sx={{ mt: 4, mb: 4 }}>
                <Routes>
                    <Route path="/" element={token ? <Navigate to="/jobs" /> : <Navigate to="/login" />} />
                    <Route path="/jobs" element={<JobList />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Registration />} />
                    <Route path="/jobs/create" element={<JobCreate />} />
                    <Route path="/jobs/:jobId" element={<JobDetail />} />
                </Routes>
            </Container>
        </Router>
    );
}

export default App;