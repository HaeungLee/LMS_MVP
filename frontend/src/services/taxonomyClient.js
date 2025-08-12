const API_BASE_URL = 'http://localhost:8000/api/v1';

export const fetchTaxonomyTopics = async (subject = 'python_basics') => {
  const res = await fetch(`${API_BASE_URL}/taxonomy/topics?subject=${encodeURIComponent(subject)}`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('failed to fetch topics');
  return res.json();
};


