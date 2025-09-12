import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function ChartCard({ title, data, dataKey }) {
  return (
    <div className="bg-white shadow rounded p-6">
      <h3 className="text-gray-700 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={dataKey} stroke="#3b82f6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ChartCard;
