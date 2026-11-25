import { useState } from 'react';
import { api } from '../services';
import { Button, Card, CardHeader, CardTitle, CardContent, Loading, ErrorAlert, EmptyState, Input } from '../components';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }

    setLoading(true);
    setSearched(true);
    try {
      const response = await api.get(`/search?q=${encodeURIComponent(query)}`);
      // Flatten the response structure into a single array
      const flatResults = [];
      if (response.data.hobbies) {
        flatResults.push(...response.data.hobbies.map(h => ({ ...h, type: 'Hobby' })));
      }
      if (response.data.skills) {
        flatResults.push(...response.data.skills.map(s => ({ ...s, type: 'Skill' })));
      }
      if (response.data.posts) {
        flatResults.push(...response.data.posts.map(p => ({ ...p, type: 'Post' })));
      }
      if (response.data.profiles) {
        flatResults.push(...response.data.profiles.map(p => ({ ...p, type: 'Profile' })));
      }
      setResults(flatResults);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Search</h1>
        <p className="text-gray-600 mt-1">Find hobbies, skills, and community content</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <Input
          type="search"
          placeholder="Search for hobbies, skills, posts..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <Button variant="primary" type="submit" size="lg">
          Search
        </Button>
      </form>

      {error && <ErrorAlert message={error} />}

      {loading && <Loading />}

      {searched && !loading && results.length === 0 && (
        <EmptyState
          icon="🔍"
          title="No Results"
          description={`No results found for "${query}"`}
        />
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Found {results.length} result{results.length !== 1 ? 's' : ''}
          </p>
          {results.map((result, idx) => (
            <Card key={idx}>
              <CardHeader>
                <CardTitle>{result.name || result.username || result.title || 'Result'}</CardTitle>
              </CardHeader>
              <CardContent>
                {result.description && (
                  <p className="text-gray-700 mb-2">{result.description}</p>
                )}
                {result.display_name && (
                  <p className="text-gray-700 mb-2">{result.display_name}</p>
                )}
                {result.content && (
                  <p className="text-gray-700 mb-2">{result.content.substring(0, 150)}...</p>
                )}
                <div className="text-xs text-gray-500 mt-2 flex gap-2">
                  {result.type && <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded">{result.type}</span>}
                  {result.proficiency_level && <span className="inline-block bg-green-100 text-green-800 px-2 py-1 rounded capitalize">{result.proficiency_level}</span>}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!searched && (
        <EmptyState
          icon="🔍"
          title="Start Searching"
          description="Enter a query above to search for hobbies, skills, and community content"
        />
      )}
    </div>
  );
}
