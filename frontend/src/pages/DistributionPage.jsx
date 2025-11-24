import { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { FileUpload } from '../components/upload/FileUpload'
import { api } from '../services/api'

export function DistributionPage() {
  const [mode, setMode] = useState('mode1')
  const [files, setFiles] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [error, setError] = useState(null)
  const [downloadReady, setDownloadReady] = useState(false)
  const [statusInfo, setStatusInfo] = useState(null)
  const [fileInputKey, setFileInputKey] = useState(Date.now())
  const [isDragging, setIsDragging] = useState(false)
  const pollingIntervalRef = useRef(null)

  const handleFilesSelect = (selectedFiles) => {
    console.log('handleFilesSelect called with', selectedFiles.length, 'files')
    setFiles(selectedFiles)
    setError(null)
    setDownloadReady(false)
    setJobId(null)
    setStatusInfo(null)
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const droppedFiles = Array.from(e.dataTransfer.files).filter(file => file.name.endsWith('.csv'))
    if (droppedFiles.length > 0) {
      handleFilesSelect(droppedFiles)
    } else {
      setError('Please drop CSV files only')
    }
  }

  const checkStatus = async (currentJobId) => {
    try {
      console.log('Checking status for job:', currentJobId)
      const status = await api.getDistributionStatus(currentJobId)
      console.log('FULL Status response:', JSON.stringify(status, null, 2))
      console.log('Status value:', status.status)
      console.log('Download ready state BEFORE update:', downloadReady)
      console.log('Is processing state BEFORE update:', isProcessing)

      setStatusInfo(status)

      if (status.status === 'completed') {
        console.log('STATUS IS COMPLETED - Setting downloadReady=true, isProcessing=false')
        setDownloadReady(true)
        setIsProcessing(false)
        if (pollingIntervalRef.current) {
          console.log('Clearing polling interval')
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }
        return true
      } else if (status.status === 'failed') {
        console.log('Processing failed:', status.error_message)
        setIsProcessing(false)
        setError(status.error_message || 'Processing failed')
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }
        return true
      } else {
        console.log('Status is still:', status.status, '- continuing to poll')
      }
      return false
    } catch (err) {
      console.error('Failed to get status:', err)
      return false
    }
  }

  const startPolling = (currentJobId) => {
    console.log('Starting polling for job:', currentJobId)

    // Clear any existing interval
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
    }

    // Check immediately
    checkStatus(currentJobId)

    // Then poll every 2 seconds
    pollingIntervalRef.current = setInterval(() => {
      checkStatus(currentJobId)
    }, 2000)
  }

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [])

  const handleProcess = async () => {
    if (files.length === 0) {
      setError('Please upload at least one CSV file')
      return
    }

    setIsProcessing(true)
    setError(null)
    setDownloadReady(false)
    setStatusInfo(null)

    try {
      console.log('Submitting processing request with mode:', mode, 'files:', files.length)
      const result = await api.processDistribution(files, mode)
      console.log('Processing started, job_id:', result.job_id)
      setJobId(result.job_id)

      // Start polling for status
      startPolling(result.job_id)
    } catch (err) {
      console.error('Process error:', err)
      setIsProcessing(false)
      setError(err.message || 'Failed to process files')
    }
  }

  const handleDownload = async () => {
    if (!jobId) return

    try {
      console.log('Downloading file for job:', jobId)
      const blob = await api.downloadByJobId(jobId)

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = statusInfo?.filename || `${mode}_distribution.zip`
      document.body.appendChild(a)
      a.click()

      setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }, 100)

      console.log('Download triggered successfully')
    } catch (err) {
      console.error('Download error:', err)
      setError(err.message || 'Failed to download file')
    }
  }

  const handleReset = () => {
    setFiles([])
    setIsProcessing(false)
    setJobId(null)
    setError(null)
    setDownloadReady(false)
    setStatusInfo(null)
    setFileInputKey(Date.now()) // Reset file input
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }

  return (
    <div className="space-y-4">
      {/* Header - Compact */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">Supplier Distribution Reports</h2>
        <p className="text-xs text-gray-600">Upload merged CSV files and generate Excel reports</p>
      </div>

      {/* Mode Selector - Side by Side */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Select Report Mode</h3>
          <div className="grid grid-cols-2 gap-3">
            {/* Mode 1 */}
            <label className="flex items-start space-x-2 p-3 border-2 rounded cursor-pointer hover:bg-gray-50"
              style={{ borderColor: mode === 'mode1' ? '#178dc3' : '#e5e7eb' }}>
              <input
                type="radio"
                name="mode"
                value="mode1"
                checked={mode === 'mode1'}
                onChange={(e) => setMode(e.target.value)}
                className="mt-0.5"
                style={{ accentColor: '#178dc3' }}
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-900">Supplier Reports</span>
                <p className="text-xs text-gray-600 mt-0.5">One Excel per supplier with product tabs</p>
              </div>
            </label>

            {/* Mode 2 */}
            <label className="flex items-start space-x-2 p-3 border-2 rounded cursor-pointer hover:bg-gray-50"
              style={{ borderColor: mode === 'mode2' ? '#178dc3' : '#e5e7eb' }}>
              <input
                type="radio"
                name="mode"
                value="mode2"
                checked={mode === 'mode2'}
                onChange={(e) => setMode(e.target.value)}
                className="mt-0.5"
                style={{ accentColor: '#178dc3' }}
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-900">Territory Manager Reports</span>
                <p className="text-xs text-gray-600 mt-0.5">One Excel per TM with supplier tabs</p>
              </div>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* File Upload - Compact */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Upload CSV Files</h3>
          <div
            className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors cursor-pointer ${
              isDragging ? 'border-[#178dc3] bg-blue-50' : 'border-gray-300 hover:border-[#178dc3]'
            }`}
            onClick={() => document.getElementById('csv-file-input').click()}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              key={fileInputKey}
              id="csv-file-input"
              type="file"
              accept=".csv"
              multiple
              onChange={(e) => {
                handleFilesSelect(Array.from(e.target.files))
              }}
              className="hidden"
            />
            <svg className="w-8 h-8 mx-auto text-[#178dc3] opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-xs text-gray-700 mt-1 font-medium">
              {isDragging ? 'Drop CSV files here' : 'Click to upload CSV files'}
            </p>
            <p className="text-xs text-gray-500">or drag and drop (multiple files supported)</p>
          </div>
          {files.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600 font-medium">{files.length} file{files.length !== 1 ? 's' : ''} selected</p>
              <div className="mt-1 space-y-1 max-h-24 overflow-y-auto">
                {files.map((file, idx) => (
                  <div key={idx} className="text-xs text-gray-500 flex items-center justify-between bg-gray-50 p-1.5 rounded">
                    <span className="truncate">{file.name}</span>
                    <button onClick={(e) => {
                      e.stopPropagation()
                      const newFiles = files.filter((_, i) => i !== idx)
                      handleFilesSelect(newFiles)
                      if (newFiles.length === 0) {
                        setFileInputKey(Date.now())
                      }
                    }} className="text-red-500 hover:text-red-700 ml-2 font-bold">×</button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Process Button */}
      {!isProcessing && !downloadReady && (
        <Button
          onClick={handleProcess}
          disabled={files.length === 0}
          className="w-full py-3"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Generate Reports
        </Button>
      )}

      {/* Processing Status - Compact with Real Progress Bar */}
      {isProcessing && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-4 pb-4">
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#178dc3]"></div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-blue-900">Processing Reports...</h3>
                  <p className="text-xs text-blue-700">{mode === 'mode1' ? 'Generating supplier reports' : 'Generating TM reports'}</p>
                  {statusInfo && statusInfo.total_rows > 0 && (
                    <p className="text-xs text-blue-600 mt-1">{statusInfo.total_rows?.toLocaleString()} rows</p>
                  )}
                </div>
              </div>

              {/* Real Progress Bar */}
              <div className="space-y-1">
                <div className="w-full bg-blue-200 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="h-full bg-[#178dc3] rounded-full transition-all duration-300 ease-out"
                    style={{
                      width: `${statusInfo?.metadata?.progress || 0}%`
                    }}>
                  </div>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-blue-700">
                    {statusInfo?.metadata?.progress_message || 'Starting...'}
                  </span>
                  <span className="text-blue-600 font-medium">
                    {statusInfo?.metadata?.progress || 0}%
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Download Ready - Compact */}
      {downloadReady && jobId && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-4 pb-4">
            <div className="flex items-start space-x-3">
              <svg className="h-8 w-8 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-green-900">Reports Ready!</h3>
                <p className="text-xs text-green-700">Reports generated successfully.</p>
                {statusInfo && (
                  <p className="text-xs text-green-600 mt-1">
                    {statusInfo.total_rows?.toLocaleString()} rows | {(statusInfo.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                  </p>
                )}
                <div className="mt-3 flex space-x-2">
                  <Button onClick={handleDownload} className="bg-green-600 hover:bg-green-700 text-sm py-2">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download ZIP
                  </Button>
                  <Button onClick={handleReset} variant="outline" className="text-sm py-2">
                    Reset
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display - Compact */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-4 pb-4">
            <div className="flex items-start space-x-3">
              <svg className="h-5 w-5 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-red-900">Error</h3>
                <p className="text-xs text-red-700 mt-1">{error}</p>
                <Button onClick={() => setError(null)} variant="outline" className="mt-2 text-xs py-1">
                  Dismiss
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Information Card - Compact */}
      {!isProcessing && !downloadReady && !error && (
        <Card className="border-gray-200 bg-gray-50">
          <CardContent className="pt-3 pb-3">
            <h4 className="text-xs font-semibold text-gray-900 mb-1.5">Quick Info:</h4>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• Mode 1: One Excel per supplier with product tabs</li>
              <li>• Mode 2: One Excel per TM with supplier tabs</li>
              <li>• All packaged in ZIP | 24-hour cache</li>
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
