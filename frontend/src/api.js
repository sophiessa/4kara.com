// frontend/src/api.js
import axios from 'axios';

const api = axios.create({
    // Use your actual domain name!
    baseURL: 'https://4kara.com',
});

export default api;