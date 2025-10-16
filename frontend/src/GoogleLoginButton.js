// frontend/src/GoogleLoginButton.js
import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import api from './api';

function GoogleLoginButton() {
    const navigate = useNavigate();

    const handleGoogleSuccess = async (credentialResponse) => {
        // The 'credential' field contains the JWT ID token from Google.
        const idToken = credentialResponse.credential;

        try {
            // Send the ID token to our backend for verification and user creation
            const response = await api.post('/api/google/', { 
                id_token: idToken,
            });

            // The backend will respond with our own app's token and user data
            const { key, user } = response.data;
            
            // Store the token and user data, then navigate
            localStorage.setItem('authToken', key);
            localStorage.setItem('user', JSON.stringify(user));
            navigate('/jobs');
            window.location.reload();

        } catch (error) {
            console.error("Google login failed", error);
            // Handle login failure (e.g., show an error message)
        }
    };

    const handleGoogleError = () => {
        console.error("Google login failed");
    };

    return (
        <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            useOneTap // This provides a more seamless login experience
        />
    );
}

export default GoogleLoginButton;