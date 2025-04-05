// src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext'; // Import AuthProvider and useAuth
import ProtectedRoute from './components/ProtectedRoute'; // Import ProtectedRoute
import ChatContainer from './components/ChatContainer';
import LoginPage from './pages/LoginPage'; // Import LoginPage
import SignupPage from './pages/SignupPage'; // Import SignupPage
import ForgotPasswordPage from './pages/ForgotPasswordPage'; // Import ForgotPasswordPage
import { Box, CircularProgress } from '@mui/material'; // For centering and loading

// A small component to handle redirection logic
function RootRedirect() {
    const { isLoggedIn } = useAuth();
    // Redirect to chat if logged in, otherwise to login
    return isLoggedIn ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />;
}

function App() {
    return (
        <AuthProvider> {/* Wrap everything with AuthProvider */}
            <BrowserRouter>
                {/* Use Box for centering content in auth pages if needed */}
                <Box
                    sx={{
                        minHeight: '100vh', // Ensure it takes full viewport height
                        display: 'flex',
                        flexDirection: 'column',
                        fontFamily: "Iranian Sans",
                        // Center content IF it's an auth page (simple check)
                        // We remove explicit centering here, pages handle their own layout
                        // justifyContent: 'center', // Remove global centering
                        // alignItems: 'center', // Remove global centering
                        backgroundColor: '#eef2f6' // Optional: Light background for the whole app area
                    }}
                >
                    <Routes>
                        {/* Public Routes */}
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/signup" element={<SignupPage />} />
                        <Route path="/forgot-password" element={<ForgotPasswordPage />} />

                        {/* Protected Route */}
                        <Route
                            path="/chat"
                            element={
                                <ProtectedRoute>
                                    {/* ChatContainer will now take full height within its parent */}
                                    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100vh' }}>
                                        <ChatContainer />
                                    </Box>
                                </ProtectedRoute>
                            }
                        />

                        {/* Redirect root path */}
                        <Route path="/" element={<RootRedirect />} />

                        {/* Optional: Catch-all route for 404 */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </Box>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;