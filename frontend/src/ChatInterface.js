// frontend/src/ChatInterface.js
import React, { useState } from 'react';
import { Box, TextField, IconButton, Paper, Typography } from '@mui/material';
import SendIcon from '@mui/icons-material/Send'; // Import the send icon

function ChatInterface() {
    const [message, setMessage] = useState('');

    const handleSend = (e) => {
        e.preventDefault(); // Prevent form submission from reloading the page
        if (!message.trim()) return; // Don't send empty messages

        console.log("Sending message:", message);
        // --- Placeholder for AI interaction ---
        // Later, you'll add code here to send 'message' to your AI backend
        // and display the response.
        // For now, we just clear the input.
        // --- End Placeholder ---
        setMessage(''); // Clear the input field
    };

    return (
        // Flexbox container to center content vertically and horizontally
        <Box
            sx={{
                flexGrow: 1, // Take up remaining vertical space in the Container
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center', // Center vertically
                alignItems: 'center', // Center horizontally
                textAlign: 'center',
                p: 2,
            }}
        >
            <Typography variant="h4" gutterBottom>
                How can I help you today?
            </Typography>

            {/* Paper component to create the chat input area */}
            <Paper
                component="form" // Use form element for accessibility and Enter key submission
                onSubmit={handleSend}
                sx={{
                    p: '2px 4px',
                    display: 'flex',
                    alignItems: 'center',
                    width: '100%', // Full width on small screens
                    maxWidth: '700px', // Max width for larger screens
                    borderRadius: '28px', // Rounded corners
                    boxShadow: 3, // Add some shadow
                }}
            >
                <TextField
                    sx={{ ml: 1, flex: 1, '& .MuiOutlinedInput-notchedOutline': { border: 'none' } }} // Remove border
                    placeholder="Ask about home repairs, maintenance, or improvements..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    variant="outlined"
                    fullWidth
                    multiline
                    maxRows={5} // Allow some vertical expansion
                />
                <IconButton color="primary" sx={{ p: '10px' }} aria-label="send message" type="submit">
                    <SendIcon />
                </IconButton>
            </Paper>
            
        </Box>
    );
}

export default ChatInterface;