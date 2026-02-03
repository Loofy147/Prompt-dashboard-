import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, ScatterChart, Scatter, ZAxis, Treemap, Cell
} from 'recharts';
import {
  LayoutDashboard, Users, MessageSquare, Video, Filter, Layers,
  Calendar, ChevronRight, AlertCircle, TrendingDown, Clock, Search
} from 'lucide-react';

const SENTIMENT_DATA = [
  { x: 45, y: 82, z: 10, name: 'P-102' },
  { x: 120, y: 45, z: 15, name: 'P-405' },
  { x: 60, y: 70, z: 20, name: 'P-203' },
  { x: 200, y: 30, z: 25, name: 'P-892' },
  { x: 30, y: 95, z: 12, name: 'P-110' },
  { x: 180, y: 20, z: 18, name: 'P-551' },
  { x: 90, y: 60, z: 22, name: 'P-304' },
  { x: 150, y: 55, z: 30, name: 'P-707' },
];

const SUS_TREND_DATA = [
  { month: 'Jan', sus: 72, features: 2 },
  { month: 'Feb', sus: 70, features: 3 },
  { month: 'Mar', sus: 65, features: 5 },
  { month: 'Apr', sus: 68, features: 4 },
  { month: 'May', sus: 74, features: 6 },
  { month: 'Jun', sus: 71, features: 8 },
];

const THEME_DATA = [
  { name: 'Navigation Friction', value: 45, color: '#e11d48' },
  { name: 'Confusing Icons', value: 32, color: '#fbbf24' },
  { name: 'Speed/Performance', value: 28, color: '#22c55e' },
  { name: 'Feature Discoverability', value: 25, color: '#6366f1' },
  { name: 'Onboarding Flow', value: 20, color: '#ec4899' },
];

const TAG_DATA = [
  { name: 'UI/UX', children: [
    { name: 'Confusion', size: 400 },
    { name: 'Delight', size: 200 },
    { name: 'Frustration', size: 300 },
  ]},
  { name: 'Process', children: [
    { name: 'Checkout', size: 500 },
    { name: 'Search', size: 200 },
    { name: 'Profile', size: 100 },
  ]},
];

const ResearchDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const renderActiveWidget = () => {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Widget 1: Sentiment-Success Matrix */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-black text-palette-dark tracking-tight">SENTIMENT-SUCCESS MATRIX</h3>
            <span className="text-[10px] bg-indigo-50 text-indigo-600 px-2 py-1 rounded font-bold uppercase">Task Efficiency vs Sentiment</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis type="number" dataKey="x" name="Task Time" unit="s" label={{ value: 'Task Time (s)', position: 'insideBottom', offset: -10 }} />
                <YAxis type="number" dataKey="y" name="Sentiment" unit="%" label={{ value: 'Sentiment (%)', angle: -90, position: 'insideLeft' }} />
                <ZAxis type="number" dataKey="z" range={[60, 400]} name="Impact" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Participants" data={SENTIMENT_DATA} fill="#6366f1">
                  {SENTIMENT_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.y < 50 && entry.x > 100 ? '#e11d48' : '#6366f1'} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 p-3 bg-rose-50 rounded-lg border border-rose-100 flex items-center gap-3">
            <AlertCircle className="text-rose-600 w-5 h-5" />
            <p className="text-xs text-rose-800 font-medium">
              High Task Time + Low Sentiment detected in <strong>Participant P-892</strong>. Possible UX blocker in Checkout.
            </p>
          </div>
        </div>

        {/* Widget 2: SUS vs Feature Usage */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-black text-palette-dark tracking-tight">SUS CORRELATION TREND</h3>
            <span className="text-[10px] bg-indigo-50 text-indigo-600 px-2 py-1 rounded font-bold uppercase">v2.4 Deployment Impact</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={SUS_TREND_DATA}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" orientation="left" stroke="#6366f1" />
                <YAxis yAxisId="right" orientation="right" stroke="#fbbf24" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="sus" stroke="#6366f1" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} name="SUS Score" />
                <Line yAxisId="right" type="monotone" dataKey="features" stroke="#fbbf24" strokeWidth={3} strokeDasharray="5 5" name="Features Shipped" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-gray-400">
            <div className="flex items-center gap-2">
              <TrendingDown size={12} className="text-rose-500" />
              <span>SUS DROP IN MARCH (-5.2 pts)</span>
            </div>
            <span>TARGET: &gt; 80.0</span>
          </div>
        </div>

        {/* Widget 3: Thematic Resonance */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-black text-palette-dark tracking-tight">THEMATIC RESONANCE</h3>
            <span className="text-[10px] bg-indigo-50 text-indigo-600 px-2 py-1 rounded font-bold uppercase">Qualitative Frequency</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={THEME_DATA} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={150} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {THEME_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Widget 4: Tag Heatmap */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-black text-palette-dark tracking-tight">QUALITATIVE TAG HEATMAP</h3>
            <span className="text-[10px] bg-indigo-50 text-indigo-600 px-2 py-1 rounded font-bold uppercase">System-Wide Impact</span>
          </div>
          <div className="h-64">
             {/* Mock Treemap using a Grid because Treemap is complex to style perfectly here */}
             <div className="grid grid-cols-3 grid-rows-2 gap-2 h-full">
                <div
                  className="col-span-2 row-span-1 bg-indigo-600 rounded-lg p-4 flex flex-col justify-end text-white cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => setSelectedTag('Checkout')}
                >
                  <span className="text-[10px] font-bold opacity-60 uppercase">Process</span>
                  <span className="text-xl font-black">Checkout</span>
                  <span className="text-xs font-medium">500 Mentions</span>
                </div>
                <div
                  className="col-span-1 row-span-2 bg-rose-600 rounded-lg p-4 flex flex-col justify-end text-white cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => setSelectedTag('Confusion')}
                >
                  <span className="text-[10px] font-bold opacity-60 uppercase">UI/UX</span>
                  <span className="text-xl font-black">Confusion</span>
                  <span className="text-xs font-medium">400 Mentions</span>
                </div>
                <div
                  className="col-span-1 row-span-1 bg-indigo-400 rounded-lg p-4 flex flex-col justify-end text-white cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => setSelectedTag('Frustration')}
                >
                  <span className="text-[10px] font-bold opacity-60 uppercase">UI/UX</span>
                  <span className="text-xl font-black">Frustration</span>
                  <span className="text-xs font-medium">300 Mentions</span>
                </div>
                <div
                  className="col-span-1 row-span-1 bg-emerald-500 rounded-lg p-4 flex flex-col justify-end text-white cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => setSelectedTag('Delight')}
                >
                  <span className="text-[10px] font-bold opacity-60 uppercase">UI/UX</span>
                  <span className="text-xl font-black">Delight</span>
                  <span className="text-xs font-medium">200 Mentions</span>
                </div>
             </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-[800px] bg-gray-50 rounded-3xl overflow-hidden border border-gray-200">
      {/* Sidebar */}
      <aside className="w-64 bg-palette-dark text-white flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <LayoutDashboard className="text-bolt-light" />
            <span className="font-black tracking-tighter text-lg uppercase">RES-OPS v1.0</span>
          </div>

          <nav className="space-y-2">
            {[
              { id: 'overview', label: 'EXECUTIVE OVERVIEW', icon: LayoutDashboard },
              { id: 'modules', label: 'STUDY MODULES', icon: Layers },
              { id: 'library', label: 'PARTICIPANT LIBRARY', icon: Users },
              { id: 'artifacts', label: 'RESEARCH ARTIFACTS', icon: Video },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition-all ${
                  activeTab === item.id
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <item.icon size={16} />
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-auto p-6">
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Global SUS</span>
              <span className="text-xs font-black text-bolt-light">71.4</span>
            </div>
            <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-bolt-light w-[71.4%]"></div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-20 bg-white border-b border-gray-100 flex items-center justify-between px-8">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-gray-400">
              <Calendar size={18} />
              <span className="text-xs font-bold">JAN 1, 2026 - JUN 30, 2026</span>
            </div>
            <div className="h-4 w-px bg-gray-200"></div>
            <div className="flex items-center gap-4">
              <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Segment:</span>
              <select className="bg-gray-100 border-none rounded-lg text-xs font-bold px-3 py-1.5 focus:ring-palette-primary">
                <option>ALL PARTICIPANTS (1,024)</option>
                <option>POWER USERS (256)</option>
                <option>NEW USERS (768)</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-4">
             <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="SEARCH INSIGHTS..."
                  className="bg-gray-100 border-none rounded-xl pl-10 pr-4 py-2 text-xs font-bold w-64 focus:ring-palette-primary"
                />
             </div>
             <button className="p-2 bg-indigo-50 text-indigo-600 rounded-xl hover:bg-indigo-100 transition-colors">
                <Filter size={18} />
             </button>
          </div>
        </header>

        {/* Dashboard Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="flex justify-between items-end mb-8">
            <div>
              <div className="flex items-center gap-2 text-indigo-600 font-black text-[10px] uppercase tracking-[0.2em] mb-1">
                <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-pulse"></div>
                LIVE RESEARCH DATA
              </div>
              <h2 className="text-3xl font-black text-palette-dark tracking-tighter uppercase leading-none">
                Insight Dashboard
              </h2>
            </div>

            <div className="flex gap-2">
              <div className="bg-white px-4 py-2 rounded-xl border border-gray-200 flex items-center gap-4">
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-gray-400 uppercase leading-none mb-1">Success Rate</span>
                  <span className="text-xl font-black text-emerald-600 leading-none">88.2%</span>
                </div>
                <TrendingDown className="text-rose-500 rotate-180" size={20} />
              </div>
              <div className="bg-white px-4 py-2 rounded-xl border border-gray-200 flex items-center gap-4">
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-gray-400 uppercase leading-none mb-1">Task Time</span>
                  <span className="text-xl font-black text-palette-dark leading-none">124s</span>
                </div>
                <Clock className="text-indigo-400" size={20} />
              </div>
            </div>
          </div>

          {renderActiveWidget()}

          {/* Tag Interactive Protocol Overlay */}
          {selectedTag && (
            <div className="mt-8 p-6 bg-indigo-600 rounded-3xl text-white flex items-center justify-between shadow-2xl shadow-indigo-200 animate-in fade-in slide-in-from-bottom-4 duration-300">
               <div className="flex items-center gap-6">
                  <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
                    <Filter size={32} />
                  </div>
                  <div>
                    <h4 className="text-2xl font-black tracking-tighter uppercase leading-none">
                      FILTERED BY: {selectedTag}
                    </h4>
                    <p className="text-indigo-100 text-sm font-medium mt-1">
                      Showing impact on System Usability Scale (SUS) for this specific tag.
                    </p>
                  </div>
               </div>
               <div className="flex items-center gap-8 px-8 border-l border-white/20">
                  <div className="text-center">
                    <div className="text-[10px] font-black text-indigo-200 uppercase mb-1">Segment SUS</div>
                    <div className="text-4xl font-black">59.2</div>
                  </div>
                  <div className="text-center">
                    <div className="text-[10px] font-black text-indigo-200 uppercase mb-1">Delta</div>
                    <div className="text-4xl font-black text-rose-300">-12.2</div>
                  </div>
                  <button
                    onClick={() => setSelectedTag(null)}
                    className="bg-white text-indigo-600 px-6 py-3 rounded-xl font-black text-xs hover:bg-indigo-50 transition-colors uppercase"
                  >
                    Clear Filter
                  </button>
               </div>
            </div>
          )}

          {/* Design-to-Data Table Section */}
          <div className="mt-12 bg-white rounded-3xl border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h3 className="text-xl font-black text-palette-dark tracking-tight uppercase">Design-to-Data Mapping</h3>
              <button className="text-[10px] font-black text-indigo-600 flex items-center gap-1 uppercase">
                EXPORT SCHEMA <ChevronRight size={12} />
              </button>
            </div>
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-6 py-3 text-[10px] font-black text-gray-400 uppercase">UI Element</th>
                  <th className="px-6 py-3 text-[10px] font-black text-gray-400 uppercase">Visualization</th>
                  <th className="px-6 py-3 text-[10px] font-black text-gray-400 uppercase">Backend Source</th>
                  <th className="px-6 py-3 text-[10px] font-black text-gray-400 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="text-xs">
                {[
                  { ui: 'Global SUS Score', viz: 'Gauge Chart', source: 'avg(survey_responses.score)', status: 'LIVE' },
                  { ui: 'Sentiment Matrix', viz: 'Scatter Chart', source: 'interview_analysis.nlp_score', status: 'LIVE' },
                  { ui: 'Task Success', viz: 'Bar Chart', source: 'avg(task_logs.success)', status: 'SYNCING' },
                  { ui: 'Heatmap', viz: 'Treemap', source: 'tag_mentions.count', status: 'LIVE' },
                ].map((row, i) => (
                  <tr key={i} className="border-t border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 font-bold text-palette-dark">{row.ui}</td>
                    <td className="px-6 py-4 text-gray-500">{row.viz}</td>
                    <td className="px-6 py-4 font-mono text-[10px] text-indigo-400">{row.source}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded-full text-[8px] font-black ${
                        row.status === 'LIVE' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                      }`}>
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ResearchDashboard;
