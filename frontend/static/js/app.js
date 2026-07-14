// ---------- Theme toggle ----------
const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'dark';
if (currentTheme === 'light') document.documentElement.setAttribute('data-theme', 'light');
themeToggle.textContent = currentTheme === 'light' ? '☀️' : '🌙';

themeToggle.addEventListener('click', () => {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  if (isLight) {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'dark');
    themeToggle.textContent = '🌙';
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
    themeToggle.textContent = '☀️';
  }
});

// ---------- Risk distribution chart ----------
let riskChart = null;

function renderRiskChart(distribution) {
  const ctx = document.getElementById('riskChart').getContext('2d');
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  const data = {
    labels: Object.keys(distribution),
    datasets: [{
      data: Object.values(distribution),
      backgroundColor: ['#35c17a', '#eab13f', '#e5484d'],
      borderColor: isLight ? '#ffffff' : '#10151d',
      borderWidth: 2,
    }]
  };
  if (riskChart) {
    riskChart.data = data;
    riskChart.update();
  } else {
    riskChart = new Chart(ctx, {
      type: 'doughnut',
      data,
      options: {
        plugins: { legend: { position: 'bottom', labels: { color: '#8791a1', font: { family: 'Inter' } } } },
        cutout: '68%',
      }
    });
  }
}

// ---------- Dashboard stats ----------
async function loadStats() {
  const loading = document.getElementById('loading-indicator');
  loading.classList.remove('hidden');
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    document.getElementById('total-txn').textContent = data.total_transactions;
    document.getElementById('fraud-txn').textContent = data.fraud_transactions;
    document.getElementById('safe-txn').textContent = data.safe_transactions;
    document.getElementById('fraud-pct').textContent = data.fraud_percentage + '%';
    renderRiskChart(data.risk_distribution);
  } catch (err) {
    console.error('Failed to load dashboard stats', err);
  } finally {
    loading.classList.add('hidden');
  }
}

// ---------- Transaction history ----------
async function loadHistory() {
  const user = document.getElementById('search-user').value;
  const risk = document.getElementById('filter-risk').value;
  const params = new URLSearchParams();
  if (user) params.append('user', user);
  if (risk) params.append('risk_level', risk);

  const res = await fetch(`/api/transactions?${params.toString()}`);
  const rows = await res.json();
  const tbody = document.getElementById('history-body');
  tbody.innerHTML = '';

  rows.forEach(r => {
    const riskClass = r.risk_level.includes('High') ? 'high' : r.risk_level.includes('Medium') ? 'medium' : 'low';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${new Date(r.created_at).toLocaleString()}</td>
      <td>${r.sender_name}</td>
      <td>$${r.amount.toFixed(2)}</td>
      <td><span class="badge ${riskClass}">${r.risk_level}</span></td>
      <td>${r.confidence_score}%</td>
      <td>${riskClass === 'high' ? '⚠ Flagged' : 'Cleared'}</td>
      <td><button class="delete-btn" onclick="deleteTransaction(${r.id})">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

async function deleteTransaction(id) {
  if (!confirm('Delete this transaction record?')) return;
  await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
  loadHistory();
  loadStats();
}

// ---------- Transaction analysis form ----------
document.getElementById('txn-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('analyze-btn');
  btn.disabled = true;
  btn.textContent = 'Analyzing…';

  const payload = {
    sender_name: document.getElementById('sender_name').value,
    receiver_name: document.getElementById('receiver_name').value,
    amount: parseFloat(document.getElementById('amount').value),
    merchant_category: document.getElementById('merchant_category').value,
    transaction_type: document.getElementById('transaction_type').value,
    device_type: document.getElementById('device_type').value,
    location: document.getElementById('location').value,
    transaction_hour: parseInt(document.getElementById('transaction_hour').value),
    previous_fraud_history: document.getElementById('previous_fraud_history').checked,
    customer_age: parseInt(document.getElementById('customer_age').value),
    payment_method: document.getElementById('payment_method').value,
  };

  const card = document.getElementById('result-card');
  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Prediction failed');
    }
    const result = await res.json();
    const riskClass = result.risk_level.includes('High') ? 'high' : result.risk_level.includes('Medium') ? 'medium' : 'low';
    const prob = Math.min(100, Math.max(0, result.fraud_probability));
    card.className = `result-card ${riskClass}`;
    card.innerHTML = `
      <h3>${result.risk_level.includes('High') ? '⚠ High Risk Transaction' : '✓ ' + result.risk_level}</h3>
      <div class="result-figures">
        <div><p>Fraud Probability</p><p>${result.fraud_probability}%</p></div>
        <div><p>Confidence Score</p><p>${result.confidence_score}%</p></div>
      </div>
      <div class="risk-gauge">
        <div class="risk-gauge-track"><div class="risk-gauge-marker" style="left: calc(${prob}% - 1px);"></div></div>
        <div class="risk-gauge-scale"><span>0</span><span>50</span><span>100</span></div>
      </div>
      <p><strong>Reasons:</strong></p>
      <ul>${result.reasons.map(r => `<li>${r}</li>`).join('')}</ul>
    `;
    loadStats();
    loadHistory();
  } catch (err) {
    card.className = 'result-card high';
    card.innerHTML = `<h3>⚠ Error</h3><p>${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze Transaction';
  }
});

// ---------- Init ----------
loadStats();
loadHistory();
