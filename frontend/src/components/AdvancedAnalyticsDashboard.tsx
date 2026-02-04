// @ts-nocheck
import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { TrendingUp, Activity, Target, Calendar, Download } from 'lucide-react';

const COLORS = ['#10b981', '#6366f1', '#f59e0b', '#ec4899'];

const AdvancedAnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/analytics?days=${days}`);
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="w-12 h-12 border-4 border-palette-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const distributionData = data ? Object.entries(data.distribution).map(([name, value]) => ({ name, value })) : [];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-black text-palette-dark tracking-tighter uppercase">Advanced Analytics</h2>
          <p className="text-gray-400 font-medium">Real-time performance metrics and distribution trends.</p>
        </div>
        <div className="flex gap-4">
          <div className="flex bg-white rounded-xl shadow-sm border border-gray-100 p-1">
            {[7, 30, 90].map(d => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${days === d ? 'bg-palette-primary text-white shadow-md' : 'text-gray-400 hover:text-gray-600'}`}
              >
                {d}D
              </button>
            ))}
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-bold text-gray-600 hover:bg-gray-50 transition-colors">
            <Download size={14} /> EXPORT
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl">
              <Activity size={20} />
            </div>
          </div>
          <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Avg Q Score</div>
          <div className="text-3xl font-black text-palette-dark tracking-tighter">{data?.avg_q.toFixed(4)}</div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-2xl">
              <Target size={20} />
            </div>
          </div>
          <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Directives</div>
          <div className="text-3xl font-black text-palette-dark tracking-tighter">{data?.count}</div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-amber-50 text-amber-600 rounded-2xl">
              <TrendingUp size={20} />
            </div>
          </div>
          <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Max Quality</div>
          <div className="text-3xl font-black text-palette-dark tracking-tighter">{data?.range?.max.toFixed(2)}</div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl">
              <Calendar size={20} />
            </div>
          </div>
          <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Floor Quality</div>
          <div className="text-3xl font-black text-palette-dark tracking-tighter">{data?.range?.min.toFixed(2)}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-sm font-black text-palette-dark uppercase tracking-widest mb-8">Quality Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-2 bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-sm font-black text-palette-dark uppercase tracking-widest mb-8">Quality Trend</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.trends || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 1]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Area type="monotone" dataKey="avg_q" stroke="#6366f1" fill="#6366f1" fillOpacity={0.1} strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;
