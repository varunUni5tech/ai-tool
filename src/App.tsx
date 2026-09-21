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
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Premium Glassmorphic Navigation Bar */}
      <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-2xl sticky top-0 z-50 flex items-center justify-between px-6 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 rounded-xl shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400/30">
            <Atom className="w-5 h-5 text-white animate-spin-slow" />
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-tight text-white flex items-center space-x-2">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyan-400">
                Quantum Optics & Motion Lab
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950/80 text-cyan-400 border border-cyan-700/60 rounded-full shadow-inner">
                3D WebGL Engine
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">
              SymPy Optics Math • SciPy ODE Solver • Three.js Spectral Renderer
            </p>
          </div>
        </div>

        {/* Python API Health Status & Mode Toggle */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-900/90 px-3.5 py-1.5 rounded-xl border border-slate-800 text-xs font-mono shadow-inner">
            <Server className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Python API:</span>
            {isPythonConnected ? (
              <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Connected</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-amber-400">
                <XCircle className="w-3.5 h-3.5" />
                <span>Client Engine</span>
              </span>
            )}
          </div>

          <button
            onClick={() => setUsePythonBackend(!usePythonBackend)}
            className={`flex items-center space-x-2 px-3.5 py-1.5 text-xs font-semibold rounded-xl border transition-all cursor-pointer ${
              usePythonBackend && isPythonConnected
                ? 'bg-gradient-to-r from-cyan-950 to-blue-950 text-cyan-300 border-cyan-600/60 shadow-lg shadow-cyan-950/50'
                : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Mode: {usePythonBackend && isPythonConnected ? 'Python FastAPI' : 'Client JS Engine'}</span>
          </button>
        </div>
      </header>

      {/* AI Prompt Generator Textarea Section */}
      <section className="bg-slate-900/60 border-b border-slate-800/80 px-6 py-4 backdrop-blur-xl">
        <div className="max-w-[1900px] w-full mx-auto flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400 font-semibold">
              <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
              <span>Enter Natural Language Physics Prompt:</span>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              Type any simulation description below & click Generate Spec
            </span>
          </div>

          <div className="flex flex-col md:flex-row items-stretch gap-3">
            <div className="flex-1 relative bg-slate-950/90 rounded-xl border border-slate-800 focus-within:border-cyan-500/80 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all p-3 shadow-inner">
              <textarea
                rows={3}
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Type your physics or math simulation requirement here... (e.g. 'Show prism dispersion with apex angle 50 and incident angle 40', 'Simulate projectile motion at 30 m/s and 45 degrees angle', or 'Plot cos(x) from 0 to 2pi')"
                className="w-full bg-transparent border-none text-xs text-slate-100 focus:outline-none font-sans placeholder:text-slate-500 resize-none leading-relaxed"
              />
            </div>

            <button
              onClick={handleGenerateAiPrompt}
              disabled={isGeneratingAi}
              className="flex items-center justify-center space-x-2 px-6 py-4 text-xs font-bold text-slate-950 bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 disabled:opacity-50 rounded-xl shadow-lg shadow-cyan-500/20 transition-all active:scale-95 shrink-0 cursor-pointer md:w-56"
            >
              {isGeneratingAi ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Generating Spec...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Generate Spec via Python AI</span>
                </>
              )}
            </button>
          </div>
        </div>

          {/* Quick Prompt Suggestions */}
          <div className="flex flex-wrap items-center space-x-2 text-[11px] text-slate-400 font-mono">
            <span className="shrink-0 text-amber-400 font-semibold">Try Prompts:</span>
            {PROMPT_SUGGESTIONS.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => setAiPrompt(sug)}
                className="px-2.5 py-0.5 bg-slate-950 hover:bg-slate-800 text-slate-300 rounded-lg border border-slate-800 hover:border-cyan-700/50 transition-all cursor-pointer truncate max-w-[220px]"
                title={sug}
              >
                {sug}
              </button>
            ))}
          </div>

        {/* API Notification Banner */}
        {apiStatusMessage && (
          <div className="max-w-[1900px] mx-auto mt-2 text-xs font-mono text-cyan-300 bg-cyan-950/60 p-2 rounded-xl border border-cyan-700/50 flex items-center space-x-2 animate-pulse shadow-lg">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>{apiStatusMessage}</span>
          </div>
        )}
      </section>

      {/* Main Workspace Layout */}
      <main className="flex-1 p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1900px] w-full mx-auto">
        {/* Left Column: Monaco JSON Spec Editor & Physics Controls */}
        <div className="lg:col-span-5 flex flex-col space-y-4">
          <div className="h-[480px]">
            <JsonEditor
              value={jsonText}
              onChange={(val) => {
                setJsonText(val);
                try {
                  const parsed = JSON.parse(val);
                  loadSimulation(parsed);
                } catch (e) {
                  // Wait for manual trigger
                }
              }}
              onRender={handleRender}
              onReset={handleResetSpec}
              onFormat={handleFormatSpec}
              validationError={validationError}
            />
          </div>

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

        {/* Right Column: 3D WebGL Canvas & Output Results Panels */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          {/* Main 3D Viewport */}
          <div className="h-[520px] rounded-2xl overflow-hidden shadow-2xl border border-slate-800">
            <SimulationViewer
              result={simResult}
              displayOptions={displayOptions}
              isPlaying={isPlaying}
              speed={speed}
              resetTrigger={resetTrigger}
              cameraView={cameraView}
            />
          </div>

          {/* Physics Parameters Card */}
          <ParameterPanel result={simResult} />

          {/* Computed Physics Calculations Summary */}
          <ResultsPanel result={simResult} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 bg-slate-950 py-3.5 px-6 text-center text-xs text-slate-500 font-mono">
        AI Mathematical & Physics 3D Simulation Platform • FastAPI Server Running @ http://localhost:8000
      </footer>
    </div>
  );
};

export default App;
