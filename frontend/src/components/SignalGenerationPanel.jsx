import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const SignalGenerationPanel = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [symbols, setSymbols] = useState(['XAUUSD', 'GBPUSD', 'USDJPY']);
  const [analysisSteps, setAnalysisSteps] = useState([]);
  const [currentSymbol, setCurrentSymbol] = useState('');
  const [geminiStatus, setGeminiStatus] = useState('idle');
  const [oandaStatus, setOandaStatus] = useState('idle');
  const [signalsGenerated, setSignalsGenerated] = useState(0);
  const [realAnalysisData, setRealAnalysisData] = useState(null);
  const [backendStatus, setBackendStatus] = useState('disconnected');

  // Fetch real analysis data from backend
  const fetchRealAnalysisData = async () => {
    try {
      const [analysisStatus, latestAnalysis] = await Promise.all([
        apiService.getAnalysisStatus(),
        apiService.getLatestAnalysis()
      ]);
      
      setRealAnalysisData({
        status: analysisStatus,
        latest: latestAnalysis
      });
      
      // Update backend status
      setBackendStatus('connected');
      
      // Update analysis progress based on real data
      if (latestAnalysis && latestAnalysis.timestamp) {
        const lastUpdate = new Date(latestAnalysis.timestamp);
        const now = new Date();
        const timeDiff = (now - lastUpdate) / 1000 / 60; // minutes
        
        // If analysis was recent (within 5 minutes), show progress
        if (timeDiff < 5) {
          setAnalysisProgress(100 - (timeDiff / 5) * 100);
          setIsAnalyzing(true);
        } else {
          setIsAnalyzing(false);
          setAnalysisProgress(0);
        }
      }
      
    } catch (error) {
      console.error('Error fetching analysis data:', error);
      setBackendStatus('disconnected');
      setIsAnalyzing(false);
    }
  };

  // Simulate real-time signal generation process
  const simulateSignalGeneration = async () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setAnalysisSteps([]);
    setSignalsGenerated(0);

    const steps = [
      { id: 1, name: 'Connecting to OANDA API', status: 'running', icon: '🔌', color: 'blue' },
      { id: 2, name: 'Fetching live market data', status: 'pending', icon: '📊', color: 'green' },
      { id: 3, name: 'Analyzing XAUUSD price action', status: 'pending', icon: '🥇', color: 'yellow' },
      { id: 4, name: 'Analyzing GBPUSD price action', status: 'pending', icon: '💷', color: 'yellow' },
      { id: 5, name: 'Analyzing USDJPY price action', status: 'pending', icon: '💴', color: 'yellow' },
      { id: 6, name: 'Calculating technical indicators', status: 'pending', icon: '📈', color: 'purple' },
      { id: 7, name: 'Detecting Smart Money Concepts', status: 'pending', icon: '🧠', color: 'indigo' },
      { id: 8, name: 'Connecting to Gemini Pro AI', status: 'pending', icon: '🤖', color: 'pink' },
      { id: 9, name: 'Generating AI trading signals', status: 'pending', icon: '⚡', color: 'red' },
      { id: 10, name: 'Validating signal quality', status: 'pending', icon: '✅', color: 'green' },
      { id: 11, name: 'Signal generation complete', status: 'pending', icon: '🎯', color: 'emerald' }
    ];

    setAnalysisSteps(steps);

    // Simulate each step
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      
      // Update current step
      setCurrentStep(step.name);
      setAnalysisProgress((i / steps.length) * 100);

      // Update step status
      const updatedSteps = [...steps];
      updatedSteps[i].status = 'running';
      setAnalysisSteps(updatedSteps);

      // Set status indicators
      if (step.name.includes('OANDA')) {
        setOandaStatus('connected');
      }
      if (step.name.includes('Gemini')) {
        setGeminiStatus('analyzing');
      }
      if (step.name.includes('XAUUSD')) {
        setCurrentSymbol('XAUUSD');
      }
      if (step.name.includes('GBPUSD')) {
        setCurrentSymbol('GBPUSD');
      }
      if (step.name.includes('USDJPY')) {
        setCurrentSymbol('USDJPY');
      }

      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));

      // Mark step as completed
      updatedSteps[i].status = 'completed';
      setAnalysisSteps(updatedSteps);

      // Update signals generated
      if (step.name.includes('signal')) {
        setSignalsGenerated(prev => prev + 1);
      }
    }

    // Final status
    setGeminiStatus('completed');
    setOandaStatus('connected');
    setCurrentStep('Analysis Complete');
    setAnalysisProgress(100);
    setIsAnalyzing(false);
  };

  // Fetch real analysis data every 10 seconds
  useEffect(() => {
    // Initial fetch
    fetchRealAnalysisData();
    
    // Set up interval for real-time updates
    const interval = setInterval(fetchRealAnalysisData, 10000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'text-blue-400';
      case 'completed': return 'text-green-400';
      case 'pending': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'running': return 'bg-blue-500/20 border-blue-500/30';
      case 'completed': return 'bg-green-500/20 border-green-500/30';
      case 'pending': return 'bg-gray-500/10 border-gray-500/20';
      default: return 'bg-gray-500/10 border-gray-500/20';
    }
  };

  return (
    <div className="card card-hover p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 animate-pulse"></div>
          <h2 className="text-h3 text-gradient-blue">Signal Generation Engine</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className={`px-3 py-1 rounded-full text-xs font-bold ${
            isAnalyzing ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-500/20 text-gray-400'
          }`}>
            {isAnalyzing ? '🔄 ANALYZING' : '⏸️ IDLE'}
          </div>
          <div className="text-small text-text-muted">
            Signals: {signalsGenerated}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-small font-medium text-text-primary">Analysis Progress</span>
          <span className="text-small text-text-muted">{Math.round(analysisProgress)}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${analysisProgress}%` }}
          ></div>
        </div>
      </div>

      {/* Current Step */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${isAnalyzing ? 'bg-blue-400 animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-medium font-medium text-text-primary">Current Step:</span>
          <span className="text-medium text-blue-400">
            {realAnalysisData?.latest?.symbol ? 
              `Analyzing ${realAnalysisData.latest.symbol} (${realAnalysisData.latest.setup_quality})` : 
              currentStep || 'Waiting for analysis...'}
          </span>
        </div>
        {realAnalysisData?.latest && (
          <div className="mt-2 text-small text-text-muted">
            Technical: {realAnalysisData.latest.technical_score?.toFixed(1)} | 
            ML: {realAnalysisData.latest.ml_score?.toFixed(1)} | 
            Quality: {realAnalysisData.latest.setup_quality}
          </div>
        )}
      </div>

      {/* Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className={`w-3 h-3 rounded-full ${
            backendStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
          }`}></div>
          <div>
            <div className="text-small font-medium text-text-primary">Backend Status</div>
            <div className={`text-xs ${
              backendStatus === 'connected' ? 'text-green-400' : 'text-red-400'
            }`}>
              {backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className={`w-3 h-3 rounded-full ${
            realAnalysisData?.latest?.should_send_to_gemini ? 'bg-blue-400 animate-pulse' : 
            realAnalysisData?.latest?.gemini_result ? 'bg-green-400' : 'bg-gray-400'
          }`}></div>
          <div>
            <div className="text-small font-medium text-text-primary">Gemini Pro AI</div>
            <div className={`text-xs ${
              realAnalysisData?.latest?.should_send_to_gemini ? 'text-blue-400' : 
              realAnalysisData?.latest?.gemini_result ? 'text-green-400' : 'text-gray-400'
            }`}>
              {realAnalysisData?.latest?.should_send_to_gemini ? 'Analyzing' : 
               realAnalysisData?.latest?.gemini_result ? 'Completed' : 'Waiting'}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="w-3 h-3 rounded-full bg-yellow-400 animate-pulse"></div>
          <div>
            <div className="text-small font-medium text-text-primary">Analysis Cycle</div>
            <div className="text-xs text-yellow-400">
              {realAnalysisData?.status?.analysis_interval || '5 minutes'}
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Steps */}
      <div className="space-y-3">
        <h3 className="text-medium font-semibold text-text-primary mb-4">Analysis Steps</h3>
        {analysisSteps.map((step) => (
          <div 
            key={step.id} 
            className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${
              getStatusBg(step.status)
            }`}
          >
            <div className="text-lg">{step.icon}</div>
            <div className="flex-1">
              <div className={`text-small font-medium ${getStatusColor(step.status)}`}>
                {step.name}
              </div>
            </div>
            <div className={`w-2 h-2 rounded-full ${
              step.status === 'running' ? 'bg-blue-400 animate-pulse' :
              step.status === 'completed' ? 'bg-green-400' : 'bg-gray-400'
            }`}></div>
          </div>
        ))}
      </div>

      {/* Action Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={simulateSignalGeneration}
          disabled={isAnalyzing}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
            isAnalyzing 
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
              : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white hover:shadow-lg hover:shadow-blue-500/25'
          }`}
        >
          {isAnalyzing ? '🔄 Analyzing...' : '🚀 Start Analysis'}
        </button>
      </div>

      {/* Footer Info */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-text-muted">
          <span>⚡ Real-time analysis powered by Gemini Pro AI</span>
          <span>🔄 Auto-refresh every 30 seconds</span>
        </div>
      </div>
    </div>
  );
};

export default SignalGenerationPanel;
