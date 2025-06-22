const apiBaseUrl = 'http://localhost:5000';

let accessToken = null;

const loginSection = document.getElementById('login-section');
const mainSection = document.getElementById('main-section');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const usernameInput = document.getElementById('username');
const loginError = document.getElementById('login-error');
const entriesList = document.getElementById('entries-list');

loginBtn.addEventListener('click', async () => {
  const username = usernameInput.value.trim();
  if (!username) {
    loginError.textContent = 'Please enter a username.';
    return;
  }
  loginError.textContent = '';
  try {
    const response = await fetch(\`\${apiBaseUrl}/login\`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      loginError.textContent = errorData.msg || 'Login failed.';
      return;
    }
    const data = await response.json();
    accessToken = data.access_token;
    showMainSection();
    loadEntries();
  } catch (err) {
    loginError.textContent = 'Network error.';
  }
});

logoutBtn.addEventListener('click', () => {
  accessToken = null;
  usernameInput.value = '';
  entriesList.innerHTML = '';
  mainSection.classList.add('hidden');
  loginSection.classList.remove('hidden');
});

function showMainSection() {
  loginSection.classList.add('hidden');
  mainSection.classList.remove('hidden');
}

async function loadEntries() {
  entriesList.innerHTML = '<p>Loading entries...</p>';
  try {
    const response = await fetch(\`\${apiBaseUrl}/entries\`, {
      headers: { Authorization: \`Bearer \${accessToken}\` },
    });
    if (!response.ok) {
      entriesList.innerHTML = '<p>Failed to load entries.</p>';
      return;
    }
    const data = await response.json();
    displayEntries(data.items || []);
  } catch (err) {
    entriesList.innerHTML = '<p>Network error loading entries.</p>';
  }
}

function displayEntries(entries) {
  if (entries.length === 0) {
    entriesList.innerHTML = '<p>No entries found.</p>';
    return;
  }
  entriesList.innerHTML = '';
  entries.forEach(entry => {
    const div = document.createElement('div');
    div.className = 'entry';
    div.innerHTML = \`
      <h3>\${entry.title}</h3>
      <p>\${entry.content}</p>
      <small>User ID: \${entry.user_id}</small>
    \`;
    entriesList.appendChild(div);
  });
}
