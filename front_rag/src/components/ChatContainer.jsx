// src/components/ChatContainer.jsx
import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import {
    Box,
    Typography,
    TextField,
    Button,
    Paper,
    useMediaQuery,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    IconButton, // Added for logout button icon
    Tooltip    // Added for tooltip on logout
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout'; // Added logout icon
import { v4 as uuidv4 } from 'uuid';
import { useAuth } from '../context/AuthContext'; // Import useAuth hook
import { useNavigate } from 'react-router-dom'; // Import useNavigate hook

const ChatContainer = () => {
    // State for the API info
    const [apiInfo, setApiInfo] = useState(null);

    // Auth context and navigation
    const auth = useAuth(); // Get auth context methods and state
    const navigate = useNavigate(); // Get navigate function for redirection

    // Fetch API info on component mount
    useEffect(() => {
        const fetchApiInfo = async () => {
            try {
                // --- Placeholder: In a real app, only fetch if logged in ---
                // if (!auth.isLoggedIn) return; // Example check

                const response = await fetch('http://130.185.77.114:8111/api/info');
                if (!response.ok) {
                    throw new Error(`Error fetching API info: ${response.statusText}`);
                }
                const data = await response.json();
                setApiInfo(data);
            } catch (error) {
                console.error("Error fetching API info:", error);
                // Optionally handle error display for API info
            }
        };

        fetchApiInfo();
        // Add auth.isLoggedIn to dependency array if you add the check above
    }, []); // Dependency array is empty for now

    // Chat messages and related states
    const [messages, setMessages] = useState([
        {
            id: uuidv4(),
            text: `سلام!
به دستیار هوشمند ایپکو خوش آمدید. برای شروع، می‌توانید نام بخشی که مشکل دارد مانند "موتور"، یا با جزئیات بیشتر مثل "تغییر تایمینگ موتور" یا "روشن نشدن خودرو" را وارد کنید. ما با جستجوی دقیق در بانک اطلاعاتی، راهکارهای مربوط به خرابی را برایتان بازمی‌گردانیم.`,
            sender: 'bot',
        },
    ]);
    const [userInput, setUserInput] = useState("");
    const [autoScroll, setAutoScroll] = useState(true);
    const [isSending, setIsSending] = useState(false); // State to disable input/button while sending

    // "About Us" dialog state
    const [aboutOpen, setAboutOpen] = useState(false);

    const messagesEndRef = useRef(null);
    const messagesContainerRef = useRef(null);

    const isSmallScreen = useMediaQuery('(max-width: 600px)');
    const isLargeScreen = useMediaQuery('(min-width: 1920px)'); // Consider if still needed with new layout
    // const isTabletScreen = useMediaQuery('(min-width: 601px) and (max-width: 1024px)'); // Keep if needed for specific styles

    // Scroll handler to detect if user is near the bottom.
    const handleScroll = () => {
        const container = messagesContainerRef.current;
        if (!container) return;
        const threshold = 50; // px from bottom
        const scrollPos = container.scrollTop + container.clientHeight;
        const scrollHeight = container.scrollHeight;
        if (scrollHeight - scrollPos <= threshold) {
            setAutoScroll(true);
        } else {
            setAutoScroll(false);
        }
    };

    // Scroll to bottom when new messages arrive or when sending starts.
    useEffect(() => {
        if (autoScroll) {
            // Use 'auto' for instant scroll when sending, 'smooth' could be used otherwise
            messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
        }
    }, [messages, autoScroll]); // Dependency on messages and autoScroll

    const handleSend = async () => {
        const trimmedInput = userInput.trim();
        if (!trimmedInput || isSending) return; // Prevent sending empty messages or double sending

        setIsSending(true); // Disable input/button
        setAutoScroll(true); // Ensure scroll happens

        const userMessage = {
            id: uuidv4(),
            text: trimmedInput,
            sender: 'user',
        };
        setMessages((prev) => [...prev, userMessage]);
        setUserInput(""); // Clear input immediately

        // Prepare bot message placeholder
        const botMessageId = uuidv4();
        setMessages((prev) => [...prev, { id: botMessageId, text: "در حال پردازش...", sender: 'bot' }]); // Placeholder text

        try {
            // --- Placeholder: Add Auth Token if required by backend ---
            // const token = localStorage.getItem('authToken'); // Example
            // const headers = {
            //     "Content-Type": "application/json",
            //     // 'Authorization': `Bearer ${token}` // Example auth header
            // };

            const response = await fetch("http://130.185.77.114:8111/api/search-stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" }, // Use headers variable if auth is added
                body: JSON.stringify({ query: trimmedInput, top_k: 20 }),
            });

            if (!response.ok || !response.body) {
                throw new Error(`Network error: Status ${response.status}`);
            }

            // Read the response as a stream.
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let botText = "";

            // Clear placeholder text before streaming starts
            setMessages((prevMessages) =>
                prevMessages.map((msg) => {
                    if (msg.id === botMessageId) {
                        return { ...msg, text: "" }; // Clear the "در حال پردازش..."
                    }
                    return msg;
                })
            );


            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                botText += chunk;
                // Update the bot message content incrementally
                setMessages((prevMessages) =>
                    prevMessages.map((msg) => {
                        if (msg.id === botMessageId) {
                            // Append chunk to existing text for the streaming message
                            return { ...msg, text: botText };
                        }
                        return msg;
                    })
                );
            }
        } catch (error) {
            console.error("Streaming error:", error);
            // Update the specific bot message with the error
            setMessages((prevMessages) =>
                prevMessages.map((msg) => {
                    if (msg.id === botMessageId) {
                        return { ...msg, text: `خطایی در دریافت پاسخ رخ داد: ${error.message}` };
                    }
                    return msg;
                })
            );
        } finally {
            setIsSending(false); // Re-enable input/button
        }
    };

    // Handle Enter key press.
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isSending) { // Also check isSending here
            e.preventDefault();
            handleSend();
        }
    };

    // Handlers for About Us dialog.
    const handleAboutOpen = () => setAboutOpen(true);
    const handleAboutClose = () => setAboutOpen(false);

    // Handler for Logout
    const handleLogout = () => {
        auth.logout();
        // No need to navigate here explicitly, ProtectedRoute and RootRedirect handle it.
        // navigate('/login'); // Can keep for explicitness if preferred
    };


    return (
        <Box
            display="flex"
            flexDirection="column"
            width="100%" // Occupy full width of parent
            height="100%" // Occupy full height of parent (e.g., 100vh in App.js)
            maxWidth={isLargeScreen ? "1200px" : "100%"} // Optional max width for large screens
            margin="0 auto" // Center if maxWidth is applied
            sx={{
                backgroundColor: "#fff",
                borderRadius: { xs: 0, sm: 2 }, // No rounded corners on mobile edge-to-edge
                boxShadow: { xs: 0, sm: 3 },     // No shadow on mobile edge-to-edge
                overflow: 'hidden', // Prevent this main box from scrolling, children will scroll
            }}
        >
            {/* Header */}
            <Paper
                elevation={3}
                square={isSmallScreen} // Remove rounded corners if flush with edges
                sx={{
                    backgroundColor: "#0b3d91",
                    p: 2,
                    flexShrink: 0, // Prevent header from shrinking
                    // borderTopLeftRadius: isSmallScreen ? 0 : 'inherit', // Match parent border radius
                    // borderTopRightRadius: isSmallScreen ? 0 : 'inherit',
                }}
            >
                {isSmallScreen ? (
                    // Mobile layout: stacked rows + last row adjusted
                    <>
                        {/* Row 1: Main Title */}
                        <Box sx={{ width: "100%", mb: 1, display: "flex", justifyContent: "center" }}>
                            <Typography variant="h5" sx={{ color: "#fff", textAlign: "center" }}>
                                گزارش‌یار هوشمند ایپکو
                            </Typography>
                        </Box>

                        {/* Row 2: API Data Count */}
                        <Box sx={{ width: "100%", mb: 0.5, display: "flex", justifyContent: "center" }}>
                            <Typography variant="caption" sx={{ color: "#eee", textAlign: "center" }}>
                                تعداد خرابی ها: {apiInfo?.data_count || "-"}
                            </Typography>
                        </Box>

                        {/* Row 3: API Update Time & Version */}
                        <Box sx={{ width: "100%", mb: 1, display: "flex", justifyContent: "center", gap: 1 }}>
                            <Typography variant="caption" sx={{ color: "#eee", textAlign: "center" }}>
                                به‌روزرسانی: {apiInfo?.data_update_time || "-"}
                            </Typography>
                            <Typography variant="caption" sx={{ color: "#eee", textAlign: "center" }}>
                                نسخه: {apiInfo?.version || "-"}
                            </Typography>
                        </Box>

                        {/* Row 4: Logo, Buttons */}
                        <Box
                            sx={{
                                width: "100%",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: 'space-between', // Space out items
                                mt: 1,
                            }}
                        >
                            {/* Left: Logout */}
                            <Tooltip title="خروج از حساب">
                                {/* Add padding compensation if needed */}
                                <IconButton onClick={handleLogout} sx={{ color: '#fff', p: 0.5 }}>
                                    <LogoutIcon fontSize="small"/>
                                </IconButton>
                            </Tooltip>

                            {/* Center: Logo */}
                            <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
                                <img src="/logo.png" alt="Logo" height="35" />
                            </Box>

                            {/* Right: About Us */}
                            <Button
                                variant="outlined"
                                onClick={handleAboutOpen}
                                size="small"
                                sx={{
                                    color: "#fff",
                                    borderColor: "#fff",
                                    fontSize: "0.65rem", // Adjusted size
                                    lineHeight: 1.2,
                                    px: 1, py: 0.3, // Adjusted padding
                                    minWidth: 'auto' // Allow button to shrink
                                }}
                            >
                                درباره ما
                            </Button>
                        </Box>
                    </>
                ) : (
                    // Large screens: three-column layout
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                        }}
                    >
                        {/* Left Section: API Info */}
                        <Box sx={{ flex: 1, display: "flex", alignItems: "center", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            <Typography variant="subtitle2" sx={{ color: "#fff", mt: 1 }}>
                                تعداد خرابی های ثبت شده: {apiInfo?.data_count || "..."} | به‌روزرسانی: {apiInfo?.data_update_time || "..."} | نسخه: {apiInfo?.version || "..."}
                            </Typography>
                        </Box>

                        {/* Center Section: Main Title */}
                        <Box sx={{ flex: 1.5, /* Give title slightly more space */ display: "flex", justifyContent: "center", alignItems: "center", px: 2 }}>
                            <Typography variant="h4" sx={{ color: "#fff", textAlign: "center", whiteSpace: 'nowrap' }}>
                                گزارش‌یار هوشمند ایپکو
                            </Typography>
                        </Box>

                        {/* Right Section: Buttons and Logo */}
                        <Box sx={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "flex-end" }}>
                            <Button
                                variant="outlined"
                                onClick={handleAboutOpen}
                                sx={{ color: "#fff", borderColor: "#fff", mr: 2, fontSize: "0.9rem" }} // Slightly smaller font
                            >
                                درباره ما
                            </Button>
                            {/* Logout Button */}
                            <Tooltip title="خروج از حساب">
                                <IconButton onClick={handleLogout} sx={{ color: '#fff', mr: 2 }}>
                                    <LogoutIcon />
                                </IconButton>
                            </Tooltip>
                            {/* Logo */}
                            <Box>
                                <img src="/logo.png" alt="Logo" height="50" /> {/* Slightly smaller logo */}
                            </Box>
                        </Box>
                    </Box>
                )}
            </Paper>

            {/* Messages Area */}
            <Box
                ref={messagesContainerRef}
                flexGrow={1} // Allow this area to expand and take available vertical space
                p={2}
                overflow="auto" // Enable scrolling ONLY for this message area
                display="flex"
                flexDirection="column"
                gap={2}
                onScroll={handleScroll}
                sx={{
                    backgroundColor: "#f7f9fc", // Light background for message area
                    // Custom scrollbar styles
                    "&::-webkit-scrollbar": { width: '8px' },
                    "&::-webkit-scrollbar-track": { background: 'transparent' },
                    "&::-webkit-scrollbar-thumb": { backgroundColor: 'rgba(0, 0, 0, 0.2)', borderRadius: '4px' },
                    scrollbarWidth: 'thin',
                    scrollbarColor: 'rgba(0, 0, 0, 0.2) transparent'
                }}
            >
                {messages.map((msg) => {
                    const isUser = msg.sender === 'user';
                    return (
                        <Box
                            key={msg.id}
                            // Align user left (start), bot right (end) to match input direction
                            alignSelf={isUser ? "flex-start" : "flex-end"}
                            maxWidth={isSmallScreen ? "90%" : "75%"} // Max width constraint
                            p={1.5} // Padding inside message bubble
                            borderRadius={2} // Standard border radius
                            sx={{
                                backgroundColor: isUser ? "#0b3d91" : "#e0e0e0", // User vs Bot bubble color
                                color: isUser ? "#fff" : "#000",        // User vs Bot text color
                                whiteSpace: "pre-wrap", // Preserve line breaks and spaces
                                wordBreak: 'break-word', // Prevent long words from overflowing
                                position: "relative", // Needed for potential future elements like timestamps
                                // Font sizes adjusted based on screen size
                                fontSize: isSmallScreen ? '0.9rem' : '1rem',
                                lineHeight: 1.5, // Improve readability
                                direction: isUser ? 'rtl' : 'rtl', // Ensure text direction is RTL for both
                                textAlign: isUser ? 'right' : 'right', // Align text right for both
                            }}
                        >
                            <ReactMarkdown
                                components={{
                                    // Customize rendering of paragraphs, links, etc. if needed
                                    p: ({ node, ...props }) => (
                                        <Typography
                                            component="span" // Render as span to avoid extra margins
                                            sx={{
                                                // Inherit font size and line height from parent Box
                                                fontSize: 'inherit',
                                                lineHeight: 'inherit',
                                            }}
                                            {...props}
                                        />
                                    ),
                                    // Example: Styling links
                                    a: ({node, ...props}) => <a style={{color: isUser ? '#aed6f1' : '#0d47a1', textDecoration: 'underline'}} {...props} />
                                }}
                            >
                                {msg.text}
                            </ReactMarkdown>
                        </Box>
                    );
                })}
                {/* Invisible element to scroll to */}
                <div ref={messagesEndRef} style={{ height: '1px' }} />
            </Box>

            {/* Input Area */}
            <Paper
                elevation={3} // Keep shadow for separation
                square={isSmallScreen} // Remove rounded corners on mobile if needed
                sx={{
                    display: "flex",
                    alignItems: "center", // Align items vertically center
                    p: isSmallScreen ? 1 : 2, // Less padding on small screens
                    backgroundColor: "#0b3d91",
                    flexShrink: 0, // Prevent input area from shrinking
                    // borderBottomLeftRadius: isSmallScreen ? 0 : 'inherit', // Match parent radius
                    // borderBottomRightRadius: isSmallScreen ? 0 : 'inherit',
                }}
            >
                <TextField
                    variant="outlined"
                    fullWidth
                    multiline // Allow multiline input
                    maxRows={4} // Limit vertical expansion
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="متن جست‌وجو را وارد کنید..."
                    disabled={isSending} // Disable when sending
                    sx={{
                        backgroundColor: "#fff",
                        borderRadius: "20px", // More rounded input field
                        mr: 1, // Margin between text field and button
                        '& .MuiOutlinedInput-root': {
                            borderRadius: "20px", // Ensure root also has radius
                            '& fieldset': {
                                borderColor: 'transparent', // Hide default border
                            },
                            '&:hover fieldset': {
                                borderColor: 'rgba(0, 0, 0, 0.1)', // Slight border on hover
                            },
                            '&.Mui-focused fieldset': {
                                borderColor: '#0b3d91', // Border color when focused
                            },
                        },
                        input: {
                            textAlign: "right",
                            fontSize: isSmallScreen ? '0.9rem' : '1rem', // Adjust font size
                            padding: isSmallScreen ? '10px 14px' : '12px 16px', // Adjust padding
                        },
                        textarea: { // Style textarea specifically for multiline
                            textAlign: "right",
                            fontSize: isSmallScreen ? '0.9rem' : '1rem',
                            padding: isSmallScreen ? '10px 14px' : '12px 16px',
                            lineHeight: 1.4, // Improve multiline readability
                        }
                    }}
                    size={isSmallScreen ? "small" : "medium"}
                />
                <Button
                    variant="contained"
                    onClick={handleSend}
                    disabled={isSending || !userInput.trim()} // Disable if sending or input is empty/whitespace
                    sx={{
                        backgroundColor: isSending ? "#cccccc" : "#0056b3", // Different color when disabled/sending
                        ":hover": { backgroundColor: isSending ? "#cccccc" : "#004494" }, // Adjust hover color
                        fontSize: isSmallScreen ? '0.9rem' : '1rem',
                        px: isSmallScreen ? 2 : 3,
                        py: isSmallScreen ? 0.8 : 1.2, // Adjust padding
                        borderRadius: '20px', // Match text field rounding
                        minWidth: 'auto', // Allow button to shrink if needed
                        ml: 1, // Ensure margin from text field
                    }}
                    size={isSmallScreen ? "small" : "medium"}
                >
                    {isSending ? "..." : "ارسال"} {/* Change text while sending */}
                </Button>
            </Paper>

            {/* About Us Dialog */}
            <Dialog open={aboutOpen} onClose={handleAboutClose} maxWidth="sm" fullWidth>
                <DialogTitle sx={{ fontSize: isSmallScreen ? '1.1rem' : '1.3rem', textAlign: 'right', borderBottom: '1px solid #eee' }}>
                    درباره گزارش‌یار هوشمند ایپکو
                </DialogTitle>
                <DialogContent sx={{ pt: 2 }}> {/* Add padding top */}
                    <DialogContentText
                        component="div" // Use div to contain multiple paragraphs
                        sx={{
                            fontSize: isSmallScreen ? '0.9rem' : '1rem',
                            lineHeight: 1.6, // Increase line height for readability
                            textAlign: 'right',
                            color: '#333' // Darker text color
                        }}
                    >
                        <p><strong>مدیران پروژه:</strong> امیرحسین پریور، سیامک علیزاده نیا</p>
                        <p><strong>توسعه‌دهندگان:</strong> عرفان شهمیری، محمدباربد امیرمزلقانی</p>
                        <p><strong>با تشکر از:</strong> امین قدیرزاده و نیما عجمی</p>
                        <p style={{ marginTop: '16px' }}> {/* Add space before description */}
                            این دستیار هوشمند با بهره‌گیری از روش بازیابی اطلاعات پیشرفته (RAG) و مدل‌های زبانی بزرگ (LLM)،
                            اطلاعات فنی مورد نیاز را از بانک داده‌های تخصصی ایپکو استخراج و ارائه می‌دهد.
                            هدف ما کمک به تشخیص سریع‌تر و دقیق‌تر مشکلات و ارائه راهکارهای مرتبط است.
                        </p>
                        <p style={{ marginTop: '16px', fontSize: '0.85em', color: '#666' }}> {/* Version/info in footer style */}
                            نسخه: {apiInfo?.version || "-"} | به‌روزرسانی داده: {apiInfo?.data_update_time || "-"}
                        </p>
                    </DialogContentText>
                </DialogContent>
                <DialogActions sx={{ padding: '8px 24px' }}>
                    <Button
                        onClick={handleAboutClose}
                        variant='contained' // Make button more prominent
                        sx={{ fontSize: isSmallScreen ? '0.9rem' : '1rem' }}
                    >
                        بستن
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ChatContainer;