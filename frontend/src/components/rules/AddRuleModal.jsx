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
  // New nested structure: array of conditions or groups
  const [conditionItems, setConditionItems] = useState([
    { type: 'condition', field: 'product_id', operator: 'contains', value: '' }
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

      // Handle NEW NESTED format (type: group)
      if (condition.type === 'group') {
        setConditionLogic(condition.logic || 'AND')
        setConditionItems(condition.children || [])
      }
      // Handle OLD format (single action)
      else if (condition.supplier_name_equals) {
        setConditionItems([{ type: 'condition', field: 'supplier_name', operator: 'equals', value: condition.supplier_name_equals }])
        setActions([{ type: 'set_value', field: 'supplier_name', value: config.set_supplier || '' }])
      } else if (condition.product_id_contains) {
        setConditionItems([{ type: 'condition', field: 'product_id', operator: 'contains', value: condition.product_id_contains }])
        setActions([{ type: 'set_value', field: 'supplier_name', value: config.set_supplier || '' }])
      }
      // Handle FLAT format (logic + rules)
      else if (condition.logic && condition.rules) {
        setConditionLogic(condition.logic)
        // Convert flat rules to typed conditions
        setConditionItems(condition.rules.map(r => ({
          type: 'condition',
          field: r.field,
          operator: r.operator,
          value: r.value
        })))
      }

      // Handle actions
      if (config.then_actions) {
        setActions(config.then_actions)
      } else if (config.then_action) {
        setActions([config.then_action])
      }

      if (config.else_action) {
        setHasElse(true)
        setElseValue(config.else_action.value)
      }
    } else {
      // Reset form for new rule
      resetForm()
    }
  }, [editingRule, isOpen])

  const resetForm = () => {
    setRuleName('')
    setConditionLogic('AND')
    setConditionItems([{ type: 'condition', field: 'product_id', operator: 'contains', value: '' }])
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

  // Add a condition to root level
  const addCondition = () => {
    setConditionItems([...conditionItems, { type: 'condition', field: 'product_id', operator: 'contains', value: '' }])
  }

  // Add a condition group to root level
  const addConditionGroup = () => {
    setConditionItems([...conditionItems, {
      type: 'group',
      logic: 'OR',
      children: [
        { type: 'condition', field: 'state', operator: 'equals', value: '' }
      ]
    }])
  }

  // Remove a condition or group at root level
  const removeConditionItem = (index) => {
    if (conditionItems.length > 1) {
      setConditionItems(conditionItems.filter((_, i) => i !== index))
    }
  }

  // Update a condition at root level
  const updateCondition = (index, field, value) => {
    const updated = [...conditionItems]
    updated[index] = { ...updated[index], [field]: value }
    setConditionItems(updated)
  }

  // Update group logic
  const updateGroupLogic = (index, logic) => {
    const updated = [...conditionItems]
    updated[index] = { ...updated[index], logic }
    setConditionItems(updated)
  }

  // Add condition to a group
  const addConditionToGroup = (groupIndex) => {
    const updated = [...conditionItems]
    const group = updated[groupIndex]
    group.children = [...group.children, { type: 'condition', field: 'state', operator: 'equals', value: '' }]
    setConditionItems(updated)
  }

  // Remove condition from a group
  const removeConditionFromGroup = (groupIndex, conditionIndex) => {
    const updated = [...conditionItems]
    const group = updated[groupIndex]
    if (group.children.length > 1) {
      group.children = group.children.filter((_, i) => i !== conditionIndex)
      setConditionItems(updated)
    }
  }

  // Update a condition within a group
  const updateGroupCondition = (groupIndex, conditionIndex, field, value) => {
    const updated = [...conditionItems]
    const group = updated[groupIndex]
    group.children[conditionIndex] = { ...group.children[conditionIndex], [field]: value }
    setConditionItems(updated)
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

    // Validate all conditions (including nested)
    const validateConditions = (items, path = '') => {
      for (let i = 0; i < items.length; i++) {
        const item = items[i]
        const itemPath = path ? `${path} > Condition ${i + 1}` : `Condition ${i + 1}`

        if (item.type === 'condition') {
          if (!item.value && !['is_empty', 'is_not_empty'].includes(item.operator)) {
            return `${itemPath}: Value is required`
          }
        } else if (item.type === 'group') {
          if (!item.children || item.children.length === 0) {
            return `Group ${i + 1}: At least one condition required`
          }
          const groupError = validateConditions(item.children, `Group ${i + 1}`)
          if (groupError) return groupError
        }
      }
      return null
    }

    const conditionError = validateConditions(conditionItems)
    if (conditionError) {
      setError(conditionError)
      return
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

    // Build the new nested condition format
    const ruleConfig = {
      name: ruleName,
      rule_type: 'if_then_else',
      priority: editingRule ? editingRule.priority : nextPriority,
      enabled: true,
      config: {
        condition: {
          type: 'group',
          logic: conditionLogic,
          children: conditionItems
        },
        then_actions: validatedActions
      }
    }

    // Add ELSE action if enabled
    if (hasElse && elseValue) {
      // Get first set_value action's field for else
      const firstSetValueAction = validatedActions.find(a => a.type === 'set_value')
      const thenField = firstSetValueAction?.field || 'supplier_name'

      ruleConfig.config.else_action = {
        field: thenField,
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

  // Render a single condition row
  const renderCondition = (condition, index, onUpdate, onRemove, canRemove) => (
    <div key={index} className="flex items-start space-x-2">
      <div className="flex-1 flex gap-2">
        {/* Field */}
        <select
          value={condition.field}
          onChange={(e) => onUpdate(index, 'field', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
        >
          {AVAILABLE_FIELDS.map(field => (
            <option key={field} value={field}>{field}</option>
          ))}
        </select>

        {/* Operator */}
        <select
          value={condition.operator}
          onChange={(e) => onUpdate(index, 'operator', e.target.value)}
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
            onChange={(e) => onUpdate(index, 'value', e.target.value)}
            placeholder="Value"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
          />
        )}
      </div>

      {canRemove && (
        <button
          onClick={() => onRemove(index)}
          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
          title="Remove condition"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )

  // Render a condition group
  const renderGroup = (group, groupIndex) => (
    <div key={groupIndex} className="border-2 border-blue-200 rounded-lg p-3 bg-blue-50">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-blue-700">Group</span>
          <select
            value={group.logic}
            onChange={(e) => updateGroupLogic(groupIndex, e.target.value)}
            className="px-2 py-1 border border-blue-300 rounded text-xs bg-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="AND">ALL (AND)</option>
            <option value="OR">ANY (OR)</option>
          </select>
        </div>
        <button
          onClick={() => removeConditionItem(groupIndex)}
          className="p-1 text-red-600 hover:bg-red-50 rounded"
          title="Remove group"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="space-y-2">
        {group.children.map((condition, condIndex) =>
          renderCondition(
            condition,
            condIndex,
            (idx, field, value) => updateGroupCondition(groupIndex, idx, field, value),
            (idx) => removeConditionFromGroup(groupIndex, idx),
            group.children.length > 1
          )
        )}
      </div>

      <button
        onClick={() => addConditionToGroup(groupIndex)}
        className="mt-2 text-xs text-blue-600 hover:text-blue-800 flex items-center"
      >
        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add to group
      </button>
    </div>
  )

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
            </div>

            <div className="space-y-3">
              {conditionItems.map((item, index) => {
                if (item.type === 'group') {
                  return renderGroup(item, index)
                } else {
                  return renderCondition(
                    item,
                    index,
                    updateCondition,
                    removeConditionItem,
                    conditionItems.length > 1
                  )
                }
              })}
            </div>

            <div className="flex space-x-2 mt-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={addCondition}
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Condition
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={addConditionGroup}
                className="text-blue-600 hover:bg-blue-50"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Add Group
              </Button>
            </div>
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
                  If condition doesn't match, set field to:
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
