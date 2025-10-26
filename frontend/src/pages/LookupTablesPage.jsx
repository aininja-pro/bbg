import { useState } from 'react'
import { MembersTable } from '../components/lookups/MembersTable'
import { SuppliersTable } from '../components/lookups/SuppliersTable'

export function LookupTablesPage() {
  const [activeSubTab, setActiveSubTab] = useState('members')

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Lookup Tables</h2>
        <p className="mt-1 text-sm text-gray-500">
          Manage TradeNet Members and Suppliers directories
        </p>
      </div>

      {/* Sub-Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveSubTab('members')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeSubTab === 'members'
                  ? 'border-[#178dc3] text-[#178dc3]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              TradeNet Members
            </button>

            <button
              onClick={() => setActiveSubTab('suppliers')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeSubTab === 'suppliers'
                  ? 'border-[#178dc3] text-[#178dc3]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              Suppliers
            </button>
          </nav>
        </div>

        {/* Content Area */}
        <div className="p-6">
          {activeSubTab === 'members' && <MembersTable />}
          {activeSubTab === 'suppliers' && <SuppliersTable />}
        </div>
      </div>
    </div>
  )
}
