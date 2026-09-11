const API = '/api';

export async function startScreening(inputDir = './data/resumes', outputPath = './data/output/results.json') {
  const res = await fetch(`${API}/screen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_dir: inputDir, output_path: outputPath }),
  });
  if (!res.ok) throw new Error(`Screening failed: ${res.status}`);
  return res.json();
}

export async function getResults() {
  const res = await fetch(`${API}/results`);
  if (!res.ok) throw new Error('No results found');
  return res.json();
}
