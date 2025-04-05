// src/pages/SignupPage.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
    Box,
    TextField,
    Button,
    Typography,
    Paper,
    Container,
    Stack,
    Link,
    Alert
} from '@mui/material';

const SignupPage = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const auth = useAuth();
    const navigate = useNavigate();

    const handleSignup = (event) => {
        event.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError("گذرواژه‌ها مطابقت ندارند.");
            return;
        }

        // --- Use Auth Context's signup (placeholder) ---
        const signupSuccess = auth.signup(name, email, password);
        if (signupSuccess) {
            // Don't log in automatically, show success and let them log in
            setSuccess("ثبت نام با موفقیت انجام شد! اکنون می‌توانید وارد شوید.");
            // Optional: Redirect to login after a short delay
            setTimeout(() => {
                navigate('/login');
            }, 2000); // 2 seconds delay
        } else {
            // The signup function itself handles the alert for now
            setError("ثبت نام ناموفق بود. لطفا همه فیلدها را بررسی کنید.");
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
                    ثبت نام در گزارش‌یار
                </Typography>
                {error && <Alert severity="error" sx={{ width: '100%', mb: 2 }}>{error}</Alert>}
                {success && <Alert severity="success" sx={{ width: '100%', mb: 2 }}>{success}</Alert>}
                <Box component="form" onSubmit={handleSignup} noValidate sx={{ mt: 1, width: '100%' }}>
                    <Stack spacing={2}>
                        <TextField
                            required
                            fullWidth
                            id="name"
                            label="نام کامل"
                            name="name"
                            autoComplete="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                        <TextField
                            required
                            fullWidth
                            id="email"
                            label="آدرس ایمیل"
                            name="email"
                            autoComplete="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            dir="ltr"
                        />
                        <TextField
                            required
                            fullWidth
                            name="password"
                            label="گذرواژه"
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            dir="ltr"
                        />
                        <TextField
                            required
                            fullWidth
                            name="confirmPassword"
                            label="تکرار گذرواژه"
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            dir="ltr"
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2, backgroundColor: '#0b3d91', '&:hover': { backgroundColor: '#002244' } }}
                            disabled={!!success} // Disable button after successful signup
                        >
                            ثبت نام
                        </Button>
                        <Stack direction="row" justifyContent="flex-end">
                            <Link component={RouterLink} to="/login" variant="body2">
                                قبلا ثبت نام کردید؟ ورود
                            </Link>
                        </Stack>
                    </Stack>
                </Box>
            </Paper>
        </Container>
    );
};

export default SignupPage;