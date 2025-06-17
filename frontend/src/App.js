import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import translations from "./translations";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const t = translations; // Abreviação para facilitar o uso

console.log('Frontend starting with API URL:', API);

function App() {
  const [formData, setFormData] = useState({
    // Batch identification
    batch_id: '',
    shed_number: '',
    handler_name: '',
    entry_date: '',
    exit_date: '',
    
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
        entry_date: formData.entry_date,
        exit_date: formData.exit_date,
        
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
        setError(t.batchIdRequired);
        return;
      }
      if (!numericData.shed_number) {
        setError(t.shedNumberRequired);
        return;
      }
      if (!numericData.handler_name) {
        setError(t.handlerNameRequired);
        return;
      }
      if (!numericData.entry_date) {
        setError(t.entryDateRequired);
        return;
      }
      if (!numericData.exit_date) {
        setError(t.exitDateRequired);
        return;
      }

      // Validate date logic
      const entryDate = new Date(numericData.entry_date);
      const exitDate = new Date(numericData.exit_date);
      
      if (exitDate <= entryDate) {
        setError(t.exitDateAfterEntry);
        return;
      }

      const daysDifference = Math.ceil((exitDate - entryDate) / (1000 * 60 * 60 * 24));
      if (daysDifference < 30) {
        setError(t.batchDurationMinimum);
        return;
      }
      if (daysDifference > 70) {
        setError(t.batchDurationMaximum);
        return;
      }

      if (numericData.removal_batches.length === 0) {
        setError(t.atLeastOneRemovalBatch);
        return;
      }

      // Choose endpoint based on whether we're editing or creating
      let response;
      if (editingBatch) {
        // Update existing batch
        response = await axios.put(`${API}/batches/${numericData.batch_id}`, numericData);
        setEditingBatch(false);
      } else {
        // Create new batch
        response = await axios.post(`${API}/calculate`, numericData);
      }
      
      setResult(response.data);
      
      // Reload history and performance data
      loadHistory();
      loadHandlers();
      loadSheds();
      loadHandlerPerformance();
      loadAllHandlers();
      loadAllSheds();
      
    } catch (err) {
      setError(err.response?.data?.detail || t.anErrorOccurredDuringCalculation);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      batch_id: '',
      shed_number: '',
      handler_name: '',
      entry_date: '',
      exit_date: '',
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
    setEditingBatch(false);
    setSelectedBatch(null);
  };

  // Admin functions
  const createHandler = async (handlerData) => {
    try {
      await axios.post(`${API}/handlers`, handlerData);
      loadAllHandlers();
      loadHandlers();
    } catch (err) {
      alert(err.response?.data?.detail || t.errorCreatingHandler);
    }
  };

  const updateHandler = async (handlerId, handlerData) => {
    try {
      await axios.put(`${API}/handlers/${handlerId}`, handlerData);
      loadAllHandlers();
      loadHandlers();
    } catch (err) {
      alert(err.response?.data?.detail || t.errorUpdatingHandler);
    }
  };

  const deleteHandler = async (handlerId) => {
    console.log('Attempting to delete handler with ID:', handlerId);
    console.log('API URL being used:', API);
    console.log('Full delete URL:', `${API}/handlers/${handlerId}`);
    
    if (!window.confirm(t.deleteHandlerConfirm)) return;
    
    try {
      console.log('Making delete request...');
      const response = await axios.delete(`${API}/handlers/${handlerId}`);
      console.log('Delete response:', response);
      alert(t.handlerDeletedSuccess);
      await loadAllHandlers();
      await loadHandlers();
    } catch (err) {
      console.error('Delete error details:', err);
      console.error('Error response:', err.response);
      const errorMsg = err.response?.data?.detail || err.message || t.errorDeletingHandler;
      alert(t.deleteFailed.replace('{error}', errorMsg));
    }
  };

  const createShed = async (shedData) => {
    try {
      await axios.post(`${API}/admin/sheds`, shedData);
      loadAllSheds();
      loadSheds();
    } catch (err) {
      alert(err.response?.data?.detail || t.errorCreatingShed);
    }
  };

  const updateShed = async (shedId, shedData) => {
    try {
      await axios.put(`${API}/admin/sheds/${shedId}`, shedData);
      loadAllSheds();
      loadSheds();
    } catch (err) {
      alert(err.response?.data?.detail || t.errorUpdatingShed);
    }
  };

  const deleteShed = async (shedId) => {
    console.log('Attempting to delete shed with ID:', shedId);
    console.log('API URL being used:', API);
    console.log('Full delete URL:', `${API}/admin/sheds/${shedId}`);
    
    if (!window.confirm(t.deleteShedConfirm)) return;
    
    try {
      console.log('Making delete request...');
      const response = await axios.delete(`${API}/admin/sheds/${shedId}`);
      console.log('Delete response:', response);
      alert(t.shedDeletedSuccess);
      await loadAllSheds();
      await loadSheds();
    } catch (err) {
      console.error('Delete error details:', err);
      console.error('Error response:', err.response);
      const errorMsg = err.response?.data?.detail || err.message || t.errorDeletingShed;
      alert(t.deleteFailed.replace('{error}', errorMsg));
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
        entry_date: batch.input_data.entry_date ? batch.input_data.entry_date.split('T')[0] : '',
        exit_date: batch.input_data.exit_date ? batch.input_data.exit_date.split('T')[0] : '',
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
      alert(t.errorLoadingBatchDetails.replace('{error}', err.response?.data?.detail || err.message));
    }
  };

  const regeneratePDF = async (batchId) => {
    try {
      const response = await axios.get(`${API}/batches/${batchId}/export-pdf`);
      const filename = response.data.filename;
      alert(t.pdfRegeneratedSuccess.replace('{filename}', filename));
      
      // Download the PDF immediately
      downloadPDF(filename);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || t.errorRegeneratingPdf;
      alert(errorMsg);
    }
  };

  const deleteBatch = async (batchId) => {
    console.log('Attempting to delete batch with ID:', batchId);
    console.log('API URL being used:', API);
    console.log('Full delete URL:', `${API}/batches/${batchId}`);
    
    if (!window.confirm(t.deleteBatchConfirm)) return;
    
    try {
      console.log('Making delete request...');
      const response = await axios.delete(`${API}/batches/${batchId}`);
      console.log('Delete response:', response);
      alert(t.batchDeletedSuccess);
      await loadHistory();
    } catch (err) {
      console.error('Delete error details:', err);
      console.error('Error response:', err.response);
      const errorMsg = err.response?.data?.detail || err.message || 'Error deleting batch';
      alert(t.deleteFailed.replace('{error}', errorMsg));
    }
  };

  // Test function to check API connectivity
  const testAPI = async () => {
    try {
      console.log('Testing API connectivity...');
      console.log('API URL:', API);
      
      // Test GET request
      const getResponse = await axios.get(`${API}/`);
      console.log('GET request successful:', getResponse.data);
      
      // Test if we can reach the handlers endpoint
      const handlersResponse = await axios.get(`${API}/handlers`);
      console.log('Handlers GET successful, count:', handlersResponse.data.length);
      
      alert(t.apiTestSuccess);
    } catch (err) {
      console.error('API connectivity test failed:', err);
      alert(t.apiTestFailed.replace('{error}', err.message));
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
      { name: t.chicks, value: costBreakdown.chick_cost_percent, color: '#3B82F6' },
      { name: t.preStarterFeedLabel, value: costBreakdown.pre_starter_cost_percent, color: '#10B981' },
      { name: t.starterFeedLabel, value: costBreakdown.starter_cost_percent, color: '#F59E0B' },
      { name: t.growthFeedLabel, value: costBreakdown.growth_cost_percent, color: '#EF4444' },
      { name: t.finalFeedLabel, value: costBreakdown.final_cost_percent, color: '#8B5CF6' },
      { name: t.medicine, value: costBreakdown.medicine_cost_percent, color: '#06B6D4' },
      { name: t.miscellaneous, value: costBreakdown.miscellaneous_cost_percent, color: '#84CC16' },
      { name: t.costVariationsLabel, value: costBreakdown.cost_variations_percent, color: '#F97316' }
    ].filter(item => item.value > 0);

    return (
      <div className="bg-white p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{t.costBreakdownTitle}</h3>
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
    if (!showPerformanceTab) return null;

    if (handlerPerformance.length === 0) {
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t.handlerPerformanceTitle}</h2>
          <div className="text-center py-8 text-gray-500">
            {t.noPerformanceDataText}
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t.handlerPerformanceTitle}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.rankHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.handlerHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.batchesHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.avgFcrHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.avgMortalityHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.avgDailyGainHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.scoreHeader}</th>
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
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">{t.farmAdministrationTitle}</h2>
        
        {/* Handler Management */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">{t.handlerManagementTitle}</h3>
          
          {/* Add New Handler Form */}
          <form onSubmit={handleCreateHandler} className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold mb-3">{t.addNewHandlerTitle}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder={t.handlerNameStar}
                value={newHandler.name}
                onChange={(e) => setNewHandler({...newHandler, name: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <input
                type="email"
                placeholder={t.emailOptional}
                value={newHandler.email}
                onChange={(e) => setNewHandler({...newHandler, email: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="tel"
                placeholder={t.phoneOptional}
                value={newHandler.phone}
                onChange={(e) => setNewHandler({...newHandler, phone: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="text"
                placeholder={t.notesOptional}
                value={newHandler.notes}
                onChange={(e) => setNewHandler({...newHandler, notes: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <button
              type="submit"
              className="mt-3 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
            >
              {t.addHandler}
            </button>
          </form>

          {/* Handlers List */}
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.nameHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.emailHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.phoneHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.actionsHeader}</th>
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
                        {t.edit}
                      </button>
                      <button
                        onClick={() => {
                          console.log('Delete button clicked for handler:', handler.id);
                          if (window.confirm(t.deleteHandlerConfirm)) {
                            deleteHandler(handler.id);
                          }
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        {t.delete}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Handler Edit Modal */}
          {editingHandler && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                <h4 className="text-lg font-semibold mb-4">{t.edit} {t.handlerHeader}: {editingHandler.name}</h4>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  handleUpdateHandler(editingHandler.id, {
                    name: formData.get('name'),
                    email: formData.get('email') || null,
                    phone: formData.get('phone') || null,
                    notes: formData.get('notes') || null
                  });
                }}>
                  <div className="space-y-4">
                    <input
                      name="name"
                      type="text"
                      placeholder={t.handlerNameStar}
                      defaultValue={editingHandler.name}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                    <input
                      name="email"
                      type="email"
                      placeholder={t.emailOptional}
                      defaultValue={editingHandler.email || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <input
                      name="phone"
                      type="tel"
                      placeholder={t.phoneOptional}
                      defaultValue={editingHandler.phone || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <input
                      name="notes"
                      type="text"
                      placeholder={t.notesOptional}
                      defaultValue={editingHandler.notes || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div className="flex space-x-3 mt-6">
                    <button
                      type="submit"
                      className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
                    >
                      {t.updateHandler}
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingHandler(null)}
                      className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                    >
                      {t.cancel}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>

        {/* Shed Management */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">{t.shedManagementTitle}</h3>
          
          {/* Add New Shed Form */}
          <form onSubmit={handleCreateShed} className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold mb-3">{t.addNewShedTitle}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder={t.shedNumberStar}
                value={newShed.number}
                onChange={(e) => setNewShed({...newShed, number: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <input
                type="number"
                placeholder={t.capacityOptional}
                value={newShed.capacity}
                onChange={(e) => setNewShed({...newShed, capacity: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="text"
                placeholder={t.locationOptional}
                value={newShed.location}
                onChange={(e) => setNewShed({...newShed, location: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <select
                value={newShed.status}
                onChange={(e) => setNewShed({...newShed, status: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="active">{t.active}</option>
                <option value="maintenance">{t.maintenance}</option>
                <option value="inactive">{t.inactive}</option>
              </select>
            </div>
            <button
              type="submit"
              className="mt-3 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
            >
              {t.addShed}
            </button>
          </form>

          {/* Sheds List */}
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.numberHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.capacityHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.locationHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.statusHeader}</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.actionsHeader}</th>
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
                        {shed.status === 'active' ? t.active : 
                         shed.status === 'maintenance' ? t.maintenance : t.inactive}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <button
                        onClick={() => setEditingShed(shed)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        {t.edit}
                      </button>
                      <button
                        onClick={() => {
                          console.log('Delete button clicked for shed:', shed.id);
                          if (window.confirm(t.deleteShedConfirm.replace('{shedNumber}', shed.number))) {
                            deleteShed(shed.id);
                          }
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        {t.delete}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Shed Edit Modal */}
          {editingShed && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                <h4 className="text-lg font-semibold mb-4">{t.edit} {t.shedHeader}: {editingShed.number}</h4>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  handleUpdateShed(editingShed.id, {
                    number: formData.get('number'),
                    capacity: formData.get('capacity') ? parseInt(formData.get('capacity')) : null,
                    location: formData.get('location') || null,
                    status: formData.get('status'),
                    notes: formData.get('notes') || null
                  });
                }}>
                  <div className="space-y-4">
                    <input
                      name="number"
                      type="text"
                      placeholder={t.shedNumberStar}
                      defaultValue={editingShed.number}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                    <input
                      name="capacity"
                      type="number"
                      placeholder={t.capacityOptional}
                      defaultValue={editingShed.capacity || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <input
                      name="location"
                      type="text"
                      placeholder={t.locationOptional}
                      defaultValue={editingShed.location || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <select
                      name="status"
                      defaultValue={editingShed.status}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="active">{t.active}</option>
                      <option value="maintenance">{t.maintenance}</option>
                      <option value="inactive">{t.inactive}</option>
                    </select>
                    <input
                      name="notes"
                      type="text"
                      placeholder={t.notesOptional}
                      defaultValue={editingShed.notes || ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div className="flex space-x-3 mt-6">
                    <button
                      type="submit"
                      className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
                    >
                      {t.updateShed}
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingShed(null)}
                      className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                    >
                      {t.cancel}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
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
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">{t.batchManagementHeader}</h2>
        
        {/* Search and Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.searchBatches}</label>
            <input
              type="text"
              placeholder={t.searchPlaceholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.filterByHandler}</label>
            <select
              value={filterHandler}
              onChange={(e) => setFilterHandler(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">{t.allHandlers}</option>
              {handlers.map(handler => (
                <option key={handler} value={handler}>{handler}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.filterByShed}</label>
            <select
              value={filterShed}
              onChange={(e) => setFilterShed(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">{t.allSheds}</option>
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
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.batchIdHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.dateHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.shedHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.handlerHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.chicksHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.fcrHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.mortalityPercentHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.costKgHeader}</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.actionsHeader}</th>
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
                    <div className="flex space-x-1">
                      <button
                        onClick={() => loadBatchDetails(batch.batch_id)}
                        className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700"
                        title={t.editButton}
                      >
                        {t.editButton}
                      </button>
                      <button
                        onClick={() => regeneratePDF(batch.batch_id)}
                        className="bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700"
                        title={t.printButton}
                      >
                        {t.printButton}
                      </button>
                      <button
                        onClick={() => {
                          console.log('Delete button clicked for batch:', batch.batch_id);
                          deleteBatch(batch.batch_id);
                        }}
                        className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700"
                        title={t.deleteButton}
                      >
                        {t.deleteButton}
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
                ? t.noBatchesMatchCriteria
                : t.noBatchesFound + ' ' + t.createFirstBatch}
            </div>
          )}
        </div>
        
        {editingBatch && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-blue-800">
              {t.editingModeText}
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
            {t.enhancedBroilerCalculatorTitle}
          </h1>
          <p className="text-lg text-gray-600">
            {t.professionalPoultrySubtitle}
          </p>
          {/* Temporary API Test Button */}
          <button 
            onClick={testAPI}
            className="mt-4 bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
          >
            {t.testApiConnection}
          </button>
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
                {t.basicInfo}
              </button>
              <button
                onClick={() => setActiveTab('feed')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'feed' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                {t.feedPhases}
              </button>
              <button
                onClick={() => setActiveTab('costs')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'costs' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                {t.additionalCosts}
              </button>
              <button
                onClick={() => setActiveTab('removals')}
                className={`px-4 py-2 font-medium whitespace-nowrap ${activeTab === 'removals' ? 'border-b-2 border-green-500 text-green-600' : 'text-gray-500'}`}
              >
                {t.removals}
              </button>
              <button
                onClick={() => setShowPerformanceTab(!showPerformanceTab)}
                className={`px-4 py-2 font-medium whitespace-nowrap ${showPerformanceTab ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
              >
                {t.performance}
              </button>
              <button
                onClick={() => setShowAdminTab(!showAdminTab)}
                className={`px-4 py-2 font-medium whitespace-nowrap ${showAdminTab ? 'border-b-2 border-purple-500 text-purple-600' : 'text-gray-500'}`}
              >
                {t.admin}
              </button>
              <button
                onClick={() => setShowBatchManagementTab(!showBatchManagementTab)}
                className={`px-4 py-2 font-medium whitespace-nowrap ${showBatchManagementTab ? 'border-b-2 border-orange-500 text-orange-600' : 'text-gray-500'}`}
              >
                {t.batchManagement}
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info Tab */}
              {activeTab === 'basic' && (
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800">{t.batchProductionData}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.batchIdLabel}
                      </label>
                      <input
                        type="text"
                        name="batch_id"
                        value={formData.batch_id}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.batchIdExample}
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.shedNumberLabel}
                      </label>
                      <input
                        type="text"
                        name="shed_number"
                        value={formData.shed_number}
                        onChange={handleInputChange}
                        list="sheds-list"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.shedNumberExample}
                        required
                      />
                      <datalist id="sheds-list">
                        {sheds.map(shed => <option key={shed} value={shed} />)}
                      </datalist>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.handlerNameLabel}
                      </label>
                      <input
                        type="text"
                        name="handler_name"
                        value={formData.handler_name}
                        onChange={handleInputChange}
                        list="handlers-list"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.handlerNameExample}
                        required
                      />
                      <datalist id="handlers-list">
                        {handlers.map(handler => <option key={handler} value={handler} />)}
                      </datalist>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.entryDateLabel}
                      </label>
                      <input
                        type="date"
                        name="entry_date"
                        value={formData.entry_date}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.exitDateLabel}
                      </label>
                      <input
                        type="date"
                        name="exit_date"
                        value={formData.exit_date}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.initialChicksLabel}
                      </label>
                      <input
                        type="number"
                        name="initial_chicks"
                        value={formData.initial_chicks}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.initialChicksExample}
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.costPerChickLabel}
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="chick_cost_per_unit"
                        value={formData.chick_cost_per_unit}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.costPerChickExample}
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.chicksDiedLabel}
                      </label>
                      <input
                        type="number"
                        name="chicks_died"
                        value={formData.chicks_died}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.chicksDiedExample}
                        required
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Feed Phases Tab */}
              {activeTab === 'feed' && (
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-gray-800">{t.feedPhasesTitle}</h3>
                  
                  {/* Pre-starter Feed */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-3">{t.preStarterFeedTitle}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.consumptionLabel}
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="pre_starter_consumption"
                          value={formData.pre_starter_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={t.consumptionExample}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.costPerKgLabel}
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="pre_starter_cost_per_kg"
                          value={formData.pre_starter_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={t.costPerKgExample}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Starter Feed */}
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-green-800 mb-3">{t.starterFeedTitle}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.consumptionLabel}
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="starter_consumption"
                          value={formData.starter_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                          placeholder="ex: 2500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.costPerKgLabel}
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="starter_cost_per_kg"
                          value={formData.starter_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                          placeholder="ex: 0,45"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Growth Feed */}
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-yellow-800 mb-3">{t.growthFeedTitle}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.consumptionLabel}
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="growth_consumption"
                          value={formData.growth_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="ex: 8000"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.costPerKgLabel}
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="growth_cost_per_kg"
                          value={formData.growth_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="ex: 0,40"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Final Feed */}
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-800 mb-3">{t.finalFeedTitle}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.consumptionLabel}
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          name="final_consumption"
                          value={formData.final_consumption}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="ex: 12000"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t.costPerKgLabel}
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          name="final_cost_per_kg"
                          value={formData.final_cost_per_kg}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="ex: 0,35"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Additional Costs Tab */}
              {activeTab === 'costs' && (
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800">{t.additionalCosts}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.medicineCosts}
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="medicine_costs"
                        value={formData.medicine_costs}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.medicineCostsPlaceholder}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.miscellaneousCosts}
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="miscellaneous_costs"
                        value={formData.miscellaneous_costs}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.miscellaneousCostsPlaceholder}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.costVariations}
                        <span className="text-xs text-gray-500 ml-1">({t.costVariationsHelp})</span>
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="cost_variations"
                        value={formData.cost_variations}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.costVariationsPlaceholder}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.sawdustBeddingCost}
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="sawdust_bedding_cost"
                        value={formData.sawdust_bedding_cost}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.sawdustBeddingCostPlaceholder}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t.chickenBeddingSale}
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="chicken_bedding_sale_revenue"
                        value={formData.chicken_bedding_sale_revenue}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder={t.chickenBeddingSalePlaceholder}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Removals Tab */}
              {activeTab === 'removals' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xl font-semibold text-gray-800">{t.removalBatches}</h3>
                    <button
                      type="button"
                      onClick={addRemovalBatch}
                      className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 text-sm"
                      disabled={removalBatches.length >= 15}
                    >
                      {t.addBatch}
                    </button>
                  </div>
                  
                  <div className="space-y-3">
                    {removalBatches.map((batch, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-center mb-3">
                          <h4 className="font-medium text-gray-700">{t.batchNumber} {index + 1}</h4>
                          {removalBatches.length > 1 && (
                            <button
                              type="button"
                              onClick={() => removeRemovalBatch(index)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              {t.removeBatch}
                            </button>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              {t.quantityRemoved} *
                            </label>
                            <input
                              type="number"
                              value={batch.quantity}
                              onChange={(e) => handleRemovalBatchChange(index, 'quantity', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                              placeholder={t.quantityRemovedPlaceholder}
                              required
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              {t.totalWeight} *
                            </label>
                            <input
                              type="number"
                              step="0.1"
                              value={batch.total_weight_kg}
                              onChange={(e) => handleRemovalBatchChange(index, 'total_weight_kg', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                              placeholder={t.totalWeightPlaceholder}
                              required
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              {t.ageDays} * (35-60)
                            </label>
                            <input
                              type="number"
                              value={batch.age_days}
                              onChange={(e) => handleRemovalBatchChange(index, 'age_days', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                              placeholder={t.ageDaysPlaceholder}
                              min="35"
                              max="60"
                              required
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 disabled:opacity-50 font-medium"
                >
                  {loading ? t.loadingCalculation : t.calculateCosts}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="bg-gray-400 text-white py-3 px-6 rounded-md hover:bg-gray-500 font-medium"
                >
                  {t.resetForm}
                </button>
              </div>
            </form>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {result && (
              <>
                {/* Key Performance Metrics */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t.keyPerformanceMetrics}</h2>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-sm text-blue-600 font-medium">{t.feedConversionRatio}</div>
                      <div className="text-2xl font-bold text-blue-800">{result.feed_conversion_ratio}</div>
                    </div>
                    
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="text-sm text-red-600 font-medium">{t.mortalityRate}</div>
                      <div className="text-2xl font-bold text-red-800">{result.mortality_rate}%</div>
                    </div>
                    
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-sm text-green-600 font-medium">{t.viabilityRate}</div>
                      <div className="text-2xl font-bold text-green-800">{result.viability_rate}%</div>
                    </div>
                    
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-sm text-purple-600 font-medium">{t.netCostPerKg}</div>
                      <div className="text-lg text-purple-600">{t.afterBeddingRevenue}</div>
                      <div className="text-2xl font-bold text-purple-800">{formatCurrency(result.net_cost_per_kg)}</div>
                    </div>
                    
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="text-sm text-yellow-600 font-medium">{t.weightedAvgAge}</div>
                      <div className="text-2xl font-bold text-yellow-800">{result.weighted_avg_age} {t.days}</div>
                    </div>
                    
                    <div className="bg-indigo-50 p-4 rounded-lg">
                      <div className="text-sm text-indigo-600 font-medium">{t.dailyWeightGain}</div>
                      <div className="text-2xl font-bold text-indigo-800">{result.daily_weight_gain} {t.kg}</div>
                    </div>
                  </div>
                </div>

                {/* Production Summary */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t.productionSummary}</h2>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium">{t.batchIdLabel}</span>
                      <span>{result.batch_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.shed}:</span>
                      <span>{result.shed_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.handler}:</span>
                      <span>{result.handler_name}</span>
                    </div>
                    {result.entry_date && (
                      <div className="flex justify-between">
                        <span className="font-medium">{t.entryDateLabel}</span>
                        <span>{new Date(result.entry_date).toLocaleDateString()}</span>
                      </div>
                    )}
                    {result.exit_date && (
                      <div className="flex justify-between">
                        <span className="font-medium">{t.exitDateLabel}</span>
                        <span>{new Date(result.exit_date).toLocaleDateString()}</span>
                      </div>
                    )}
                    {result.batch_duration_days && (
                      <div className="flex justify-between">
                        <span className="font-medium">{t.batchDuration}:</span>
                        <span>{result.batch_duration_days} {t.days}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="font-medium">{t.survivingChicks}:</span>
                      <span>{result.surviving_chicks.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.viabilityCaught}:</span>
                      <span>{result.viability_caught.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.viabilityRateLabel}</span>
                      <span>{result.viability_rate}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.missingChicks}:</span>
                      <span>{result.missing_chicks.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.totalWeightProduced}:</span>
                      <span>{result.total_weight_produced} {t.kg}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t.totalFeedConsumed}:</span>
                      <span>{result.total_feed_consumed} {t.kg}</span>
                    </div>
                    {result.bedding_revenue && (
                      <div className="flex justify-between">
                        <span className="font-medium">{t.beddingRevenue}:</span>
                        <span>{formatCurrency(result.bedding_revenue)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Cost Breakdown Chart */}
                {result.cost_breakdown && <CostBreakdownChart costBreakdown={result.cost_breakdown} />}

                {/* Business Insights */}
                {result.business_insights && result.business_insights.length > 0 && (
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t.insights}</h2>
                    <div className="space-y-3">
                      {result.business_insights.map((insight, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                          {insight}
                        </div>
                      ))}
                    </div>
                    
                    {/* PDF Download Button */}
                    {result.pdf_filename && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <button
                          onClick={() => downloadPDF(result.pdf_filename)}
                          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium"
                        >
                          📄 {t.downloadPDF || "Download PDF Report"}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            {/* Calculation History */}
            {history.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">{t.calculationHistory}</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full table-auto">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.batchIdHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.dateHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.shedHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.handlerHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.chicksHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.fcrHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.mortalityPercentHeader}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{t.costKgHeader}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {history.slice(0, 5).map((calc, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-3 py-2 text-xs font-mono font-semibold text-gray-900">{calc.batch_id}</td>
                          <td className="px-3 py-2 text-xs text-gray-600">
                            {new Date(calc.date).toLocaleDateString()}
                          </td>
                          <td className="px-3 py-2 text-xs text-gray-900">{calc.shed_number}</td>
                          <td className="px-3 py-2 text-xs text-gray-900">{calc.handler_name}</td>
                          <td className="px-3 py-2 text-xs text-gray-900">{calc.initial_chicks.toLocaleString()}</td>
                          <td className="px-3 py-2 text-xs text-gray-900">{calc.fcr}</td>
                          <td className="px-3 py-2 text-xs text-gray-900">{calc.mortality_percent}%</td>
                          <td className="px-3 py-2 text-xs text-gray-900">{formatCurrency(calc.cost_per_kg)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {history.length === 0 && (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    {t.noHistoryData}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Handler Performance Table */}
        <HandlerPerformanceTable />

        {/* Admin Management */}
        {showAdminTab && <AdminManagement />}

        {/* Batch Management */}
        {showBatchManagementTab && <BatchManagement />}
      </div>
    </div>
  );
}

export default App;