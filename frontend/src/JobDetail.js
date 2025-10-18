// frontend/src/JobDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import api from './api';

// Import a larger set of MUI components for layout and display
import { Paper, Typography, Box, Divider, TextField, Button, List, ListItem, ListItemText, Alert, CircularProgress } from '@mui/material';

function JobDetail() {
    const [job, setJob] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [bidAmount, setBidAmount] = useState('');
    const [bidDetails, setBidDetails] = useState('');
    
    const { jobId } = useParams();
    const navigate = useNavigate();

    const token = localStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user'));

    

    const handleAcceptBid = async (bidId) => {
        if (!window.confirm("Are you sure you want to accept this bid? This will close the job to further bidding.")) {
            return;
        }
        try {
            await api.post('/api/bids/${bidId}/accept/' , {}, {
                headers: { 'Authorization': `Token ${token}` }
            });
            // Reload to see the updated job status
            window.location.reload();
        } catch (err) {
            console.error('Error accepting bid:', err);
            setError('Failed to accept the bid.');
        }
    };

    useEffect(() => {
        // ... (fetchJob logic remains the same, just add setLoading)
        if (!token) {
            navigate('/login');
            return;
        }
        const fetchJob = async () => {
            try {
                const response = await api.get('/api/jobs/${jobId}/', {
                    headers: { 'Authorization': `Token ${token}` }
                });
                setJob(response.data);
            } catch (err) {
                setError('Failed to fetch job details.');
            } finally {
                setLoading(false);
            }
        };
        fetchJob();
    }, [jobId, token, navigate]);

    const handleBidSubmit = async (e) => {
        // ... (handleBidSubmit logic is the same)
        e.preventDefault();
        try {
            await api.post('/api/jobs/${jobId}/bid/', { amount: bidAmount, details: bidDetails }, {
                headers: { 'Authorization': `Token ${token}` }
            });
            window.location.reload();
        } catch (err) {
            setError('Failed to submit bid.');
        }
    };

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }
    if (error) return <Alert severity="error">{error}</Alert>;
    if (!job) return null; // Or some other placeholder

    const isOwner = user && user.id === job.customer;
    const isHiredPro = user && job.accepted_bid && user.id === job.accepted_bid.pro;

  

    return (
        // Paper provides a clean, elevated surface for the content.
        <Paper elevation={3} sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h3" component="h1" gutterBottom>
                    {job.title}
                </Typography>
                
                {/* Show button only if job is closed AND user is the owner or the hired pro */}
                
                {job.is_completed && (isOwner || isHiredPro) && (
                    <Button 
                        variant="contained" 
                        component={RouterLink} 
                        to={`/jobs/${job.id}/conversation`}
                    >
                        View Conversation
                    </Button>
                )}
            </Box>
            <Typography variant="body1" color="text.secondary" paragraph>
                {job.description}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
                Location: {job.street_address}, {job.city}, {job.state} {job.zip_code}
            </Typography>
            
            <Divider sx={{ my: 3 }} />

            {/* Bid Form for Professionals - ONLY if the job is still open */}
            {user && user.is_pro && !job.is_completed && (
                <Box component="form" onSubmit={handleBidSubmit} noValidate sx={{ mb: 4 }}>
                    <Typography variant="h5" component="h2" gutterBottom>Place Your Bid</Typography>
                    <TextField
                        type="number"
                        label="Bid Amount ($)"
                        value={bidAmount}
                        onChange={(e) => setBidAmount(e.target.value)}
                        required
                        fullWidth
                        margin="normal"
                    />
                    <TextField
                        label="Details"
                        value={bidDetails}
                        onChange={(e) => setBidDetails(e.target.value)}
                        required
                        fullWidth
                        multiline
                        rows={3}
                        margin="normal"
                    />
                    <Button type="submit" variant="contained" sx={{ mt: 2 }}>Submit Bid</Button>
                </Box>
            )}
            

            {/* Bids List for the Job Owner */}
            {isOwner && (
                <Box>
                    <Typography variant="h5" component="h2" gutterBottom>
                        {/* Show a different title if the job is completed */}
                        {job.is_completed ? "Job Status: Closed" : "Bids Received"}
                    </Typography>
                    {job.bids.length > 0 ? (
                        <List>
                            {job.bids.map(bid => (
                                <ListItem key={bid.id} divider
                                    // Highlight the accepted bid
                                    sx={job.accepted_bid === bid.id ? { backgroundColor: 'action.selected' } : {}}
                                >
                                    <ListItemText
                                        primary={`$${bid.amount}`}
                                        secondary={bid.details}
                                    />
                                    {/* Show the Accept button ONLY if the job is not yet completed */}
                                    {!job.is_completed && (
                                        <Button 
                                            variant="outlined" 
                                            onClick={() => handleAcceptBid(bid.id)}
                                        >
                                            Accept
                                        </Button>
                                    )}
                                </ListItem>
                            ))}
                        </List>
                    ) : ( <Typography>No bids have been placed yet.</Typography> )}
                </Box>
            )}
        </Paper>
    );
}

export default JobDetail;