// frontend/src/MyJobs.js
import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Grid, Card, CardActionArea, CardContent, Typography, Alert, CircularProgress, Box } from '@mui/material';
import api from './api';


function MyJobs() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const authToken = localStorage.getItem('authToken');

    useEffect(() => {
        const fetchMyJobs = async () => {
            if (!authToken) {
                setError('You must be logged in to view your jobs.');
                setLoading(false);
                return;
            }
            try {
                // Call the new endpoint we just created
                const response = await api.get('/api/my-jobs/', {
                    headers: { 'Authorization': `Token ${authToken}` }
                });
                setJobs(response.data);
            } catch (err) {
                setError('Failed to fetch your jobs.');
            } finally {
                setLoading(false);
            }
        };
        fetchMyJobs();
    }, [authToken]);

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Alert severity="error">{error}</Alert>;
    }

    return (
        <div>
            <Typography variant="h4" component="h1" gutterBottom>
                My Posted Jobs
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
                                            Status: {job.is_completed ? "Closed" : "Open"}
                                        </Typography>
                                    </CardContent>
                                </CardActionArea>
                            </Card>
                        </Grid>
                    ))
                ) : (
                    <Grid item xs={12}>
                        <Typography>You have not posted any jobs yet.</Typography>
                    </Grid>
                )}
            </Grid>
        </div>
    );
}

export default MyJobs;