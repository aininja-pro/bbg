import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '../ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'

export function FileUpload({ onFileSelect, isProcessing, batchMode = false, onFilesSelect }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedFiles, setSelectedFiles] = useState([])

  const onDrop = useCallback((acceptedFiles) => {
    console.log('onDrop called with', acceptedFiles.length, 'files, batchMode:', batchMode)
    if (acceptedFiles && acceptedFiles.length > 0) {
      if (batchMode) {
        // Add to existing files instead of replacing
        setSelectedFiles(prev => {
          const newFiles = [...prev, ...acceptedFiles]
          if (onFilesSelect) {
            onFilesSelect(newFiles)
          }
          return newFiles
        })
      } else {
        const file = acceptedFiles[0]
        setSelectedFile(file)
        if (onFileSelect) {
          onFileSelect(file)
        }
      }
    }
  }, [onFileSelect, onFilesSelect, batchMode])

  const removeFile = (indexToRemove) => {
    setSelectedFiles(prev => {
      const newFiles = prev.filter((_, index) => index !== indexToRemove)
      if (onFilesSelect) {
        onFilesSelect(newFiles)
      }
      return newFiles
    })
  }

  // Create separate dropzone configurations for single and batch modes
  const singleDropzoneOptions = {
    onDrop,
    accept: {
      'application/vnd.ms-excel.sheet.macroEnabled.12': ['.xlsm'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
    multiple: false,
    disabled: isProcessing,
  }

  const batchDropzoneOptions = {
    onDrop,
    accept: {
      'application/vnd.ms-excel.sheet.macroEnabled.12': ['.xlsm'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 0, // unlimited
    multiple: true,
    disabled: isProcessing,
  }

  const dropzoneOptions = batchMode ? batchDropzoneOptions : singleDropzoneOptions
  console.log('Dropzone options:', dropzoneOptions)

  const { getRootProps, getInputProps, isDragActive } = useDropzone(dropzoneOptions)

  const displayFiles = batchMode ? selectedFiles : (selectedFile ? [selectedFile] : [])

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Upload Rebate {batchMode ? 'Files' : 'File'}</CardTitle>
        <CardDescription>
          {batchMode
            ? 'Drag and drop multiple Excel files (.xlsm) or click to browse'
            : 'Drag and drop your quarterly rebate Excel file (.xlsm) or click to browse'
          }
        </CardDescription>
      </CardHeader>
      <CardContent key={batchMode ? 'batch-mode' : 'single-mode'}>
        <div
          {...getRootProps()}
          key={batchMode ? 'dropzone-batch' : 'dropzone-single'}
          className={`
            relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-all duration-200 ease-in-out
            ${isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
            }
            ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />

          <div className="flex flex-col items-center space-y-4">
            {/* Upload Icon */}
            <svg
              className={`w-16 h-16 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>

            {/* Show selected file in single mode */}
            {!batchMode && selectedFile && !isProcessing ? (
              <div className="space-y-2">
                <svg className="w-12 h-12 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-lg font-medium text-gray-900">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <p className="text-xs text-gray-400">
                  Click to replace or drag a new file
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-700">
                  {isDragActive ? 'Drop your files here' : batchMode ? 'Drag & drop files or click to browse' : 'Drag & drop your rebate file'}
                </p>
                <p className="text-sm text-gray-500">
                  {batchMode && displayFiles.length > 0 ? 'Add more files by dragging or clicking' : 'or click to browse'}
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Supported formats: .xlsm, .xlsx (Max 50MB{batchMode ? ' per file' : ''})
                </p>
              </div>
            )}

            {isProcessing && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                <span className="text-sm text-gray-600">Processing file...</span>
              </div>
            )}
          </div>
        </div>

        {/* File List for Batch Mode */}
        {batchMode && selectedFiles.length > 0 && (
          <div className="mt-6 space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">
                {selectedFiles.length} / 50 file{selectedFiles.length > 1 ? 's' : ''} ready
              </h4>
              <Button
                onClick={() => {
                  setSelectedFiles([])
                  if (onFilesSelect) onFilesSelect([])
                }}
                variant="ghost"
                size="sm"
                className="text-xs"
              >
                Clear All
              </Button>
            </div>
            <div className="max-h-60 overflow-y-auto space-y-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="ml-3 p-1 text-red-600 hover:bg-red-50 rounded flex-shrink-0"
                    title="Remove file"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Clear button for single file */}
        {!batchMode && selectedFile && !isProcessing && (
          <div className="mt-4 flex justify-center">
            <Button
              onClick={() => {
                setSelectedFile(null)
              }}
              variant="outline"
              size="sm"
            >
              Clear File
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
