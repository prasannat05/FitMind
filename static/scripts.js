let stepsChartInstance, caloriesChartInstance;

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

function loadTheme() {
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
  }
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
  return await res.json();
}

async function loadLogsAndCharts() {
  try {
    const logs = await fetchJSON('/logs');
    const dates = logs.map(log => log.date);
    const steps = logs.map(log => log.steps);
    const calories = logs.map(log => log.calories);

    renderChart('stepsChart', 'Steps Over Time', dates, steps, 'rgba(13,110,253,0.7)');
    renderChart('caloriesChart', 'Calories Burned Over Time', dates, calories, 'rgba(220,53,69,0.7)');
  } catch (error) {
    console.error('Error loading logs:', error);
  }
}

function renderChart(canvasId, label, labels, data, color) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (window[canvasId]) window[canvasId].destroy();
  window[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label,
        data,
        fill: true,
        backgroundColor: color,
        borderColor: color,
        tension: 0.3,
        pointRadius: 3,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true } },
      plugins: {
        tooltip: { mode: 'index', intersect: false }
      }
    }
  });
}

async function loadRecommendations() {
  const recDiv = document.getElementById('recommendations');
  recDiv.setAttribute('aria-busy', 'true');
  recDiv.textContent = 'Loading recommendations...';

  try {
    const recs = await fetchJSON('/recommendations', { method: 'POST' });
    recDiv.setAttribute('aria-busy', 'false');

    let html = `<h6>Workouts</h6><ul>`;
    recs.workouts.forEach(w => (html += `<li>${w}</li>`));
    html += `</ul><h6>Meals</h6><ul>`;
    recs.meals.forEach(m => (html += `<li>${m}</li>`));
    html += `</ul><h6>Tips</h6><ul>`;
    recs.tips.forEach(t => (html += `<li>${t}</li>`));
    html += '</ul>';

    recDiv.innerHTML = html;
  } catch (err) {
    recDiv.setAttribute('aria-busy', 'false');
    recDiv.textContent = 'Failed to load recommendations.';
    console.error(err);
  }
}

async function submitLogData(e) {
  e.preventDefault();

  const data = {
    date: new Date().toISOString().slice(0, 10),
    steps: parseInt(document.getElementById('steps').value) || 0,
    calories: parseFloat(document.getElementById('calories').value) || 0,
    heart_rate: parseInt(document.getElementById('heart_rate').value) || 0,
    sleep_hours: parseFloat(document.getElementById('sleep_hours').value) || 0,
    mood: document.getElementById('mood').value || '',
    hydration: parseFloat(document.getElementById('hydration').value) || 0
  };

  try {
    const resp = await fetch('/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const res = await resp.json();

    if (res.success) {
      const statusEl = document.getElementById('logStatus');
      const errorEl = document.getElementById('logError');
      statusEl.style.display = 'block';
      errorEl.style.display = 'none';
      setTimeout(() => (statusEl.style.display = 'none'), 3000);

      loadLogsAndCharts();
      e.target.reset();
    } else {
      showLogError();
    }
  } catch {
    showLogError();
  }
}

function showLogError() {
  const errorEl = document.getElementById('logError');
  const statusEl = document.getElementById('logStatus');
  statusEl.style.display = 'none';
  errorEl.style.display = 'block';
  setTimeout(() => (errorEl.style.display = 'none'), 3000);
}

function appendMessage(sender, text) {
  const chatWindow = document.getElementById('chatWindow');
  const msgDiv = document.createElement('div');
  msgDiv.className = sender === 'user' ? 'chat-message user-message' : 'chat-message ai-message';
  msgDiv.textContent = text;
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(message) {
  appendMessage('user', message);
  appendMessage('ai', '…'); // Loading indicator

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    const data = await response.json();
    const chatWindow = document.getElementById('chatWindow');
    const loadingMsg = Array.from(chatWindow.children).find(child => child.textContent === '…');
    if (loadingMsg) {
      loadingMsg.textContent = data.reply;
      loadingMsg.className = 'chat-message ai-message';
    }
  } catch (err) {
    const chatWindow = document.getElementById('chatWindow');
    const loadingMsg = Array.from(chatWindow.children).find(child => child.textContent === '…');
    if (loadingMsg) {
      loadingMsg.textContent = "Sorry, something went wrong. Please try again.";
      loadingMsg.className = 'chat-message ai-message error-message';
    }
  }
}

function setupChat() {
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');

  chatForm.addEventListener('submit', e => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (msg === '') return;
    chatInput.value = '';
    sendMessage(msg);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('logForm').addEventListener('submit', submitLogData);
  document.getElementById('refreshRec').addEventListener('click', loadRecommendations);
  setupChat();

  loadLogsAndCharts();
  loadRecommendations();
  loadTheme();
});
