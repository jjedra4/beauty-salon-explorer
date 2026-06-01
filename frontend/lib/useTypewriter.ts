"use client";

import { useEffect, useState } from "react";

/**
 * Cycles through `phrases`, typing each one out character by character, holding,
 * then deleting it before moving to the next. Powers the ghosted example
 * prompts that "write themselves" inside the search bar.
 *
 * Pauses entirely when `enabled` is false (e.g. while the user is typing) and
 * respects `prefers-reduced-motion` by simply swapping whole phrases in turn.
 *
 * All state transitions happen inside the scheduled timeout (never synchronously
 * in the effect body) so the loop advances one tick at a time.
 */
export function useTypewriter(
  phrases: string[],
  { typeMs = 55, deleteMs = 28, holdMs = 1800, enabled = true } = {},
): string {
  const [text, setText] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!enabled || phrases.length === 0) return;

    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;

    const phrase = phrases[phraseIndex % phrases.length];
    const atFullPhrase = !deleting && text === phrase;
    const fullyDeleted = deleting && text === "";

    // Pick how long to wait before the next single transition.
    const delay = reduced || atFullPhrase ? holdMs : fullyDeleted ? 0 : deleting ? deleteMs : typeMs;

    const timer = setTimeout(() => {
      if (reduced) {
        setText(phrase);
        setPhraseIndex((i) => (i + 1) % phrases.length);
      } else if (atFullPhrase) {
        setDeleting(true);
      } else if (fullyDeleted) {
        setDeleting(false);
        setPhraseIndex((i) => (i + 1) % phrases.length);
      } else {
        setText((current) =>
          deleting ? current.slice(0, -1) : phrase.slice(0, current.length + 1),
        );
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [text, deleting, phraseIndex, phrases, enabled, typeMs, deleteMs, holdMs]);

  return text;
}
