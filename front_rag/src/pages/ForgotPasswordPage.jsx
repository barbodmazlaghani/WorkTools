// src/pages/ForgotPasswordPage.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link as RouterLink } from 'react-router-dom';
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

const ForgotPasswordPage = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const auth = useAuth();

    const handleForgotPassword = (event) => {
        event.preventDefault();
        setMessage('');
        setError('');

        // --- Use Auth Context's forgotPassword (placeholder) ---
        const success = auth.forgotPassword(email);
        if (success) {
            setMessage(`شبیه سازی: اگر حسابی با ایمیل ${email} وجود داشته باشد، ایمیل بازیابی ارسال شد (در واقع ارسال نشده!).`);
            setEmail(''); // Clear the input field on success
        } else {
            setError("لطفا یک آدرس ایمیل معتبر وارد کنید.");
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
                <Typography component="h1" variant="h5" sx={{ mb: 1 }}>
                    بازیابی گذرواژه
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
                    ایمیل حساب کاربری خود را وارد کنید تا لینک بازیابی (شبیه‌سازی شده) برایتان ارسال شود.
                </Typography>
                {error && <Alert severity="error" sx={{ width: '100%', mb: 2 }}>{error}</Alert>}
                {message && <Alert severity="info" sx={{ width: '100%', mb: 2 }}>{message}</Alert>}
                <Box component="form" onSubmit={handleForgotPassword} noValidate sx={{ mt: 1, width: '100%' }}>
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
                            dir="ltr"
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2, backgroundColor: '#0b3d91', '&:hover': { backgroundColor: '#002244' } }}
                        >
                            ارسال لینک بازیابی
                        </Button>
                        <Stack direction="row" justifyContent="flex-end">
                            <Link component={RouterLink} to="/login" variant="body2">
                                بازگشت به صفحه ورود
                            </Link>
                        </Stack>
                    </Stack>
                </Box>
            </Paper>
        </Container>
    );
};

export default ForgotPasswordPage;