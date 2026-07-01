document.getElementById('search-btn').addEventListener('click', async () => {
  const profile = {
    field: document.getElementById('field').value,
    role: document.getElementById('role').value,
    skills: document.getElementById('skills').value.split(',').map(s => s.trim()),
    location: document.getElementById('location').value,
    experience: document.getElementById('experience').value,
    remote: document.getElementById('remote').checked
  };

  document.getElementById('results').innerHTML = '<p>Searching...</p>';

  const resp = await fetch('http://localhost:8000/api/jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile)
  });

  const jobs = await resp.json();
  renderJobs(jobs);
});

function renderJobs(jobs) {
  const el = document.getElementById('results');

  if (jobs.length === 0) {
    el.innerHTML = "<p>No new jobs found — you've already seen everything matching this search.</p>";
    return;
  }

  el.innerHTML = jobs.map(j => `
    <div class='job-card score-${j.score >= 8 ? 'high' : j.score >= 5 ? 'mid' : 'low'}' id='job-${j.job_id}'>
      <div class='score'>${j.score}/10</div>
      <h3>${j.job.title}</h3>
      <p class='company'>${j.job.company} — ${j.job.location}</p>
      <p class='reason'>${j.reason}</p>
      <a href='${j.job.url}' target='_blank'>View Job</a>
      <div class='actions'>
        <button onclick='updateStatus("${j.job_id}", "applied")'>Applied</button>
        <button onclick='updateStatus("${j.job_id}", "rejected")'>Not interested</button>
      </div>
    </div>
  `).join('');
}

async function updateStatus(jobId, status) {
  const card = document.getElementById(`job-${jobId}`);
  await fetch('http://localhost:8000/api/status', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, status })
  });
  if (card) {
    card.querySelectorAll('.actions button').forEach(btn => btn.disabled = true);
    card.classList.add(`status-${status}`);
  }
}

document.getElementById('ask-btn').addEventListener('click', async () => {
  const question = document.getElementById('question').value;
  document.getElementById('qa-answer').innerHTML = '<p>Searching...</p>';

  const resp = await fetch('http://localhost:8000/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  const data = await resp.json();
  document.getElementById('qa-answer').innerHTML =
    `<div class='answer-card'>${data.answer}</div>`;
});
