import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import {jwtDecode} from 'jwt-decode';
import '../styles.css';

const DealsList = () => {
  const [deals, setDeals] = useState([]);
  const [error, setError] = useState('');
  const [stages, setStages] = useState([]);
  const [newDeal, setNewDeal] = useState({
    title: '',
    stage_id: '',
  });
  const [message, setMessage] = useState('');
  const [currentUserId, setCurrentUserId] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('jwt');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setCurrentUserId(decoded.user_id);
      } catch (err) {
        console.error('Error decoding token:', err);
      }
    }

    const fetchDealsAndStages = async () => {
      try {
        if (!token) return;

        // Fetch stages
        const stagesResponse = await axios.get('http://localhost:5001/deals/stages', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setStages(stagesResponse.data);

        // Fetch deals
        const dealsResponse = await axios.get('http://localhost:5001/deals/all', {
          headers: { Authorization: `Bearer ${token}` },
        });

        // Enrich deals with owner names and stage names
        const enrichedDeals = await Promise.all(
          dealsResponse.data.map(async (deal) => {
            const ownerResponse = await axios.get(`http://localhost:5000/users/${deal.owner_id}`, {
              headers: { Authorization: `Bearer ${token}` },
            });

            const stageName = stagesResponse.data.find((stage) => stage.id === deal.stage_id)?.name || 'Unknown';

            return {
              ...deal,
              owner_name: ownerResponse.data.username,
              stage_name: stageName,
            };
          })
        );

        setDeals(enrichedDeals);
      } catch (err) {
        setError('Error fetching deals or stages.');
      }
    };

    fetchDealsAndStages();
  }, []);

  const handleCreateDeal = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const token = localStorage.getItem('jwt');
      await axios.post(
        'http://localhost:5001/deals/create',
        newDeal,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setMessage('Deal created successfully!');
      setNewDeal({ title: '', stage_id: '' });

      // Refresh deals list
      const fetchUpdatedDeals = async () => {
        const updatedDealsResponse = await axios.get('http://localhost:5001/deals/all', {
          headers: { Authorization: `Bearer ${token}` },
        });

        const updatedDeals = await Promise.all(
          updatedDealsResponse.data.map(async (deal) => {
            const ownerResponse = await axios.get(`http://localhost:5000/users/${deal.owner_id}`, {
              headers: { Authorization: `Bearer ${token}` },
            });

            const stageName = stages.find((stage) => stage.id === deal.stage_id)?.name || 'Unknown';

            return {
              ...deal,
              owner_name: ownerResponse.data.username,
              stage_name: stageName,
            };
          })
        );

        setDeals(updatedDeals);
      };

      fetchUpdatedDeals();
    } catch (err) {
      setMessage('Error creating deal. Please check the details.');
    }
  };

  const handleRemoveDeal = async (dealId) => {
    const confirmDelete = window.confirm('Are you sure you want to delete this deal? This action cannot be undone.');
    if (!confirmDelete) return;
  
    try {
      const token = localStorage.getItem('jwt');
      console.log('Token:', token);
      console.log('Attempting to delete deal with ID:', dealId);
  
      // Send delete request with the deal ID in the URL
      const response = await axios.delete(`http://localhost:5001/deals/delete/${dealId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
  
      console.log('Delete response:', response.data);
  
      setMessage('Deal deleted successfully!');
  
      // Refresh deals list
      const updatedDeals = deals.filter((deal) => deal.id !== dealId);
      console.log('Updated deals after deletion:', updatedDeals);
      setDeals(updatedDeals);
    } catch (err) {
      console.error('Error during deal deletion:', err);
      console.error('Error response data:', err.response?.data);
      setMessage('Error deleting deal. Please try again.');
    }
  };
  

  return (
    <div className='main-container'>
      <h2>Deals</h2>

      {/* Form to create a new deal */}
      <div className="">
        <form onSubmit={handleCreateDeal}>
          <input
            type="text"
            placeholder="Deal Title"
            value={newDeal.title}
            onChange={(e) => setNewDeal({ ...newDeal, title: e.target.value })}
            required
          />
          <select
            value={newDeal.stage_id}
            onChange={(e) => setNewDeal({ ...newDeal, stage_id: e.target.value })}
            required
          >
            <option value="">Select Stage</option>
            {stages.map((stage) => (
              <option key={stage.id} value={stage.id}>
                {stage.name}
              </option>
            ))}
          </select>
          <button type="submit">Create Deal</button>
        </form>
        {message && <p>{message}</p>}
      </div>

      {/* List of deals */}
      {error ? (
        <p>{error}</p>
      ) : deals.length ? (
        <div className="deal-cards-list">
          {deals.map((deal) => (
            <div key={deal.id} className="deal-card">
              <Link to={`/deals/${deal.id}`}className='deal_info'>
                <h3>{deal.title}</h3>
                <p>Owner: {deal.owner_name}</p>
                <p>Stage: {deal.stage_name}</p>
                <p>Date Created: {new Date(deal.date_created).toLocaleDateString()}</p>
              </Link>
              {deal.owner_id === currentUserId && (
                <button className='deal-remove' onClick={() => handleRemoveDeal(deal.id)}>Delete</button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p>No deals available.</p>
      )}
    </div>
  );
};

export default DealsList;
