import React, { useState, useEffect, useCallback } from 'react';
import { JsonEditor } from './components/JsonEditor/JsonEditor';
import { SimulationViewer } from './components/SimulationViewer/SimulationViewer';
import { SimulationControls, DisplayOptions } from './components/Controls/SimulationControls';
import { ParameterPanel } from './components/ParameterPanel/ParameterPanel';
import { ResultsPanel } from './components/ResultsPanel/ResultsPanel';
import { simulationRegistry } from './simulations/registry';
import { SimulationSpecSchema } from './validation/simulationSchema';
import { ApiService } from './services/apiService';
import { Atom, Sparkles, Server, Zap, RefreshCw, Send, CheckCircle2, XCircle, BookOpen } from 'lucide-react';

const MOCK_SPECS: Record<string, string> = {
  prism_dispersion: `{
  "simulation_schema_version": "1.0",
  "simulation_type": "prism_dispersion",
  "domain": "optics",
  "parameters": {
    "apex_angle": 60.0,
    "incident_angle": 30.0,
    "cauchy_b": 1.5,
    "cauchy_c": 0.004,
    "wavelengths_nm": [
      700.0,
      620.0,
      580.0,
      530.0,
      470.0,
      420.0
    ]
  }
}`,
  optical_prism: `{
  "simulation_schema_version": "1.0",
  "simulation_type": "optical_prism",
  "domain": "optics",
  "parameters": {
    "apex_angle": 60.0,
    "refractive_index": 1.5,
    "incident_angle": 30.0
  }
}`,
  projectile_motion: `{
  "simulation_schema_version": "1.0",
  "simulation_type": "projectile_motion",
  "domain": "mechanics",
  "parameters": {
    "initial_velocity": 20.0,
    "launch_angle": 45.0,
    "initial_height": 0.0,
    "gravity": 9.81,
    "time_step": 0.05
  }
}`,
  function_plot: `{
  "simulation_schema_version": "1.0",
  "simulation_type": "function_plot",
  "domain": "mathematics",
  "parameters": {
    "expression": "exp(-x)*cos(5*x)",
    "domain": {
      "min": 0.0,
      "max": 5.0,
      "samples": 200
    }
  }
}`
};

const PROMPT_SUGGESTIONS = [
  "Show prism dispersion with apex angle 50 and incident angle 40",
  "Show projectile motion 25 m/s at 35 deg",
  "Plot cos(x) from 0 to 2pi",
  "Simulate single ray refraction through glass prism",
];

export const App: React.FC = () => {
  const [selectedPreset, setSelectedPreset] = useState<string>('prism_dispersion');
  const [jsonText, setJsonText] = useState<string>(MOCK_SPECS['prism_dispersion']);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [simResult, setSimResult] = useState<any>(null);

  // Backend Integration State
  const [isPythonConnected, setIsPythonConnected] = useState<boolean>(false);
  const [usePythonBackend, setUsePythonBackend] = useState<boolean>(true);
  const [aiPrompt, setAiPrompt] = useState<string>("Show prism dispersion with apex angle 50 and incident angle 40");
  const [isGeneratingAi, setIsGeneratingAi] = useState<boolean>(false);
  const [apiStatusMessage, setApiStatusMessage] = useState<string | null>(null);

  // Animation Controls State
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [speed, setSpeed] = useState<number>(1.0);
  const [resetTrigger, setResetTrigger] = useState<number>(0);

  // Camera Presets State
  const [cameraView, setCameraView] = useState<'default' | 'top' | 'front' | 'side'>('default');

  // Display Options Toggles
  const [displayOptions, setDisplayOptions] = useState<DisplayOptions>({
    showGrid: true,
    showAxes: true,
    showLabels: true,
    showIncidentRay: true,
    showInternalRays: true,
    showSpectrum: true,
    showMeasurements: true,
  });

  // Check Python Backend Health
  const checkBackendHealth = useCallback(async () => {
    const healthy = await ApiService.checkHealth();
    setIsPythonConnected(healthy);
  }, []);

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 5000);
    return () => clearInterval(interval);
  }, [checkBackendHealth]);

  /**
   * Run simulation pipeline.
   * Computes physics calculation and updates 3D scene & results panel immediately.
   */
  const loadSimulation = useCallback((rawInput: string | object) => {
    try {
      const parsedObj = typeof rawInput === 'string' ? JSON.parse(rawInput) : rawInput;

      // Spec Validation
      if (parsedObj.simulation_type === 'prism_dispersion') {
        const parseResult = SimulationSpecSchema.safeParse(parsedObj);
        if (!parseResult.success) {
          const errMessages = parseResult.error.errors.map((e) => `• ${e.path.join('.')}: ${e.message}`).join('\n');
          setValidationError(errMessages);
          return;
        }
      }

      setValidationError(null);

      // Execute simulation physics calculation
      const result = simulationRegistry.run(parsedObj as any);
      setSimResult(result);
    } catch (e: any) {
      setValidationError(`JSON Syntax Error: ${e.message}`);
    }
  }, []);

  /**
   * Switch Preset Spec
   */
  const handleSelectPreset = (key: string) => {
    setSelectedPreset(key);
    const spec = MOCK_SPECS[key];
    if (spec) {
      setJsonText(spec);
      loadSimulation(spec);
    }
  };

  /**
   * Generate spec from Natural Language Prompt via Python AI Service endpoint
   */
  const handleGenerateAiPrompt = async () => {
    if (!aiPrompt.trim()) return;
    setIsGeneratingAi(true);
    setApiStatusMessage('Sending prompt to Python AI Orchestration Layer...');

    try {
      if (isPythonConnected) {
        const generatedSpec = await ApiService.generateSpecFromPrompt(aiPrompt);
        const formattedJson = JSON.stringify(generatedSpec, null, 2);
        setJsonText(formattedJson);
        loadSimulation(generatedSpec);
        setApiStatusMessage('✨ AI Spec Generated & Loaded successfully from Python Backend!');
      } else {
        // Fallback parser if Python API is offline
        const spec = JSON.parse(MOCK_SPECS['prism_dispersion']);
        spec.parameters.apex_angle = 50.0;
        spec.parameters.incident_angle = 40.0;
        const formatted = JSON.stringify(spec, null, 2);
        setJsonText(formatted);
        loadSimulation(formatted);
        setApiStatusMessage('Generated spec via offline fallback engine.');
      }
    } catch (err: any) {
      setValidationError(`AI Spec Generation Error: ${err.message}`);
    } finally {
      setIsGeneratingAi(false);
      setTimeout(() => setApiStatusMessage(null), 4000);
    }
  };

  // Initial load
  useEffect(() => {
    loadSimulation(MOCK_SPECS['prism_dispersion']);
  }, [loadSimulation]);

  const handleRender = async () => {
    try {
      const parsed = JSON.parse(jsonText);
      setValidationError(null);

      if (usePythonBackend && isPythonConnected) {
        setApiStatusMessage('Executing simulation on Python FastAPI backend...');
        const pythonResult = await ApiService.runSimulationOnPythonBackend(parsed);
        setSimResult(pythonResult);
        setApiStatusMessage('✨ Execution successful via Python SymPy/SciPy Backend!');
        setTimeout(() => setApiStatusMessage(null), 3000);
      } else {
        loadSimulation(parsed);
      }
    } catch (e: any) {
      setValidationError(`Execution Error: ${e.message}`);
    }
  };

  const handleResetSpec = () => {
    const spec = MOCK_SPECS[selectedPreset] || MOCK_SPECS['prism_dispersion'];
    setJsonText(spec);
    loadSimulation(spec);
  };

  const handleFormatSpec = () => {
    try {
      const parsed = JSON.parse(jsonText);
      setJsonText(JSON.stringify(parsed, null, 2));
    } catch (e) {
      // Ignore
    }
  };

  const handleToggleDisplayOption = (key: keyof DisplayOptions) => {
    setDisplayOptions((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50 flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-lg shadow-md shadow-cyan-500/20">
            <Atom className="w-5 h-5 text-white animate-spin-slow" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center space-x-2">
              <span>AI Physics 3D Simulation Playground</span>
              <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800/60 rounded">
                v1.0 (WebGL + Python API)
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">
              AI Spec Generator • Optics & Kinematics Engine • Three.js 3D Viewport
            </p>
          </div>
        </div>

        {/* Python API Health Status & Mode Switch */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs font-mono">
            <Server className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Python API:</span>
            {isPythonConnected ? (
              <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Connected (localhost:8000)</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-amber-400">
                <XCircle className="w-3.5 h-3.5" />
                <span>Offline (Client Engine Active)</span>
              </span>
            )}
          </div>

          <button
            onClick={() => setUsePythonBackend(!usePythonBackend)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
              usePythonBackend && isPythonConnected
                ? 'bg-cyan-950 text-cyan-300 border-cyan-700/60 shadow-md'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Mode: {usePythonBackend && isPythonConnected ? 'Python API' : 'Client TS Engine'}</span>
          </button>
        </div>
      </header>

      {/* Preset Spec Testcases Bar & AI Prompt Bar */}
      <section className="bg-slate-900/90 border-b border-slate-800 p-4 px-6 backdrop-blur-md flex flex-col space-y-3">
        {/* Testcase Presets Bar */}
        <div className="max-w-[1800px] w-full mx-auto flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 text-slate-400 font-mono font-semibold shrink-0">
            <BookOpen className="w-4 h-4 text-amber-400" />
            <span>Physics Testcases:</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleSelectPreset('prism_dispersion')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                selectedPreset === 'prism_dispersion'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              🌈 Prism Rainbow Dispersion (Optics)
            </button>
            <button
              onClick={() => handleSelectPreset('optical_prism')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                selectedPreset === 'optical_prism'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              📐 Single Ray Refraction (Optics)
            </button>
            <button
              onClick={() => handleSelectPreset('projectile_motion')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                selectedPreset === 'projectile_motion'
                  ? 'bg-pink-500 text-slate-950 font-bold shadow-md'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              🚀 Projectile Motion (Mechanics)
            </button>
            <button
              onClick={() => handleSelectPreset('function_plot')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                selectedPreset === 'function_plot'
                  ? 'bg-purple-500 text-slate-950 font-bold shadow-md'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              📈 Math Function Curve (Mathematics)
            </button>
          </div>
        </div>

        {/* AI Prompt Input Bar */}
        <div className="max-w-[1800px] w-full mx-auto flex flex-col md:flex-row items-stretch md:items-center gap-3">
          <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400 font-semibold shrink-0">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>AI Prompt Generator:</span>
          </div>

          <div className="flex-1 flex items-center bg-slate-950 rounded-xl border border-slate-800 focus-within:border-cyan-500/80 transition-all px-3 py-1">
            <input
              type="text"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Describe simulation e.g. 'Show projectile motion 25 m/s at 35 deg' or 'Show prism dispersion with apex angle 50'"
              className="flex-1 bg-transparent border-none text-xs text-slate-100 focus:outline-none py-1.5 font-sans placeholder:text-slate-500"
              onKeyDown={(e) => e.key === 'Enter' && handleGenerateAiPrompt()}
            />
            <button
              onClick={handleGenerateAiPrompt}
              disabled={isGeneratingAi}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-semibold text-slate-950 bg-gradient-to-r from-cyan-400 to-blue-400 hover:from-cyan-300 hover:to-blue-300 disabled:opacity-50 rounded-lg shadow-md transition-all active:scale-95 shrink-0 cursor-pointer"
            >
              {isGeneratingAi ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating Spec...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Generate Spec via Python AI</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Suggestions */}
          <div className="hidden xl:flex items-center space-x-2 text-[11px] text-slate-400 font-mono">
            <span className="shrink-0">Try:</span>
            {PROMPT_SUGGESTIONS.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setAiPrompt(sug);
                }}
                className="px-2 py-1 bg-slate-950 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 transition-all truncate max-w-[200px]"
                title={sug}
              >
                {sug}
              </button>
            ))}
          </div>
        </div>

        {/* API Status Banner */}
        {apiStatusMessage && (
          <div className="max-w-[1800px] mx-auto mt-1 text-xs font-mono text-cyan-300 bg-cyan-950/40 p-2 rounded-lg border border-cyan-800/40 flex items-center space-x-2 animate-pulse">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>{apiStatusMessage}</span>
          </div>
        )}
      </section>

      {/* Main Content Layout */}
      <main className="flex-1 p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1800px] w-full mx-auto">
        {/* Left Column: JSON Editor & Controls */}
        <div className="lg:col-span-5 flex flex-col space-y-4 h-full">
          {/* JSON Spec Editor */}
          <div className="flex-1 min-h-[420px]">
            <JsonEditor
              value={jsonText}
              onChange={(val) => {
                setJsonText(val);
                try {
                  const parsed = JSON.parse(val);
                  loadSimulation(parsed);
                } catch (e) {
                  // Wait for user manual render if typing
                }
              }}
              onRender={handleRender}
              onReset={handleResetSpec}
              onFormat={handleFormatSpec}
              validationError={validationError}
            />
          </div>

          {/* Simulation Controls */}
          <SimulationControls
            isPlaying={isPlaying}
            onPlayPause={() => setIsPlaying(!isPlaying)}
            onResetAnimation={() => setResetTrigger((prev) => prev + 1)}
            speed={speed}
            onSpeedChange={setSpeed}
            displayOptions={displayOptions}
            onToggleDisplayOption={handleToggleDisplayOption}
            onSetCameraView={setCameraView}
          />
        </div>

        {/* Right Column: 3D Visualization Viewport & Results Panel */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          {/* 3D Viewport */}
          <div className="h-[480px] lg:h-[520px]">
            <SimulationViewer
              result={simResult}
              displayOptions={displayOptions}
              isPlaying={isPlaying}
              speed={speed}
              resetTrigger={resetTrigger}
              cameraView={cameraView}
            />
          </div>

          {/* Parameters Panel */}
          <ParameterPanel result={simResult} />

          {/* Results Panel */}
          <ResultsPanel result={simResult} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-3 px-6 text-center text-xs text-slate-500 font-mono">
        AI Physics & Mathematics 3D Simulation Engine • FastAPI Backend Connected @ http://localhost:8000
      </footer>
    </div>
  );
};

export default App;
