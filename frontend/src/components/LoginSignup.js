import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginSignup = ({ isLogin }) => {
  const [formData, setFormData] = useState({ email: '', password: '', username: '' });
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const response = await axios.post(`http://localhost:5000${endpoint}`, formData);
      
      if (isLogin) {
        localStorage.setItem('userId', response.data.user_id); // Store user ID
        setMessage('Login successful!');
        navigate('/user');
      } else {
        setMessage(response.data.message);
      }
    } catch (error) {
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
