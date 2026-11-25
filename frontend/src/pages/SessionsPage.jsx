import { useEffect, useState } from 'react';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState, Modal, Input, Select, Textarea } from '../components';

export function SessionsPage() {
  const [sessions, setSessionsData] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    skill_id: '',
    duration_minutes: '',
  });
  const [formErrors, setFormErrors] = useState({});

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sessionsRes, skillsRes] = await Promise.all([
        api.get('/sessions'),
        api.get('/skills'),
      ]);
      setSessionsData(sessionsRes.data);
      setSkills(skillsRes.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenModal = () => {
    setFormData({ skill_id: '', duration_minutes: '' });
    setFormErrors({});
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({ skill_id: '', duration_minutes: '' });
    setFormErrors({});
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.skill_id) errors.skill_id = 'Please select a skill';
    if (!formData.duration_minutes || parseInt(formData.duration_minutes) <= 0) {
      errors.duration_minutes = 'Duration must be greater than 0';
    }
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
        duration_minutes: parseInt(formData.duration_minutes),
      };
      await api.post('/sessions', data);
      await fetchData();
      handleCloseModal();
    } catch (err) {
      setFormErrors({ form: err.response?.data?.detail || 'Failed to record session' });
    }
  };

  if (loading) return <Loading />;

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours === 0) return `${mins}m`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}m`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Practice Sessions</h1>
          <p className="text-gray-600 mt-1">Track your practice history</p>
        </div>
        <Button variant="primary" onClick={handleOpenModal}>
          + Log Session
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {sessions.length === 0 ? (
        <EmptyState
          icon="⏱️"
          title="No Sessions Yet"
          description="Start logging your practice sessions to track your progress"
          action={<Button onClick={handleOpenModal}>Log Your First Session</Button>}
        />
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => {
            const skill = skills.find((s) => s.id === session.skill_id);
            return (
              <Card key={session.id}>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-gray-900">{skill?.name || 'Unknown Skill'}</p>
                      <p className="text-sm text-gray-600">
                        Duration: {formatDuration(session.duration_minutes)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(session.created_at)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={handleCloseModal} title="Log Practice Session">
        <form onSubmit={handleSubmit} className="space-y-4">
          {formErrors.form && <ErrorAlert message={formErrors.form} />}
          <Select
            label="Select Skill"
            options={skills.map((s) => ({ value: s.id, label: s.name }))}
            value={formData.skill_id}
            onChange={(e) => setFormData({ ...formData, skill_id: e.target.value })}
            error={formErrors.skill_id}
            required
          />
          <Input
            type="number"
            label="Duration (minutes)"
            value={formData.duration_minutes}
            onChange={(e) => setFormData({ ...formData, duration_minutes: e.target.value })}
            error={formErrors.duration_minutes}
            required
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Log Session
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
