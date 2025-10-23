import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { AddRuleModal } from './AddRuleModal'

export function RulesManager() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState(null)

  useEffect(() => {
    fetchRules()
  }, [])

  const fetchRules = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/rules')
      const data = await response.json()
      setRules(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleRule = async (ruleId, currentEnabled) => {
    try {
      await fetch(`http://localhost:8001/api/rules/${ruleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !currentEnabled }),
      })
      fetchRules()
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteRule = async (ruleId) => {
    if (!confirm('Are you sure you want to delete this rule?')) return

    try {
      await fetch(`http://localhost:8001/api/rules/${ruleId}`, {
        method: 'DELETE',
      })
      fetchRules()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleSaveRule = async (ruleConfig) => {
    try {
      const url = editingRule
        ? `http://localhost:8001/api/rules/${editingRule.id}`
        : 'http://localhost:8001/api/rules'

      const method = editingRule ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ruleConfig),
      })

      if (!response.ok) {
        throw new Error('Failed to save rule')
      }

      fetchRules()
      setEditingRule(null)
    } catch (err) {
      throw err
    }
  }

  const handleEditRule = (rule) => {
    setEditingRule(rule)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingRule(null)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Supplier Mapping Rules</CardTitle>
            <CardDescription>
              Manage business rules for supplier name overrides. Rules are applied in priority order.
            </CardDescription>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Rule
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="space-y-3">
          {rules.map((rule) => (
            <div
              key={rule.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-4 flex-1">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-700 rounded font-semibold text-sm">
                  {rule.priority}
                </div>

                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{rule.name}</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {rule.config.condition && Object.entries(rule.config.condition).map(([key, value]) => (
                      <span key={key}>
                        {key.replace(/_/g, ' ')}: <span className="font-mono">{value}</span>
                        {' → '}
                      </span>
                    ))}
                    <span className="font-semibold">{rule.config.set_supplier}</span>
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  {/* Enable/Disable Toggle */}
                  <button
                    onClick={() => toggleRule(rule.id, rule.enabled)}
                    className={`
                      relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${rule.enabled ? 'bg-blue-600' : 'bg-gray-200'}
                    `}
                  >
                    <span
                      className={`
                        inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${rule.enabled ? 'translate-x-6' : 'translate-x-1'}
                      `}
                    />
                  </button>
                  <span className="text-xs text-gray-500 w-16">
                    {rule.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditRule(rule)}
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteRule(rule.id)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}

          {rules.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No rules configured. Click "Add Rule" to create your first supplier mapping rule.
            </div>
          )}
        </div>
      </CardContent>

      <AddRuleModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveRule}
        editingRule={editingRule}
      />
    </Card>
  )
}
