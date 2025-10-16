// frontend/src/ConversationPage.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from './api';
import { Box, Paper, Typography, List, ListItem, ListItemText, TextField, Button, CircularProgress, Alert } from '@mui/material';

function ConversationPage() {
    const { jobId } = useParams();
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('authToken');

    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const response = await api.get(`/api/jobs/${jobId}/messages/`, {
                    headers: { 'Authorization': `Token ${token}` }
                });
                setMessages(response.data);
            } catch (err) {
                setError('Failed to load messages.');
            } finally {
                setLoading(false);
            }
        };
        fetchMessages();
    }, [jobId, token]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        try {
            const response = await api.post(`/api/jobs/${jobId}/messages/create/`, 
                { body: newMessage },
                { headers: { 'Authorization': `Token ${token}` } }
            );
            // Add the new message to the list and clear the input field
            setMessages([...messages, response.data]);
            setNewMessage('');
        } catch (err) {
            setError('Failed to send message.');
        }
    };

    if (loading) return <CircularProgress />;
    if (error) return <Alert severity="error">{error}</Alert>;

    return (
        <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
            <Typography variant="h4" gutterBottom>Conversation</Typography>
            <List sx={{ mb: 2, maxHeight: '500px', overflow: 'auto' }}>
                {messages.map(msg => (
                    <ListItem key={msg.id} sx={{ 
                        // Align messages left or right based on the sender
                        flexDirection: 'column', 
                        alignItems: msg.sender === user.id ? 'flex-end' : 'flex-start' 
                    }}>
                        <Paper elevation={1} sx={{ 
                            p: 1.5, 
                            maxWidth: '70%',
                            backgroundColor: msg.sender === user.id ? 'primary.light' : 'grey.200'
                        }}>
                            <ListItemText
                                primary={msg.body}
                                secondary={`${msg.sender_name} - ${new Date(msg.timestamp).toLocaleString()}`}
                            />
                        </Paper>
                    </ListItem>
                ))}
            </List>
            <Box component="form" onSubmit={handleSendMessage}>
                <TextField
                    label="Type your message"
                    fullWidth
                    multiline
                    rows={3}
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    variant="outlined"
                />
                <Button type="submit" variant="contained" sx={{ mt: 2 }}>
                    Send
                </Button>
            </Box>
        </Paper>
    );
}

export default ConversationPage;