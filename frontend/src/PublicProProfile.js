import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from './api';
import { Container, Box, Typography, Paper, Avatar, CircularProgress, Alert } from '@mui/material';

function PublicProProfile() {
    const { userId } = useParams(); 
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await api.get(`/api/profiles/pro/${userId}/`);
                setProfile(response.data);
            } catch (err) {
                setError('Could not load profile. The user may not be a professional or the profile does not exist.');
                console.error("Fetch public profile error:", err.response);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [userId]);

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Alert severity="error">{error}</Alert>;
    }

    if (!profile) {
        return <Typography>Profile not found.</Typography>;
    }

    return (
        <Container maxWidth="md">
            <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar
                        alt={profile.first_name + ' ' + profile.last_name|| 'Professional'}
                        src={profile.profile_picture_url || '/default-avatar.png'} 
                        sx={{ width: 80, height: 80, mr: 2 }}
                    />
                    <Typography variant="h4" component="h1">
                        {profile.first_name + ' ' + profile.last_name|| 'Professional Profile'}
                    </Typography>
                </Box>
                <Typography variant="h6" gutterBottom>About</Typography>
                <Typography paragraph>{profile.bio || 'No bio provided.'}</Typography>

                <Typography variant="h6" gutterBottom>Service Area</Typography>
                <Typography paragraph>{profile.service_area_zip_codes || 'Not specified.'}</Typography>

                {/* Optional: Add link back or other actions */}
            </Paper>
        </Container>
    );
}

export default PublicProProfile;