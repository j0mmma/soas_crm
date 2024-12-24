import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import '../styles.css';

const TeamInfo = () => {
  const [teamData, setTeamData] = useState(null);
  const [error, setError] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newTeamName, setNewTeamName] = useState('');
  const [message, setMessage] = useState('');
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('jwt');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUserId(decoded.user_id);
      } catch (err) {
        console.error('Error decoding token:', err);
        setError('Invalid or expired token. Please log in again.');
        return;
      }
    }

    const fetchTeamInfo = async () => {
      try {
        if (!token) {
          setError('No token found. Please log in.');
          return;
        }
        const response = await axios.get('http://localhost:5000/teams/my-team', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setTeamData(response.data);
      } catch (err) {
        if (err.response?.status === 404) {
          setError('You are not part of any team.');
        } else if (err.response?.status === 401) {
          setError('You are not authorized. Please log in.');
        } else {
          setError('Error fetching team information.');
        }
      }
    };

    fetchTeamInfo();
  }, []);

  const handleAddUser = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const token = localStorage.getItem('jwt');
      const response = await axios.post(
        'http://localhost:5000/teams/add-user',
        { email: newUserEmail },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage(response.data.message);
      setNewUserEmail('');
      const updatedTeamResponse = await axios.get('http://localhost:5000/teams/my-team', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTeamData(updatedTeamResponse.data);
    } catch (err) {
      if (err.response?.status === 400) {
        setMessage('Invalid email. Please enter a valid email address.');
      } else if (err.response?.status === 404) {
        setMessage('User does not exist.');
      } else if (err.response?.status === 403) {
        setMessage('User is already in a team.');
      } else {
        setMessage('An error occurred while adding the user.');
      }
    }
  };

  const handleRemoveUser = async (idToRemove) => {
    try {
      const token = localStorage.getItem('jwt');
      const response = await axios.post(
        'http://localhost:5000/teams/remove-user',
        { team_id: teamData.team_id, user_id: idToRemove },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage(response.data.message);
      const updatedTeamResponse = await axios.get('http://localhost:5000/teams/my-team', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTeamData(updatedTeamResponse.data);
    } catch (err) {
      setMessage(err.response?.data?.message || 'An error occurred while removing the user.');
    }
  };

  const handleDeleteTeam = async () => {
    const confirmDelete = window.confirm('Are you sure you want to delete this team? This action cannot be undone.');
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem('jwt');
      const response = await axios.delete('http://localhost:5000/teams/delete', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        data: { team_id: teamData.team_id },
      });
      setMessage(response.data.message);
      setTeamData(null); // Clear team data after deletion
      setError('You have successfully deleted your team.');
    } catch (err) {
      setMessage(err.response?.data?.message || 'An error occurred while deleting the team.');
    }
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const token = localStorage.getItem('jwt');
      const response = await axios.post(
        'http://localhost:5000/teams/new',
        { name: newTeamName },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage('Team created successfully!');
      setNewTeamName('');
      const updatedTeamResponse = await axios.get('http://localhost:5000/teams/my-team', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTeamData(updatedTeamResponse.data);
    } catch (err) {
      if (err.response?.status === 400) {
        setMessage('Invalid team name. Please try again.');
      } else {
        setMessage('An error occurred while creating the team.');
      }
    }
  };

  if (error) {
    return (
      <div>
        <p>{error}</p>
        {error === 'You are not part of any team.' && (
          <form onSubmit={handleCreateTeam}>
            <input
              type="text"
              placeholder="Enter new team name"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              required
            />
            <button type="submit">Create Team</button>
          </form>
        )}
      </div>
    );
  }

  if (!teamData) return <p>Loading team info...</p>;

  return (
    <div>
      <h2>Team Information</h2>
      <p>
        <strong>Team Name:</strong> {teamData.team_name}
      </p>
      <p>
        <strong>Owner:</strong> {teamData.owner_name}
      </p>
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {teamData.members.map((member) => (
            <tr key={member.user_id}>
              <td>{member.username}</td>
              <td>{member.email}</td>
              <td>{member.role_name}</td>
              <td>{member.status_name}</td>
              <td>
                {member.user_id !== teamData.owner_id && teamData.members.some(
                  (m) => m.user_id === userId && m.role_name === 'Admin'
                ) && (
                  <button onClick={() => handleRemoveUser(member.user_id)}>Remove</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {teamData.owner_id === userId && (
        <div>
          <button onClick={handleDeleteTeam}>Delete Team</button>
        </div>
      )}
      {teamData.members.some((m) => m.user_id === userId && m.role_name === 'Admin') ? (
        <div>
          <h3>Add User to Team</h3>
          <form onSubmit={handleAddUser}>
            <input
              type="email"
              placeholder="Enter user email"
              value={newUserEmail}
              onChange={(e) => setNewUserEmail(e.target.value)}
              required
            />
            <button type="submit">Add User</button>
          </form>
          {message && <p>{message}</p>}
        </div>
      ) : (
        <p>You do not have permission to add users to this team.</p>
      )}
    </div>
  );
};

export default TeamInfo;
