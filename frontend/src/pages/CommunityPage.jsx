import { useEffect, useState } from 'react';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState, Modal, Textarea, Input, Select } from '../components';

export function CommunityPage() {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const [isCommentModalOpen, setIsCommentModalOpen] = useState(false);
  const [currentPostId, setCurrentPostId] = useState(null);
  const [hobbies, setHobbies] = useState([]);
  const [postData, setPostData] = useState({ hobby_id: '', title: '', content: '', visibility: 'public' });
  const [commentData, setCommentData] = useState({ content: '' });
  const [postErrors, setPostErrors] = useState({});
  const [commentErrors, setCommentErrors] = useState({});

  const fetchFeed = async () => {
    setLoading(true);
    try {
      const response = await api.get('/feed');
      setFeed(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load feed');
    } finally {
      setLoading(false);
    }
  };

  const fetchHobbies = async () => {
    try {
      const response = await api.get('/hobbies');
      setHobbies(response.data);
    } catch (err) {
      console.error('Failed to load hobbies:', err);
    }
  };

  useEffect(() => {
    fetchFeed();
    fetchHobbies();
  }, []);

  const handleOpenPostModal = () => {
    setPostData({ hobby_id: '', title: '', content: '', visibility: 'public' });
    setPostErrors({});
    setIsPostModalOpen(true);
  };

  const handleClosePostModal = () => {
    setIsPostModalOpen(false);
    setPostData({ hobby_id: '', title: '', content: '', visibility: 'public' });
    setPostErrors({});
  };

  const handleOpenCommentModal = (postId) => {
    setCurrentPostId(postId);
    setCommentData({ content: '' });
    setCommentErrors({});
    setIsCommentModalOpen(true);
  };

  const handleCloseCommentModal = () => {
    setIsCommentModalOpen(false);
    setCommentData({ content: '' });
    setCommentErrors({});
  };

  const handleSubmitPost = async (e) => {
    e.preventDefault();
    const errors = {};
    if (!postData.hobby_id) errors.hobby_id = 'Please select a hobby';
    if (!postData.title) errors.title = 'Title is required';
    if (!postData.content) errors.content = 'Content is required';

    if (Object.keys(errors).length > 0) {
      setPostErrors(errors);
      return;
    }

    try {
      await api.post('/posts', postData);
      await fetchFeed();
      handleClosePostModal();
    } catch (err) {
      setPostErrors({ form: err.response?.data?.detail || 'Failed to create post' });
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!commentData.content) {
      setCommentErrors({ content: 'Comment cannot be empty' });
      return;
    }

    try {
      await api.post(`/posts/${currentPostId}/comments`, commentData);
      await fetchFeed();
      handleCloseCommentModal();
    } catch (err) {
      setCommentErrors({ form: err.response?.data?.detail || 'Failed to add comment' });
    }
  };

  const handleLike = async (postId) => {
    try {
      await api.post(`/posts/${postId}/likes`);
      await fetchFeed();
    } catch (err) {
      setError('Failed to like post');
    }
  };

  const handleUnlike = async (postId) => {
    try {
      await api.delete(`/posts/${postId}/likes`);
      await fetchFeed();
    } catch (err) {
      setError('Failed to unlike post');
    }
  };

  if (loading) return <Loading />;

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
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Community Feed</h1>
          <p className="text-gray-600 mt-1">Share your hobbies and connect with others</p>
        </div>
        <Button variant="primary" onClick={handleOpenPostModal}>
          + Share Post
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {feed.length === 0 ? (
        <EmptyState
          icon="👥"
          title="No Posts Yet"
          description="Be the first to share your hobby journey"
          action={<Button onClick={handleOpenPostModal}>Create Your First Post</Button>}
        />
      ) : (
        <div className="space-y-4">
          {feed.map((post) => (
            <Card key={post.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{post.title}</CardTitle>
                    <p className="text-sm text-gray-600 mt-1">
                      by <span className="font-semibold">{post.username}</span>
                    </p>
                  </div>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {post.visibility}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">{post.content}</p>
                <p className="text-xs text-gray-500 mb-4">{formatDate(post.created_at)}</p>
                <div className="flex gap-4 items-center">
                  <button
                    onClick={() => handleLike(post.id)}
                    className="text-sm text-gray-600 hover:text-red-600"
                  >
                    ❤️ {post.like_count}
                  </button>
                  <button
                    onClick={() => handleOpenCommentModal(post.id)}
                    className="text-sm text-gray-600 hover:text-blue-600"
                  >
                    💬 {post.comment_count}
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal isOpen={isPostModalOpen} onClose={handleClosePostModal} title="Share a Post" size="lg">
        <form onSubmit={handleSubmitPost} className="space-y-4">
          {postErrors.form && <ErrorAlert message={postErrors.form} />}
          <Select
            label="Select Hobby"
            options={hobbies.map((h) => ({ value: h.id, label: h.name }))}
            value={postData.hobby_id}
            onChange={(e) => setPostData({ ...postData, hobby_id: e.target.value })}
            error={postErrors.hobby_id}
            required
          />
          <Input
            label="Title"
            value={postData.title}
            onChange={(e) => setPostData({ ...postData, title: e.target.value })}
            error={postErrors.title}
            required
          />
          <Textarea
            label="Content"
            value={postData.content}
            onChange={(e) => setPostData({ ...postData, content: e.target.value })}
            error={postErrors.content}
            rows={5}
            required
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleClosePostModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Post
            </Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={isCommentModalOpen} onClose={handleCloseCommentModal} title="Add Comment">
        <form onSubmit={handleSubmitComment} className="space-y-4">
          {commentErrors.form && <ErrorAlert message={commentErrors.form} />}
          <Textarea
            label="Your Comment"
            value={commentData.content}
            onChange={(e) => setCommentData({ ...commentData, content: e.target.value })}
            error={commentErrors.content}
            rows={3}
            required
          />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={handleCloseCommentModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Comment
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
