// frontend/src/EditProProfile.js
import React, { useState, useEffect } from 'react';
import api from './api';
import { useNavigate } from 'react-router-dom';
import { Container, Box, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';

function EditProProfile() {
    const [profile, setProfile] = useState({
        bio: '',
        service_area_zip_codes: '',
        profile_picture_url: '',
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();
    const token = localStorage.getItem('authToken');

    useEffect(() => {
        if (!token) {
            navigate('/login'); // Redirect if not logged in
            return;
        }

        const fetchProfile = async () => {
            try {
                const response = await api.get('/api/profile/pro/', {
                    headers: { 'Authorization': `Token ${token}` }
                });
                setProfile(response.data); // Load existing profile data
            } catch (err) {
                setError('Failed to load profile.');
                console.error("Fetch profile error:", err.response);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [token, navigate]);

    const handleChange = (e) => {
        setProfile({
            ...profile,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            // Use PUT or PATCH to update the profile
            const response = await api.patch('/api/profile/pro/', profile, {
                headers: { 'Authorization': `Token ${token}` }
            });
            setSuccess(response.data.message || 'Profile updated successfully!');
            // Optionally update the local profile state again if needed
            setProfile(response.data.data || profile);
        } catch (err) {
            setError('Failed to update profile. Please try again.');
            console.error("Update profile error:", err.response);
        } finally {
            setLoading(false);
        }
    };

    if (loading && !profile.bio) { // Show loading only on initial load
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    return (
        <Container component="main" maxWidth="md">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Typography component="h1" variant="h5">
                    Edit Your Professional Profile
                </Typography>
                {error && <Alert severity="error" sx={{ width: '100%', mt: 2 }}>{error}</Alert>}
                {success && <Alert severity="success" sx={{ width: '100%', mt: 2 }}>{success}</Alert>}
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3, width: '100%' }}>
                    <TextField
                        margin="normal"
                        fullWidth
                        id="bio"
                        label="Bio / Description of Services"
                        name="bio"
                        multiline
                        rows={4}
                        value={profile.bio || ''}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="normal"
                        fullWidth
                        id="service_area_zip_codes"
                        label="Service Area Zip Codes (comma-separated)"
                        name="service_area_zip_codes"
                        value={profile.service_area_zip_codes || ''}
                        onChange={handleChange}
                        helperText="e.g., 75201, 75205, 75206"
                    />
                    <TextField
                        margin="normal"
                        fullWidth
                        id="profile_picture_url"
                        label="Profile Picture URL"
                        name="profile_picture_url"
                        type="url"
                        value={profile.profile_picture_url || ''}
                        onChange={handleChange}
                        helperText="Link to an image hosted online (e.g., Imgur, Cloudinary)"
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                        disabled={loading} // Disable button while submitting
                    >
                        {loading ? <CircularProgress size={24} /> : 'Save Profile'}
                    </Button>
                </Box>
            </Box>
        </Container>
    );
}

export default EditProProfile;