function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  disabled = false
}) {
  return (
    <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-200 rounded-full mb-4">
          {icon || (
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          )}
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {title || 'No data yet'}
        </h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          {description || 'Get started by adding your first item.'}
        </p>
        {(actionLabel || secondaryActionLabel) && (
          <div className="flex items-center justify-center space-x-3">
            {actionLabel && (
              <button
                onClick={onAction}
                disabled={disabled}
                className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {actionLabel}
              </button>
            )}
            {secondaryActionLabel && (
              <button
                onClick={onSecondaryAction}
                disabled={disabled}
                className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-gray-700 bg-white rounded-lg hover:bg-gray-50 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {secondaryActionLabel}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default EmptyState;
