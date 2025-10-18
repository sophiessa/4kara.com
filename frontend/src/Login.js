// frontend/src/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './api';

// Import MUI components
import { Container, Box, TextField, Button, Typography, Alert, Divider } from '@mui/material';
import GoogleLoginButton from './GoogleLoginButton';


function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await api.post('/api/users/login/', {
                username,
                password,
            });
            
            const { token, user } = response.data;
            
            localStorage.setItem('authToken', token);
            localStorage.setItem('user', JSON.stringify(user));
            
            navigate('/jobs');
            window.location.reload();

        } catch (err) {
            console.error('Login failed:', err);
            setError('Login failed. Please check your username and password.');
        }
    };

    return (
        // Container centers the content and sets a max-width.
        <Container component="main" maxWidth="xs">
            {/* Box is a generic container for layout. We use it to create the form structure. */}
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                {/* Typography is used for all text elements. */}
                <Typography component="h1" variant="h5">
                    Sign In
                </Typography>

                <Box sx={{ mt: 3, mb: 2, width: '100%', display: 'flex', justifyContent: 'center' }}>
                    <GoogleLoginButton />
                </Box>

                <Divider sx={{ width: '100%' }}>OR</Divider>
                {/* We use Box for the form element itself to attach the onSubmit handler. */}
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                    {/* TextField is the MUI equivalent of an <input> tag. */}
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="username"
                        label="Username"
                        name="username"
                        autoComplete="username"
                        autoFocus
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Password"
                        type="password"
                        id="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                
                    {/* Button provides styled buttons with ripple effects. */}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Sign In
                    </Button>
                    {/* Use the Alert component for displaying errors. */}
                    {error && <Alert severity="error">{error}</Alert>}

                    
                </Box>
            </Box>
        </Container>
    );
}

export default Login;