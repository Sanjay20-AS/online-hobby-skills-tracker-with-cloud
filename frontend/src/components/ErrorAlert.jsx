export function ErrorAlert({ title = 'Error', message, onDismiss = null }) {
  return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-red-600 text-xl">⚠️</span>
        <div className="flex-1">
          <h4 className="font-semibold text-red-900">{title}</h4>
          <p className="text-red-800 text-sm mt-1">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-600 hover:text-red-900 text-xl font-light leading-none"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

export function SuccessAlert({ title = 'Success', message, onDismiss = null }) {
  return (
    <div className="rounded-lg bg-green-50 border border-green-200 p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-green-600 text-xl">✓</span>
        <div className="flex-1">
          <h4 className="font-semibold text-green-900">{title}</h4>
          <p className="text-green-800 text-sm mt-1">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-green-600 hover:text-green-900 text-xl font-light leading-none"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
