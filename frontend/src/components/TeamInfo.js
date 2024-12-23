import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles.css';

// Component to display team members
const TeamMembers = ({ teamId }) => {
  const [members, setMembers] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/teams/${teamId}/members`);
        setMembers(response.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Error fetching members');
      }
    };

    fetchMembers();
  }, [teamId]);

  return (
    <div>
      <h3>Team Members</h3>
      {error ? (
        <p className="error">{error}</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id}>
                <td>{member.id}</td>
                <td>{member.username}</td>
                <td>{member.email}</td>
                <td>{member.role_id === 2 ? 'Admin' : 'Member'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

// Component to display team details
const TeamInfo = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await axios.get('http://localhost:5000/teams/');
        setTeams(response.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Error fetching teams');
      }
    };

    fetchTeams();
  }, []);

  return (
    <div className="team-info-container">
      <h2>Teams</h2>
      {error ? (
        <p className="error">{error}</p>
      ) : (
        <div>
          <ul>
            {teams.map((team) => (
              <li key={team.id}>
                <button onClick={() => setSelectedTeamId(team.id)}>
                  {team.name} (Owner: {team.owner_name})
                </button>
              </li>
            ))}
          </ul>
          {selectedTeamId && <TeamMembers teamId={selectedTeamId} />}
        </div>
      )}
    </div>
  );
};

export default TeamInfo;
