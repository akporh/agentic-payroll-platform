interface Props {
  type: 'error' | 'warning' | 'success' | 'info';
  title?: string;
  messages: string[];
}

const STYLES = {
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-amber-50 border-amber-200 text-amber-800',
  success: 'bg-green-50 border-green-200 text-green-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

export function AlertBox({ type, title, messages }: Props) {
  if (!messages.length) return null;
  return (
    <div className={`rounded border px-4 py-3 text-sm ${STYLES[type]}`}>
      {title && <p className="font-semibold mb-1">{title}</p>}
      <ul className="space-y-0.5 list-disc list-inside">
        {messages.map((m, i) => (
          <li key={i}>{m}</li>
        ))}
      </ul>
    </div>
  );
}
