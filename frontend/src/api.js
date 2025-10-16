// frontend/src/api.js
import axios from 'axios';

const api = axios.create({
    // Use dynamic hostname for cross-device compatibility
    baseURL: process.env.REACT_APP_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`,
});

export default api;