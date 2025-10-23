import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'

export function DataPreview({ data, onDownload, onCancel }) {
  if (!data || !data.preview || data.preview.length === 0) {
    return null
  }

  const columns = Object.keys(data.preview[0])
  const allRows = data.preview

  return (
    <Card className="w-full max-w-[95vw]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Data Preview</CardTitle>
            <CardDescription>
              Scroll to view all {data.total_rows} rows processed for {data.member_name}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-500">
              {data.active_products} products found
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Warnings */}
        {data.warnings && data.warnings.length > 0 && (
          <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <svg className="w-5 h-5 text-amber-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <h4 className="text-sm font-medium text-amber-900">Data Warnings</h4>
                <ul className="mt-1 text-sm text-amber-700 space-y-1">
                  {data.warnings.map((warning, idx) => (
                    <li key={idx}>• {warning.message}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Scrollable Table Container */}
        <div className="overflow-auto rounded-lg border border-gray-200" style={{ maxHeight: '500px' }}>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0 z-10">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap bg-gray-50"
                  >
                    {col.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {allRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  {columns.map((col) => (
                    <td key={col} className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                      {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-2 text-sm text-gray-500 text-center">
          Showing all {allRows.length} rows - scroll to view more
        </div>

        {/* Actions */}
        <div className="mt-6 flex items-center justify-between">
          <Button onClick={onCancel} variant="outline">
            Cancel
          </Button>
          <Button onClick={onDownload} size="lg" className="px-8">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download CSV ({data.total_rows} rows)
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
