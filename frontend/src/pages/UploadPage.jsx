import { useState } from 'react'
import { FileUpload } from '../components/upload/FileUpload'
import { DataPreview } from '../components/preview/DataPreview'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { api } from '../services/api'

export function UploadPage() {
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

    setIsProcessing(true)
    setError(null)

    try {
      const blob = await api.processAndDownload(selectedFile)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const filename = `${selectedFile.name.replace('.xlsm', '').replace('.xlsx', '')}_processed.csv`
      a.download = filename
      document.body.appendChild(a)
      a.click()

      setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }, 100)

      setDownloadSuccess(true)
      setPreviewData(null)
    } catch (err) {
      setError(err.message || 'Download failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewData(null)
    setError(null)
    setDownloadSuccess(false)
  }

  return (
    <div className="space-y-8">
      {/* Upload Section */}
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

      {/* Preview */}
      {previewData && !downloadSuccess && (
        <DataPreview
          data={previewData}
          onDownload={handleDownload}
          onCancel={handleReset}
        />
      )}

      {/* Success */}
      {downloadSuccess && (
        <Card className="max-w-2xl mx-auto border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-4">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-green-900">Processing Complete!</h3>
                <p className="mt-1 text-sm text-green-700">
                  Your CSV file has been downloaded successfully. Ready for FMS import!
                </p>
                <Button onClick={handleReset} variant="outline" size="sm" className="mt-4">
                  Process Another File
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {error && (
        <Card className="max-w-2xl mx-auto border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-4">
              <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-red-900">Processing Error</h3>
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
      {!selectedFile && !isProcessing && !previewData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <Card>
            <div className="p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">Fast Processing</h3>
              <p className="text-sm text-gray-500">
                Process files in under 2 minutes. What used to take weeks now takes seconds.
              </p>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">Automatic Validation</h3>
              <p className="text-sm text-gray-500">
                Built-in data validation and enrichment with TradeNet lookups.
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
              <h3 className="text-lg font-semibold mb-2">FMS Ready</h3>
              <p className="text-sm text-gray-500">
                CSV output is formatted and ready for direct FMS import.
              </p>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
