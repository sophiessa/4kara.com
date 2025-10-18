// frontend/src/MyWorkPage.js
import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import api from './api';
import { Grid, Card, CardActionArea, CardContent, Typography, Alert, CircularProgress } from '@mui/material';

function MyWorkPage() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const authToken = localStorage.getItem('authToken');

    useEffect(() => {
        const fetchMyWork = async () => {
            if (!authToken) {
                setError('You must be logged in to view your work.');
                setLoading(false);
                return;
            }
            try {
                // Call the new /api/my-work/ endpoint
                const response = await api.get('/api/my-work/', {
                    headers: { 'Authorization': `Token ${authToken}` }
                });
                setJobs(response.data);
            } catch (err) {
                setError('Failed to fetch your accepted jobs.');
            } finally {
                setLoading(false);
            }
        };
        fetchMyWork();
    }, [authToken]);

    if (loading) return <CircularProgress />;
    if (error) return <Alert severity="error">{error}</Alert>;

    return (
        <div>
            <Typography variant="h4" component="h1" gutterBottom>
                My Accepted Jobs
            </Typography>
            <Grid container spacing={3}>
                {jobs.length > 0 ? (
                    jobs.map(job => (
                        <Grid item xs={12} sm={6} md={4} key={job.id}>
                            <Card sx={{ height: '100%' }}>
                                <CardActionArea component={RouterLink} to={`/jobs/${job.id}`} sx={{ height: '100%' }}>
                                    <CardContent>
                                        <Typography gutterBottom variant="h5" component="div">
                                            {job.title}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Status: In Progress
                                        </Typography>
                                    </CardContent>
                                </CardActionArea>
                            </Card>
                        </Grid>
                    ))
                ) : (
                    <Grid item xs={12}>
                        <Typography>You have not been hired for any jobs yet.</Typography>
                    </Grid>
                )}
            </Grid>
        </div>
    );
}

export default MyWorkPage;