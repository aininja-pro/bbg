import { useState } from 'react'
import { FileUpload } from './components/upload/FileUpload'
import { DataPreview } from './components/preview/DataPreview'
import { Button } from './components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/Card'
import { api } from './services/api'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [previewData, setPreviewData] = useState(null)
  const [error, setError] = useState(null)
  const [downloadSuccess, setDownloadSuccess] = useState(false)

  const handleFileSelect = (file) => {
    setSelectedFile(file)
    setPreviewData(null)
    setError(null)
    setDownloadSuccess(false)
  }

  const handleProcess = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError(null)

    try {
      // Upload file and get preview
      const result = await api.uploadFile(selectedFile)

      if (result.success) {
        setPreviewData(result.data)
      } else {
        setError('Processing failed')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDownload = async () => {
    if (!selectedFile) return

    try {
      // Process and download CSV
      const blob = await api.processAndDownload(selectedFile)

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${selectedFile.name.replace('.xlsm', '')}_processed.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setDownloadSuccess(true)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewData(null)
    setError(null)
    setDownloadSuccess(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-600 rounded-lg">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                BBG Rebate Processing Tool
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Transform quarterly rebate files in seconds
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* Upload Section - Only show if no preview */}
          {!previewData && (
            <FileUpload onFileSelect={handleFileSelect} isProcessing={isProcessing} />
          )}

          {/* Process Button */}
          {selectedFile && !isProcessing && !previewData && (
            <div className="flex justify-center">
              <Button onClick={handleProcess} size="lg" className="px-12">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Process & Preview
              </Button>
            </div>
          )}

          {/* Preview Section */}
          {previewData && !downloadSuccess && (
            <DataPreview
              data={previewData}
              onDownload={handleDownload}
              onCancel={handleReset}
            />
          )}

          {/* Success Message */}
          {downloadSuccess && (
            <Card className="max-w-2xl mx-auto border-green-200 bg-green-50">
              <CardContent className="pt-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-green-900">
                      Processing Complete!
                    </h3>
                    <p className="mt-1 text-sm text-green-700">
                      Your CSV file has been downloaded successfully. Ready for FMS import!
                    </p>
                    <Button
                      onClick={handleReset}
                      variant="outline"
                      size="sm"
                      className="mt-4"
                    >
                      Process Another File
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error Message */}
          {error && (
            <Card className="max-w-2xl mx-auto border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-red-900">
                      Processing Error
                    </h3>
                    <p className="mt-1 text-sm text-red-700">
                      {error}
                    </p>
                    <Button
                      onClick={() => setError(null)}
                      variant="outline"
                      size="sm"
                      className="mt-4"
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info Cards */}
          {!selectedFile && !isProcessing && !previewData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <Card>
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <CardTitle className="text-lg">Fast Processing</CardTitle>
                  <CardDescription>
                    Process files in under 2 minutes. What used to take weeks now takes seconds.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <CardTitle className="text-lg">Automatic Validation</CardTitle>
                  <CardDescription>
                    Built-in data validation and enrichment with TradeNet lookups.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </div>
                  <CardTitle className="text-lg">FMS Ready</CardTitle>
                  <CardDescription>
                    CSV output is formatted and ready for direct FMS import.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            Builders Buying Group - Rebate Processing Automation Tool
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
