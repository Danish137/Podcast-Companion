import ReactMarkdown from 'react-markdown';
import { SourceCard } from './SourceCard';
import type { SourceEvidence } from '../../types/api';

interface AssistantMessageProps {
  content: string;
  sources?: SourceEvidence[];
}

export function AssistantMessage({ content, sources }: AssistantMessageProps) {
  return (
    <div className="mb-12">
      <div className="prose max-w-none">
        <ReactMarkdown
          components={{
            p: ({ children }) => (
              <p 
                className="leading-relaxed mb-5"
                style={{ 
                  color: 'var(--color-text-primary)',
                  fontSize: 'var(--text-base)',
                  lineHeight: '1.8'
                }}
              >
                {children}
              </p>
            ),
            ul: ({ children }) => (
              <ul 
                className="list-disc pl-6 space-y-2 mb-5"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol 
                className="list-decimal pl-6 space-y-2 mb-5"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {children}
              </ol>
            ),
            li: ({ children }) => (
              <li style={{ lineHeight: '1.75' }}>{children}</li>
            ),
            strong: ({ children }) => (
              <strong 
                className="font-semibold"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {children}
              </strong>
            ),
            em: ({ children }) => (
              <em>{children}</em>
            ),
            code: ({ children }) => (
              <code 
                className="px-1.5 py-0.5 rounded text-sm font-mono"
                style={{
                  backgroundColor: 'var(--color-bg-subtle)',
                  color: 'var(--color-text-primary)'
                }}
              >
                {children}
              </code>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>

      {sources && sources.length > 0 && (
        <div className="mt-8 space-y-4">
          {sources.map((source, index) => (
            <SourceCard key={index} source={source} />
          ))}
        </div>
      )}
    </div>
  );
}
