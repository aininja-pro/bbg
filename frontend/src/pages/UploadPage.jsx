import { useState } from 'react'
import { FileUpload } from '../components/upload/FileUpload'
import { DataPreview } from '../components/preview/DataPreview'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { api } from '../services/api'

export function UploadPage() {
  const [batchMode, setBatchMode] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [outputMode, setOutputMode] = useState('zip')
  const [isProcessing, setIsProcessing] = useState(false)
  const [previewData, setPreviewData] = useState(null)
  const [error, setError] = useState(null)
  const [downloadSuccess, setDownloadSuccess] = useState(false)
  const [jobId, setJobId] = useState(null) // Store job_id for cached downloads

  const handleFileSelect = (file) => {
    setSelectedFile(file)
    setPreviewData(null)
    setError(null)
    setDownloadSuccess(false)
    setJobId(null) // Clear job_id when new file selected
  }

  const handleFilesSelect = (files) => {
    // Check if exceeds limit
    if (files.length > 50) {
      setError(`Maximum batch size is 50 files. You selected ${files.length} files. Please reduce the number of files.`)
      return
    }

    setSelectedFiles(files)
    setPreviewData(null)
    setError(null)
    setDownloadSuccess(false)
    setJobId(null) // Clear job_id when new files selected
  }

  const handleBatchModeToggle = () => {
    setBatchMode(!batchMode)
    setSelectedFile(null)
    setSelectedFiles([])
    setPreviewData(null)
    setError(null)
  }

  const handleProcess = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError(null)

    try {
      // Process in parallel: get preview AND cache the result
      const [previewResult, cacheResult] = await Promise.all([
        api.uploadFile(selectedFile),  // Old endpoint for preview
        api.uploadWithCache(selectedFile)  // New endpoint for caching
      ])

      if (previewResult.success) {
        setPreviewData(previewResult.data)

        // Store job_id from cache for instant downloads
        if (cacheResult.job_id) {
          setJobId(cacheResult.job_id)
        }
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
    if (!selectedFile && !jobId) return

    setIsProcessing(true)
    setError(null)

    try {
      let blob

      if (jobId) {
        // INSTANT DOWNLOAD from cache using job_id!
        blob = await api.downloadByJobId(jobId)
      } else {
        // Fallback to old method (reprocess)
        blob = await api.processAndDownload(selectedFile)
      }

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

  const handleBatchProcess = async () => {
    if (selectedFiles.length === 0) return

    setIsProcessing(true)
    setError(null)

    try {
      // Use CACHED batch processing for both modes
      const result = await api.batchProcessWithCache(selectedFiles, outputMode)

      if (result.job_id && result.status === 'completed') {
        // Store job_id for instant downloads
        setJobId(result.job_id)

        if (outputMode === 'merged') {
          // For merged mode, download the CSV and parse it for preview
          const blob = await api.downloadByJobId(result.job_id)
          const text = await blob.text()
          const rows = text.split('\n').filter(row => row.trim())
          const headers = rows[0].split(',')
          const dataRows = rows.slice(1, 201).map(row => { // Show first 200 rows
            const values = row.split(',')
            return headers.reduce((obj, header, index) => {
              obj[header] = values[index]
              return obj
            }, {})
          })

          // Show preview
          setPreviewData({
            preview: dataRows,
            total_rows: rows.length - 1, // Exclude header
            member_name: `${selectedFiles.length} files merged`,
            bbg_member_id: 'Batch',
          })
        } else {
          // ZIP mode - automatically download
          const blob = await api.downloadByJobId(result.job_id)
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url

          const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
          const filename = `Batch_Processed_${selectedFiles.length}_files_${timestamp}.zip`

          a.download = filename
          document.body.appendChild(a)
          a.click()

          setTimeout(() => {
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
          }, 100)

          setDownloadSuccess(true)
        }
      } else {
        setError('Processing failed')
      }
    } catch (err) {
      setError(err.message || 'Batch processing failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleBatchDownload = async () => {
    // This is called from preview after user confirms
    if (!jobId && selectedFiles.length === 0) return

    setIsProcessing(true)
    setError(null)

    try {
      let blob

      if (jobId) {
        // INSTANT DOWNLOAD from cache using job_id!
        blob = await api.downloadByJobId(jobId)
      } else {
        // Fallback to old method (reprocess)
        blob = await api.batchProcess(selectedFiles, 'merged')
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
      const filename = `Batch_Merged_${selectedFiles.length}_files_${timestamp}.csv`

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
      setError(err.message || 'Batch download failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setSelectedFiles([])
    setPreviewData(null)
    setError(null)
    setDownloadSuccess(false)
    setJobId(null)
  }

  const hasFiles = batchMode ? selectedFiles.length > 0 : selectedFile !== null

  return (
    <div className="space-y-8">
      {/* Batch Mode Toggle & Output Format */}
      {!previewData && !downloadSuccess && (
        <div className="flex justify-center">
          <Card className="inline-block">
            <CardContent className="pt-6">
              <div className="flex items-start gap-6">
                {/* Batch Mode Checkbox */}
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={batchMode}
                    onChange={handleBatchModeToggle}
                    disabled={isProcessing}
                    className="w-5 h-5 rounded focus:ring-2"
                    style={{ accentColor: '#178dc3' }}
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      Batch Mode
                    </span>
                    <p className="text-xs text-gray-500">Process up to 50 files at once</p>
                  </div>
                </label>

                {/* Output Format (shown when batch mode is enabled) */}
                {batchMode && (
                  <div className="flex items-start gap-4 pl-6 border-l-2 border-gray-200">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        value="merged"
                        checked={outputMode === 'merged'}
                        onChange={(e) => setOutputMode(e.target.value)}
                        className="w-4 h-4"
                        style={{ accentColor: '#178dc3' }}
                      />
                      <div>
                        <span className="text-sm font-medium text-gray-900">Merged CSV</span>
                        <p className="text-xs text-gray-500">Single combined file</p>
                      </div>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        value="zip"
                        checked={outputMode === 'zip'}
                        onChange={(e) => setOutputMode(e.target.value)}
                        className="w-4 h-4"
                        style={{ accentColor: '#178dc3' }}
                      />
                      <div>
                        <span className="text-sm font-medium text-gray-900">ZIP Archive</span>
                        <p className="text-xs text-gray-500">Individual files</p>
                      </div>
                    </label>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Upload Section */}
      {!previewData && !downloadSuccess && (
        <FileUpload
          onFileSelect={handleFileSelect}
          onFilesSelect={handleFilesSelect}
          isProcessing={isProcessing}
          batchMode={batchMode}
        />
      )}


      {/* Process Button */}
      {!batchMode && selectedFile && !isProcessing && !previewData && !downloadSuccess && (
        <div className="flex justify-center">
          <Button onClick={handleProcess} size="lg" className="px-12">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Process & Preview
          </Button>
        </div>
      )}

      {/* Batch Process Button */}
      {batchMode && selectedFiles.length > 0 && !isProcessing && !downloadSuccess && !previewData && (
        <div className="flex justify-center">
          <Button onClick={handleBatchProcess} size="lg" className="px-12">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {outputMode === 'merged' ? `Process & Preview ${selectedFiles.length} Files` : `Process & Download ${selectedFiles.length} Files`}
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
                <h3 className="text-lg font-medium text-blue-900">Processing...</h3>
                <p className="text-sm text-blue-700">
                  {batchMode ? `Processing ${selectedFiles.length} files...` : 'Processing file...'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Preview */}
      {previewData && !downloadSuccess && (
        <DataPreview
          data={previewData}
          onDownload={batchMode ? handleBatchDownload : handleDownload}
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
                  {batchMode
                    ? `${selectedFiles.length} files processed successfully. ${outputMode === 'merged' ? 'All data merged into a single CSV.' : 'Individual CSVs bundled in a ZIP file.'}`
                    : 'Your CSV file has been downloaded successfully. Ready for FMS import!'
                  }
                </p>
                <Button onClick={handleReset} variant="outline" size="sm" className="mt-4">
                  Process {batchMode ? 'More' : 'Another'} File{batchMode ? 's' : ''}
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
      {!hasFiles && !isProcessing && !previewData && !downloadSuccess && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <Card>
            <div className="p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-[#178dc3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
              <h3 className="text-lg font-semibold mb-2">Batch Processing</h3>
              <p className="text-sm text-gray-500">
                Process hundreds of files at once. Merged CSV or individual files in a ZIP.
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
              <h3 className="text-lg font-semibold mb-2">TradeNet Ready</h3>
              <p className="text-sm text-gray-500">
                CSV output is formatted and ready for direct TradeNet import.
              </p>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
