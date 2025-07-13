import axios from 'axios';

const API_BASE = 'https://616d9a2c9d20.ngrok-free.app';

console.log("API file loaded");

export async function loginUser(email: string, password: string) {
  console.log('Login URL:', `${API_BASE}/login`);
  try {
    const response = await axios.post(`${API_BASE}/login`, { email, password });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function signupUser({ name, gender, email, password }: { name: string; gender: string; email: string; password: string }) {
  console.log('Signup URL:', `${API_BASE}/signup`);
  try {
    const response = await axios.post(`${API_BASE}/signup`, { name, gender, email, password });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function getSavedArticles(token: string) {
  if (!token) {
    console.log('No token found for getSavedArticles!');
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.get(`${API_BASE}/news/saved`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function verifyClaim(claim: string) {
  try {
    // Correct endpoint: POST /claim-verdict
    const response = await axios.post(`${API_BASE}/claim-verdict`, { claim });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

// Placeholder for getProfile (since no endpoint is specified)
export async function getProfile(token: string) {
  try {
    const response = await axios.get(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    return { detail: 'Failed to fetch profile' };
  }
}

export async function getNews(token: string) {
  if (!token) {
    console.log('No token found for getNews!');
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.get(`${API_BASE}/news`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function saveArticle(token: string, articleId: string) {
  if (!token) {
    console.log('No token found for saveArticle!');
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.post(`${API_BASE}/news/save/${articleId}`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function searchNews(token: string, query: string) {
  if (!token) {
    console.log('No token found for searchNews!');
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.get(`${API_BASE}/news/search?query=${encodeURIComponent(query)}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function trackReading(token: string, articleId: string, duration: number) {
  if (!token) {
    console.log('No token found for trackReading!');
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.post(`${API_BASE}/read/${articleId}`, { duration }, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function startAIChat(articleId: string) {
  try {
    const response = await axios.post(`${API_BASE}/get_more_about_news`, { article_id: articleId });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function askFollowUp(sessionId: string, question: string) {
  try {
    const response = await axios.post(`${API_BASE}/get_more_follow_up`, { session_id: sessionId, question });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function fetchLatestNews(token: string) {
  if (!token) {
    console.log('No token found for fetchLatestNews!');
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.post(`${API_BASE}/fetch-latest-news`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
}

export async function getSavedArticle(token: string, articleId: string) {
  if (!token) {
    return { detail: 'Not authenticated' };
  }
  try {
    const response = await axios.get(`${API_BASE}/news/saved/${articleId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { detail: 'Network error' };
  }
} 