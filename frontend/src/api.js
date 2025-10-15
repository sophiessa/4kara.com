// frontend/src/api.js
import axios from 'axios';

const api = axios.create({
    // Use the variable from .env, but if it's not there, default to localhost.
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

export default api;