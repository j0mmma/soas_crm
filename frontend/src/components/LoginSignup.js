import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {jwtDecode} from 'jwt-decode';

import '../styles.css';

const LoginSignup = ({ isLogin, onAuthChange = () => {} }) => {
  const [formData, setFormData] = useState({ email: '', password: '', username: '' });
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Form data submitted:", formData); // Debug log
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const response = await axios.post(`http://localhost:5000${endpoint}`, formData);

      console.log("Server response:", response.data); // Debug log

      const token = response.data.token; // JWT token returned from the backend
      if (token) {
        console.log("Decoded token:", jwtDecode(token)); // Log decoded token
        localStorage.setItem('jwt', token); // Store JWT in localStorage
        setMessage(isLogin ? 'Login successful!' : 'Signup and login successful!');
        onAuthChange(); // Notify App component about auth change
        navigate('/'); // Redirect to the home page
      } else {
        setMessage(response.data.message);
      }
    } catch (error) {
      console.error("Error occurred during request:", error); // Debug log
      setMessage(error.response?.data?.message || 'An error occurred.');
    }
  };

  return (
    <div>
      <h2>{isLogin ? 'Login' : 'Signup'}</h2>
      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
          />
        )}
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
        />
        <button type="submit">{isLogin ? 'Login' : 'Signup'}</button>
      </form>
      {message && <p>{message}</p>}
      <p>
        {isLogin ? (
          <span>
            Don't have an account? <a href="/signup">Signup</a>
          </span>
        ) : (
          <span>
            Already have an account? <a href="/login">Login</a>
          </span>
        )}
      </p>
    </div>
  );
};

export default LoginSignup;
