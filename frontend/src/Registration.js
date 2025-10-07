// frontend/src/Registration.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Container, Box, TextField, Button, Typography, Alert, FormControlLabel, Checkbox } from '@mui/material';

function Registration() {
    // State for each form field
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    // The is_pro flag defaults to false (a Customer)
    const [isPro, setIsPro] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const userData = {
            username,
            email,
            password,
            is_pro: isPro,
        };

        try {
            // Post the new user data to the registration endpoint
            await axios.post('http://127.0.0.1:8000/api/users/register/', userData);
            
            // On success, redirect the user to the login page
            navigate('/login');

        } catch (err) {
            console.error('Registration failed:', err.response.data);
            // Concatenate error messages from the backend for display
            const errorData = err.response.data;
            const errorMessages = Object.keys(errorData).map(key => `${key}: ${errorData[key].join(' ')}`).join('; ');
            setError(`Registration failed: ${errorMessages}`);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Typography component="h1" variant="h5">
                    Register
                </Typography>
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
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
                        id="email"
                        label="Email"
                        name="email"
                        autoComplete="email"
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
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={isPro}
                                onChange={(e) => setIsPro(e.target.checked)}
                            />
                        }
                        label="I am a professional"
                    />
                    {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Register
                    </Button>
                </Box>
            </Box>
        </Container>
    );
}

export default Registration;