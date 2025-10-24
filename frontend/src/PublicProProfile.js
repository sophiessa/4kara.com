import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from './api';
import { Container, Box, Typography, Paper, Avatar, CircularProgress, Alert, Grid, Link, Divider, Rating , List, ListItem, ListItemText} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import LinkIcon from '@mui/icons-material/Link';
import InstagramIcon from '@mui/icons-material/Instagram';
import FacebookIcon from '@mui/icons-material/Facebook';
import TwitterIcon from '@mui/icons-material/Twitter'; 

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
                setError('Could not load profile.');
                console.error("Fetch public profile error:", err.response);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [userId]);

    if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    if (error) return <Alert severity="error">{error}</Alert>;
    if (!profile) return <Typography>Profile not found.</Typography>;

    // Helper to display optional links
    const renderLink = (url, IconComponent, text) => (
        url && (
            <Grid item xs={12} sm={6}>
                 <Link href={url} target="_blank" rel="noopener noreferrer" sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none', color: 'inherit' }}>
                    <IconComponent sx={{ mr: 1 }} /> {text || url}
                 </Link>
            </Grid>
        )
    );

    return (
        <Container maxWidth="md">
            <Paper elevation={3} sx={{ p: { xs: 2, sm: 4 }, mt: 4 }}>
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, alignItems: 'center', mb: 3 }}>
                    <Avatar alt={`${profile.first_name} ${profile.last_name}`} src={profile.profile_picture_url || '/default-avatar.png'} sx={{ width: 100, height: 100, mr: { sm: 3 }, mb: { xs: 2, sm: 0 } }} />
                    <Box>
                        <Typography variant="h4" component="h1"> {profile.first_name} {profile.last_name} </Typography>
                        {profile.years_experience && (
                             <Typography variant="subtitle1" color="text.secondary"> {profile.years_experience} years of experience </Typography>
                        )}
                    </Box>
                </Box>
                <Divider sx={{ my: 2 }} />

                {profile.bio && (
                    <>
                        <Typography variant="h6" gutterBottom>About</Typography>
                        <Typography paragraph sx={{ whiteSpace: 'pre-wrap' }}>{profile.bio}</Typography>
                        <Divider sx={{ my: 2 }} />
                    </>
                )}

                {profile.services_offered && (
                    <>
                        <Typography variant="h6" gutterBottom>Services Offered</Typography>
                        <Typography paragraph sx={{ whiteSpace: 'pre-wrap' }}>{profile.services_offered}</Typography>
                        <Divider sx={{ my: 2 }} />
                    </>
                )}

                <Typography variant="h6" gutterBottom>Details</Typography>
                <Grid container spacing={1}>
                    {profile.service_area_zip_codes && (
                        <Grid item xs={12} sx={{ display: 'flex', alignItems: 'center' }}>
                            <LocationOnIcon sx={{ mr: 1 }} color="action"/> Service Area (Zip Codes): {profile.service_area_zip_codes}
                        </Grid>
                    )}
                     {profile.availability_notes && (
                        <Grid item xs={12} sx={{ display: 'flex', alignItems: 'center' }}>
                            <BusinessIcon sx={{ mr: 1 }} color="action"/> Availability: {profile.availability_notes}
                        </Grid>
                    )}
                    {renderLink(profile.personal_website_url, LinkIcon, "Personal Website")}
                    {renderLink(profile.instagram_url, InstagramIcon, "Instagram")}
                    {renderLink(profile.facebook_url, FacebookIcon, "Facebook")}
                    {renderLink(profile.twitter_url, TwitterIcon, "Twitter/X")}
                </Grid>

                 {profile.faq && (
                    <>
                         <Divider sx={{ my: 2 }} />
                         <Typography variant="h6" gutterBottom>FAQ</Typography>
                         <Typography paragraph sx={{ whiteSpace: 'pre-wrap' }}>{profile.faq}</Typography>
                    </>
                )}

                {profile.average_rating !== null ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <Rating value={profile.average_rating} precision={0.1} readOnly />
                        <Typography sx={{ ml: 1 }}>({profile.average_rating} / 5)</Typography>
                        <Typography sx={{ ml: 1, color: 'text.secondary' }}>
                            ({profile.reviews_received?.length || 0} reviews)
                        </Typography>
                    </Box>
                ) : (
                    <Typography variant="subtitle1" color="text.secondary" sx={{mt: 1}}>No reviews yet</Typography>
                )}

                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Reviews</Typography>
                {profile.reviews_received && profile.reviews_received.length > 0 ? (
                    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
                        {profile.reviews_received.map((review) => (
                            <ListItem key={review.id} alignItems="flex-start" divider>
                                <ListItemText
                                    primary={
                                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                            <Rating value={review.rating} readOnly size="small" sx={{ mr: 1 }} />
                                            <Typography variant="body1">
                                                For job: {/* Add link to job if desired */}
                                                "{review.job_title || `Job #${review.job}`}"
                                             </Typography>
                                        </Box>
                                    }
                                    secondary={
                                        <>
                                            <Typography
                                                sx={{ display: 'inline' }}
                                                component="span"
                                                variant="body2"
                                                color="text.primary"
                                            >
                                                {review.customer_name || `Customer #${review.customer}`}
                                            </Typography>
                                            {` — ${review.comment || 'No comment provided.'}`}
                                            <br />
                                            <Typography component="span" variant="caption" color="text.secondary">
                                                 {new Date(review.created_at).toLocaleDateString()}
                                            </Typography>
                                        </>
                                    }
                                />
                            </ListItem>
                        ))}
                    </List>
                ) : (
                    <Typography>This professional has not received any reviews yet.</Typography>
                )}

            </Paper>
        </Container>
    );
}

export default PublicProProfile;