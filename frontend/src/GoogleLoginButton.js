import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import api from './api';

function GoogleLoginButton() {
    const navigate = useNavigate();

    const handleGoogleSuccess = async (credentialResponse) => {
        const idToken = credentialResponse.credential;
        try {
            const response = await api.post('/api/google/', { 
                id_token: idToken,
            });
            const { key, user } = response.data;
            localStorage.setItem('authToken', key);
            localStorage.setItem('user', JSON.stringify(user));
            navigate('/jobs');
            window.location.reload();

        } catch (error) {
            console.error("Google login failed", error);
        }
    };

    const handleGoogleError = () => {
        console.error("Google login failed");
    };

    return (
        <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            useOneTap
        />
    );
}

export default GoogleLoginButton;