import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export function FieldsPage() {
  const [columns, setColumns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    fetchColumns()
  }, [])

  const fetchColumns = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/columns/all`)

      if (response.status === 404 || response.status === 500) {
        // No columns yet, initialize them
        await initializeColumns()
        return
      }

      const data = await response.json()

      if (data.length === 0) {
        // No columns, initialize
        await initializeColumns()
      } else {
        setColumns(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const initializeColumns = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/columns/initialize`, {
        method: 'POST',
      })
      const data = await response.json()
      setColumns(data)
    } catch (err) {
      setError('Failed to initialize column settings')
    } finally {
      setLoading(false)
    }
  }

  const toggleColumn = (columnName) => {
    setColumns(columns.map(col =>
      col.column_name === columnName
        ? { ...col, enabled: !col.enabled }
        : col
    ))
    setHasChanges(true)
    setSaveSuccess(false)
  }

  const handleSave = async () => {
    setError(null)
    setSaveSuccess(false)

    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/columns/bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          columns: columns.map(col => ({
            column_name: col.column_name,
            enabled: col.enabled,
            display_order: col.display_order,
            is_custom: col.is_custom,
            description: col.description,
          }))
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to save settings')
      }

      setSaveSuccess(true)
      setHasChanges(false)

      // Auto-hide success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleReset = async () => {
    if (!confirm('Reset all column settings to defaults?')) return
    await initializeColumns()
    setHasChanges(false)
    setSaveSuccess(false)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#178dc3]"></div>
      </div>
    )
  }

  // Group columns
  const standardColumns = columns.filter(c => !c.is_custom)
  const customColumns = columns.filter(c => c.is_custom)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Output Fields</h2>
        <p className="mt-1 text-sm text-gray-500">
          Select which columns to include in your CSV output
        </p>
      </div>

      {/* Save Bar */}
      {hasChanges && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium text-blue-900">
                  You have unsaved changes
                </span>
              </div>
              <Button onClick={handleSave}>
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Message */}
      {saveSuccess && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-medium text-green-900">
                Settings saved successfully!
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm text-red-700">{error}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setError(null)}>
                Dismiss
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Standard Columns */}
      <Card>
        <CardHeader>
          <CardTitle>Standard Columns</CardTitle>
          <CardDescription>
            Required TradeNet fields - these should generally remain enabled
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {standardColumns.map((column) => (
              <div
                key={column.column_name}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4 flex-1">
                  <div className="flex items-center justify-center w-8 h-8 bg-gray-100 text-gray-600 rounded font-mono text-xs">
                    {column.display_order}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 font-mono text-sm">
                      {column.column_name}
                    </h4>
                    {column.description && (
                      <p className="text-xs text-gray-500 mt-0.5">{column.description}</p>
                    )}
                  </div>
                </div>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <span className="text-xs text-gray-500 w-16 text-right">
                    {column.enabled ? 'Included' : 'Excluded'}
                  </span>
                  <button
                    onClick={() => toggleColumn(column.column_name)}
                    className={`
                      relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${column.enabled ? 'bg-[#178dc3]' : 'bg-gray-200'}
                    `}
                  >
                    <span
                      className={`
                        inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${column.enabled ? 'translate-x-6' : 'translate-x-1'}
                      `}
                    />
                  </button>
                </label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* New Proof Point Columns */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>New Proof Point Fields</CardTitle>
              <CardDescription>
                Additional proof point columns requested by client (currently disabled pending data source confirmation)
              </CardDescription>
            </div>
            <div className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
              Pending Data Source
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {customColumns.map((column) => (
              <div
                key={column.column_name}
                className="flex items-center justify-between p-3 border rounded-lg bg-gray-50"
              >
                <div className="flex items-center space-x-4 flex-1">
                  <div className="flex items-center justify-center w-8 h-8 bg-yellow-100 text-yellow-700 rounded font-mono text-xs">
                    {column.display_order}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-700 font-mono text-sm">
                      {column.column_name}
                    </h4>
                    {column.description && (
                      <p className="text-xs text-gray-500 mt-0.5">{column.description}</p>
                    )}
                    <p className="text-xs text-yellow-600 mt-1">
                      ⚠️ Data source not yet configured - will be enabled when Rob provides details
                    </p>
                  </div>
                </div>

                <label className="flex items-center space-x-2 opacity-50 cursor-not-allowed">
                  <span className="text-xs text-gray-400 w-16 text-right">
                    Disabled
                  </span>
                  <button
                    disabled
                    className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 cursor-not-allowed"
                  >
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-1" />
                  </button>
                </label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-gray-600">
              <p className="font-medium text-gray-900 mb-1">How it works:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Toggle columns on/off to customize your CSV output</li>
                <li>Disabled columns won't appear in downloaded files</li>
                <li>Column order matches the display order number</li>
                <li>Changes apply to all future file processing</li>
                <li>Click "Save Changes" to apply your preferences</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4">
        <Button variant="outline" onClick={handleReset}>
          Reset to Defaults
        </Button>
        {hasChanges && (
          <Button onClick={handleSave} size="lg">
            Save Changes
          </Button>
        )}
      </div>
    </div>
  )
}
