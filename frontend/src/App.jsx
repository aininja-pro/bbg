import { useState } from 'react'
import { UploadPage } from './pages/UploadPage'
import { RulesManager } from './components/rules/RulesManager'
import { LookupTablesPage } from './pages/LookupTablesPage'
import { FieldsPage } from './pages/FieldsPage'
import { DistributionPage } from './pages/DistributionPage'
import bbgLogo from './assets/bbg-logo.svg'

function App() {
  const [mainTab, setMainTab] = useState('processing')
  const [processingSubTab, setProcessingSubTab] = useState('upload')
  const [reportsSubTab, setReportsSubTab] = useState('distribution')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-4">
            <img src={bbgLogo} alt="Builders Buying Group" className="h-10 w-auto" />
            <div className="h-10 w-px bg-gray-300"></div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Rebate Processing Tool
              </h1>
              <p className="text-xs text-gray-500">
                Transform quarterly rebate files in seconds
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Navigation Tabs */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-12">
            <button
              onClick={() => setMainTab('processing')}
              className={`
                py-4 px-1 inline-flex items-center border-b-4 font-semibold text-base transition-colors
                ${mainTab === 'processing'
                  ? 'border-[#178dc3] text-[#178dc3]'
                  : 'border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300'
                }
              `}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Import Converter
            </button>

            <button
              onClick={() => setMainTab('reports')}
              className={`
                py-4 px-1 inline-flex items-center border-b-4 font-semibold text-base transition-colors
                ${mainTab === 'reports'
                  ? 'border-[#178dc3] text-[#178dc3]'
                  : 'border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300'
                }
              `}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export Converter
            </button>
          </nav>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="bg-gray-50 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {mainTab === 'processing' && (
            <nav className="flex space-x-8">
              <button
                onClick={() => setProcessingSubTab('upload')}
                className={`
                  py-3 px-1 inline-flex items-center border-b-2 font-medium text-sm transition-colors
                  ${processingSubTab === 'upload'
                    ? 'border-[#178dc3] text-[#178dc3]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Upload & Process
              </button>

              <button
                onClick={() => setProcessingSubTab('rules')}
                className={`
                  py-3 px-1 inline-flex items-center border-b-2 font-medium text-sm transition-colors
                  ${processingSubTab === 'rules'
                    ? 'border-[#178dc3] text-[#178dc3]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                Rules Engine
              </button>

              <button
                onClick={() => setProcessingSubTab('fields')}
                className={`
                  py-3 px-1 inline-flex items-center border-b-2 font-medium text-sm transition-colors
                  ${processingSubTab === 'fields'
                    ? 'border-[#178dc3] text-[#178dc3]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                </svg>
                Fields
              </button>

              <button
                onClick={() => setProcessingSubTab('lookups')}
                className={`
                  py-3 px-1 inline-flex items-center border-b-2 font-medium text-sm transition-colors
                  ${processingSubTab === 'lookups'
                    ? 'border-[#178dc3] text-[#178dc3]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Lookup Tables
              </button>
            </nav>
          )}

          {mainTab === 'reports' && (
            <nav className="flex space-x-8">
              <button
                onClick={() => setReportsSubTab('distribution')}
                className={`
                  py-3 px-1 inline-flex items-center border-b-2 font-medium text-sm transition-colors
                  ${reportsSubTab === 'distribution'
                    ? 'border-[#178dc3] text-[#178dc3]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Reports
              </button>

              <button
                onClick={() => setReportsSubTab('lookups')}
                className={`
                  py-3 px-1 inline-flex items-center border-b-2 font-medium text-sm transition-colors
                  ${reportsSubTab === 'lookups'
                    ? 'border-[#178dc3] text-[#178dc3]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Lookup Tables
              </button>
            </nav>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Phase 1 - Processing Content */}
        {mainTab === 'processing' && processingSubTab === 'upload' && <UploadPage />}
        {mainTab === 'processing' && processingSubTab === 'rules' && <RulesManager />}
        {mainTab === 'processing' && processingSubTab === 'fields' && <FieldsPage />}
        {mainTab === 'processing' && processingSubTab === 'lookups' && <LookupTablesPage />}

        {/* Phase 2 - Reports Content */}
        {mainTab === 'reports' && reportsSubTab === 'distribution' && <DistributionPage />}
        {mainTab === 'reports' && reportsSubTab === 'lookups' && <LookupTablesPage />}
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
