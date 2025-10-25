import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { Box, Paper, Typography, List, ListItem, ListItemText, TextField, Button, CircularProgress, Alert } from '@mui/material';

function ConversationPage() {
    const { jobId } = useParams();
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [error, setError] = useState('');
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('authToken');
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    const socketUrl = `${protocol}://${host}/ws/chat/${jobId}/?token=${token}`;
    const {
        sendMessage,
        lastMessage,
        readyState,
    } = useWebSocket(socketUrl, {
        onOpen: () => console.log('WebSocket connection opened.'),
        onClose: () => console.log('WebSocket connection closed.'),
        onError: (event) => {
            console.error('WebSocket error:', event);
            setError('WebSocket connection error. Please refresh.');
        },
        shouldReconnect: (closeEvent) => true,
    });
    useEffect(() => {
        if (lastMessage !== null) {
            try {
                const data = JSON.parse(lastMessage.data);
                if (data.type === 'message_history' && Array.isArray(data.messages)) {
                    setMessages(data.messages);
                } else if (data.message && typeof data.message === 'object') {
                    setMessages((prev) => [...prev, data.message]);
                } else {
                    console.warn("Received unexpected WebSocket message format:", data);
                }
            } catch (e) {
                console.error("Failed to parse incoming WebSocket message:", lastMessage.data, e);
            }
        }
    }, [lastMessage, setMessages]);
    const handleSendMessage = useCallback((e) => {
        e.preventDefault();
        const messageToSend = newMessage.trim();
        if (!messageToSend) return;
        sendMessage(JSON.stringify({ message: messageToSend }));
        setNewMessage('');
    }, [newMessage, sendMessage]);

    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];

    const isLoading = readyState === ReadyState.CONNECTING && messages.length === 0;

    return (
        <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Conversation (Status: {connectionStatus})
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            <List sx={{ mb: 2, maxHeight: '500px', overflow: 'auto', border: '1px solid #eee', borderRadius: '4px' }}>
                {isLoading && (
                    <ListItem sx={{ justifyContent: 'center' }}>
                        <CircularProgress />
                    </ListItem>
                )}
                {messages.map((msg, index) => (
                    <ListItem key={msg.id || index} sx={{
                        flexDirection: 'column',
                        alignItems: msg.sender === user?.id ? 'flex-end' : 'flex-start'
                    }}>
                        <Paper elevation={1} sx={{
                            p: 1.5,
                            maxWidth: '70%',
                            backgroundColor: msg.sender === user?.id ? 'primary.light' : 'grey.200',
                            wordBreak: 'break-word',
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
                    disabled={readyState !== ReadyState.OPEN}
                />
                <Button type="submit" variant="contained" sx={{ mt: 2 }} disabled={readyState !== ReadyState.OPEN}>
                    Send
                </Button>
            </Box>
        </Paper>
    );
}

export default ConversationPage;