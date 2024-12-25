import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {jwtDecode} from 'jwt-decode';

import '../styles.css'

const UserInfo = () => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('jwt');
    if (!token) return;

    try {
      const decodedToken = jwtDecode(token);
      const userId = decodedToken.user_id;

      axios
        .get(`http://localhost:5000/users/${userId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => setUserData(response.data))
        .catch((error) => console.error('Error fetching user data:', error));
    } catch (error) {
      console.error('Invalid token:', error);
    }
  }, []);

  if (!userData) return <p>Loading user info...</p>;

  return (
    <div className='main-container'>
      <h2>User Info</h2>
      <p>
        <strong>Username:</strong> {userData.username}
      </p>
      <p>
        <strong>Email:</strong> {userData.email}
      </p>
    </div>
  );
};

export default UserInfo;
