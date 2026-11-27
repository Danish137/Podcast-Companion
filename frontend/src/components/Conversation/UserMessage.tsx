export function UserMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-end rise">
      <p
        className="max-w-[85%] m-0 whitespace-pre-wrap px-4 py-2.5 text-[0.97rem]"
        style={{
          background: 'var(--accent-tint)',
          color: 'var(--ink)',
          borderRadius: '18px 18px 6px 18px',
        }}
      >
        {content}
      </p>
    </div>
  );
}
