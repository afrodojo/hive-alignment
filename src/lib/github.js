import { base44 } from '@/api/base44Client';

export const GITHUB_REPO_URL = 'https://github.com/afrodojo/hive-alignment';
export const LIVE_SITE_URL = 'https://hive-align.eds-360.com';

const REPO_API = 'https://api.github.com/repos/afrodojo/hive-alignment';

export const commitUrl = (hash) => `${GITHUB_REPO_URL}/commit/${hash}`;
export const fileUrl = (path) => `${GITHUB_REPO_URL}/blob/main/${path}`;
export const liveSiteHost = (url = LIVE_SITE_URL) => url.replace(/^https?:\/\//, '').replace(/\/$/, '');

const CARD_SCHEMA = {
  type: 'object',
  properties: {
    title: { type: 'string', description: 'Core technical architectural achievement. Max 110 characters.' },
    hook: { type: 'string', description: 'One-sentence hook framing the problem or breakthrough.' },
    core_insight: { type: 'string', description: 'High-density paragraph explaining the mechanism or proof.' },
    takeaways: { type: 'array', items: { type: 'string' }, description: 'Two or three actionable principles.' },
    proof_or_code: { type: 'string', description: 'Formal invariant in LaTeX, or the load-bearing code snippet from the diff.' },
    external_reference: { type: 'string', description: 'Single most relevant file path from the diff.' },
    read_time_seconds: { type: 'integer', description: 'Estimated read time in seconds, 40-60.' },
  },
  required: ['title', 'hook', 'core_insight', 'takeaways', 'external_reference'],
};

async function getJson(url) {
  const res = await fetch(url, { headers: { Accept: 'application/vnd.github+json' } });
  if (!res.ok) throw new Error(`GitHub API responded ${res.status}`);
  return res.json();
}

/** The N most recent commits on the repo, with their touched files and diffs. */
export async function fetchLatestCommits(limit = 3) {
  const list = await getJson(`${REPO_API}/commits?per_page=${limit}`);
  return Promise.all(
    list.slice(0, limit).map(async (commit) => {
      const detail = await getJson(`${REPO_API}/commits/${commit.sha}`).catch(() => null);
      const files = detail?.files ?? [];
      return {
        sha: commit.sha.slice(0, 7),
        message: commit.commit?.message ?? '',
        files: files.map((file) => ({ filename: file.filename, patch: (file.patch ?? '').slice(0, 4000) })),
      };
    })
  );
}

async function synthesizeCard(commit) {
  const diff = commit.files
    .map((file) => `--- ${file.filename}\n${file.patch}`)
    .join('\n\n')
    .slice(0, 12000);

  const draft = await base44.integrations.Core.InvokeLLM({
    prompt: `You are an executive research compiler for an AI Solutions Architect, Cyber SME, and computer-science doctoral researcher working on autonomic multi-agent zero-trust swarms.

Input: a git commit from the repository afrodojo/hive-alignment.

Commit message:
${commit.message}

Files changed and diffs:
${diff || '(no diff available — work from the commit message alone)'}

Compress the key architectural, mathematical, security, or algorithmic change into a 45-second micro-learning card. Discard formatting, typos, and dependency bumps. If the diff carries a formal invariant or state-transition safety check, express it in LaTeX for proof_or_code; otherwise quote the load-bearing code snippet. external_reference must be the single most relevant file path from the diff. Tone: uncompromising, high-density, jargon-precise.`,
    response_json_schema: CARD_SCHEMA,
  });

  return {
    domain: 'CS_RESEARCH',
    title: (draft.title ?? commit.message.split('\n')[0]).slice(0, 118),
    hook: draft.hook ?? '',
    core_insight: draft.core_insight ?? '',
    takeaways: draft.takeaways ?? [],
    proof_or_code: draft.proof_or_code,
    read_time_seconds: draft.read_time_seconds ?? 45,
    repo_url: GITHUB_REPO_URL,
    commit_hash: commit.sha,
    live_site_url: LIVE_SITE_URL,
    external_reference: draft.external_reference || commit.files[0]?.filename,
  };
}

/** Synthesize cards for recent commits that have not been ingested yet. */
export async function syncLatestCards(limit = 3) {
  const commits = await fetchLatestCommits(limit);
  const known = await base44.entities.Card.filter({ commit_hash: { $in: commits.map((c) => c.sha) } });
  const seen = new Set((known?.items ?? known ?? []).map((card) => card.commit_hash));

  const created = [];
  for (const commit of commits) {
    if (seen.has(commit.sha)) continue;
    created.push(await base44.entities.Card.create(await synthesizeCard(commit)));
  }
  return created;
}