import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import LoginSignup from './components/LoginSignup';
import UserInfo from './components/UserInfo';

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
              <Link to="/user">User Page</Link>
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
  const isAuthenticated = !!localStorage.getItem('userId');

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/auth/logout'); // Call the logout endpoint
      localStorage.removeItem('userId'); // Clear userId from localStorage
      window.location.href = '/login'; // Redirect to login page
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <Router>
      <Header isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<div>Home Page</div>} />
        <Route path="/login" element={<LoginSignup isLogin={true} />} />
        <Route path="/signup" element={<LoginSignup isLogin={false} />} />
        <Route path="/user" element={isAuthenticated ? <UserInfo /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;
