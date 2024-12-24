import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import {jwtDecode} from 'jwt-decode';
import LoginSignup from './components/LoginSignup';
import UserInfo from './components/UserInfo';
import TeamInfo from './components/TeamInfo';
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
              <Link to="/my-team">My Team</Link>
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
        if (decoded.exp * 1000 > Date.now()) {
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem('jwt');
        }
      } catch {
        localStorage.removeItem('jwt');
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('jwt');
    setIsAuthenticated(false);
    window.location.href = '/login';
  };

  return (
    <Router>
      <Header isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<div>Home Page</div>} />
        <Route path="/login" element={<LoginSignup isLogin={true} onAuthChange={() => setIsAuthenticated(true)} />} />
        <Route path="/signup" element={<LoginSignup isLogin={false} onAuthChange={() => setIsAuthenticated(true)} />} />
        <Route path="/profile" element={isAuthenticated ? <UserInfo /> : <Navigate to="/login" />} />
        <Route path="/my-team" element={isAuthenticated ? <TeamInfo /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/login'} />} />
      </Routes>
    </Router>
  );
};

export default App;
