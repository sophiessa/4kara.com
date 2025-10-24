import React, { useState } from 'react';
import { Box, TextField, IconButton, Paper, List, ListItem, ListItemText, CircularProgress, Alert, Typography } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import SendIcon from '@mui/icons-material/Send';
import api from './api';

function ChatInterface() {
    const [message, setMessage] = useState('');
    const [conversation, setConversation] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend(event);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        const userMessage = message.trim();
        if (!userMessage) return;
        const currentConversationHistory = [...conversation];
        setConversation(prev => [...prev, { sender: 'user', text: userMessage }]);
        setMessage('');
        setLoading(true);
        setError('');

        try {
            const response = await api.post('/api/chat/', { 
                message: userMessage,
                history: currentConversationHistory
             });

            const aiReply = response.data.reply;
            setConversation(prev => [...prev, { sender: 'ai', text: aiReply }]);

        } catch (err) {
            console.error("Chat API error:", err.response);
            setError(err.response?.data?.error || 'Failed to get response from AI.');
            setConversation(prev => [...prev, { sender: 'ai', text: 'Sorry, I encountered an error.' }]);
        } finally {
            setLoading(false);
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
                height: 'calc(80vh - 64px)',
                position: 'relative',
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
                overflow: 'auto', 
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
                                wordBreak: 'break-word', 
                            }}>
                                {msg.sender === 'ai' ? (
                                    <ReactMarkdown components={{ 
                                        p: ({node, ...props}) => <Typography variant="body1" {...props} />
                                    }}>
                                        {msg.text}
                                    </ReactMarkdown>
                                ) : (
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
                    maxWidth: '800px', 
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