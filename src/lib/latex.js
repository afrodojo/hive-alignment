import katex from 'katex';

const CODE_FENCE = /```/;
const LATEX_HINT = /\\(?:[a-zA-Z]{2,}|square|mathcal|Sigma|forall|exists|land|lor|Rightarrow)|\\\(|\\\[|\$\$|\^\{|_\{/;

/** Heuristic: does this snippet carry LaTeX rather than a plain code block? */
export function isLatex(text = '') {
  if (!text) return false;
  if (CODE_FENCE.test(text)) return false;
  return LATEX_HINT.test(text);
}

/**
 * Render a proof snippet. Returns { mode: 'latex' | 'code', html }.
 * Anything KaTeX cannot typeset falls back to the monospaced terminal.
 */
export function renderProof(text = '') {
  const value = String(text || '').trim();
  if (!value || !isLatex(value)) return { mode: 'code', html: null };

  try {
    const html = katex.renderToString(value, {
      displayMode: true,
      throwOnError: false,
      strict: false,
      trust: false,
      output: 'html',
    });
    if (!html || html.includes('katex-error')) return { mode: 'code', html: null };
    return { mode: 'latex', html };
  } catch {
    return { mode: 'code', html: null };
  }
}