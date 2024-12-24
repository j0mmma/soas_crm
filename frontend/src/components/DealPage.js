import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

import '../styles.css';

const DealPage = () => {
  const { id } = useParams(); // Correctly access route params
  const [deal, setDeal] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [newContact, setNewContact] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
  });
  const [ownerName, setOwnerName] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchDealDetails = async () => {
      try {
        const token = localStorage.getItem('jwt');

        // Fetch deal details from the deals service
        const dealResponse = await axios.get(`http://localhost:5001/deals/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setDeal(dealResponse.data);

        // Fetch contacts associated with the deal
        const contactsResponse = await axios.get(`http://localhost:5001/contacts/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setContacts(contactsResponse.data);

        // Fetch the owner's name from the users service
        const ownerResponse = await axios.get(`http://localhost:5000/users/${dealResponse.data.owner_id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setOwnerName(ownerResponse.data.username);
      } catch (error) {
        console.error('Error fetching deal, contacts, or owner:', error);
      }
    };

    fetchDealDetails();
  }, [id]);

  const handleAddContact = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const token = localStorage.getItem('jwt');

      // Add a new contact to the deal
      const response = await axios.post(
        `http://localhost:5001/contacts/create`,
        { ...newContact, deal_id: id },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage('Contact added successfully!');
      setNewContact({ firstName: '', lastName: '', email: '', phone: '' });

      // Refresh the contacts list
      const updatedContacts = await axios.get(`http://localhost:5001/contacts/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setContacts(updatedContacts.data);
    } catch (error) {
      setMessage(error.response?.data?.message || 'An error occurred while adding the contact.');
    }
  };

  if (!deal) return <p>Loading deal details...</p>;

  return (
    <div>
      <h2>Deal Details</h2>
      <p>
        <strong>Title:</strong> {deal.title}
      </p>
      <p>
        <strong>Stage:</strong> {deal.stage_name}
      </p>
      <p>
        <strong>Owner:</strong> {ownerName}
      </p>
      <h3>Contacts</h3>
      <ul>
        {contacts.map((contact) => (
          <li key={contact.contact_id}>
            {contact.firstName} {contact.lastName} ({contact.email}, {contact.phone})
          </li>
        ))}
      </ul>
      <h3>Add New Contact</h3>
      <form onSubmit={handleAddContact}>
        <input
          type="text"
          placeholder="First Name"
          value={newContact.firstName}
          onChange={(e) => setNewContact({ ...newContact, firstName: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Last Name"
          value={newContact.lastName}
          onChange={(e) => setNewContact({ ...newContact, lastName: e.target.value })}
        />
        <input
          type="email"
          placeholder="Email"
          value={newContact.email}
          onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
          required
        />
        <input
          type="tel"
          placeholder="Phone"
          value={newContact.phone}
          onChange={(e) => setNewContact({ ...newContact, phone: e.target.value })}
        />
        <button type="submit">Add Contact</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default DealPage;
