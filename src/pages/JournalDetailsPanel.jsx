import React from 'react';

const JournalDetailsPanel = ({ trade, onChange, onAttachScreenshot }) => {
  if (!trade) return (
    <div className="text-gray-400 text-sm">Select a trade to edit notes, tags, emotion, and attach a screenshot.</div>
  );

  return (
    <div className="space-y-3">
      <div>
        <label className="text-xs text-gray-400">Notes</label>
        <textarea
          className="w-full mt-1 bg-[#1E2139] border border-[#2A2F45] rounded p-2 text-sm"
          rows={3}
          value={trade.notes || ''}
          onChange={(e) => onChange({ ...trade, notes: e.target.value })}
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-400">Tags (comma separated)</label>
          <input
            className="w-full mt-1 bg-[#1E2139] border border-[#2A2F45] rounded p-2 text-sm"
            value={trade.tags || ''}
            onChange={(e) => onChange({ ...trade, tags: e.target.value })}
          />
        </div>
        <div>
          <label className="text-xs text-gray-400">Emotion</label>
          <select
            className="w-full mt-1 bg-[#1E2139] border border-[#2A2F45] rounded p-2 text-sm"
            value={trade.emotion || 'Neutral'}
            onChange={(e) => onChange({ ...trade, emotion: e.target.value })}
          >
            <option>Neutral</option>
            <option>Confident</option>
            <option>Anxious</option>
            <option>Fearful</option>
            <option>Greedy</option>
          </select>
        </div>
      </div>
      <div>
        <label className="text-xs text-gray-400">Screenshot</label>
        <div className="mt-1 flex items-center space-x-3">
          <input type="file" accept="image/*" onChange={(e) => onAttachScreenshot(e.target.files?.[0])} />
          {trade.screenshot && (
            <img src={trade.screenshot} alt="screenshot" className="h-16 w-28 object-cover rounded border border-[#2A2F45]" />
          )}
        </div>
      </div>
    </div>
  );
};

export default JournalDetailsPanel;






