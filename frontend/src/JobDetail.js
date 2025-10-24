import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import api from './api';
import { Paper, Typography, Box, Divider, TextField, Button, List, ListItem, ListItemText, Alert, CircularProgress, Rating } from '@mui/material';

function JobDetail() {
    const [job, setJob] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [bidAmount, setBidAmount] = useState('');
    const [bidDetails, setBidDetails] = useState('');
    
    const [rating, setRating] = useState(0);
    const [comment, setComment] = useState('');
    const [reviewError, setReviewError] = useState('');
    const [reviewSubmitted, setReviewSubmitted] = useState(false);
    
    const { jobId } = useParams();
    const navigate = useNavigate();
    const token = localStorage.getItem('authToken');
    const user = JSON.parse(localStorage.getItem('user'));

    

    const handleAcceptBid = async (bidId) => {
        if (!window.confirm("Are you sure you want to accept this bid? This will close the job to further bidding.")) {
            return;
        }
        try {
            await api.post(`/api/bids/${bidId}/accept/`, {}, {
                headers: { 'Authorization': `Token ${token}` }
            });
            window.location.reload();
        } catch (err) {
            console.error('Error accepting bid:', err);
            setError('Failed to accept the bid.');
        }
    };

    useEffect(() => {
        if (!token) {
            navigate('/login');
            return;
        }
        const fetchJob = async () => {
            try {
                const response = await api.get(`/api/jobs/${jobId}/`, {
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
        if (job && user) {
            const userReview = job.reviews?.find(review => review.customer === user.id);
            if (userReview) {
                setReviewSubmitted(true);
            }
        }
    }, [jobId, token, navigate, job, user]);


    const handleReviewSubmit = async (e) => {
        e.preventDefault();
        setReviewError('');
        if (rating === 0) {
            setReviewError('Please select a star rating.');
            return;
        }
        try {
            await api.post(`/api/jobs/${jobId}/reviews/`,
                { rating: rating, comment: comment },
                { headers: { 'Authorization': `Token ${token}` } }
            );
            setReviewSubmitted(true);
            window.location.reload(); 
        } catch (err) {
            setReviewError(err.response?.data?.detail || err.response?.data?.non_field_errors?.[0] || 'Failed to submit review.');
            console.error("Review submit error:", err.response);
        }
    };

    const handleBidSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post(`/api/jobs/${jobId}/bid/`, { amount: bidAmount, details: bidDetails }, {
                headers: { 'Authorization': `Token ${token}` }
            });
            window.location.reload();
        } catch (err) {
            setError('Failed to submit bid.');
        }
    };

    if (loading) {return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;}
    if (error) return <Alert severity="error">{error}</Alert>;
    if (!job) return null;

    const isOwner = user && user.id === job.customer;
    const isHiredPro = user && job.accepted_bid && user.id === job.accepted_bid.pro;

  

    return (
        <Paper elevation={3} sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h3" component="h1" gutterBottom>
                    {job.title}
                </Typography>
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
            {isOwner && (
                <Box>
                    <Typography variant="h5" component="h2" gutterBottom>
                        {job.is_completed ? "Job Status: Closed" : "Bids Received"}
                    </Typography>
                    {job.bids.length > 0 ? (
                        <List>
                            {job.bids.map(bid => (
                                <ListItem key={bid.id} divider
                                    sx={job.accepted_bid === bid.id ? { backgroundColor: 'action.selected' } : {}}
                                >
                                    <ListItemText
                                        primary={
                                            <Typography variant="h6" component={RouterLink} to={`/profile/${bid.pro}`} sx={{ textDecoration: 'none', color: 'primary.main' }}>
                                                Bid by Pro #{bid.pro} {/* We'll add name later */}
                                            </Typography>
                                        }
                                        secondary={
                                            <>
                                                <Typography component="span" variant="body1" color="text.primary">
                                                    Amount: ${bid.amount}
                                                </Typography>
                                                <br />
                                                {bid.details}
                                            </>
                                        }
                                    />
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
            {isOwner && job.is_completed && !reviewSubmitted && (
                <Box component="form" onSubmit={handleReviewSubmit} noValidate sx={{ mt: 4, borderTop: '1px solid lightgray', pt: 3 }}>
                    <Typography variant="h5" component="h2" gutterBottom>Leave a Review</Typography>
                    <Typography component="legend">Rating</Typography>
                    <Rating
                        name="job-rating"
                        value={rating}
                        onChange={(event, newValue) => {
                            setRating(newValue || 0);
                        }}
                    />
                    <TextField
                        margin="normal"
                        fullWidth
                        id="comment"
                        label="Comment (Optional)"
                        name="comment"
                        multiline
                        rows={3}
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                    />
                    {reviewError && <Alert severity="error" sx={{ mt: 1, mb: 1 }}>{reviewError}</Alert>}
                    <Button type="submit" variant="contained" sx={{ mt: 2 }}>Submit Review</Button>
                </Box>
            )}

            {isOwner && reviewSubmitted && (
                 <Typography sx={{ mt: 4, pt: 3, borderTop: '1px solid lightgray' }}>Thank you for submitting your review!</Typography>
            )}
        </Paper>
    );
}

export default JobDetail;