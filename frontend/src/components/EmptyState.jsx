export function EmptyState({ icon = '📭', title, description, action = null }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-gray-600 text-center max-w-xs mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}
