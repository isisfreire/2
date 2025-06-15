import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [formData, setFormData] = useState({
    initial_chicks: '',
    chick_cost_per_unit: '',
    total_feed_consumed_kg: '',
    feed_cost_per_kg: '',
    chicks_died: '',
    final_weight_per_chick_kg: '',
    other_costs: '',
    revenue_per_kg: ''
  });
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);

  // Load calculation history on component mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API}/calculations`);
      setHistory(response.data);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Convert string inputs to numbers
      const numericData = {
        initial_chicks: parseInt(formData.initial_chicks) || 0,
        chick_cost_per_unit: parseFloat(formData.chick_cost_per_unit) || 0,
        total_feed_consumed_kg: parseFloat(formData.total_feed_consumed_kg) || 0,
        feed_cost_per_kg: parseFloat(formData.feed_cost_per_kg) || 0,
        chicks_died: parseInt(formData.chicks_died) || 0,
        final_weight_per_chick_kg: parseFloat(formData.final_weight_per_chick_kg) || 0,
        other_costs: parseFloat(formData.other_costs) || 0,
        revenue_per_kg: parseFloat(formData.revenue_per_kg) || 0
      };

      const response = await axios.post(`${API}/calculate`, numericData);
      setResult(response.data);
      
      // Reload history to include new calculation
      loadHistory();
      
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during calculation');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      initial_chicks: '',
      chick_cost_per_unit: '',
      total_feed_consumed_kg: '',
      feed_cost_per_kg: '',
      chicks_died: '',
      final_weight_per_chick_kg: '',
      other_costs: '',
      revenue_per_kg: ''
    });
    setResult(null);
    setError('');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🐔 Broiler Chicken Cost Calculator
          </h1>
          <p className="text-lg text-gray-600">
            Calculate production costs, feed conversion, and profitability for your broiler operation
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Production Data</h2>
            
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Initial Number of Chicks
                  </label>
                  <input
                    type="number"
                    name="initial_chicks"
                    value={formData.initial_chicks}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 1000"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cost per Chick ($)
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
                    Total Feed Consumed (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    name="total_feed_consumed_kg"
                    value={formData.total_feed_consumed_kg}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 3500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Feed Cost per kg ($)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="feed_cost_per_kg"
                    value={formData.feed_cost_per_kg}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 0.35"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Chicks Died
                  </label>
                  <input
                    type="number"
                    name="chicks_died"
                    value={formData.chicks_died}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 50"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Final Weight per Chick (kg)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="final_weight_per_chick_kg"
                    value={formData.final_weight_per_chick_kg}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 2.5"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Other Costs ($) - Optional
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="other_costs"
                    value={formData.other_costs}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 200"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Revenue per kg ($) - Optional
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="revenue_per_kg"
                    value={formData.revenue_per_kg}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="e.g., 4.50"
                  />
                </div>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {loading ? 'Calculating...' : '📊 Calculate'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>

          {/* Results */}
          {result && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Calculation Results</h2>
              
              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-blue-600">Feed Conversion Ratio</h3>
                  <p className="text-2xl font-bold text-blue-800">{result.calculation.feed_conversion_ratio}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-red-600">Mortality Rate</h3>
                  <p className="text-2xl font-bold text-red-800">{result.calculation.mortality_rate_percent}%</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-green-600">Cost per kg</h3>
                  <p className="text-2xl font-bold text-green-800">{formatCurrency(result.calculation.cost_per_kg)}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-purple-600">Total Weight Produced</h3>
                  <p className="text-2xl font-bold text-purple-800">{result.calculation.total_weight_produced_kg} kg</p>
                </div>
              </div>

              {/* Financial Summary */}
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Financial Summary</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total Cost:</span>
                    <span className="font-semibold">{formatCurrency(result.calculation.total_cost)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Revenue:</span>
                    <span className="font-semibold">{formatCurrency(result.calculation.total_revenue)}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="font-semibold">Profit/Loss:</span>
                    <span className={`font-bold ${result.calculation.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(result.calculation.profit_loss)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Production Details */}
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Production Details</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Initial Chicks:</span>
                    <span className="ml-2 font-semibold">{result.calculation.initial_chicks}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Surviving Chicks:</span>
                    <span className="ml-2 font-semibold">{result.calculation.surviving_chicks}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Feed Consumed:</span>
                    <span className="ml-2 font-semibold">{result.calculation.total_feed_consumed_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Avg Final Weight:</span>
                    <span className="ml-2 font-semibold">{result.calculation.final_weight_per_chick_kg} kg</span>
                  </div>
                </div>
              </div>

              {/* Insights */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Business Insights</h3>
                <div className="space-y-2">
                  {result.insights.map((insight, index) => (
                    <div key={index} className="bg-blue-50 p-3 rounded-lg text-sm">
                      {insight}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Calculation History */}
        {history.length > 0 && (
          <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Recent Calculations</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Chicks</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">FCR</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Mortality %</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cost/kg</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Profit/Loss</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {history.slice(0, 5).map((calc, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm text-gray-600">
                        {new Date(calc.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.initial_chicks}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.feed_conversion_ratio}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{calc.mortality_rate_percent}%</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{formatCurrency(calc.cost_per_kg)}</td>
                      <td className={`px-4 py-2 text-sm font-semibold ${calc.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(calc.profit_loss)}
                      </td>
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