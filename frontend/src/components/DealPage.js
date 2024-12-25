import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

import '../styles.css';

const DealPage = () => {
  const { id } = useParams(); // Correctly access route params
  const [deal, setDeal] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [newContact, setNewContact] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    due: '',
    assignee_id: '', // Added field for assignee
  });
  const [ownerName, setOwnerName] = useState('');
  const [message, setMessage] = useState('');
  const [assigneeNames, setAssigneeNames] = useState({});

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
  
        // Fetch tasks associated with the deal
        const tasksResponse = await axios.get(`http://localhost:5001/tasks/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
  
        const tasks = tasksResponse.data;
  
        // Fetch assignee names for tasks
        const names = {};
        await Promise.all(
          tasks.map(async (task) => {
            if (task.assignee_id && !names[task.assignee_id]) {
              try {
                console.log(`Fetching assignee name for ID: ${task.assignee_id}`);
                const assigneeResponse = await axios.get(`http://localhost:5000/users/${task.assignee_id}`, {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                });
                console.log(`Assignee name fetched: ${assigneeResponse.data.username}`);
                names[task.assignee_id] = assigneeResponse.data.username;
              } catch (error) {
                console.error(`Error fetching assignee with ID ${task.assignee_id}:`, error);
              }
            }
          })
        );
  
        setTasks(tasks);
        setAssigneeNames(names);
  
        // Fetch the owner's name from the users service
        const ownerResponse = await axios.get(`http://localhost:5000/users/${dealResponse.data.owner_id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setOwnerName(ownerResponse.data.username);
      } catch (error) {
        console.error('Error fetching deal, contacts, tasks, or owner:', error);
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
      setNewContact({ first_name: '', last_name: '', email: '', phone: '' });

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

  const handleRemoveContact = async (contactId) => {
    const confirmDelete = window.confirm('Are you sure you want to delete this contact? This action cannot be undone.');
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem('jwt');
      await axios.delete(`http://localhost:5001/contacts/delete/${contactId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setMessage('Contact deleted successfully!');

      // Refresh the contacts list
      const updatedContacts = contacts.filter((contact) => contact.contact_id !== contactId);
      setContacts(updatedContacts);
    } catch (error) {
      setMessage('Error deleting contact. Please try again.');
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const token = localStorage.getItem('jwt');
  
      // Decode the token to extract the current user's ID
      const decodedToken = JSON.parse(atob(token.split('.')[1]));
      const currentUserId = decodedToken.user_id;
  
      // Add a new task to the deal with the current user as assignee
      const response = await axios.post(
        `http://localhost:5001/tasks/create`,
        { ...newTask, deal_id: id, assignee_id: currentUserId },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
  
      setMessage('Task added successfully!');
      setNewTask({ title: '', description: '', due: '' });
  
      // Refresh the tasks list
      const updatedTasks = await axios.get(`http://localhost:5001/tasks/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTasks(updatedTasks.data);
    } catch (error) {
      setMessage(error.response?.data?.message || 'An error occurred while adding the task.');
    }
  };
  

  const handleRemoveTask = async (taskId) => {
    const confirmDelete = window.confirm('Are you sure you want to delete this task? This action cannot be undone.');
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem('jwt');
      await axios.delete(`http://localhost:5001/tasks/delete/${taskId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setMessage('Task deleted successfully!');

      // Refresh the tasks list
      const updatedTasks = tasks.filter((task) => task.id !== taskId);
      setTasks(updatedTasks);
    } catch (error) {
      setMessage('Error deleting task. Please try again.');
    }
  };
  
  const handleUpdateTaskStatus = async (taskId, currentStatus) => {
    try {
      const token = localStorage.getItem('jwt');
      await axios.patch(
        `http://localhost:5001/tasks/update-status/${taskId}`,
        { done: !currentStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, done: !currentStatus } : task
        )
      );
    } catch (error) {
      console.error('Error updating task status:', error);
      setMessage('Failed to update task status');
    }
  };


  if (!deal) return <p>Loading deal details...</p>;

  return (
    <div className='main-container deal-info-container'>
        <div className='deal-info'>
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
        </div>
        <div className='deal-tasks'>
        <h3>Tasks</h3>
        <details>
                <summary>
                    Add New Task
                </summary>
                <form onSubmit={handleAddTask}>
                    <input
                    type="text"
                    placeholder="Task Title"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    required
                    />
                    <textarea
                    placeholder="Task Description"
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                    />
                    <input
                    type="date"
                    value={newTask.due}
                    onChange={(e) => setNewTask({ ...newTask, due: e.target.value })}
                    />
                    <button type="submit">Add Task</button>
                </form>
                {message && <p>{message}</p>}
            </details>
            <ul>
                {tasks.map((task) => (
                <li key={task.id} className='deal-task-card'>
                    <h4>
                        {task.title}
                    </h4>
                    <p>
                        Status: {task.done ? 'Completed' : 'TODO'}
                    </p>
                    <p>
                        Due: {new Date(task.due).toLocaleDateString()}
                    </p>
                    <p>Assigned to: {assigneeNames[task.assignee_id] || 'Unknown'}</p>
                    <div className='task-buttons'>
                        <button onClick={() => handleUpdateTaskStatus(task.id, task.done)}>
                            Mark as {task.done ? 'TODO' : 'Completed'}
                        </button>
                        <button onClick={() => handleRemoveTask(task.id)}>Delete</button>
                    </div>
                </li>
                ))}
            </ul>
            

        </div>
        <div className='deal-contacts'>
            <h3>Contacts</h3>
            <details>
                <summary>
                    Add New Contact

                </summary>
                <form onSubmit={handleAddContact}>
                    <input
                    type="text"
                    placeholder="First Name"
                    value={newContact.first_name}
                    onChange={(e) => setNewContact({ ...newContact, first_name: e.target.value })}
                    required
                    />
                    <input
                    type="text"
                    placeholder="Last Name"
                    value={newContact.last_name}
                    onChange={(e) => setNewContact({ ...newContact, last_name: e.target.value })}
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
            </details>
            <ul>
                {contacts.map((contact) => (
                <li key={contact.contact_id} className='deal-contacts-list'>
                    <div>
                        <h4>
                            {contact.first_name} {contact.last_name}
                        </h4>
                        <p>
                        Email: {contact.email}
                        </p>
                        <p>
                            Phone:  {contact.phone}
                        </p>
                    </div>
                    <button onClick={() => handleRemoveContact(contact.contact_id)}>Delete</button>
                </li>
                ))}
            </ul>
            
        </div>
    </div>
  );
};

export default DealPage;
