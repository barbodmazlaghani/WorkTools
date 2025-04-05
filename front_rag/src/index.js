// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import "./assets/fonts/IranianSans.ttf"
import './index.css';
import App from './App';
import {ThemeProvider} from "@mui/material";
import theme from './theme';


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <ThemeProvider theme={theme}>
            <App />
        </ThemeProvider>
    </React.StrictMode>,
);
