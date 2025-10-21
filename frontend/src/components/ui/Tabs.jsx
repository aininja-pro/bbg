import { cn } from '../../lib/utils'

export function Tabs({ value, onValueChange, children, className }) {
  return (
    <div className={cn('w-full', className)}>
      {children({ value, onValueChange })}
    </div>
  )
}

export function TabsList({ children, className }) {
  return (
    <div className={cn('inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1', className)}>
      {children}
    </div>
  )
}

export function TabsTrigger({ value, activeValue, onValueChange, children, className }) {
  const isActive = value === activeValue

  return (
    <button
      onClick={() => onValueChange(value)}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        isActive
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-600 hover:bg-gray-200/50',
        className
      )}
    >
      {children}
    </button>
  )
}

export function TabsContent({ value, activeValue, children, className }) {
  if (value !== activeValue) return null

  return (
    <div className={cn('mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2', className)}>
      {children}
    </div>
  )
}
