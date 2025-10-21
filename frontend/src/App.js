import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link as RouterLink } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';

import JobList from './JobList';
import Login from './Login';
import Registration from './Registration';
import JobCreate from './JobCreate';
import JobDetail from './JobDetail';
import MyJobs from './MyJobs';
import ConversationPage from './ConversationPage';
import MyWorkPage from './MyWorkPage';
import ChatInterface from './ChatInterface';
import EditProProfile from './EditProProfile';
import PublicProProfile from './PublicProProfile';

import './App.css';

function App() {
    const token = localStorage.getItem('authToken');
    let user = null;
    const userItem = localStorage.getItem('user');
    if (userItem !== null && typeof userItem !== 'undefined') {
        try {
            if (userItem !== "undefined") {
                 user = JSON.parse(userItem);
            } else {
                 localStorage.removeItem('user');
            }
        } catch (error) {
            localStorage.removeItem('user');
            user = null;
        }
    } else {
         console.log("[DEBUG] No user item found or item was null/undefined.");
    }

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
    };

    return (
        <Router>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        <RouterLink to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                            4KARA LLC
                        </RouterLink>
                    </Typography>
                    {user && (
                        <Typography sx={{ mr: 2 }}>Welcome {user.full_name}</Typography>
                    )}
                    
                    {user && user.is_pro && (
                        <>
                            <Button color="inherit" component={RouterLink} to="/jobs">Browse Jobs</Button>
                            <Button color="inherit" component={RouterLink} to="/my-work">My Work</Button>
                            <Button color="inherit" component={RouterLink} to="/profile/edit">My Profile</Button>
                        </>
                    )}
                    
                    {/* Conditional links for Customers */}
                    {user && !user.is_pro && (
                         <>
                            {/* The new "My Jobs" link */}
                            <Button color="inherit" component={RouterLink} to="/my-jobs">My Jobs</Button>
                            <Button color="inherit" component={RouterLink} to="/jobs/create">Post Job</Button>
                         </>
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
            
            <Container component="main" sx={{ mt: 4, mb: 4 }}>
                <Routes>
                    <Route path="/" element={<ChatInterface />} />
                    <Route path="/jobs" element={<JobList />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Registration />} />
                    <Route path="/jobs/create" element={<JobCreate />} />
                    <Route path="/jobs/:jobId" element={<JobDetail />} />
                    <Route path="/my-jobs" element={<MyJobs />} />
                    <Route path="/jobs/:jobId/conversation" element={<ConversationPage />} />
                    <Route path="/my-work" element={<MyWorkPage />} />
                    <Route path="/profile/edit" element={<EditProProfile />} />
                    <Route path="/profile/:userId" element={<PublicProProfile />} />
                    <Route path="/auth/email-verified" element={<Typography variant="h5" align="center">Email successfully verified! You can now log in.</Typography>} />
                    <Route path="/auth/verification-error" element={<Typography variant="h5" align="center">Email verification failed or link expired. Please request a new verification email.</Typography>} />
                </Routes>
            </Container>
        </Router>
    );
}

export default App;