import { useEffect, useState } from 'react';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState, Modal, Input, Select } from '../components';

export function SkillsPage() {
  const [skills, setSkills] = useState([]);
  const [hobbies, setHobbies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [editingSkillId, setEditingSkillId] = useState(null);
  const [deletingSkillId, setDeletingSkillId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ hobby_id: '', name: '', proficiency_level: 'beginner' });
  const [formErrors, setFormErrors] = useState({});

  const fetchData = async () => {
    setLoading(true);
    try {
      const [skillsRes, hobbiesRes] = await Promise.all([
        api.get('/skills'),
        api.get('/hobbies'),
      ]);
      setSkills(skillsRes.data);
      setHobbies(hobbiesRes.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load skills');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenModal = (skill = null) => {
    if (skill) {
      setEditingSkillId(skill.id);
      setFormData({
        hobby_id: skill.hobby_id,
        name: skill.name,
        proficiency_level: skill.proficiency_level,
      });
    } else {
      setEditingSkillId(null);
      setFormData({ hobby_id: '', name: '', proficiency_level: 'beginner' });
    }
    setFormErrors({});
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingSkillId(null);
    setFormData({ hobby_id: '', name: '', proficiency_level: 'beginner' });
    setFormErrors({});
  };

  const handleOpenDeleteModal = (skillId) => {
    setDeletingSkillId(skillId);
    setIsDeleteModalOpen(true);
  };

  const handleCloseDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setDeletingSkillId(null);
    setError('');
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.hobby_id) errors.hobby_id = 'Please select a hobby';
    if (!formData.name) errors.name = 'Skill name is required';
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setIsSubmitting(true);
    try {
      if (editingSkillId) {
        await api.put(`/skills/${editingSkillId}`, formData);
      } else {
        await api.post('/skills', formData);
      }
      await fetchData();
      handleCloseModal();
    } catch (err) {
      setFormErrors({ form: err.response?.data?.detail || 'Failed to save skill' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setIsSubmitting(true);
    try {
      await api.delete(`/skills/${deletingSkillId}`);
      await fetchData();
      handleCloseDeleteModal();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete skill');
      handleCloseDeleteModal();
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <Loading />;

  const proficiencyColors = {
    beginner: 'bg-blue-100 text-blue-800',
    intermediate: 'bg-yellow-100 text-yellow-800',
    advanced: 'bg-green-100 text-green-800',
    expert: 'bg-purple-100 text-purple-800',
  };

  const deletingSkill = skills.find(s => s.id === deletingSkillId);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Skills</h1>
          <p className="text-gray-600 mt-1">Track and develop your skills</p>
        </div>
        <Button variant="primary" onClick={() => handleOpenModal()}>
          + Add Skill
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {skills.length === 0 ? (
        <EmptyState
          icon="⭐"
          title="No Skills Yet"
          description="Add a skill to track your progress"
          action={<Button onClick={() => handleOpenModal()}>Add Your First Skill</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {skills.map((skill) => {
            const hobby = hobbies.find((h) => h.id === skill.hobby_id);
            return (
              <Card key={skill.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{skill.name}</CardTitle>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleOpenModal(skill)}
                        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleOpenDeleteModal(skill.id)}
                        className="text-sm text-red-600 hover:text-red-800 font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-semibold">Hobby:</span> {hobby?.name || 'Unknown'}
                  </p>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        proficiencyColors[skill.proficiency_level] || 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {skill.proficiency_level?.toUpperCase()}
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Add/Edit Skill Modal */}
      <Modal isOpen={isModalOpen} onClose={handleCloseModal} title={editingSkillId ? "Edit Skill" : "Add New Skill"}>
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
            label="Skill Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={formErrors.name}
            required
          />
          <Select
            label="Proficiency Level"
            options={[
              { value: 'beginner', label: 'Beginner' },
              { value: 'intermediate', label: 'Intermediate' },
              { value: 'advanced', label: 'Advanced' },
              { value: 'expert', label: 'Expert' },
            ]}
            value={formData.proficiency_level}
            onChange={(e) => setFormData({ ...formData, proficiency_level: e.target.value })}
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseModal} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : editingSkillId ? 'Update Skill' : 'Add Skill'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isDeleteModalOpen} onClose={handleCloseDeleteModal} title="Delete Skill">
        <div className="space-y-4">
          <p className="text-gray-700">
            Are you sure you want to delete the skill "<strong>{deletingSkill?.name}</strong>"? This action cannot be undone.
          </p>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseDeleteModal} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleDelete}
              disabled={isSubmitting}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {isSubmitting ? 'Deleting...' : 'Delete Skill'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
