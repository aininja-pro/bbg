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
  'pp_receipt',              // NEW
  'pp_brand_name',           // NEW
  'pp_dist_subcontractor',
  'pp_prod_purchase',        // NEW
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

export function AddRuleModal({ isOpen, onClose, onSave, editingRule = null, existingRules = [] }) {
  const [ruleName, setRuleName] = useState('')
  const [conditionLogic, setConditionLogic] = useState('AND')
  const [conditions, setConditions] = useState([
    { field: 'product_id', operator: 'contains', value: '' }
  ])
  const [actions, setActions] = useState([
    { type: 'set_value', field: 'supplier_name', value: '' }
  ])
  const [hasElse, setHasElse] = useState(false)
  const [elseValue, setElseValue] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (editingRule) {
      // Populate form with existing rule data
      setRuleName(editingRule.name)

      const config = editingRule.config
      const condition = config.condition

      // Handle OLD format (single action)
      if (condition.supplier_name_equals) {
        setConditions([{ field: 'supplier_name', operator: 'equals', value: condition.supplier_name_equals }])
        setActions([{ type: 'set_value', field: 'supplier_name', value: config.set_supplier || '' }])
      } else if (condition.product_id_contains) {
        setConditions([{ field: 'product_id', operator: 'contains', value: condition.product_id_contains }])
        setActions([{ type: 'set_value', field: 'supplier_name', value: config.set_supplier || '' }])
      }
      // Handle NEW format
      else if (condition.logic && condition.rules) {
        setConditionLogic(condition.logic)
        setConditions(condition.rules)

        // Handle multiple actions (new) or single action (backward compatible)
        if (config.then_actions) {
          setActions(config.then_actions)
        } else if (config.then_action) {
          setActions([config.then_action])
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
    setActions([{ type: 'set_value', field: 'supplier_name', value: '' }])
    setHasElse(false)
    setElseValue('')
    setError(null)
  }

  const addAction = () => {
    setActions([...actions, { type: 'set_value', field: 'supplier_name', value: '' }])
  }

  const removeAction = (index) => {
    if (actions.length > 1) {
      setActions(actions.filter((_, i) => i !== index))
    }
  }

  const updateAction = (index, field, value) => {
    const newActions = [...actions]
    newActions[index] = { ...newActions[index], [field]: value }

    // If changing action type, set defaults for that type
    if (field === 'type') {
      if (value === 'move_column') {
        newActions[index] = {
          type: 'move_column',
          source_field: 'pp_dist_subcontractor',
          target_field: 'pp_brand_name',
          clear_source: true
        }
      } else if (value === 'set_value') {
        newActions[index] = {
          type: 'set_value',
          field: 'supplier_name',
          value: ''
        }
      }
    }

    setActions(newActions)
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

    // Validate all actions (apply defaults if missing)
    const validatedActions = actions.map(action => {
      if (action.type === 'set_value') {
        return {
          type: 'set_value',
          field: action.field || 'supplier_name',
          value: action.value || ''
        }
      } else if (action.type === 'move_column') {
        return {
          type: 'move_column',
          source_field: action.source_field || 'pp_dist_subcontractor',
          target_field: action.target_field || 'pp_brand_name',
          clear_source: action.clear_source !== false
        }
      }
      return action
    })

    // Now validate with defaults applied
    for (let i = 0; i < validatedActions.length; i++) {
      const action = validatedActions[i]

      if (action.type === 'set_value') {
        if (!action.value.trim()) {
          setError(`Action ${i + 1}: Value is required`)
          return
        }
      } else if (action.type === 'move_column') {
        if (action.source_field === action.target_field) {
          setError(`Action ${i + 1}: Source and target fields must be different`)
          return
        }
      }
    }

    // Calculate next priority (max + 1)
    const maxPriority = existingRules.length > 0
      ? Math.max(...existingRules.map(r => r.priority))
      : 0
    const nextPriority = maxPriority + 1

    const ruleConfig = {
      name: ruleName,
      rule_type: 'if_then_else',
      priority: editingRule ? editingRule.priority : nextPriority,
      enabled: true,
      config: {
        condition: {
          logic: conditionLogic,
          rules: conditions
        },
        then_actions: validatedActions  // Use validated actions with defaults
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

          {/* THEN Actions (Multiple) */}
          <div className="border border-green-200 rounded-lg p-4 bg-green-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">THEN Actions</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={addAction}
                className="text-green-700 hover:bg-green-100"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Action
              </Button>
            </div>

            <div className="space-y-4">
              {actions.map((action, index) => (
                <div key={index} className="bg-white rounded-lg p-3 border border-green-300">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-xs font-semibold">
                      {index + 1}
                    </div>

                    <div className="flex-1 space-y-3">
                      {/* Action Type Selector */}
                      <select
                        value={action.type}
                        onChange={(e) => updateAction(index, 'type', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                      >
                        <option value="set_value">Set Field to Value</option>
                        <option value="move_column">Move Column Data</option>
                      </select>

                      {/* Set Value Fields */}
                      {action.type === 'set_value' && (
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Field</label>
                            <select
                              value={action.field || 'supplier_name'}
                              onChange={(e) => updateAction(index, 'field', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            >
                              {AVAILABLE_FIELDS.map(field => (
                                <option key={field} value={field}>{field}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Value</label>
                            <input
                              type="text"
                              value={action.value || ''}
                              onChange={(e) => updateAction(index, 'value', e.target.value)}
                              placeholder="Enter value"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                        </div>
                      )}

                      {/* Move Column Fields */}
                      {action.type === 'move_column' && (
                        <div className="space-y-2">
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <label className="block text-xs text-gray-600 mb-1">Source</label>
                              <select
                                value={action.source_field || 'pp_dist_subcontractor'}
                                onChange={(e) => updateAction(index, 'source_field', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                              >
                                {AVAILABLE_FIELDS.map(field => (
                                  <option key={field} value={field}>{field}</option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-xs text-gray-600 mb-1">Target</label>
                              <select
                                value={action.target_field || 'pp_brand_name'}
                                onChange={(e) => updateAction(index, 'target_field', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                              >
                                {AVAILABLE_FIELDS.map(field => (
                                  <option key={field} value={field}>{field}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                          <label className="flex items-center space-x-2 cursor-pointer text-sm">
                            <input
                              type="checkbox"
                              checked={action.clear_source !== false}
                              onChange={(e) => updateAction(index, 'clear_source', e.target.checked)}
                              className="w-4 h-4 rounded"
                              style={{ accentColor: '#178dc3' }}
                            />
                            <span className="text-gray-700">Clear source after move</span>
                          </label>
                        </div>
                      )}
                    </div>

                    {/* Remove Button */}
                    {actions.length > 1 && (
                      <button
                        onClick={() => removeAction(index)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                        title="Remove action"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              ))}
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
                  className="w-4 h-4 text-[#178dc3] rounded focus:ring-2 focus:ring-blue-500"
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
