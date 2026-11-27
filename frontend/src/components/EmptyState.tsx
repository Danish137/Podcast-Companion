import { useConversation } from '../contexts/ConversationContext';
import { useEpisodes } from '../hooks/useEpisodes';
import { displayTitle, shortTitle } from '../utils/format';

const SUGGESTIONS = [
  'Explain the light clock thought experiment simply',
  'Compare Gödel and Turing on the limits of proof',
  'Which episodes cover biology?',
];

/**
 * First screen: the sixteen papers themselves, in the order they were
 * published, so the learner sees what the companion knows before asking.
 */
export function EmptyState() {
  const { sendMessage } = useConversation();
  const { episodes, failed } = useEpisodes();
  const papers = [...episodes].sort((a, b) => (a.publication_year ?? 0) - (b.publication_year ?? 0));

  return (
    <div className="flex-1 min-h-0 overflow-y-auto">
      <div className="max-w-[46rem] mx-auto px-4 sm:px-6 pt-10 sm:pt-16 pb-8">
        <h2
          className="m-0 text-[1.9rem] sm:text-[2.35rem] leading-[1.15] font-semibold"
          style={{ fontFamily: 'var(--font-read)', letterSpacing: '-0.01em', color: 'var(--ink)' }}
        >
          Understand the papers that changed science, straight from the podcast.
        </h2>
        <p className="mt-3 mb-0 text-[1rem] max-w-[36rem]" style={{ color: 'var(--ink-soft)' }}>
          Ask about an idea, ask again if it doesn’t click, and press any timestamp to hear the hosts explain it in their own words.
        </p>

        <div className="mt-8 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => sendMessage(s)}
              className="px-3.5 py-2 rounded-full border text-[0.88rem] transition-colors hover:border-[var(--accent)] hover:text-[var(--accent)]"
              style={{ borderColor: 'var(--line-strong)', background: 'var(--surface)', color: 'var(--ink)' }}
            >
              {s}
            </button>
          ))}
        </div>

        {papers.length > 0 && (
          <section className="mt-10" aria-label="Episodes in the collection">
            <h3 className="m-0 mb-3 text-[0.85rem] font-medium" style={{ color: 'var(--ink-soft)' }}>
              {papers.length} episodes, oldest paper first
            </h3>
            <ol className="grid grid-cols-2 sm:grid-cols-4 gap-px overflow-hidden border list-none p-0 m-0"
              style={{ borderColor: 'var(--line)', background: 'var(--line)', borderRadius: 'var(--radius-row)' }}
            >
              {papers.map((ep) => (
                <li key={ep.episode_id} className="flex">
                  <button
                    type="button"
                    onClick={() => sendMessage(`What is the main idea of the episode "${displayTitle(ep.episode_title)}"?`)}
                    title={displayTitle(ep.episode_title)}
                    className="group w-full flex flex-col items-start justify-start text-left px-3.5 py-3 transition-colors hover:bg-[var(--accent-tint)]"
                    style={{ background: 'var(--surface)' }}
                  >
                    <span
                      className="block text-[1.25rem] leading-none font-semibold tabular group-hover:text-[var(--accent)]"
                      style={{ fontFamily: 'var(--font-read)', color: 'var(--ink)' }}
                    >
                      {ep.publication_year ?? '—'}
                    </span>
                    <span className="block mt-1.5 text-[0.8rem] leading-snug" style={{ color: 'var(--ink-soft)' }}>
                      {shortTitle(ep.episode_title, 42)}
                    </span>
                  </button>
                </li>
              ))}
            </ol>
          </section>
        )}

        {failed && (
          <p className="mt-10 text-[0.9rem]" style={{ color: 'var(--danger)' }}>
            Couldn’t load the episode list. Check that the backend is running on port 8000.
          </p>
        )}
      </div>
    </div>
  );
}
