import { useState } from 'react'
import { FileUpload } from '../components/upload/FileUpload'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { api } from '../services/api'

const XLSX_TYPES = {
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
}

const XLSM_TYPES = {
  'application/vnd.ms-excel.sheet.macroEnabled.12': ['.xlsm'],
}

export function GenerateReportsPage() {
  const [masterList, setMasterList] = useState(null)
  const [template, setTemplate] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showWarnings, setShowWarnings] = useState(false)

  const handleGenerate = async () => {
    if (!masterList || !template) return

    setIsProcessing(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.generateReports(masterList, template)

      // Auto-download the ZIP
      const url = window.URL.createObjectURL(response.blob)
      const a = document.createElement('a')
      a.href = url

      const now = new Date()
      const quarter = Math.floor(now.getMonth() / 3) + 1
      const year = String(now.getFullYear()).slice(-2)
      a.download = `BBG_Usage_Reports_Q${quarter}_${year}.zip`

      document.body.appendChild(a)
      a.click()
      setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }, 100)

      setResult(response)
    } catch (err) {
      setError(err.message || 'Report generation failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setMasterList(null)
    setTemplate(null)
    setResult(null)
    setError(null)
    setShowWarnings(false)
  }

  const hasFiles = masterList && template

  return (
    <div className="space-y-8">
      {/* File Upload Section */}
      {!result && !isProcessing && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FileUpload
            onFileSelect={setMasterList}
            isProcessing={isProcessing}
            acceptedFileTypes={XLSX_TYPES}
            title="Master Builder List"
            description="Upload the .xlsx file with Member ID, Builder Name, State, and File Name columns"
            dropzoneText="Drag & drop your Master Builder List"
          />
          <FileUpload
            onFileSelect={setTemplate}
            isProcessing={isProcessing}
            acceptedFileTypes={XLSM_TYPES}
            title="Usage Report Template"
            description="Upload the .xlsm template with macros and formatting intact"
            dropzoneText="Drag & drop your template file"
          />
        </div>
      )}

      {/* Generate Button */}
      {hasFiles && !isProcessing && !result && (
        <div className="flex justify-center">
          <Button onClick={handleGenerate} size="lg" className="px-12">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Generate Reports
          </Button>
        </div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <Card className="max-w-2xl mx-auto border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#178dc3]"></div>
              <div>
                <h3 className="text-lg font-medium text-blue-900">Generating Reports...</h3>
                <p className="text-sm text-blue-700">
                  This may take a few minutes for large builder lists. Please don't close this tab.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Card */}
      {result && (
        <Card className="max-w-2xl mx-auto border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-4">
              <svg className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-green-900">Reports Generated!</h3>
                <p className="mt-1 text-sm text-green-700">
                  {result.filesGenerated} report{result.filesGenerated !== 1 ? 's' : ''} created successfully.
                  {result.rowsSkipped > 0 && (
                    <span className="text-amber-700">
                      {' '}{result.rowsSkipped} row{result.rowsSkipped !== 1 ? 's' : ''} skipped.
                    </span>
                  )}
                </p>

                {/* Collapsible Warnings */}
                {result.warnings.length > 0 && (
                  <div className="mt-3">
                    <button
                      onClick={() => setShowWarnings(!showWarnings)}
                      className="text-sm text-amber-700 hover:text-amber-800 font-medium flex items-center gap-1"
                    >
                      <svg
                        className={`w-4 h-4 transition-transform ${showWarnings ? 'rotate-90' : ''}`}
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      {result.warnings.length} warning{result.warnings.length !== 1 ? 's' : ''}
                    </button>
                    {showWarnings && (
                      <ul className="mt-2 space-y-1 text-xs text-amber-700 bg-amber-50 rounded p-3 border border-amber-200">
                        {result.warnings.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                <Button onClick={handleReset} variant="outline" size="sm" className="mt-4">
                  Generate More Reports
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Card */}
      {error && (
        <Card className="max-w-2xl mx-auto border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-4">
              <svg className="h-6 w-6 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-red-900">Generation Failed</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
                <Button onClick={() => setError(null)} variant="outline" size="sm" className="mt-4">
                  Dismiss
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info Cards */}
      {!hasFiles && !isProcessing && !result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <Card>
            <div className="p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-[#178dc3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">Master Builder List</h3>
              <p className="text-sm text-gray-500">
                Upload the .xlsx file with Member ID, Builder Name, State, and File Name columns.
              </p>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">Template File</h3>
              <p className="text-sm text-gray-500">
                Upload the .xlsm Usage Reporting template with macros and formatting intact.
              </p>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">ZIP Download</h3>
              <p className="text-sm text-gray-500">
                One XLSM per builder — auto-downloaded as a single ZIP file.
              </p>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
