import React from 'react';
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#3b82f6', '#f97316', '#10b981', '#8b5cf6', '#ef4444', '#eab308'];

const DynamicChart = ({ type, data, xKey, yKey }) => {
    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg border border-dashed border-gray-300 text-gray-400">
                データがありません
            </div>
        );
    }

    const CommonTooltip = () => (
        <Tooltip
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
            itemStyle={{ color: '#374151' }}
        />
    );

    const renderChart = () => {
        switch (type) {
            case 'bar':
                return (
                    <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                        <XAxis dataKey={xKey} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                        <CommonTooltip />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        <Bar dataKey={yKey} fill="#3b82f6" radius={[4, 4, 0, 0]} name={yKey} animationDuration={1000} />
                    </BarChart>
                );

            case 'line':
                return (
                    <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                        <XAxis dataKey={xKey} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                        <CommonTooltip />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        <Line type="monotone" dataKey={yKey} stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} animationDuration={1000} name={yKey} />
                    </LineChart>
                );

            case 'pie':
                return (
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey={yKey}
                            nameKey={xKey}
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
                            ))}
                        </Pie>
                        <CommonTooltip />
                        <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ paddingLeft: '20px' }} />
                    </PieChart>
                );

            case 'scatter':
                return (
                    <ScatterChart margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis type="category" dataKey={xKey} name={xKey} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis type="number" dataKey={yKey} name={yKey} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                        <CommonTooltip />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        <Scatter name={yKey} data={data} fill="#f97316" animationDuration={1000} />
                    </ScatterChart>
                );

            default:
                // Fallback to Table
                return (
                    <div className="overflow-auto h-full w-full custom-scrollbar">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    {Object.keys(data[0]).map((key) => (
                                        <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            {key}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {data.map((row, i) => (
                                    <tr key={i} className="hover:bg-gray-50 transition-colors">
                                        {Object.values(row).map((val, j) => (
                                            <td key={j} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                                {val}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                );
        }
    };

    // Tableの場合はResponsiveContainerを使わない（スクロールさせるため）
    if (!type || type === 'table' || !['bar', 'line', 'pie', 'scatter'].includes(type)) {
        return renderChart();
    }

    return (
        <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
        </ResponsiveContainer>
    );
};

export default DynamicChart;
