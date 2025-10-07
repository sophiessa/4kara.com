// frontend/src/JobList.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link as RouterLink } from 'react-router-dom';

// Import necessary MUI components for a card grid layout
import { Grid, Card, CardActionArea, CardContent, Typography, Alert, CircularProgress, Box } from '@mui/material';

function JobList() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const authToken = localStorage.getItem('authToken');

    useEffect(() => {
        const fetchJobs = async () => {
            if (!authToken) {
                setError('You must be logged in to view jobs.');
                setLoading(false);
                return;
            }
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/jobs/', {
                    headers: { 'Authorization': `Token ${authToken}` }
                });
                setJobs(response.data);
                setError('');
            } catch (err) {
                console.error('Error fetching jobs:', err);
                setError('Failed to fetch jobs. Your token may be invalid or you are not a professional user.');
            } finally {
                setLoading(false);
            }
        };
        fetchJobs();
    }, [authToken]);

    if (loading) {
        // Display a loading spinner while data is being fetched.
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Alert severity="error">{error}</Alert>;
    }

    return (
        <div>
            <Typography variant="h4" component="h1" gutterBottom>
                Available Jobs
            </Typography>
            {/* Grid container handles the overall layout. 'spacing' adds gaps between items. */}
            <Grid container spacing={3}>
                {jobs.length > 0 ? (
                    jobs.map(job => (
                        // Grid item defines how much space each card takes on different screen sizes.
                        // xs=12: full width on extra-small screens.
                        // sm=6: half width on small screens.
                        // md=4: one-third width on medium screens.
                        <Grid item xs={12} sm={6} md={4} key={job.id}>
                            <Card sx={{ height: '100%' }}>
                                {/* CardActionArea makes the entire card a clickable surface. */}
                                <CardActionArea component={RouterLink} to={`/jobs/${job.id}`} sx={{ height: '100%' }}>
                                    <CardContent>
                                        <Typography gutterBottom variant="h5" component="div">
                                            {job.title}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            {/* Truncate long descriptions for the list view */}
                                            {job.description.substring(0, 100)}{job.description.length > 100 && '...'}
                                        </Typography>
                                    </CardContent>
                                </CardActionArea>
                            </Card>
                        </Grid>
                    ))
                ) : (
                    <Grid item xs={12}>
                        <Typography>No jobs available.</Typography>
                    </Grid>
                )}
            </Grid>
        </div>
    );
}

export default JobList;