import { useState, useEffect } from 'react'
import { Button } from '../ui/Button'

const AVAILABLE_FIELDS = [
  'member_name',
  'bbg_member_id',
  'confirmed_occupancy',
  'job_code',
  'address1',
  'city',
  'state',
  'zip_postal',
  'address_type',
  'quantity',
  'product_id',
  'supplier_name',
  'tradenet_supplier_id',
  'pp_dist_subcontractor',
  'tradenet_company_id',
]

const TEXT_OPERATORS = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Does Not Contain' },
  { value: 'starts_with', label: 'Starts With' },
  { value: 'ends_with', label: 'Ends With' },
  { value: 'is_empty', label: 'Is Empty' },
  { value: 'is_not_empty', label: 'Is Not Empty' },
]

const NUMERIC_OPERATORS = [
  { value: 'equals', label: 'Equals (=)' },
  { value: 'not_equals', label: 'Not Equals (≠)' },
  { value: 'greater_than', label: 'Greater Than (>)' },
  { value: 'less_than', label: 'Less Than (<)' },
  { value: 'greater_or_equal', label: 'Greater or Equal (≥)' },
  { value: 'less_or_equal', label: 'Less or Equal (≤)' },
]

const NUMERIC_FIELDS = ['bbg_member_id', 'quantity', 'tradenet_supplier_id', 'tradenet_company_id']

export function AddRuleModal({ isOpen, onClose, onSave, editingRule = null }) {
  const [ruleName, setRuleName] = useState('')
  const [conditionLogic, setConditionLogic] = useState('AND')
  const [conditions, setConditions] = useState([
    { field: 'product_id', operator: 'contains', value: '' }
  ])
  const [thenField, setThenField] = useState('supplier_name')
  const [thenValue, setThenValue] = useState('')
  const [hasElse, setHasElse] = useState(false)
  const [elseValue, setElseValue] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (editingRule) {
      // Populate form with existing rule data
      setRuleName(editingRule.name)

      const config = editingRule.config
      const condition = config.condition

      // Handle OLD format
      if (condition.supplier_name_equals) {
        setConditions([{ field: 'supplier_name', operator: 'equals', value: condition.supplier_name_equals }])
        setThenField('supplier_name')
        setThenValue(config.set_supplier || '')
      } else if (condition.product_id_contains) {
        setConditions([{ field: 'product_id', operator: 'contains', value: condition.product_id_contains }])
        setThenField('supplier_name')
        setThenValue(config.set_supplier || '')
      }
      // Handle NEW format
      else if (condition.logic && condition.rules) {
        setConditionLogic(condition.logic)
        setConditions(condition.rules)

        if (config.then_action) {
          setThenField(config.then_action.field)
          setThenValue(config.then_action.value)
        }

        if (config.else_action) {
          setHasElse(true)
          setElseValue(config.else_action.value)
        }
      }
    } else {
      // Reset form for new rule
      resetForm()
    }
  }, [editingRule, isOpen])

  const resetForm = () => {
    setRuleName('')
    setConditionLogic('AND')
    setConditions([{ field: 'product_id', operator: 'contains', value: '' }])
    setThenField('supplier_name')
    setThenValue('')
    setHasElse(false)
    setElseValue('')
    setError(null)
  }

  const addCondition = () => {
    setConditions([...conditions, { field: 'product_id', operator: 'contains', value: '' }])
  }

  const removeCondition = (index) => {
    if (conditions.length > 1) {
      setConditions(conditions.filter((_, i) => i !== index))
    }
  }

  const updateCondition = (index, field, value) => {
    const updated = [...conditions]
    updated[index][field] = value
    setConditions(updated)
  }

  const getOperatorsForField = (field) => {
    return NUMERIC_FIELDS.includes(field) ? NUMERIC_OPERATORS : TEXT_OPERATORS
  }

  const handleSave = async () => {
    // Validation
    if (!ruleName.trim()) {
      setError('Rule name is required')
      return
    }

    for (let i = 0; i < conditions.length; i++) {
      if (!conditions[i].value && !['is_empty', 'is_not_empty'].includes(conditions[i].operator)) {
        setError(`Condition ${i + 1}: Value is required`)
        return
      }
    }

    if (!thenValue.trim()) {
      setError('THEN value is required')
      return
    }

    // Build rule config
    const ruleConfig = {
      name: ruleName,
      rule_type: 'if_then_else',
      priority: editingRule ? editingRule.priority : 999, // Will be auto-assigned by backend
      enabled: true,
      config: {
        condition: {
          logic: conditionLogic,
          rules: conditions
        },
        then_action: {
          field: thenField,
          value: thenValue
        }
      }
    }

    // Add ELSE action if enabled
    if (hasElse && elseValue) {
      ruleConfig.config.else_action = {
        field: thenField, // Same field as THEN
        value: elseValue
      }
    }

    try {
      await onSave(ruleConfig)
      resetForm()
      onClose()
    } catch (err) {
      setError(err.message || 'Failed to save rule')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {editingRule ? 'Edit Rule' : 'Add New Rule'}
            </h2>
            <button
              onClick={() => {
                resetForm()
                onClose()
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="px-6 py-4 space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Rule Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rule Name
            </label>
            <input
              type="text"
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder="e.g., Product 5534 is Air Vent"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* IF Conditions */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">IF Conditions</h3>
              {conditions.length > 1 && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Match:</span>
                  <select
                    value={conditionLogic}
                    onChange={(e) => setConditionLogic(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="AND">ALL (AND)</option>
                    <option value="OR">ANY (OR)</option>
                  </select>
                </div>
              )}
            </div>

            <div className="space-y-3">
              {conditions.map((condition, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <div className="flex-1 flex gap-2">
                    {/* Field */}
                    <select
                      value={condition.field}
                      onChange={(e) => updateCondition(index, 'field', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                    >
                      {AVAILABLE_FIELDS.map(field => (
                        <option key={field} value={field}>{field}</option>
                      ))}
                    </select>

                    {/* Operator */}
                    <select
                      value={condition.operator}
                      onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                    >
                      {getOperatorsForField(condition.field).map(op => (
                        <option key={op.value} value={op.value}>{op.label}</option>
                      ))}
                    </select>

                    {/* Value */}
                    {!['is_empty', 'is_not_empty'].includes(condition.operator) && (
                      <input
                        type="text"
                        value={condition.value}
                        onChange={(e) => updateCondition(index, 'value', e.target.value)}
                        placeholder="Value"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    )}
                  </div>

                  {conditions.length > 1 && (
                    <button
                      onClick={() => removeCondition(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      title="Remove condition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={addCondition}
              className="mt-3"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Condition
            </Button>
          </div>

          {/* THEN Action */}
          <div className="border border-green-200 rounded-lg p-4 bg-green-50">
            <h3 className="font-semibold text-gray-900 mb-3">THEN Set</h3>
            <div className="grid grid-cols-2 gap-3">
              <select
                value={thenField}
                onChange={(e) => setThenField(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {AVAILABLE_FIELDS.map(field => (
                  <option key={field} value={field}>{field}</option>
                ))}
              </select>
              <input
                type="text"
                value={thenValue}
                onChange={(e) => setThenValue(e.target.value)}
                placeholder="New value"
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* ELSE Action (Optional) */}
          <div className="border border-orange-200 rounded-lg p-4 bg-orange-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">ELSE (Optional)</h3>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={hasElse}
                  onChange={(e) => setHasElse(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Enable ELSE action</span>
              </label>
            </div>

            {hasElse && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  If condition doesn't match, set <span className="font-mono font-semibold">{thenField}</span> to:
                </p>
                <input
                  type="text"
                  value={elseValue}
                  onChange={(e) => setElseValue(e.target.value)}
                  placeholder="e.g., $(supplier_name) to keep original value"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500">
                  Tip: Use $(field_name) to keep the original value unchanged
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4 flex justify-end space-x-3">
          <Button
            variant="outline"
            onClick={() => {
              resetForm()
              onClose()
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleSave}>
            {editingRule ? 'Update Rule' : 'Create Rule'}
          </Button>
        </div>
      </div>
    </div>
  )
}
