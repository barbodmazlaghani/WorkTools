// src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom';
import {
    Box,
    TextField,
    Button,
    Typography,
    Paper,
    Container,
    Stack,
    Link,
    Alert // Import Alert for showing errors
} from '@mui/material';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(''); // State for login errors
    const auth = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    // Get the page user was trying to access before being redirected to login
    const from = location.state?.from?.pathname || "/chat"; // Default to /chat

    const handleLogin = (event) => {
        event.preventDefault(); // Prevent default form submission
        setError(''); // Clear previous errors

        // --- Use Auth Context's login (placeholder) ---
        const success = auth.login(email, password);
        if (success) {
            navigate(from, { replace: true }); // Redirect to the originally intended page or /chat
        } else {
            // The login function itself handles the alert for now,
            // but we could set a state error here for more complex UI feedback
            setError("ورود ناموفق بود. لطفا ایمیل و گذرواژه را بررسی کنید."); // Example error message
        }
        // --- End Placeholder ---
    };

    return (
        <Container component="main" maxWidth="xs">
            <Paper
                elevation={6}
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    padding: 4,
                    backgroundColor: '#f7f9fc'
                }}
            >
                <img src="/logo.png" alt="Logo" height="60" style={{ marginBottom: '16px' }}/>
                <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
                    ورود به گزارش‌یار
                </Typography>
                {error && <Alert severity="error" sx={{ width: '100%', mb: 2 }}>{error}</Alert>}
                <Box component="form" onSubmit={handleLogin} noValidate sx={{ mt: 1, width: '100%' }}>
                    <Stack spacing={2}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="آدرس ایمیل"
                            name="email"
                            autoComplete="email"
                            autoFocus
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            dir="ltr" // Keep email LTR
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="گذرواژه"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            dir="ltr" // Keep password LTR for input
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2, backgroundColor: '#0b3d91', '&:hover': { backgroundColor: '#002244' } }}
                        >
                            ورود
                        </Button>
                        <Stack direction="row" justifyContent="space-between">
                            <Link component={RouterLink} to="/forgot-password" variant="body2">
                                گذرواژه را فراموش کردید؟
                            </Link>
                            <Link component={RouterLink} to="/signup" variant="body2">
                                حساب کاربری ندارید؟ ثبت نام
                            </Link>
                        </Stack>
                    </Stack>
                </Box>
            </Paper>
        </Container>
    );
};

export default LoginPage;