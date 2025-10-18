// frontend/src/JobList.js
import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import api from './api'; // Use our centralized api instance
import { Grid, Card, CardActionArea, CardContent, Typography, Alert, CircularProgress, Box, TextField } from '@mui/material';

function JobList() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // --- New State for Search and Filter ---
    const [searchQuery, setSearchQuery] = useState('');
    const [zipFilter, setZipFilter] = useState('');

    const authToken = localStorage.getItem('authToken');

    // The useEffect hook now re-runs whenever the search or filter text changes
    useEffect(() => {
        const fetchJobs = async () => {
            if (!authToken) {
                setError('You must be logged in to view jobs.');
                setLoading(false);
                return;
            }
            
            setLoading(true); // Show loading spinner on new searches

            try {
                // Construct query parameters
                const params = new URLSearchParams();
                if (searchQuery) {
                    params.append('search', searchQuery);
                }
                if (zipFilter) {
                    params.append('zip_code', zipFilter);
                }

                // Make the API call with the parameters
                const response = await api.get('/api/jobs/', { 
                    headers: { 'Authorization': `Token ${authToken}` },
                    params: params 
                });
                
                setJobs(response.data);
                setError('');
            } catch (err) {
                setError('Failed to fetch jobs.');
            } finally {
                setLoading(false);
            }
        };

        // This timeout debounce prevents an API call on every single keystroke
        const searchTimeout = setTimeout(() => {
            fetchJobs();
        }, 500); // Wait 500ms after user stops typing

        // Cleanup function to cancel the timeout if the user types again
        return () => clearTimeout(searchTimeout);

    }, [authToken, searchQuery, zipFilter]); // <<< Dependency array updated

    return (
        <div>
            <Typography variant="h4" component="h1" gutterBottom>
                Browse Available Jobs
            </Typography>

            {/* --- Search and Filter Inputs --- */}
            <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
                <TextField 
                    label="Search by keyword..."
                    variant="outlined"
                    fullWidth
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                <TextField 
                    label="Filter by Zip Code..."
                    variant="outlined"
                    value={zipFilter}
                    onChange={(e) => setZipFilter(e.target.value)}
                />
            </Box>

            {/* --- Conditional Rendering for Loading/Error/Content --- */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /> </Box>
            ) : error ? (
                <Alert severity="error">{error}</Alert>
            ) : (
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
                                                {job.city}, {job.state} {job.zip_code}
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        ))
                    ) : (
                        <Grid item xs={12}>
                            <Typography>No jobs match your criteria.</Typography>
                        </Grid>
                    )}
                </Grid>
            )}
        </div>
    );
}

export default JobList;