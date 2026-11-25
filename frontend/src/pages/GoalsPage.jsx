import { useEffect, useState } from 'react';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState, Modal, Input, Select, Textarea } from '../components';

export function GoalsPage() {
  const [goals, setGoals] = useState([]);
  const [hobbies, setHobbies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updateError, setUpdateError] = useState('');
  const [updatingGoalId, setUpdatingGoalId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isMilestoneModalOpen, setIsMilestoneModalOpen] = useState(false);
  const [selectedGoalId, setSelectedGoalId] = useState(null);
  const [formData, setFormData] = useState({
    hobby_id: '',
    title: '',
    description: '',
    target_hours: '',
  });
  const [milestoneFormData, setMilestoneFormData] = useState({
    title: '',
    description: '',
  });
  const [formErrors, setFormErrors] = useState({});
  const [milestoneFormErrors, setMilestoneFormErrors] = useState({});

  const fetchData = async () => {
    setLoading(true);
    try {
      const [goalsRes, hobbiesRes] = await Promise.all([
        api.get('/goals'),
        api.get('/hobbies'),
      ]);
      setGoals(goalsRes.data);
      setHobbies(hobbiesRes.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenModal = () => {
    setFormData({ hobby_id: '', title: '', description: '', target_hours: '' });
    setFormErrors({});
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({ hobby_id: '', title: '', description: '', target_hours: '' });
    setFormErrors({});
  };

  const handleOpenMilestoneModal = (goalId) => {
    setSelectedGoalId(goalId);
    setMilestoneFormData({ title: '', description: '' });
    setMilestoneFormErrors({});
    setIsMilestoneModalOpen(true);
  };

  const handleCloseMilestoneModal = () => {
    setIsMilestoneModalOpen(false);
    setSelectedGoalId(null);
    setMilestoneFormData({ title: '', description: '' });
    setMilestoneFormErrors({});
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.hobby_id) errors.hobby_id = 'Please select a hobby';
    if (!formData.title) errors.title = 'Title is required';
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
      const data = {
        ...formData,
        target_hours: formData.target_hours ? parseInt(formData.target_hours) : null,
      };
      await api.post('/goals', data);
      await fetchData();
      handleCloseModal();
    } catch (err) {
      setFormErrors({ form: err.response?.data?.detail || 'Failed to create goal' });
    }
  };

  const handleStatusChange = async (goalId, newStatus) => {
    setUpdatingGoalId(goalId);
    try {
      await api.put(`/goals/${goalId}`, { status: newStatus });
      await fetchData();
      setUpdateError('');
    } catch (err) {
      setUpdateError(err.response?.data?.detail || 'Failed to update goal');
    } finally {
      setUpdatingGoalId(null);
    }
  };

  const handleMilestoneSubmit = async (e) => {
    e.preventDefault();
    const errors = {};
    if (!milestoneFormData.title) errors.title = 'Title is required';
    if (Object.keys(errors).length > 0) {
      setMilestoneFormErrors(errors);
      return;
    }

    try {
      const data = {
        goal_id: selectedGoalId,
        title: milestoneFormData.title,
        description: milestoneFormData.description || null,
      };
      await api.post('/milestones', data);
      await fetchData();
      handleCloseMilestoneModal();
    } catch (err) {
      setMilestoneFormErrors({ form: err.response?.data?.detail || 'Failed to create milestone' });
    }
  };

  if (loading) return <Loading />;

  const statusColors = {
    pending: 'bg-gray-100 text-gray-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  };

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Goals</h1>
          <p className="text-gray-600 mt-1">Set and track your practice goals</p>
        </div>
        <Button variant="primary" onClick={handleOpenModal}>
          + Create Goal
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}
      {updateError && <ErrorAlert message={updateError} />}

      {goals.length === 0 ? (
        <EmptyState
          icon="🎯"
          title="No Goals Yet"
          description="Create your first goal to stay motivated"
          action={<Button onClick={handleOpenModal}>Create Your First Goal</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {goals.map((goal) => {
            const hobby = hobbies.find((h) => h.id === goal.hobby_id);
            const isUpdating = updatingGoalId === goal.id;
            return (
              <Card key={goal.id}>
                <CardHeader>
                  <CardTitle>{goal.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  {hobby && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-semibold">Hobby:</span> {hobby.name}
                    </p>
                  )}
                  {goal.target_hours && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-semibold">Target:</span> {goal.target_hours} hours
                    </p>
                  )}
                  {goal.description && (
                    <p className="text-gray-700 mb-3">{goal.description}</p>
                  )}
                  <div className="flex items-center gap-2">
                    <select
                      value={goal.status}
                      onChange={(e) => handleStatusChange(goal.id, e.target.value)}
                      disabled={isUpdating}
                      className={`px-3 py-1 rounded-md text-sm font-semibold border border-gray-300 cursor-pointer transition-opacity ${
                        isUpdating ? 'opacity-50 cursor-not-allowed' : ''
                      } ${statusColors[goal.status] || 'bg-gray-100 text-gray-800'}`}
                    >
                      {statusOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                    <Button 
                      variant="secondary" 
                      size="sm"
                      onClick={() => handleOpenMilestoneModal(goal.id)}
                    >
                      + Milestone
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={handleCloseModal} title="Create New Goal">
        <form onSubmit={handleSubmit} className="space-y-4">
          {formErrors.form && <ErrorAlert message={formErrors.form} />}
          <Select
            label="Select Hobby"
            options={hobbies.map((h) => ({ value: h.id, label: h.name }))}
            value={formData.hobby_id}
            onChange={(e) => setFormData({ ...formData, hobby_id: e.target.value })}
            error={formErrors.hobby_id}
            required
          />
          <Input
            label="Goal Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            error={formErrors.title}
            required
          />
          <Textarea
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
          />
          <Input
            type="number"
            label="Target Hours"
            value={formData.target_hours}
            onChange={(e) => setFormData({ ...formData, target_hours: e.target.value })}
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Create Goal
            </Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={isMilestoneModalOpen} onClose={handleCloseMilestoneModal} title="Create New Milestone">
        <form onSubmit={handleMilestoneSubmit} className="space-y-4">
          {milestoneFormErrors.form && <ErrorAlert message={milestoneFormErrors.form} />}
          <Input
            label="Milestone Title"
            value={milestoneFormData.title}
            onChange={(e) => setMilestoneFormData({ ...milestoneFormData, title: e.target.value })}
            error={milestoneFormErrors.title}
            required
          />
          <Textarea
            label="Description"
            value={milestoneFormData.description}
            onChange={(e) => setMilestoneFormData({ ...milestoneFormData, description: e.target.value })}
            rows={3}
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseMilestoneModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Create Milestone
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
