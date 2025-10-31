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
      // Only save custom columns (the 3 new proof point fields)
      const customColumnsOnly = columns.filter(col => col.is_custom)

      const response = await fetch(`${API_BASE_URL}/api/settings/columns/bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          columns: customColumnsOnly.map(col => ({
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

  // Only show custom columns (3 new proof point fields)
  const customColumns = columns.filter(c => c.is_custom)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Proof Point Fields</h2>
        <p className="mt-1 text-sm text-gray-500">
          Select which additional proof point columns to include in your CSV output
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

      {/* Standard Columns Info */}
      <Card className="border-gray-200 bg-gray-50">
        <CardContent className="pt-4">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-gray-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-gray-700">
              <p className="font-medium mb-1">Standard columns are always included</p>
              <p className="text-gray-600">
                The 15 standard TradeNet columns are required and cannot be disabled.
                Use this tab to enable/disable the optional proof point fields below.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Proof Point Columns */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Optional Proof Point Fields</CardTitle>
            <CardDescription>
              Enable additional proof point columns to include in your CSV output. Data is populated from pp_dist_subcontractor via Business Rules.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {customColumns.map((column) => (
              <div
                key={column.column_name}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4 flex-1">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-50 text-blue-700 rounded font-mono text-xs font-semibold">
                    #{column.display_order}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 font-mono">
                      {column.column_name}
                    </h4>
                    {column.description && (
                      <p className="text-sm text-gray-600 mt-0.5">{column.description}</p>
                    )}
                    <div className="mt-2 text-xs">
                      <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                        Populated via Business Rules from pp_dist_subcontractor
                      </span>
                    </div>
                  </div>
                </div>

                <label className="flex items-center space-x-3 cursor-pointer">
                  <span className="text-sm text-gray-600 w-20 text-right font-medium">
                    {column.enabled ? 'Included' : 'Excluded'}
                  </span>
                  <button
                    onClick={() => toggleColumn(column.column_name)}
                    className={`
                      relative inline-flex h-7 w-12 items-center rounded-full transition-colors
                      ${column.enabled ? 'bg-[#178dc3]' : 'bg-gray-300'}
                    `}
                  >
                    <span
                      className={`
                        inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm
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

      {/* Info Card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-gray-600">
              <p className="font-medium text-gray-900 mb-2">How it works:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Enable proof point fields you want included in CSV output</li>
                <li>Data starts in <span className="font-mono text-xs bg-gray-100 px-1">pp_dist_subcontractor</span></li>
                <li>Use <strong>Rules</strong> to move data to these fields</li>
                <li>Example: Move "Carrier" from pp_dist_subcontractor → pp_brand_name</li>
                <li>Disabled columns won't appear in downloaded files</li>
              </ul>
              <div className="mt-3 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="font-medium text-blue-900 text-xs mb-1">💡 Pro Tip:</p>
                <p className="text-blue-700 text-xs">
                  Go to the Rules Engine tab to create rules that move data from pp_dist_subcontractor into these fields based on conditions like product ID or supplier name.
                </p>
              </div>
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
