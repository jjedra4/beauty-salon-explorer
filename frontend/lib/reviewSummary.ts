/**
 * Parses an AI review summary string into a one-line vibe + pros/cons lists.
 *
 * The summarizer emits a short blurb that usually contains an "Overall vibe"
 * line followed by labelled "Pros:" / "Cons:" sections (sometimes markdown-bold,
 * sometimes semicolon-separated). This parser is deliberately tolerant: when it
 * can't find the labels it returns the whole text as the vibe, so the UI always
 * has something sensible to show rather than breaking on a messy summary.
 */

export interface ParsedReview {
  vibe: string;
  pros: string[];
  cons: string[];
}

const VIBE_LABEL = /(?:overall\s+)?vibe\s*:/i;
const PROS_LABEL = /pros\s*:/i;
const CONS_LABEL = /cons\s*:/i;

/** Split a labelled section into individual bullet points. */
function splitItems(chunk: string): string[] {
  const c = chunk.trim();
  if (!c) return [];
  // Prefer explicit separators (the summarizer mostly uses semicolons).
  let parts = c.split(/[;\n•]+/);
  if (parts.length === 1) {
    // A single chunk: a comma list of 3+ becomes bullets; else keep sentences.
    const byComma = c.split(/,\s+/);
    parts = byComma.length >= 3 ? byComma : c.split(/(?<=[.!?])\s+/);
  }
  return parts
    .map((p) => p.replace(/^[\s\-–—*•]+/, "").replace(/[.;,\s]+$/, "").trim())
    .filter((p) => p.length > 1);
}

/** Remove a leading "Vibe:" / "Overall vibe:" label and stray punctuation. */
function stripVibeLabel(s: string): string {
  return s.replace(VIBE_LABEL, "").replace(/^[\s\-–—:*]+/, "").trim();
}

export function parseReviewSummary(raw: string): ParsedReview {
  const text = raw.replace(/\*\*/g, "").replace(/\r/g, "").trim();

  const prosMatch = text.match(PROS_LABEL);
  const consMatch = text.match(CONS_LABEL);
  const prosIdx = prosMatch?.index ?? -1;
  const consIdx = consMatch?.index ?? -1;

  // No structure we recognise — present the whole thing as the vibe.
  if (prosIdx === -1 && consIdx === -1) {
    return { vibe: stripVibeLabel(text), pros: [], cons: [] };
  }

  const sectionStarts = [prosIdx, consIdx].filter((i) => i >= 0);
  const vibe = stripVibeLabel(text.slice(0, Math.min(...sectionStarts)).trim());

  let pros: string[] = [];
  let cons: string[] = [];
  if (prosIdx >= 0) {
    const end = consIdx > prosIdx ? consIdx : text.length;
    pros = splitItems(text.slice(prosIdx + prosMatch![0].length, end));
  }
  if (consIdx >= 0) {
    const end = prosIdx > consIdx ? prosIdx : text.length;
    cons = splitItems(text.slice(consIdx + consMatch![0].length, end));
  }

  return { vibe, pros, cons };
}
