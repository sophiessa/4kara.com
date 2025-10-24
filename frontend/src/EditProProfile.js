import React, { useState, useEffect } from 'react';
import api from './api';
import { useNavigate } from 'react-router-dom';
import { Container, Box, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';

function EditProProfile() {
    const [profile, setProfile] = useState({
        bio: '',
        service_area_zip_codes: '',
        profile_picture_url: '',
        years_experience: '', 
        instagram_url: '',    
        facebook_url: '',     
        twitter_url: '',      
        personal_website_url: '', 
        services_offered: '', 
        availability: '', 
        faq: '',             
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();
    const token = localStorage.getItem('authToken');

    useEffect(() => {
        if (!token) {
            navigate('/login');
            return;
        }
        const fetchProfile = async () => {
            try {
                const response = await api.get('/api/profile/pro/', {
                    headers: { 'Authorization': `Token ${token}` }
                });
                setProfile({
                    bio: response.data.bio || '',
                    service_area_zip_codes: response.data.service_area_zip_codes || '',
                    profile_picture_url: response.data.profile_picture_url || '',
                    years_experience: response.data.years_experience || '',
                    instagram_url: response.data.instagram_url || '',
                    facebook_url: response.data.facebook_url || '',
                    twitter_url: response.data.twitter_url || '',
                    personal_website_url: response.data.personal_website_url || '',
                    services_offered: response.data.services_offered || '',
                    availability: response.data.availability || '',
                    faq: response.data.faq || '',
                });
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
        const { name, value } = e.target;
        const processedValue = name === 'years_experience' ? (value === '' ? null : parseInt(value, 10)) : value;
        if (name === 'years_experience' && isNaN(processedValue) && value !== '') return;

        setProfile(prevProfile => ({
            ...prevProfile,
            [name]: processedValue,
        }));
    };


    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        const dataToSubmit = {
            ...profile,
            years_experience: profile.years_experience === '' ? null : profile.years_experience,
        };


        try {
            const response = await api.patch('/api/profile/pro/', dataToSubmit, {
                headers: { 'Authorization': `Token ${token}` }
            });
            setSuccess(response.data.message || 'Profile updated successfully!');
            setProfile(response.data.data || dataToSubmit);
        } catch (err) {
            setError('Failed to update profile. Please try again.');
            console.error("Update profile error:", err.response);
        } finally {
            setLoading(false);
        }
    };

    if (loading && !profile.bio && !profile.years_experience) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    return (
        <Container component="main" maxWidth="md">
            <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5"> Edit Your Professional Profile </Typography>
                {error && <Alert severity="error" sx={{ width: '100%', mt: 2 }}>{error}</Alert>}
                {success && <Alert severity="success" sx={{ width: '100%', mt: 2 }}>{success}</Alert>}
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3, width: '100%' }}>
                    <TextField margin="normal" fullWidth id="bio" label="Bio / Description of Services" name="bio" multiline rows={4} value={profile.bio} onChange={handleChange} />
                    <TextField margin="normal" fullWidth id="service_area_zip_codes" label="Service Area Zip Codes (comma-separated)" name="service_area_zip_codes" value={profile.service_area_zip_codes} onChange={handleChange} helperText="e.g., 75201, 75205" />
                    <TextField margin="normal" fullWidth id="profile_picture_url" label="Profile Picture URL" name="profile_picture_url" type="url" value={profile.profile_picture_url} onChange={handleChange} helperText="Link to an image (e.g., Imgur)" />
                    <TextField margin="normal" fullWidth id="years_experience" label="Years of Experience" name="years_experience" type="number" value={profile.years_experience ?? ''} onChange={handleChange} InputProps={{ inputProps: { min: 0 } }} />
                    <TextField margin="normal" fullWidth id="services_offered" label="Services Offered" name="services_offered" multiline rows={3} value={profile.services_offered} onChange={handleChange} helperText="Describe your main services." />
                    <TextField margin="normal" fullWidth id="availability" label="Availability" name="availability" value={profile.availability} onChange={handleChange} helperText="e.g., Weekdays 9am-5pm" />
                    <TextField margin="normal" fullWidth id="personal_website_url" label="Personal Website URL" name="personal_website_url" type="url" value={profile.personal_website_url} onChange={handleChange} />
                    <TextField margin="normal" fullWidth id="instagram_url" label="Instagram URL" name="instagram_url" type="url" value={profile.instagram_url} onChange={handleChange} />
                    <TextField margin="normal" fullWidth id="facebook_url" label="Facebook URL" name="facebook_url" type="url" value={profile.facebook_url} onChange={handleChange} />
                    <TextField margin="normal" fullWidth id="twitter_url" label="Twitter/X URL" name="twitter_url" type="url" value={profile.twitter_url} onChange={handleChange} />
                    <TextField margin="normal" fullWidth id="faq" label="FAQ" name="faq" multiline rows={4} value={profile.faq} onChange={handleChange} helperText="Optional Q&A section."/>
                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }} disabled={loading} >
                        {loading ? <CircularProgress size={24} /> : 'Save Profile'}
                    </Button>
                </Box>
            </Box>
        </Container>
    );
}

export default EditProProfile;