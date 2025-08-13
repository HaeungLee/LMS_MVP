const API_BASE_URL = 'http://localhost:8000/api/v1';

export const listTeacherGroups = async () => {
  const res = await fetch(`${API_BASE_URL}/teacher/groups`, { credentials: 'include' });
  if (!res.ok) throw new Error('failed to list groups');
  return res.json();
};

export const createTeacherGroup = async (name) => {
  const res = await fetch(`${API_BASE_URL}/teacher/groups`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error('failed to create group');
  return res.json();
};

export const addGroupMember = async (groupId, userId) => {
  const res = await fetch(`${API_BASE_URL}/teacher/groups/${groupId}/members`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) throw new Error('failed to add member');
  return res.json();
};


