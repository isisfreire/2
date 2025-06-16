import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [formData, setFormData] = useState({
    // Batch identification
    batch_id: '',
    shed_number: '',
    handler_name: '',
    
    initial_chicks: '',
    chick_cost_per_unit: '',
    
    // Feed phases
    pre_starter_consumption: '',
    pre_starter_cost_per_kg: '',
    starter_consumption: '',
    starter_cost_per_kg: '',
    growth_consumption: '',
    growth_cost_per_kg: '',
    final_consumption: '',
    final_cost_per_kg: '',
    
    // Enhanced costs
    medicine_costs: '',
    miscellaneous_costs: '',
    cost_variations: '',
    sawdust_bedding_cost: '',
    chicken_bedding_sale_revenue: '',
    
    // Mortality
    chicks_died: ''
  });
  
  // State for removal batches (up to 15)
  const [removalBatches, setRemovalBatches] = useState([
    { quantity: '', total_weight_kg: '', age_days: '' }
  ]);
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [handlers, setHandlers] = useState([]);
  const [handlerPerformance, setHandlerPerformance] = useState([]);
  const [sheds, setSheds] = useState([]);
  const [allHandlers, setAllHandlers] = useState([]);
  const [allSheds, setAllSheds] = useState([]);
  const [activeTab, setActiveTab] = useState('basic');
  const [showPerformanceTab, setShowPerformanceTab] = useState(false);
  const [showAdminTab, setShowAdminTab] = useState(false);
  const [showBatchManagementTab, setShowBatchManagementTab] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [editingBatch, setEditingBatch] = useState(false);

  // Load calculation history on component mount
  useEffect(() => {
    loadHistory();
    loadHandlers();
    loadSheds();
    loadHandlerPerformance();
    loadAllHandlers();
    loadAllSheds();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API}/calculations`);
      setHistory(response.data);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const loadHandlers = async () => {
    try {
      const response = await axios.get(`${API}/handlers/names`);
      setHandlers(response.data);
    } catch (err) {
      console.error('Error loading handlers:', err);
    }
  };

  const loadAllHandlers = async () => {
    try {
      const response = await axios.get(`${API}/handlers`);
      setAllHandlers(response.data);
    } catch (err) {
      console.error('Error loading all handlers:', err);
    }
  };

  const loadAllSheds = async () => {
    try {
      const response = await axios.get(`${API}/admin/sheds`);
      setAllSheds(response.data);
    } catch (err) {
      console.error('Error loading all sheds:', err);
    }
  };

  const loadSheds = async () => {
    try {
      const response = await axios.get(`${API}/sheds`);
      setSheds(response.data);
    } catch (err) {
      console.error('Error loading sheds:', err);
    }
  };

  const loadHandlerPerformance = async () => {
    try {
      const response = await axios.get(`${API}/handlers/performance`);
      setHandlerPerformance(response.data);
    } catch (err) {
      console.error('Error loading handler performance:', err);
      setHandlerPerformance([]); // Set empty array on error
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRemovalBatchChange = (index, field, value) => {
    const newBatches = [...removalBatches];
    newBatches[index][field] = value;
    setRemovalBatches(newBatches);
  };

  const addRemovalBatch = () => {
    if (removalBatches.length < 15) {
      setRemovalBatches([...removalBatches, { quantity: '', total_weight_kg: '', age_days: '' }]);
    }
  };

  const removeRemovalBatch = (index) => {
    if (removalBatches.length > 1) {
      const newBatches = removalBatches.filter((_, i) => i !== index);
      setRemovalBatches(newBatches);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Convert string inputs to numbers
      const numericData = {
        // Batch identification
        batch_id: formData.batch_id.trim(),
        shed_number: formData.shed_number.trim(),
        handler_name: formData.handler_name.trim(),
        
        initial_chicks: parseInt(formData.initial_chicks) || 0,
        chick_cost_per_unit: parseFloat(formData.chick_cost_per_unit) || 0,
        
        pre_starter_feed: {
          consumption_kg: parseFloat(formData.pre_starter_consumption) || 0,
          cost_per_kg: parseFloat(formData.pre_starter_cost_per_kg) || 0
        },
        starter_feed: {
          consumption_kg: parseFloat(formData.starter_consumption) || 0,
          cost_per_kg: parseFloat(formData.starter_cost_per_kg) || 0
        },
        growth_feed: {
          consumption_kg: parseFloat(formData.growth_consumption) || 0,
          cost_per_kg: parseFloat(formData.growth_cost_per_kg) || 0
        },
        final_feed: {
          consumption_kg: parseFloat(formData.final_consumption) || 0,
          cost_per_kg: parseFloat(formData.final_cost_per_kg) || 0
        },
        
        medicine_costs: parseFloat(formData.medicine_costs) || 0,
        miscellaneous_costs: parseFloat(formData.miscellaneous_costs) || 0,
        cost_variations: parseFloat(formData.cost_variations) || 0,
        sawdust_bedding_cost: parseFloat(formData.sawdust_bedding_cost) || 0,
        chicken_bedding_sale_revenue: parseFloat(formData.chicken_bedding_sale_revenue) || 0,
        
        chicks_died: parseInt(formData.chicks_died) || 0,
        
        removal_batches: removalBatches
          .filter(batch => batch.quantity && batch.total_weight_kg && batch.age_days)
          .map(batch => ({
            quantity: parseInt(batch.quantity) || 0,
            total_weight_kg: parseFloat(batch.total_weight_kg) || 0,
            age_days: parseInt(batch.age_days) || 0
          }))
      };

      // Validate required fields
      if (!numericData.batch_id) {
        setError('Batch ID is required');
        return;
      }
      if (!numericData.shed_number) {
        setError('Shed number is required');
        return;
      }
      if (!numericData.handler_name) {
        setError('Handler name is required');
        return;
      }

      if (numericData.removal_batches.length === 0) {
        setError('At least one removal batch is required');
        return;
      }

      const response = await axios.post(`${API}/calculate`, numericData);
      setResult(response.data);
      
      // Reload history and performance data
      loadHistory();
      loadHandlers();
      loadSheds();
      loadHandlerPerformance();
      loadAllHandlers();
      loadAllSheds();
      
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during calculation');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      batch_id: '',
      shed_number: '',
      handler_name: '',
      initial_chicks: '',
      chick_cost_per_unit: '',
      pre_starter_consumption: '',
      pre_starter_cost_per_kg: '',
      starter_consumption: '',
      starter_cost_per_kg: '',
      growth_consumption: '',
      growth_cost_per_kg: '',
      final_consumption: '',
      final_cost_per_kg: '',
      medicine_costs: '',
      miscellaneous_costs: '',
      cost_variations: '',
      sawdust_bedding_cost: '',
      chicken_bedding_sale_revenue: '',
      chicks_died: ''
    });
    setRemovalBatches([{ quantity: '', total_weight_kg: '', age_days: '' }]);
    setResult(null);
    setError('');
  };

  // Admin functions
  const createHandler = async (handlerData) => {
    try {
      await axios.post(`${API}/handlers`, handlerData);
      loadAllHandlers();
      loadHandlers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error creating handler');
    }
  };

  const updateHandler = async (handlerId, handlerData) => {
    try {
      await axios.put(`${API}/handlers/${handlerId}`, handlerData);
      loadAllHandlers();
      loadHandlers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error updating handler');
    }
  };

  const deleteHandler = async (handlerId) => {
    if (!window.confirm('Are you sure you want to delete this handler?')) return;
    
    try {
      await axios.delete(`${API}/handlers/${handlerId}`);
      alert('Handler deleted successfully');
      loadAllHandlers();
      loadHandlers();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error deleting handler';
      alert(errorMsg);
    }
  };

  const createShed = async (shedData) => {
    try {
      await axios.post(`${API}/admin/sheds`, shedData);
      loadAllSheds();
      loadSheds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error creating shed');
    }
  };

  const updateShed = async (shedId, shedData) => {
    try {
      await axios.put(`${API}/admin/sheds/${shedId}`, shedData);
      loadAllSheds();
      loadSheds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error updating shed');
    }
  };

  const deleteShed = async (shedId) => {
    if (!window.confirm('Are you sure you want to delete this shed?')) return;
    
    try {
      await axios.delete(`${API}/admin/sheds/${shedId}`);
      alert('Shed deleted successfully');
      loadAllSheds();
      loadSheds();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error deleting shed';
      alert(errorMsg);
    }
  };

  const downloadPDF = (filename) => {
    // Create a temporary link and click it to download the file
    const downloadUrl = `${API}/export/${filename}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const loadBatchDetails = async (batchId) => {
    try {
      const response = await axios.get(`${API}/batches/${batchId}`);
      setSelectedBatch(response.data);
      setEditingBatch(true);
      // Populate form with batch data
      const batch = response.data;
      setFormData({
        batch_id: batch.input_data.batch_id,
        shed_number: batch.input_data.shed_number,
        handler_name: batch.input_data.handler_name,
        initial_chicks: batch.input_data.initial_chicks.toString(),
        chick_cost_per_unit: batch.input_data.chick_cost_per_unit.toString(),
        pre_starter_consumption: batch.input_data.pre_starter_feed.consumption_kg.toString(),
        pre_starter_cost_per_kg: batch.input_data.pre_starter_feed.cost_per_kg.toString(),
        starter_consumption: batch.input_data.starter_feed.consumption_kg.toString(),
        starter_cost_per_kg: batch.input_data.starter_feed.cost_per_kg.toString(),
        growth_consumption: batch.input_data.growth_feed.consumption_kg.toString(),
        growth_cost_per_kg: batch.input_data.growth_feed.cost_per_kg.toString(),
        final_consumption: batch.input_data.final_feed.consumption_kg.toString(),
        final_cost_per_kg: batch.input_data.final_feed.cost_per_kg.toString(),
        medicine_costs: batch.input_data.medicine_costs.toString(),
        miscellaneous_costs: batch.input_data.miscellaneous_costs.toString(),
        cost_variations: batch.input_data.cost_variations.toString(),
        sawdust_bedding_cost: batch.input_data.sawdust_bedding_cost.toString(),
        chicken_bedding_sale_revenue: batch.input_data.chicken_bedding_sale_revenue.toString(),
        chicks_died: batch.input_data.chicks_died.toString()
      });
      
      // Set removal batches
      setRemovalBatches(batch.input_data.removal_batches.map(rb => ({
        quantity: rb.quantity.toString(),
        total_weight_kg: rb.total_weight_kg.toString(),
        age_days: rb.age_days.toString()
      })));
      
      // Switch to basic tab to show the loaded data
      setActiveTab('basic');
      setShowBatchManagementTab(false);
    } catch (err) {
      alert('Error loading batch details: ' + (err.response?.data?.detail || err.message));
    }
  };

  const deleteBatch = async (batchId) => {
    if (!window.confirm('Are you sure you want to delete this batch? This action cannot be undone.')) return;
    
    try {
      await axios.delete(`${API}/calculations/${batchId}`);
      alert('Batch deleted successfully');
      loadHistory();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error deleting batch';
      alert(errorMsg);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  // Chart component for cost breakdown
  const CostBreakdownChart = ({ costBreakdown }) => {
    const data = [
      { name: 'Chicks', value: costBreakdown.chick_cost_percent, color: '#3B82F6' },
      { name: 'Pre-starter Feed', value: costBreakdown.pre_starter_cost_percent, color: '#10B981' },
      { name: 'Starter Feed', value: costBreakdown.starter_cost_percent, color: '#F59E0B' },
      { name: 'Growth Feed', value: costBreakdown.growth_cost_percent, color: '#EF4444' },
      { name: 'Final Feed', value: costBreakdown.final_cost_percent, color: '#8B5CF6' },
      { name: 'Medicine', value: costBreakdown.medicine_cost_percent, color: '#06B6D4' },
      { name: 'Miscellaneous', value: costBreakdown.miscellaneous_cost_percent, color: '#84CC16' },
      { name: 'Cost Variations', value: costBreakdown.cost_variations_percent, color: '#F97316' }
    ].filter(item => item.value > 0);

    return (
      <div className="bg-white p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Cost Breakdown</h3>
        <div className="space-y-2">
          {data.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center">
                <div 
                  className="w-4 h-4 rounded mr-2" 
                  style={{ backgroundColor: item.color }}
                ></div>
                <span className="text-sm text-gray-700">{item.name}</span>
              </div>
              <div className="flex items-center">
                <div 
                  className="h-2 bg-gray-200 rounded mr-2" 
                  style={{ width: '100px' }}
                >
                  <div 
                    className="h-2 rounded" 
                    style={{ 
                      width: `${item.value}%`, 
                      backgroundColor: item.color 
                    }}
                  ></div>
                </div>
                <span className="text-sm font-semibold text-gray-800 w-12 text-right">
                  {item.value}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Handler Performance Component
  const HandlerPerformanceTable = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
      const loadPerformanceData = async () => {
        setLoading(true);
        setError('');
        try {
          await loadHandlerPerformance();
        } catch (err) {
          setError('Failed to load performance data');
          console.error('Error loading performance data:', err);
        } finally {
          setLoading(false);
        }
      };

      if (showPerformanceTab) {
        loadPerformanceData();
      }
    }, [showPerformanceTab]);

    if (!showPerformanceTab) return null;

    if (loading) {
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Handler Performance Ranking</h2>
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-500">Loading performance data...</div>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Handler Performance Ranking</h2>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={() => loadHandlerPerformance()}
              className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      );
    }

    if (handlerPerformance.length === 0) {
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Handler Performance Ranking</h2>
          <div className="text-center py-8 text-gray-500">
            No performance data available. Complete some batches to see handler rankings.
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Handler Performance Ranking</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Handler</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Batches</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg FCR</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Mortality %</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Daily Gain</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {handlerPerformance.map((handler, index) => (
                <tr key={index} className={`hover:bg-gray-50 ${index === 0 ? 'bg-green-50' : ''}`}>
                  <td className="px-4 py-2 text-sm font-semibold">
                    {index === 0 ? '🏆' : ''} #{index + 1}
                  </td>
                  <td className="px-4 py-2 text-sm font-semibold text-gray-900">{handler.handler_name}</td>
                  <td className="px-4 py-2 text-sm text-gray-600">{handler.total_batches}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{handler.avg_feed_conversion_ratio}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{handler.avg_mortality_rate}%</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{handler.avg_daily_weight_gain} kg</td>
                  <td className="px-4 py-2">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${handler.performance_score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold">{handler.performance_score}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Admin Management Component
  const AdminManagement = () => {
    const [newHandler, setNewHandler] = useState({ name: '', email: '', phone: '', notes: '' });
    const [newShed, setNewShed] = useState({ number: '', capacity: '', location: '', status: 'active', notes: '' });
    const [editingHandler, setEditingHandler] = useState(null);
    const [editingShed, setEditingShed] = useState(null);

    const handleCreateHandler = async (e) => {
      e.preventDefault();
      if (!newHandler.name.trim()) return;
      
      await createHandler({
        name: newHandler.name.trim(),
        email: newHandler.email.trim() || null,
        phone: newHandler.phone.trim() || null,
        notes: newHandler.notes.trim() || null
      });
      
      setNewHandler({ name: '', email: '', phone: '', notes: '' });
    };

    const handleCreateShed = async (e) => {
      e.preventDefault();
      if (!newShed.number.trim()) return;
      
      await createShed({
        number: newShed.number.trim(),
        capacity: newShed.capacity ? parseInt(newShed.capacity) : null,
        location: newShed.location.trim() || null,
        status: newShed.status,
        notes: newShed.notes.trim() || null
      });
      
      setNewShed({ number: '', capacity: '', location: '', status: 'active', notes: '' });
    };

    const handleUpdateHandler = async (handlerId, updatedData) => {
      await updateHandler(handlerId, updatedData);
      setEditingHandler(null);
    };

    const handleUpdateShed = async (shedId, updatedData) => {
      await updateShed(shedId, updatedData);
      setEditingShed(null);
    };

    return (
      <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Farm Administration</h2>
        
        {/* Handler Management */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">👨‍🌾 Handler Management</h3>
          
          {/* Add New Handler Form */}
          <form onSubmit={handleCreateHandler} className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold mb-3">Add New Handler</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Handler Name *"
                value={newHandler.name}
                onChange={(e) => setNewHandler({...newHandler, name: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <input
                type="email"
                placeholder="Email (optional)"
                value={newHandler.email}
                onChange={(e) => setNewHandler({...newHandler, email: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="tel"
                placeholder="Phone (optional)"
                value={newHandler.phone}
                onChange={(e) => setNewHandler({...newHandler, phone: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="text"
                placeholder="Notes (optional)"
                value={newHandler.notes}
                onChange={(e) => setNewHandler({...newHandler, notes: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <button
              type="submit"
              className="mt-3 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
            >
              Add Handler
            </button>
          </form>

          {/* Handlers List */}
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {allHandlers.map((handler) => (
                  <tr key={handler.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-semibold text-gray-900">{handler.name}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{handler.email || '-'}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{handler.phone || '-'}</td>
                    <td className="px-4 py-2 text-sm">
                      <button
                        onClick={() => setEditingHandler(handler)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => {
                          if (window.confirm(`Delete handler "${handler.name}"?`)) {
                            deleteHandler(handler.id);
                          }
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Shed Management */}
        <div>
          <h3 className="text-xl font-semibold text-gray-700 mb-4">🏠 Shed Management</h3>
          
          {/* Add New Shed Form */}
          <form onSubmit={handleCreateShed} className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold mb-3">Add New Shed</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Shed Number *"
                value={newShed.number}
                onChange={(e) => setNewShed({...newShed, number: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <input
                type="number"
                placeholder="Capacity (optional)"
                value={newShed.capacity}
                onChange={(e) => setNewShed({...newShed, capacity: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="text"
                placeholder="Location (optional)"
                value={newShed.location}
                onChange={(e) => setNewShed({...newShed, location: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <select
                value={newShed.status}
                onChange={(e) => setNewShed({...newShed, status: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="active">Active</option>
                <option value="maintenance">Maintenance</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <input
              type="text"
              placeholder="Notes (optional)"
              value={newShed.notes}
              onChange={(e) => setNewShed({...newShed, notes: e.target.value})}
              className="w-full mt-4 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="submit"
              className="mt-3 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
            >
              Add Shed
            </button>
          </form>

          {/* Sheds List */}
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Number</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Capacity</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {allSheds.map((shed) => (
                  <tr key={shed.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-semibold text-gray-900">{shed.number}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{shed.capacity || '-'}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{shed.location || '-'}</td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        shed.status === 'active' ? 'bg-green-100 text-green-800' :
                        shed.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {shed.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <button
                        onClick={() => setEditingShed(shed)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => {
                          if (window.confirm(`Delete shed "${shed.number}"?`)) {
                            deleteShed(shed.id);
                          }
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  // Batch Management Component
  const BatchManagement = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [filterHandler, setFilterHandler] = useState('');
    const [filterShed, setFilterShed] = useState('');

    const filteredHistory = history.filter(batch => {
      const matchesSearch = batch.batch_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           batch.handler_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           batch.shed_number.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesHandler = !filterHandler || batch.handler_name === filterHandler;
      const matchesShed = !filterShed || batch.shed_number === filterShed;
      
      return matchesSearch && matchesHandler && matchesShed;
    });

    return (
      <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">📋 Batch Management</h2>
        
        {/* Search and Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search Batches</label>
            <input
              type="text"
              placeholder="Search by batch ID, handler, or shed..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Handler</label>
            <select
              value={filterHandler}
              onChange={(e) => setFilterHandler(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">All Handlers</option>
              {handlers.map(handler => (
                <option key={handler} value={handler}>{handler}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Shed</label>
            <select
              value={filterShed}
              onChange={(e) => setFilterShed(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">All Sheds</option>
              {sheds.map(shed => (
                <option key={shed} value={shed}>{shed}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Batch List */}
        <div className="overflow-x-auto">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Batch ID</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Shed</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Handler</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Chicks</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">FCR</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Mortality %</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cost/kg</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredHistory.map((batch, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm font-mono font-semibold text-gray-900">{batch.batch_id}</td>
                  <td className="px-4 py-2 text-sm text-gray-600">
                    {new Date(batch.date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-900">{batch.shed_number}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{batch.handler_name}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{batch.initial_chicks.toLocaleString()}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{batch.fcr}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{batch.mortality_percent}%</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{formatCurrency(batch.cost_per_kg)}</td>
                  <td className="px-4 py-2 text-sm">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => loadBatchDetails(batch.batch_id)}
                        className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700"
                        title="View/Edit Batch"
                      >
                        📝 Edit
                      </button>
                      <button
                        onClick={() => deleteBatch(batch.batch_id)}
                        className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700"
                        title="Delete Batch"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredHistory.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              {searchTerm || filterHandler || filterShed 
                ? 'No batches match your search criteria.' 
                : 'No batches found. Create your first batch to get started.'}
            </div>
          )}
        </div>
        
        {editingBatch && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-blue-800">
              📝 <strong>Editing Mode:</strong> Batch data has been loaded into the form. 
              Make your changes and click "Calculate Enhanced Metrics" to update the batch.
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🐔 Enhanced Broiler Chicken Cost Calculator
          </h1>
          <p className="text-lg text-gray-600">
            Professional poultry production cost analysis with detailed feed phases and removal tracking
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Input Form */}
          <div className="xl:col-span-2 bg-white rounded-xl shadow-lg p-6">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {/* Tab Navigation */}
            <div className="flex border-b mb-6 overflow-x-auto">
              <button
                onClick={() => setActiveTab('basic')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'basic' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                Basic Info
              </button>
              <button
                onClick={() => setActiveTab('feed')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'feed' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                Feed Phases
              </button>
              <button
                onClick={() => setActiveTab('costs')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'costs' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                Additional Costs
              </button>
              <button
                onClick={() => setActiveTab('removals')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'removals' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                Removals
              </button>
              <button
                onClick={() => setShowPerformanceTab(!showPerformanceTab)}
                className={`px-4 py-2 font-medium whitespace-nowrap ${showPerformanceTab ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
              >
                Performance
              </button>
              <button
                onClick={() => setShowAdminTab(!showAdminTab)}
                className={`px-4 py-2 font-medium whitespace-nowrap ${showAdminTab ? 'border-b-2 border-purple-500 text-purple-600' : 'text-gray-500'}`}
              >
                Admin
              </button>
              <button
                onClick={() => setShowBatchManagementTab(!showBatchManagementTab)}
                className={`px-4 py-2 font-medium whitespace-nowrap ${showBatchManagementTab ? 'border-b-2 border-orange-500 text-orange-600' : 'text-gray-500'}`}
              >
                Batch Management
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info Tab */}
              {activeTab === 'basic' && (
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800">Batch & Production Data</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Batch ID *
                      </label>
                      <input
                        type="text"
                        name="batch_id"
                        value={formData.batch_id}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., BATCH-2024-001"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Shed Number *
                      </label>
                      <input
                        type="text"
                        name="shed_number"
                        value={formData.shed_number}
                        onChange={handleInputChange}
                        list="sheds-list"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., SHED-A1"
                        required
                      />
                      <datalist id="sheds-list">
                        {sheds.map(shed => <option key={shed} value={shed} />)}
                      </datalist>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Handler Name *
                      </label>
                      <input
                        type="text"
                        name="handler_name"
                        value={formData.handler_name}
                        onChange={handleInputChange}
                        list="handlers-list"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., John Smith"
                        required
                      />
                      <datalist id="handlers-list">
                        {handlers.map(handler => <option key={handler} value={handler} />)}
                      </datalist>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Initial Number of Chicks *
                      </label>
                      <input
                        type="number"
                        name="initial_chicks"
                        value={formData.initial_chicks}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 10000"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Cost per Chick ($) *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="chick_cost_per_unit"
                        value={formData.chick_cost_per_unit}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 0.45"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Number of Chicks Died *
                      </label>
                      <input
                        type="number"
                        name="chicks_died"
                        value={formData.chicks_died}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 250"
                        required
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Feed Phases Tab */}
              {activeTab === 'feed' && (
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-gray-800">Feed Phases</h3>
                  
                  {/* Pre-starter Feed */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-3">Pre-starter Feed (0-10 days)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Consumption (kg)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="pre_starter_consumption"
                          value={formData.pre_starter_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="e.g., 500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Cost per kg ($)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="pre_starter_cost_per_kg"
                          value={formData.pre_starter_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="e.g., 0.65"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Starter Feed */}
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-green-800 mb-3">Starter Feed (10-24 days)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Consumption (kg)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="starter_consumption"
                          value={formData.starter_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                          placeholder="e.g., 2500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Cost per kg ($)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="starter_cost_per_kg"
                          value={formData.starter_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                          placeholder="e.g., 0.45"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Growth Feed */}
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-yellow-800 mb-3">Growth Feed (24-35 days)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Consumption (kg)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="growth_consumption"
                          value={formData.growth_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="e.g., 8000"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Cost per kg ($)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="growth_cost_per_kg"
                          value={formData.growth_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="e.g., 0.40"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Final Feed */}
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-800 mb-3">Final Feed (35+ days)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Consumption (kg)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="final_consumption"
                          value={formData.final_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="e.g., 12000"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Cost per kg ($)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="final_cost_per_kg"
                          value={formData.final_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="e.g., 0.35"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Additional Costs Tab */}
              {activeTab === 'costs' && (
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800">Additional Costs & Revenue</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Medicine & Vaccine Costs ($)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="medicine_costs"
                        value={formData.medicine_costs}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 800"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Miscellaneous Costs ($)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="miscellaneous_costs"
                        value={formData.miscellaneous_costs}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sawdust Bedding Cost ($)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="sawdust_bedding_cost"
                        value={formData.sawdust_bedding_cost}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 400"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Chicken Bedding Sale Revenue ($)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="chicken_bedding_sale_revenue"
                        value={formData.chicken_bedding_sale_revenue}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 600"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Cost Variations ($)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="cost_variations"
                        value={formData.cost_variations}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="e.g., 300"
                      />
                      <p className="text-xs text-gray-500 mt-1">Additional cost adjustments or variations</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Removals Tab */}
              {activeTab === 'removals' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xl font-semibold text-gray-800">Removal Batches (35-50 days)</h3>
                    <button
                      type="button"
                      onClick={addRemovalBatch}
                      disabled={removalBatches.length >= 15}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50"
                    >
                      Add Batch ({removalBatches.length}/15)
                    </button>
                  </div>

                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {removalBatches.map((batch, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-center mb-3">
                          <h4 className="font-medium text-gray-700">Batch {index + 1}</h4>
                          {removalBatches.length > 1 && (
                            <button
                              type="button"
                              onClick={() => removeRemovalBatch(index)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Quantity Removed
                            </label>
                            <input
                              type="number"
                              value={batch.quantity}
                              onChange={(e) => handleRemovalBatchChange(index, 'quantity', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                              placeholder="e.g., 2000"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Total Weight (kg)
                            </label>
                            <input
                              type="number"
                              step="0.1"
                              value={batch.total_weight_kg}
                              onChange={(e) => handleRemovalBatchChange(index, 'total_weight_kg', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                              placeholder="e.g., 4800"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Age (days)
                            </label>
                            <input
                              type="number"
                              value={batch.age_days}
                              onChange={(e) => handleRemovalBatchChange(index, 'age_days', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                              placeholder="35-50"
                              min="35"
                              max="60"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex space-x-4 pt-6 border-t">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 font-medium"
                >
                  {loading ? 'Calculating...' : '📊 Calculate Enhanced Metrics'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 font-medium"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>

          {/* Results */}
          {result && (
            <div className="xl:col-span-1 space-y-6">
              {/* Key Performance Metrics */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">Key Performance Metrics</h2>
                
                <div className="grid grid-cols-1 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-blue-600">Feed Conversion Ratio</h3>
                    <p className="text-2xl font-bold text-blue-800">{result.calculation.feed_conversion_ratio}</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-red-600">Mortality Rate</h3>
                    <p className="text-2xl font-bold text-red-800">{result.calculation.mortality_rate_percent}%</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-green-600">Net Cost per kg</h3>
                    <p className="text-2xl font-bold text-green-800">{formatCurrency(result.calculation.net_cost_per_kg)}</p>
                    <p className="text-xs text-green-600">After bedding revenue</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-purple-600">Weighted Avg Age</h3>
                    <p className="text-2xl font-bold text-purple-800">{result.calculation.weighted_average_age} days</p>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-yellow-600">Daily Weight Gain</h3>
                    <p className="text-2xl font-bold text-yellow-800">{result.calculation.daily_weight_gain} kg</p>
                  </div>
                </div>
              </div>

              {/* Production Summary */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Production Summary</h2>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Batch ID:</span>
                    <span className="font-semibold">{result.calculation.input_data.batch_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Shed:</span>
                    <span className="font-semibold">{result.calculation.input_data.shed_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Handler:</span>
                    <span className="font-semibold">{result.calculation.input_data.handler_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Initial Chicks:</span>
                    <span className="font-semibold">{result.calculation.input_data.initial_chicks.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Surviving Chicks:</span>
                    <span className="font-semibold">{result.calculation.surviving_chicks.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Removed Chicks:</span>
                    <span className="font-semibold">{result.calculation.removed_chicks.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Missing Chicks:</span>
                    <span className={`font-semibold ${result.calculation.missing_chicks > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {result.calculation.missing_chicks.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="text-gray-600">Total Weight Produced:</span>
                    <span className="font-semibold">{result.calculation.total_weight_produced_kg.toLocaleString()} kg</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Feed Consumed:</span>
                    <span className="font-semibold">{result.calculation.total_feed_consumed_kg.toLocaleString()} kg</span>
                  </div>
                  {result.calculation.total_revenue > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Bedding Revenue:</span>
                      <span className="font-semibold">{formatCurrency(result.calculation.total_revenue)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Cost Breakdown Chart */}
              <CostBreakdownChart costBreakdown={result.calculation.cost_breakdown} />
            </div>
          )}
        </div>

        {/* Performance Tab */}
        {showPerformanceTab && <HandlerPerformanceTable />}

        {/* Admin Tab */}
        {showAdminTab && <AdminManagement />}

        {/* Batch Management Tab */}
        {showBatchManagementTab && <BatchManagement />}

        {/* Full Results Display */}
        {result && (
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Financial Summary */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Financial Breakdown</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Chick Cost:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.chick_cost)} ({result.calculation.cost_breakdown.chick_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Pre-starter Feed:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.pre_starter_cost)} ({result.calculation.cost_breakdown.pre_starter_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Starter Feed:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.starter_cost)} ({result.calculation.cost_breakdown.starter_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Growth Feed:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.growth_cost)} ({result.calculation.cost_breakdown.growth_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Final Feed:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.final_cost)} ({result.calculation.cost_breakdown.final_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Medicine:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.medicine_cost)} ({result.calculation.cost_breakdown.medicine_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Miscellaneous:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.miscellaneous_cost)} ({result.calculation.cost_breakdown.miscellaneous_cost_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Cost Variations:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.cost_variations)} ({result.calculation.cost_breakdown.cost_variations_percent}%)</span>
                </div>
                <div className="flex justify-between">
                  <span>Sawdust Bedding:</span>
                  <span className="font-semibold">{formatCurrency(result.calculation.cost_breakdown.sawdust_bedding_cost)} ({result.calculation.cost_breakdown.sawdust_bedding_cost_percent}%)</span>
                </div>
                <div className="flex justify-between border-t pt-2 font-bold text-lg">
                  <span>Total Cost:</span>
                  <span>{formatCurrency(result.calculation.total_cost)}</span>
                </div>
                {result.calculation.total_revenue > 0 && (
                  <>
                    <div className="flex justify-between text-green-600">
                      <span>Bedding Revenue:</span>
                      <span className="font-semibold">-{formatCurrency(result.calculation.total_revenue)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2 font-bold text-xl text-green-600">
                      <span>Net Cost:</span>
                      <span>{formatCurrency(result.calculation.total_cost - result.calculation.total_revenue)}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Business Insights and Downloads */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Business Insights & Reports</h2>
              
              {/* Download Section */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <h3 className="text-lg font-semibold text-green-800 mb-2">📄 Batch Reports Available</h3>
                <div className="flex flex-wrap gap-2">
                  {result.insights.filter(insight => insight.includes('exported as:')).map((insight, index) => {
                    const filename = insight.split('as: ')[1].trim();
                    const isPDF = filename.endsWith('.pdf');
                    
                    return (
                      <button
                        key={index}
                        onClick={() => window.open(`${API}/export/${filename}`, '_blank')}
                        className={`flex items-center px-4 py-2 rounded-md text-sm font-medium ${
                          isPDF 
                            ? 'bg-red-600 text-white hover:bg-red-700' 
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >
                        {isPDF ? '📄 Download PDF Report' : '📊 Download JSON Data'}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Business Insights */}
              <div className="space-y-3">
                {result.insights.filter(insight => !insight.includes('exported as:')).map((insight, index) => (
                  <div key={index} className="bg-blue-50 p-3 rounded-lg text-sm">
                    {insight}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Calculation History */}
        {history.length > 0 && (
          <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Recent Calculations</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Batch ID</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Shed</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Handler</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Chicks</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">FCR</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Mortality %</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Age</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cost/kg</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {history.slice(0, 10).map((calc, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm text-gray-600">
                        {new Date(calc.date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-2 text-sm font-mono text-gray-900">{calc.batch_id}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.shed_number}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.handler_name}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.initial_chicks.toLocaleString()}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.fcr}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.mortality_percent}%</td>
                      <td className="px-4 py-2 text-sm text-gray-900">N/A</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{formatCurrency(calc.cost_per_kg)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;