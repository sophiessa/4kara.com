import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './api';

import { Container, Box, TextField, Button, Typography, Alert } from '@mui/material';

function JobCreate() {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [streetAddress, setStreetAddress] = useState('');
    const [city, setCity] = useState('');
    const [state, setState] = useState('');
    const [zipCode, setZipCode] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const token = localStorage.getItem('authToken');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!token) {
            setError("You must be logged in to post a job.");
            return;
        }

        try {
            await api.post('/api/jobs/create/', {
                title,
                description,
                street_address: streetAddress,
                city,
                state,
                zip_code: zipCode
            }, {
                headers: {
                    'Authorization': `Token ${token}`
                }
            });

            navigate('/my-jobs');

        } catch (err) {
            console.error('Job creation failed:', err);
            setError('Job creation failed. Please try again.');
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
                    Post a New Job
                </Typography>
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="title"
                        label="Title"
                        name="title"
                        autoComplete="title"
                        autoFocus
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="description"
                        label="Description"
                        name="description"
                        multiline
                        rows={4}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="streetAddress"
                        label="Street Address"
                        name="street_address"
                        autoComplete="street-address"
                        value={streetAddress}
                        onChange={(e) => setStreetAddress(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="city"
                        label="City"
                        name="city"
                        autoComplete="address-level2"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="state"
                        label="State"
                        name="state"
                        autoComplete="address-level1"
                        value={state}
                        onChange={(e) => setState(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="zipCode"
                        label="ZIP Code"
                        name="zip_code"
                        autoComplete="postal-code"
                        value={zipCode}
                        onChange={(e) => setZipCode(e.target.value)}
                    />
                    {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Post Job
                    </Button>
                </Box>
            </Box>
        </Container>
    );
}

export default JobCreate;