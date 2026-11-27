import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import type { SourceEvidence } from '../../types/api';
import { useEpisodes } from '../../hooks/useEpisodes';
import { linkCitations, parseCiteHref } from '../../utils/citations';
import { CitationChip } from './CitationChip';
import { SourceList } from './SourceList';

interface AssistantMessageProps {
  content: string;
  sources?: SourceEvidence[];
}

export function AssistantMessage({ content, sources }: AssistantMessageProps) {
  const { episodes } = useEpisodes();
  const markdown = useMemo(() => linkCitations(content, episodes, sources), [content, episodes, sources]);

  return (
    <article className="rise">
      <div className="answer">
        <ReactMarkdown
          components={{
            a: ({ href, children }) => {
              const cite = parseCiteHref(href);
              if (cite) {
                return (
                  <CitationChip episodeId={cite.episodeId} seconds={cite.seconds}>
                    {children}
                  </CitationChip>
                );
              }
              return (
                <a href={href} className="external" target="_blank" rel="noreferrer">
                  {children}
                </a>
              );
            },
          }}
        >
          {markdown}
        </ReactMarkdown>
      </div>

      {sources && sources.length > 0 && <SourceList sources={sources} />}
    </article>
  );
}
