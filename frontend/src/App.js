import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import {jwtDecode} from 'jwt-decode';
import LoginSignup from './components/LoginSignup';
import UserInfo from './components/UserInfo';

import './styles.css';

const Header = ({ isAuthenticated, onLogout }) => (
  <header>
    <nav>
      <ul>
        {isAuthenticated ? (
          <>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/profile">Profile</Link>
            </li>
            <li>
              <button onClick={onLogout}>Logout</button>
            </li>
          </>
        ) : (
          <li>
            <Link to="/login">Login</Link>
          </li>
        )}
      </ul>
    </nav>
  </header>
);

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('jwt');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        console.log("Decoded token from storage:", decoded); // Debug log
        if (decoded.exp * 1000 > Date.now()) {
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem('jwt');
        }
      } catch (error) {
        console.error("Error decoding token:", error); // Debug log
        localStorage.removeItem('jwt');
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('jwt'); // Clear JWT from localStorage
    setIsAuthenticated(false); // Update authentication state
    window.location.href = '/login'; // Redirect to login page
  };

  return (
    <Router>
      <Header isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<div>Home Page</div>} />
        <Route path="/login" element={<LoginSignup isLogin={true} onAuthChange={() => setIsAuthenticated(true)} />} />
        <Route path="/signup" element={<LoginSignup isLogin={false} onAuthChange={() => setIsAuthenticated(true)} />} />
        <Route
          path="/profile"
          element={isAuthenticated ? <UserInfo /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/login'} />} />
      </Routes>
    </Router>
  );
};

export default App;
