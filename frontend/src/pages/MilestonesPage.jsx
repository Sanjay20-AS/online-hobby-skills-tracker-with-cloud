import { useEffect, useState } from 'react';
import { api } from '../services';
import { Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState } from '../components';

export function MilestonesPage() {
  const [milestones, setMilestones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchMilestones = async () => {
    try {
      const response = await api.get('/milestones');
      setMilestones(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load milestones');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMilestones();
  }, []);

  if (loading) return <Loading />;

  const achievedMilestones = milestones.filter((m) => m.achieved_at !== null);
  const pendingMilestones = milestones.filter((m) => m.achieved_at === null);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Milestones</h1>
        <p className="text-gray-600 mt-1">Track your achievements and progress</p>
      </div>

      {error && <ErrorAlert message={error} />}

      {milestones.length === 0 ? (
        <EmptyState
          icon="🏆"
          title="No Milestones Yet"
          description="Create goals to unlock achievements"
        />
      ) : (
        <div className="space-y-6">
          {achievedMilestones.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">🎉 Achieved</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {achievedMilestones.map((milestone) => (
                  <Card key={milestone.id} className="border-green-200 bg-green-50">
                    <CardHeader>
                      <CardTitle className="text-green-900">{milestone.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {milestone.description && (
                        <p className="text-gray-700 mb-2">{milestone.description}</p>
                      )}
                      <p className="text-sm text-gray-600">
                        Achieved on {formatDate(milestone.achieved_at)}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {pendingMilestones.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">🎯 In Progress</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pendingMilestones.map((milestone) => (
                  <Card key={milestone.id} className="border-blue-200 bg-blue-50">
                    <CardHeader>
                      <CardTitle className="text-blue-900">{milestone.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {milestone.description && (
                        <p className="text-gray-700 mb-2">{milestone.description}</p>
                      )}
                      <p className="text-sm text-gray-600">
                        Created on {formatDate(milestone.created_at)}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
