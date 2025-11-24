import { useState, useEffect } from 'react'
import { Button } from '../ui/Button'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export function MembersTable() {
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [message, setMessage] = useState(null)
  const [sortColumn, setSortColumn] = useState('member_name')
  const [sortDirection, setSortDirection] = useState('asc')
  const [editingMember, setEditingMember] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [formData, setFormData] = useState({
    tradenet_company_id: '',
    bbg_member_id: '',
    member_name: '',
    territory_manager: '',
    member_status: ''
  })

  useEffect(() => {
    fetchMembers()
  }, [])

  const fetchMembers = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/lookups/members?limit=1000`)
      if (response.ok) {
        const data = await response.json()
        setMembers(data)
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load members' })
    } finally {
      setLoading(false)
    }
  }

  const handleBulkUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/api/lookups/members/bulk-upload`, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        setMessage({ type: 'success', text: result.message })
        fetchMembers()
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to upload file' })
    } finally {
      setUploading(false)
      event.target.value = '' // Reset file input
    }
  }

  const handleDelete = async (memberId) => {
    if (!confirm('Are you sure you want to delete this member?')) return

    try {
      const response = await fetch(`${API_BASE_URL}/api/lookups/members/${memberId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'Member deleted successfully' })
        fetchMembers()
      } else {
        setMessage({ type: 'error', text: 'Failed to delete member' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete member' })
    }
  }

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const handleEdit = (member) => {
    setEditingMember(member)
    setFormData({
      tradenet_company_id: member.tradenet_company_id,
      bbg_member_id: member.bbg_member_id || '',
      member_name: member.member_name,
      territory_manager: member.territory_manager || '',
      member_status: member.member_status || ''
    })
  }

  const handleAdd = () => {
    setShowAddModal(true)
    setFormData({
      tradenet_company_id: '',
      bbg_member_id: '',
      member_name: '',
      territory_manager: '',
      member_status: ''
    })
  }

  const handleSave = async () => {
    try {
      const url = editingMember
        ? `${API_BASE_URL}/api/lookups/members/${editingMember.id}`
        : `${API_BASE_URL}/api/lookups/members`

      const response = await fetch(url, {
        method: editingMember ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setMessage({ type: 'success', text: editingMember ? 'Member updated successfully' : 'Member added successfully' })
        setEditingMember(null)
        setShowAddModal(false)
        fetchMembers()
      } else {
        const error = await response.json()
        setMessage({ type: 'error', text: error.detail })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save member' })
    }
  }

  const filteredMembers = members.filter(member =>
    (member.member_name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (member.tradenet_company_id?.includes(searchTerm)) ||
    (member.bbg_member_id?.includes(searchTerm)) ||
    (member.territory_manager?.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const sortedMembers = [...filteredMembers].sort((a, b) => {
    const aVal = a[sortColumn] || ''
    const bVal = b[sortColumn] || ''
    const comparison = aVal.toString().localeCompare(bVal.toString(), undefined, { numeric: true })
    return sortDirection === 'asc' ? comparison : -comparison
  })

  return (
    <div className="space-y-4">
      {/* Actions Bar */}
      <div className="flex items-center justify-between">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search by company name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#178dc3] focus:border-transparent"
          />
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleAdd}
            className="inline-flex items-center px-4 py-2 bg-[#178dc3] text-white text-sm font-medium rounded-lg hover:bg-[#136a94] transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add New
          </button>

          <label className={`inline-flex items-center px-4 py-2 bg-white text-gray-700 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors cursor-pointer ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
            <input
              type="file"
              accept=".csv"
              onChange={handleBulkUpload}
              className="hidden"
              disabled={uploading}
            />
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#178dc3] mr-2"></div>
                Uploading...
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Bulk Upload CSV
              </>
            )}
          </label>

          <button
            onClick={fetchMembers}
            className="inline-flex items-center px-4 py-2 bg-white text-gray-700 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Message Alert */}
      {message && (
        <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          <div className="flex items-center justify-between">
            <span>{message.text}</span>
            <button onClick={() => setMessage(null)} className="text-sm underline">Dismiss</button>
          </div>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#178dc3] mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading members...</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <div className="mb-2 text-sm text-gray-600">
            Showing {sortedMembers.length} of {members.length} members
          </div>
          <div className="max-h-[600px] overflow-y-auto border border-gray-200 rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('tradenet_company_id')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>TradeNet ID</span>
                      {sortColumn === 'tradenet_company_id' && (
                        <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('bbg_member_id')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>BBG ID</span>
                      {sortColumn === 'bbg_member_id' && (
                        <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('member_name')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Member Name</span>
                      {sortColumn === 'member_name' && (
                        <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('territory_manager')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Territory Manager</span>
                      {sortColumn === 'territory_manager' && (
                        <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('member_status')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Status</span>
                      {sortColumn === 'member_status' && (
                        <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedMembers.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                      {searchTerm ? 'No members found matching your search' : 'No members found. Upload a CSV file to get started.'}
                    </td>
                  </tr>
                ) : (
                  sortedMembers.map((member) => (
                    <tr key={member.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">{member.tradenet_company_id}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{member.bbg_member_id || '-'}</td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{member.member_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{member.territory_manager || '-'}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{member.member_status || '-'}</td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEdit(member)}
                            className="text-[#178dc3] hover:text-[#136a94]"
                            title="Edit"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDelete(member.id)}
                            className="text-red-600 hover:text-red-800"
                            title="Delete"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Edit/Add Modal */}
      {(editingMember || showAddModal) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">{editingMember ? 'Edit Member' : 'Add New Member'}</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">TradeNet Company ID *</label>
                <input
                  type="text"
                  value={formData.tradenet_company_id}
                  onChange={(e) => setFormData({ ...formData, tradenet_company_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#178dc3] focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">BBG Member ID</label>
                <input
                  type="text"
                  value={formData.bbg_member_id}
                  onChange={(e) => setFormData({ ...formData, bbg_member_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#178dc3] focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Member Name *</label>
                <input
                  type="text"
                  value={formData.member_name}
                  onChange={(e) => setFormData({ ...formData, member_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#178dc3] focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Territory Manager</label>
                <input
                  type="text"
                  value={formData.territory_manager}
                  onChange={(e) => setFormData({ ...formData, territory_manager: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#178dc3] focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <input
                  type="text"
                  value={formData.member_status}
                  onChange={(e) => setFormData({ ...formData, member_status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#178dc3] focus:border-transparent"
                  placeholder="e.g., Tier 1, Tier 2"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setEditingMember(null)
                  setShowAddModal(false)
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 text-sm font-medium text-white bg-[#178dc3] rounded-lg hover:bg-[#136a94]"
              >
                {editingMember ? 'Save Changes' : 'Add Member'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
