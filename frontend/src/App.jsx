import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts';
import { Send, Upload, FileText, Activity } from 'lucide-react';

const Dashboard = () => {
  const [messages, setMessages] = useState([
    { type: 'ai', text: 'こんにちは。売上データの分析を開始しますか？ CSVファイルをアップロードするか、指示を入力してください。' }
  ]);
  const [input, setInput] = useState('');
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  // デモ用データロード処理 (本来はAPIから取得)
  const handleAnalyze = () => {
    setLoading(true);
    // バックエンドAPIコールのシミュレーション
    setTimeout(() => {
      setLoading(false);
      setChartData([
        { date: '9/01', sales: 450000, trend: 42, event: null },
        { date: '9/02', sales: 420000, trend: 43, event: null },
        { date: '9/14', sales: 850000, trend: 60, event: 'Concert' }, // Event spike
        { date: '9/21', sales: 920000, trend: 75, event: 'Soccer' },  // Event spike
        { date: '9/30', sales: 500000, trend: 88, event: null },
      ]);
      setMessages(prev => [...prev,
      { type: 'ai', text: '分析が完了しました。9/14と9/21のイベント開催日に顕著な売上増が見られます。右側のグラフをご確認ください。' }
      ]);
    }, 1500);
  };

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { type: 'user', text: input }]);
    setInput('');
    if (input.includes('分析') || input.includes('グラフ')) {
      handleAnalyze();
    } else {
      setTimeout(() => setMessages(prev => [...prev, { type: 'ai', text: '承知しました。その観点でデータを集計します（デモ）。' }]), 1000);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Left: Chat Panel */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200 bg-blue-600 text-white flex items-center gap-2">
          <Activity size={20} />
          <h1 className="font-bold text-lg">AI Data Analyst</h1>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-3 rounded-lg text-sm ${msg.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800'
                }`}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && <div className="text-gray-400 text-sm animate-pulse">AIが分析中...</div>}
        </div>
        <div className="p-4 border-t border-gray-200">
          <div className="flex gap-2 mb-2">
            <button className="flex-1 flex items-center justify-center gap-2 p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm text-gray-600">
              <Upload size={16} /> CSV Upload
            </button>
            <button className="flex-1 flex items-center justify-center gap-2 p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm text-gray-600">
              <FileText size={16} /> PDF Report
            </button>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 border border-gray-300 rounded p-2 focus:outline-none focus:border-blue-500"
              placeholder="例: 雨の日の売上傾向を教えて..."
            />
            <button onClick={handleSend} className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Right: Visualization Panel */}
      <div className="w-2/3 p-6 overflow-y-auto">
        <div className="bg-white p-6 rounded-xl shadow-sm mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Activity className="text-blue-500" />
            Real-time Analysis Dashboard
          </h2>

          {chartData ? (
            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.5} />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" label={{ value: 'Sales (JPY)', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Trend Score', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="sales" fill="#3b82f6" name="Sales" radius={[4, 4, 0, 0]} />
                  <Line yAxisId="right" type="monotone" dataKey="trend" stroke="#f97316" name="Trend Score" strokeWidth={2} />
                </ComposedChart>
              </ResponsiveContainer>
              <div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm text-yellow-800">
                <strong>💡 AI Insight:</strong> イベント開催日（9/14, 9/21）の売上が平均の2倍以上に達しています。次回のイベント日に向けて在庫を20%増やすことを推奨します。
              </div>
            </div>
          ) : (
            <div className="h-[400px] flex items-center justify-center bg-gray-50 rounded border border-dashed border-gray-300 text-gray-400">
              ここに分析結果のグラフが表示されます
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
