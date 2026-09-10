const getApiBaseUrl = () => {
  return localStorage.getItem('api_url') || 'https://nursery-catalog-advanced-controlling.trycloudflare.com';
};

const getAuthToken = () => {
  return localStorage.getItem('auth_token') || 'JcobCthole@5';
};

export async function sendChatMessage({ session_id, message }) {
  const baseUrl = getApiBaseUrl();
  const token = getAuthToken();
  
  try {
    const response = await fetch(`${baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
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
