import React from 'react';
import { Image, Tag, Heart, Brain, TrendingUp, Target, DollarSign, Clock } from 'lucide-react';

const JournalDetailsPanel = ({ trade, onChange, onAttachScreenshot }) => {
  if (!trade) return (
    <div className="text-gray-400 text-sm p-8 text-center">
      <Brain size={48} className="mx-auto mb-4 text-gray-600" />
      <p>Select a trade from the table to view details and add journal notes</p>
    </div>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      {/* Left Column - Trade Summary */}
      <div className="space-y-4">
        
        {/* Trade Overview Card */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <Target size={16} className="mr-2" />
            Trade Overview
          </h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-gray-400 text-xs mb-1">Symbol</div>
              <div className="font-medium text-white">{trade.symbol}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Direction</div>
              <div className={`font-medium ${trade.type === 'BUY' ? 'text-[#7FFF00]' : 'text-[#FF3366]'}`}>
                {trade.type}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Entry Price</div>
              <div className="font-mono text-white">{trade.entry}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Exit Price</div>
              <div className="font-mono text-white">{trade.exit}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Stop Loss</div>
              <div className="font-mono text-white">{trade.sl}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Take Profit</div>
              <div className="font-mono text-white">{trade.tp}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Lot Size</div>
              <div className="font-medium text-white">{trade.lots}</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Duration</div>
              <div className="font-medium text-white">{trade.duration}</div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <TrendingUp size={16} className="mr-2" />
            Performance Metrics
          </h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-gray-400 text-xs mb-1">Profit/Loss</div>
              <div className={`font-bold text-lg ${Number(trade.pl) >= 0 ? 'text-[#7FFF00]' : 'text-[#FF3366]'}`}>
                ${trade.pl}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Pips Gained</div>
              <div className={`font-bold text-lg ${Number(trade.pips) >= 0 ? 'text-[#7FFF00]' : 'text-[#FF3366]'}`}>
                {trade.pips}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">R-Multiple</div>
              <div className="font-medium text-white">{trade.r}R</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">MAE (Max Adverse)</div>
              <div className="font-medium text-[#FF3366]">{trade.mae} pips</div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Efficiency</div>
              <div className="flex items-center space-x-2">
                <div className="w-20 h-2 bg-[#0F1419] rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-[#7FFF00]" 
                    style={{ width: `${trade.efficiency || 0}%` }}
                  ></div>
                </div>
                <span className="text-white font-medium text-xs">{trade.efficiency}%</span>
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-xs mb-1">Setup</div>
              <div className="text-white font-medium text-xs px-2 py-1 bg-[#0F1419] rounded border border-[#7FFF00]/30 inline-block">
                {trade.setup}
              </div>
            </div>
          </div>
        </div>

        {/* Trade Times */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <Clock size={16} className="mr-2" />
            Timing
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Entry Time</span>
              <span className="text-white font-mono">{trade.openTime}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Exit Time</span>
              <span className="text-white font-mono">{trade.closeTime}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Duration</span>
              <span className="text-[#7FFF00] font-medium">{trade.duration}</span>
            </div>
          </div>
        </div>

      </div>

      {/* Right Column - Journal Entry */}
      <div className="space-y-4">
        
        {/* Trade Notes */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <Brain size={16} className="mr-2" />
            Journal Notes
          </h4>
          <textarea
            className="w-full mt-2 bg-[#0F1419] border border-[#2A2F45] rounded-lg p-3 text-sm text-white focus:border-[#7FFF00] focus:outline-none transition-colors"
            rows={6}
            placeholder="What was your thesis? What went well? What could be improved?"
            value={trade.notes || ''}
            onChange={(e) => onChange({ ...trade, notes: e.target.value })}
          />
        </div>

        {/* Psychology & Emotion */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <Heart size={16} className="mr-2" />
            Psychology & Emotion
          </h4>
          <div>
            <label className="text-xs text-gray-400 mb-2 block">How did you feel during this trade?</label>
            <select
              className="w-full bg-[#0F1419] border border-[#2A2F45] rounded-lg p-2 text-sm text-white focus:border-[#7FFF00] focus:outline-none transition-colors"
              value={trade.emotion || 'Neutral'}
              onChange={(e) => onChange({ ...trade, emotion: e.target.value })}
            >
              <option value="Confident">😎 Confident - In control</option>
              <option value="Neutral">😐 Neutral - Calm & focused</option>
              <option value="Anxious">😰 Anxious - Worried</option>
              <option value="Fearful">😨 Fearful - Scared</option>
              <option value="Greedy">🤑 Greedy - Overconfident</option>
              <option value="FOMO">😱 FOMO - Fear of missing out</option>
              <option value="Revenge">😤 Revenge - Trying to recover</option>
            </select>
          </div>
        </div>

        {/* Tags */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <Tag size={16} className="mr-2" />
            Tags & Categories
          </h4>
          <input
            className="w-full bg-[#0F1419] border border-[#2A2F45] rounded-lg p-2 text-sm text-white focus:border-[#7FFF00] focus:outline-none transition-colors"
            placeholder="e.g., breakout, earnings winner, news event..."
            value={trade.tags || ''}
            onChange={(e) => onChange({ ...trade, tags: e.target.value })}
          />
          {trade.tags && (
            <div className="flex flex-wrap gap-2 mt-3">
              {trade.tags.split(',').map((tag, idx) => (
                <span 
                  key={idx} 
                  className="px-3 py-1 bg-[#0F1419] border border-[#7FFF00]/30 rounded-full text-xs text-[#7FFF00]"
                >
                  {tag.trim()}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Chart Screenshot */}
        <div className="bg-[#1E2432] border border-[#2A2F45] rounded-xl p-4">
          <h4 className="text-sm font-semibold text-[#7FFF00] mb-3 flex items-center">
            <Image size={16} className="mr-2" />
            Chart Screenshot
          </h4>
          <div className="mt-2">
            <label className="cursor-pointer">
              <div className="border-2 border-dashed border-[#2A2F45] hover:border-[#7FFF00] rounded-lg p-6 text-center transition-colors">
                <Image size={32} className="mx-auto mb-2 text-gray-500" />
                <div className="text-sm text-gray-400">Click to upload chart image</div>
                <div className="text-xs text-gray-500 mt-1">PNG, JPG up to 10MB</div>
              </div>
              <input 
                type="file" 
                accept="image/*" 
                className="hidden"
                onChange={(e) => onAttachScreenshot(e.target.files?.[0])} 
              />
            </label>
            {trade.screenshot && (
              <div className="mt-4">
                <img 
                  src={trade.screenshot} 
                  alt="Trade chart" 
                  className="w-full rounded-lg border border-[#2A2F45]" 
                />
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default JournalDetailsPanel;







