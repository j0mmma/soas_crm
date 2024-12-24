import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

import '../styles.css';

const DealsList = () => {
  const [deals, setDeals] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const token = localStorage.getItem('jwt');
        const response = await axios.get('http://localhost:5001/deals/all', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDeals(response.data);
      } catch (err) {
        setError('Error fetching deals.');
      }
    };

    fetchDeals();
  }, []);

  if (error) return <p>{error}</p>;
  if (!deals.length) return <p>No deals available.</p>;

  return (
    <div>
      <h2>Deals</h2>
      <div className='deal-cards-list'>
        {deals.map((deal) => (
          <Link key={deal.id} to={`/deals/${deal.id}`}>
            <div className="deal-card">
              <h3>{deal.title}</h3>
              <p>Stage ID: {deal.stage_id}</p>
              <p>Owner ID: {deal.owner_id}</p>
            </div>
          </Link>
        ))}

      </div>
    </div>
  );
};

export default DealsList;
