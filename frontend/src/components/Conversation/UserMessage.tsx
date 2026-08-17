interface UserMessageProps {
  content: string;
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="flex justify-end mb-8">
      <div 
        className="max-w-[85%] rounded-xl px-5 py-3"
        style={{
          backgroundColor: 'var(--color-bg-subtle)',
          color: 'var(--color-text-primary)'
        }}
      >
        <p className="whitespace-pre-wrap" style={{ fontSize: 'var(--text-base)' }}>
          {content}
        </p>
      </div>
    </div>
  );
}
