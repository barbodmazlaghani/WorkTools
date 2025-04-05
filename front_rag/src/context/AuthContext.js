// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true); // To prevent flicker on initial load

    useEffect(() => {
        // Check local storage on initial load
        const storedLoginStatus = localStorage.getItem('isLoggedIn') === 'true';
        setIsLoggedIn(storedLoginStatus);
        setIsLoading(false); // Finished loading initial state
    }, []);

    const login = (email, password) => {
        // --- Placeholder Login Logic ---
        // In a real app, you'd call your backend API here.
        // For simulation, we'll just check if fields are non-empty.
        console.log("Attempting login simulation for:", email);
        if (email && password) {
            localStorage.setItem('isLoggedIn', 'true');
            setIsLoggedIn(true);
            return true; // Indicate success
        }
        alert("Simulated login failed: Please provide email and password.");
        return false; // Indicate failure
        // --- End Placeholder ---
    };

    const signup = (name, email, password) => {
        // --- Placeholder Signup Logic ---
        // In a real app, you'd call your backend API here.
        // For simulation, just check non-empty fields.
        console.log("Attempting signup simulation for:", email);
        if (name && email && password) {
            // Simulate successful signup, but don't log in automatically here
            // Redirect user to login page after signup.
            alert("Simulated signup successful! Please log in.");
            return true; // Indicate success
        }
        alert("Simulated signup failed: Please fill all fields.");
        return false; // Indicate failure
        // --- End Placeholder ---
    };

    const forgotPassword = (email) => {
        // --- Placeholder Forgot Password Logic ---
        console.log("Attempting forgot password simulation for:", email);
        if (email) {
            alert(`Simulated: If an account with email ${email} exists, a password reset link has been sent (not really!).`);
            return true;
        }
        alert("Simulated forgot password failed: Please provide an email.");
        return false;
        // --- End Placeholder ---
    };

    // Placeholder for Change Password - might be called from a profile page later
    const changePassword = (oldPassword, newPassword) => {
        // --- Placeholder Change Password Logic ---
        console.log("Attempting change password simulation");
        if (oldPassword && newPassword) {
            alert("Simulated: Password changed successfully (not really!). You might need to log in again.");
            // Optionally force logout after password change
            // logout();
            return true;
        }
        alert("Simulated change password failed: Please provide old and new passwords.");
        return false;
        // --- End Placeholder ---
    };


    const logout = () => {
        localStorage.removeItem('isLoggedIn');
        setIsLoggedIn(false);
        // No need to redirect here, the ProtectedRoute will handle it
    };

    // Don't render children until initial auth state is loaded
    if (isLoading) {
        return null; // Or a loading spinner
    }

    return (
        <AuthContext.Provider value={{ isLoggedIn, login, logout, signup, forgotPassword, changePassword }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};