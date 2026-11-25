import { useEffect, useState } from 'react';
import { useAuth } from '../contexts';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, Input, Textarea, Modal } from '../components';

export function ProfilePage() {
  const { user, updatePassword } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [formData, setFormData] = useState({ display_name: '', bio: '', avatar_url: '' });
  const [passwordData, setPasswordData] = useState({ newPassword: '', confirmPassword: '' });
  const [formErrors, setFormErrors] = useState({});
  const [message, setMessage] = useState('');

  const fetchProfile = async () => {
    try {
      const response = await api.get('/profiles/me');
      setProfile(response.data);
      setFormData({
        display_name: response.data.display_name || '',
        bio: response.data.bio || '',
        avatar_url: response.data.avatar_url || '',
      });
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      await api.put('/profiles/me', formData);
      await fetchProfile();
      setIsEditing(false);
      setMessage('Profile updated successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setFormErrors({ form: err.response?.data?.detail || 'Failed to update profile' });
    }
  };

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    const errors = {};
    if (!passwordData.newPassword) errors.newPassword = 'New password is required';
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      await updatePassword(passwordData.newPassword);
      setIsPasswordModalOpen(false);
      setPasswordData({ newPassword: '', confirmPassword: '' });
      setFormErrors({});
      setMessage('Password updated successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setFormErrors({ form: err.message || 'Failed to update password' });
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Profile</h1>
        <p className="text-gray-600 mt-1">Manage your account information</p>
      </div>

      {error && <ErrorAlert message={error} />}
      {message && (
        <div className="rounded-lg bg-green-50 border border-green-200 p-4">
          <p className="text-green-800">{message}</p>
        </div>
      )}

      {profile && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-semibold text-gray-700">Email</label>
                  <p className="text-gray-900 mt-1">{user?.email}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-700">Username</label>
                  <p className="text-gray-900 mt-1">{profile.username}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {!isEditing ? (
            <Card>
              <CardHeader>
                <CardTitle>Profile Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 mb-4">
                  {profile.display_name && (
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Display Name</label>
                      <p className="text-gray-900 mt-1">{profile.display_name}</p>
                    </div>
                  )}
                  {profile.bio && (
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Bio</label>
                      <p className="text-gray-900 mt-1">{profile.bio}</p>
                    </div>
                  )}
                </div>
                <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Edit Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  {formErrors.form && <ErrorAlert message={formErrors.form} />}
                  <Input
                    label="Display Name"
                    value={formData.display_name}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    error={formErrors.display_name}
                  />
                  <Textarea
                    label="Bio"
                    value={formData.bio}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    error={formErrors.bio}
                    rows={3}
                  />
                  <div className="flex gap-2">
                    <Button variant="secondary" onClick={() => setIsEditing(false)}>
                      Cancel
                    </Button>
                    <Button type="submit">Save Changes</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Security</CardTitle>
            </CardHeader>
            <CardContent>
              <Button onClick={() => setIsPasswordModalOpen(true)} variant="secondary">
                Change Password
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      <Modal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        title="Change Password"
      >
        <form onSubmit={handleUpdatePassword} className="space-y-4">
          {formErrors.form && <ErrorAlert message={formErrors.form} />}
          <Input
            type="password"
            label="New Password"
            value={passwordData.newPassword}
            onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
            error={formErrors.newPassword}
            required
          />
          <Input
            type="password"
            label="Confirm Password"
            value={passwordData.confirmPassword}
            onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
            error={formErrors.confirmPassword}
            required
          />
          <div className="flex gap-2 justify-end">
            <Button
              variant="secondary"
              onClick={() => setIsPasswordModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit">Update Password</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
