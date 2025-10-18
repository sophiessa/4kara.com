// frontend/src/ChatInterface.js
import React, { useState } from 'react';
import { Box, TextField, IconButton, Paper, List, ListItem, ListItemText, CircularProgress, Alert, Typography } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import SendIcon from '@mui/icons-material/Send';
import api from './api'; // Import our configured axios instance

function ChatInterface() {
    const [message, setMessage] = useState('');
    const [conversation, setConversation] = useState([]); // State to hold messages {sender: 'user'/'ai', text: '...'}
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleKeyDown = (event) => {
        // Check if Enter was pressed WITHOUT the Shift key
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent adding a newline
            handleSend(event); // Trigger the send function
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        const userMessage = message.trim();
        if (!userMessage) return;

        const currentConversationHistory = [...conversation];

        // Add user message to conversation history
        setConversation(prev => [...prev, { sender: 'user', text: userMessage }]);
        setMessage(''); // Clear input
        setLoading(true); // Show loading indicator
        setError(''); // Clear previous errors

        try {
            // Send user message to the backend
            const response = await api.post('/api/chat/', { 
                message: userMessage,
                history: currentConversationHistory
             });

            // Add AI response to conversation history
            const aiReply = response.data.reply;
            setConversation(prev => [...prev, { sender: 'ai', text: aiReply }]);

        } catch (err) {
            console.error("Chat API error:", err.response);
            setError(err.response?.data?.error || 'Failed to get response from AI.');
            // Optionally add an error message to the chat
            setConversation(prev => [...prev, { sender: 'ai', text: 'Sorry, I encountered an error.' }]);
        } finally {
            setLoading(false); // Hide loading indicator
        }
    };

    return (
        <Box
            sx={{
                flexGrow: 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: conversation.length > 0 ? 'flex-end' : 'center',
                alignItems: 'center',
                p: 2,
                height: 'calc(80vh - 64px)', // Adjust as needed
                position: 'relative', // Keep for buttons
            }}
        >
            {conversation.length === 0 && (
             <Typography variant="h4" gutterBottom sx={{ mt: 8 }}>
                How can I help you today?
             </Typography>
            )}
            {/* Display Conversation History */}
            {conversation.length > 0 && (
            <Paper elevation={2} sx={{ 
                width: '100%', 
                maxWidth: '800px', 
                flexGrow: 1, 
                overflow: 'auto', // Make messages scrollable
                mb: 2, 
                p: 2 
            }}>
                <List>
                    {conversation.map((msg, index) => (
                        <ListItem key={index} sx={{ 
                            justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start'
                        }}>
                            <Paper elevation={1} sx={{ 
                                p: 1.5, 
                                maxWidth: '75%',
                                backgroundColor: msg.sender === 'user' ? 'primary.light' : 'grey.200',
                                wordBreak: 'break-word', // Ensure long words wrap
                            }}>
                                {msg.sender === 'ai' ? (
                                    <ReactMarkdown components={{ // Optional: Use MUI Typography for paragraphs
                                        p: ({node, ...props}) => <Typography variant="body1" {...props} />
                                    }}>
                                        {msg.text}
                                    </ReactMarkdown>
                                ) : (
                                    // Otherwise, just display user text normally
                                    <ListItemText primary={msg.text} />
                                )}
                            </Paper>
                        </ListItem>
                    ))}
                    {/* Show loading indicator within the chat */}
                    {loading && (
                        <ListItem sx={{ justifyContent: 'flex-start' }}>
                            <CircularProgress size={24} sx={{ ml: 1 }}/>
                        </ListItem>
                    )}
                </List>
            </Paper>
            )}
            
            {/* Display API Errors */}
            {error && <Alert severity="error" sx={{ width: '100%', maxWidth: '800px', mb: 1 }}>{error}</Alert>}

            {/* Chat Input Area */}
            <Paper
                component="form"
                onSubmit={handleSend}
                sx={{
                    p: '2px 4px',
                    display: 'flex',
                    alignItems: 'center',
                    width: '100%',
                    maxWidth: '800px', // Consistent width
                    borderRadius: '28px',
                    boxShadow: 3,
                }}
            >
                <TextField
                    sx={{ ml: 1, flex: 1, '& .MuiOutlinedInput-notchedOutline': { border: 'none' } }}
                    placeholder="Ask about home repairs..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    variant="outlined"
                    fullWidth
                    multiline
                    maxRows={5}
                    disabled={loading} 
                    onKeyDown={handleKeyDown}
                />
                <IconButton color="primary" sx={{ p: '10px' }} aria-label="send message" type="submit" disabled={loading}>
                    <SendIcon />
                </IconButton>
            </Paper>
        </Box>
    );
}

export default ChatInterface;