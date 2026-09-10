const getApiBaseUrl = () => {
  return localStorage.getItem('api_url') || 'https://07a0ddddd0f3ed91-197-184-78-239.serveousercontent.com';
};

export async function sendChatMessage({ session_id, message }) {
  const baseUrl = getApiBaseUrl();
  try {
    const response = await fetch(`${baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id, message }),
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API connection error:', error);
    throw error;
  }
}
