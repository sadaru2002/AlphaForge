import axios from 'axios';

// Replace with your backend URL
// For Android Emulator: http://10.0.2.2:8000
// For Physical Device: http://161.118.218.33
const BASE_URL = 'http://161.118.218.33';

const client = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default client;
