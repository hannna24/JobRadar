document.getElementById('search-btn').addEventListener('click', async () => {
  const profile = {
    field: document.getElementById('field').value,
    role: document.getElementById('role').value,
    skills: document.getElementById('skills').value.split(',').map(s => s.trim()),
    location: document.getElementById('location').value,
    experience: document.getElementById('experience').value,
    remote: false
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
  el.innerHTML = jobs.map(j => `
    <div class='job-card score-${j.score >= 8 ? 'high' : j.score >= 5 ? 'mid' : 'low'}'>
      <div class='score'>${j.score}/10</div>
      <h3>${j.job.title}</h3>
      <p class='company'>${j.job.company} — ${j.job.location}</p>
      <p class='reason'>${j.reason}</p>
      <a href='${j.job.url}' target='_blank'>View Job</a>
    </div>
  `).join('');
}
