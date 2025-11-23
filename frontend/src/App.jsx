import React, { useState, useRef } from 'react';
import { Send, Upload, FileText, Activity } from 'lucide-react';
import DynamicChart from './components/DynamicChart';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const Dashboard = () => {
  const [messages, setMessages] = useState([
    { type: 'ai', text: 'こんにちは。売上データの分析を開始しますか？ CSVファイルをアップロードするか、指示を入力してください。' }
  ]);
  const [input, setInput] = useState('');
  const [chartConfig, setChartConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setMessages(prev => [...prev, { type: 'user', text: `ファイルをアップロード中: ${file.name}` }]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();

      // Initial view: Daily Sales Bar Chart
      const formattedData = result.data.daily_analysis.map(item => ({
        date: item.日付,
        sales: item.total_sales,
        trend: Math.round(item.avg_trend),
        event: item.has_event === 1 ? 'Event' : null
      }));

      setChartConfig({
        type: 'bar',
        data: formattedData,
        x_key: 'date',
        y_key: 'sales',
        summary: 'データ分析が完了しました。イベント日やトレンドスコアとの相関をご確認ください。'
      });

      setMessages(prev => [...prev,
      { type: 'ai', text: 'アップロード完了。初期分析結果を表示します。何か質問はありますか？（例：「雨の日の売上傾向は？」）' }
      ]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { type: 'ai', text: 'エラーが発生しました。' }]);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!input.trim()) return;
    const userText = input;
    setMessages(prev => [...prev, { type: 'user', text: userText }]);
    setInput('');
    setLoading(true);

    try {
      // Use the new /api/chat_analyze endpoint with query payload
      const response = await fetch('http://localhost:8000/api/chat_analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userText }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Analysis failed');
      }

      const result = await response.json();

      if (result.error) {
        throw new Error(result.error);
      }

      setChartConfig({
        type: result.chartType,
        data: result.data,
        x_key: result.xKey,
        y_key: result.yKey,
        summary: result.answer
      });

      setMessages(prev => [...prev, { type: 'ai', text: result.answer }]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { type: 'ai', text: `申し訳ありません。分析中にエラーが発生しました: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
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
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".csv"
              className="hidden"
            />
            <button
              onClick={handleUploadClick}
              className="flex-1 flex items-center justify-center gap-2 p-2 bg-gray-100 rounded hover:bg-gray-200 text-sm text-gray-600"
            >
              <Upload size={16} /> CSV Upload
            </button>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              className="flex-1 border border-gray-300 rounded p-2 focus:outline-none focus:border-blue-500"
              placeholder="例: 雨の日の売上傾向を教えて..."
            />
            <button onClick={handleAnalyze} className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Right: Visualization Panel */}
      <div className="w-2/3 p-6 overflow-y-auto">
        <div className="bg-white p-6 rounded-xl shadow-sm mb-6 h-[600px] flex flex-col relative">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Activity className="text-blue-500" />
            Real-time Analysis Dashboard
          </h2>

          {loading && (
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10 rounded-xl">
              <div className="flex flex-col items-center gap-2">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                <span className="text-blue-600 font-medium">AIが分析中...</span>
              </div>
            </div>
          )}

          {chartConfig ? (
            <div className="flex-1 w-full min-h-0">
              <DynamicChart
                type={chartConfig.type}
                data={chartConfig.data}
                xKey={chartConfig.x_key}
                yKey={chartConfig.y_key}
              />
              <div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm text-yellow-800">
                <strong>💡 AI Insight:</strong> {chartConfig.summary}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-50 rounded border border-dashed border-gray-300 text-gray-400">
              ここに分析結果のグラフが表示されます
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
