// frontend/src/Login.js
import React, { useState } from 'react';
import api from './api';
import { useNavigate } from 'react-router-dom';
import { Container, Box, TextField, Button, Typography, Alert, Divider } from '@mui/material';
import GoogleLoginButton from './GoogleLoginButton';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await api.post('/api/users/login/', {
                email: email,
                password,
            });
            console.log("Login API Response:", response.data);

            const token = response.data.key;
            const user = response.data.user;

            if (token) {
            localStorage.setItem('authToken', token);
            } else {
                console.error("Auth token missing in login response!");
                setError("Login failed: Could not retrieve token.");
                return;
            }
            if (user && typeof user === 'object') {
            localStorage.setItem('user', JSON.stringify(user));
            console.log("Stored user data:", user);
            } else {
                console.warn("User object not in login response. Fetching separately...");
                try {
                    const userDetailsResponse = await api.get('/dj-rest-auth/user/', {
                        headers: { 'Authorization': `Token ${token}` }
                    });
                    if (userDetailsResponse.data && typeof userDetailsResponse.data === 'object') {
                        localStorage.setItem('user', JSON.stringify(userDetailsResponse.data));
                        console.log("Stored user data after separate fetch:", userDetailsResponse.data);
                    } else {
                        console.error("Failed to fetch valid user details after login.");
                        localStorage.removeItem('user');
                    }
                } catch (fetchErr) {
                    console.error("Error fetching user details after login:", fetchErr);
                    localStorage.removeItem('user');
                }
            }

            navigate('/jobs');
            window.location.reload();

        } catch (err) {
            console.error('Login failed:', err.response?.data || err.message);
            const errorData = err.response?.data || {};
            let errorMessages = [];
             if (errorData.non_field_errors) { 
                errorMessages = errorData.non_field_errors;
             } else if (typeof errorData === 'object' && errorData !== null) {
                errorMessages = Object.keys(errorData).map(key => `${key}: ${Array.isArray(errorData[key]) ? errorData[key].join(' ') : errorData[key]}`);
             } else {
                 errorMessages.push('Login failed. Please check credentials or verify your email.');
             }
            setError(errorMessages.join('; '));
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }} >
                <Typography component="h1" variant="h5"> Sign In </Typography>
                <Box sx={{ mt: 3, mb: 2, width: '100%', display: 'flex', justifyContent: 'center' }}>
                    <GoogleLoginButton />
                </Box>
                <Divider sx={{ width: '100%' }}>OR</Divider>
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="email" 
                        label="Email Address" 
                        name="email"
                        autoComplete="email"
                        autoFocus
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
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
                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>
                        Sign In
                    </Button>
                    {error && <Alert severity="error">{error}</Alert>}
                </Box>
            </Box>
        </Container>
    );
}

export default Login;