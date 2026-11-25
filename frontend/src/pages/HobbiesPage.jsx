import { useEffect, useState } from 'react';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState, Modal, Input, Textarea } from '../components';

export function HobbiesPage() {
  const [hobbies, setHobbies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentId, setCurrentId] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', category: '' });
  const [formErrors, setFormErrors] = useState({});

  const fetchHobbies = async () => {
    setLoading(true);
    try {
      const response = await api.get('/hobbies');
      setHobbies(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load hobbies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHobbies();
  }, []);

  const handleOpenModal = (hobby = null) => {
    if (hobby) {
      setIsEditing(true);
      setCurrentId(hobby.id);
      setFormData({
        name: hobby.name,
        description: hobby.description || '',
        category: hobby.category || '',
      });
    } else {
      setIsEditing(false);
      setFormData({ name: '', description: '', category: '' });
    }
    setFormErrors({});
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({ name: '', description: '', category: '' });
    setFormErrors({});
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.name) errors.name = 'Name is required';
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      if (isEditing) {
        await api.put(`/hobbies/${currentId}`, formData);
      } else {
        await api.post('/hobbies', formData);
      }
      await fetchHobbies();
      handleCloseModal();
    } catch (err) {
      setFormErrors({ form: err.response?.data?.detail || 'Failed to save hobby' });
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this hobby?')) return;
    try {
      await api.delete(`/hobbies/${id}`);
      await fetchHobbies();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete hobby');
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">My Hobbies</h1>
          <p className="text-gray-600 mt-1">Track and manage all your hobbies</p>
        </div>
        <Button variant="primary" onClick={() => handleOpenModal()}>
          + Add Hobby
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {hobbies.length === 0 ? (
        <EmptyState
          icon="🎨"
          title="No Hobbies Yet"
          description="Create your first hobby to get started tracking your interests"
          action={<Button onClick={() => handleOpenModal()}>Add Your First Hobby</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {hobbies.map((hobby) => (
            <Card key={hobby.id}>
              <CardHeader>
                <CardTitle>{hobby.name}</CardTitle>
              </CardHeader>
              <CardContent>
                {hobby.category && (
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-semibold">Category:</span> {hobby.category}
                  </p>
                )}
                {hobby.description && (
                  <p className="text-gray-700 mb-4">{hobby.description}</p>
                )}
                <div className="flex gap-2 mt-4">
                  <Button size="sm" onClick={() => handleOpenModal(hobby)}>
                    Edit
                  </Button>
                  <Button size="sm" variant="danger" onClick={() => handleDelete(hobby.id)}>
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={isEditing ? 'Edit Hobby' : 'Add New Hobby'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formErrors.form && (
            <ErrorAlert message={formErrors.form} />
          )}
          <Input
            label="Hobby Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={formErrors.name}
            required
          />
          <Input
            label="Category"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
          />
          <Textarea
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {isEditing ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
