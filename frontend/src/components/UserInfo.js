import React, { useEffect, useState } from 'react';
import axios from 'axios';

const UserInfo = () => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (!userId) return;

    axios
      .get(`http://localhost:5000/users/${userId}`)
      .then((response) => setUserData(response.data))
      .catch((error) => console.error('Error fetching user data:', error));
  }, []);

  if (!userData) return <p>Loading user info...</p>;

  return (
    <div>
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
