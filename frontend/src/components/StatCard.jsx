function StatCard({ title, value, subtitle }) {
  return (
    <div className="bg-white shadow rounded p-6 flex flex-col">
      <h3 className="text-gray-500 text-sm">{title}</h3>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      {subtitle && <span className="text-gray-400 text-xs">{subtitle}</span>}
    </div>
  );
}

export default StatCard;
