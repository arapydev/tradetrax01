import { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000/accounts/';

function App() {
  const [accounts, setAccounts] = useState([]);
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    broker: '',
    account_number: '',
    balance: 0,
    api_key: '',
    api_secret: '',
    is_active: true,
  });

  // Función para obtener las cuentas de la API
  const fetchAccounts = async () => {
    try {
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error('La respuesta de la red no fue exitosa');
      const data = await response.json();
      setAccounts(data);
    } catch (error) {
      setError(error.message);
    }
  };

  // Obtener las cuentas una vez al cargar la página
  useEffect(() => {
    fetchAccounts();
  }, []);

  // Manejar cambios en los inputs del formulario
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // Limpiar el formulario y cancelar el modo de edición
  const resetForm = () => {
    setFormData({ name: '', broker: '', account_number: '', balance: 0, api_key: '', api_secret: '', is_active: true });
    setEditingId(null);
  };

  // Manejar el envío del formulario (Crear o Actualizar)
  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = editingId ? `${API_URL}${editingId}` : API_URL;
    const method = editingId ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, balance: parseFloat(formData.balance) }),
      });
      if (!response.ok) throw new Error(`Error al ${editingId ? 'actualizar' : 'crear'} la cuenta`);
      
      resetForm();
      fetchAccounts(); 
    } catch (error) {
      setError(error.message);
    }
  };

  // Manejar la eliminación de una cuenta
  const handleDelete = async (accountId) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar esta cuenta?")) {
      return;
    }
    try {
      const response = await fetch(`${API_URL}${accountId}`, {
        method: 'DELETE',
      });
      if (response.status !== 204) {
        throw new Error('Error al eliminar la cuenta');
      }
      setAccounts(prevAccounts => prevAccounts.filter(acc => acc.id !== accountId));
    } catch (error) {
      setError(error.message);
    }
  };

  // Cargar datos de una cuenta en el formulario para editar
  const handleEdit = (account) => {
    setEditingId(account.id);
    setFormData(account);
  };

  return (
    <>
      <h1>Panel de Control del Fondo</h1>

      <div className="form-container">
        <h2>{editingId ? 'Editando Cuenta' : 'Crear Nueva Cuenta'}</h2>
        <form onSubmit={handleSubmit}>
          <input name="name" value={formData.name} onChange={handleInputChange} placeholder="Nombre de la Cuenta" required />
          <input name="broker" value={formData.broker} onChange={handleInputChange} placeholder="Bróker" required />
          <input name="account_number" value={formData.account_number} onChange={handleInputChange} placeholder="Número de Cuenta" required />
          <input name="balance" type="number" value={formData.balance} onChange={handleInputChange} placeholder="Balance" required />
          <input name="api_key" value={formData.api_key} onChange={handleInputChange} placeholder="API Key" required />
          <input name="api_secret" value={formData.api_secret} onChange={handleInputChange} placeholder="API Secret" required />
          <label>
            <input name="is_active" type="checkbox" checked={formData.is_active} onChange={handleInputChange} />
            Activa
          </label>
          <button type="submit">{editingId ? 'Actualizar Cuenta' : 'Crear Cuenta'}</button>
          {editingId && <button type="button" className="cancel-btn" onClick={resetForm}>Cancelar</button>}
        </form>
      </div>

      <h2>Cuentas de Trading</h2>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      <div className="card-container">
        {accounts.map(account => (
          <div key={account.id} className="card">
            <h3>{account.name}</h3>
            <p><strong>Bróker:</strong> {account.broker}</p>
            <p><strong>Número:</strong> {account.account_number}</p>
            <p><strong>Balance:</strong> ${parseFloat(account.balance).toFixed(2)}</p>
            <p><strong>Estado:</strong> {account.is_active ? 'Activa' : 'Inactiva'}</p>
            <div className="card-actions">
              <button onClick={() => handleEdit(account)}>Editar</button>
              <button className="delete-btn" onClick={() => handleDelete(account.id)}>Eliminar</button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default App;