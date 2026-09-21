import React from 'react';
import Editor from '@monaco-editor/react';
import { Play, RotateCcw, AlignLeft, AlertCircle, CheckCircle2 } from 'lucide-react';

interface JsonEditorProps {
  value: string;
  onChange: (value: string) => void;
  onRender: () => void;
  onReset: () => void;
  onFormat: () => void;
  validationError: string | null;
}

export const JsonEditor: React.FC<JsonEditorProps> = ({
  value,
  onChange,
  onRender,
  onReset,
  onFormat,
  validationError,
}) => {
  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      {/* Editor Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-950/80 border-b border-slate-800 backdrop-blur-md">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-cyan-500/80 animate-pulse" />
          <span className="text-xs font-mono font-semibold tracking-wider text-slate-300 uppercase">
            Simulation JSON Spec
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={onFormat}
            className="flex items-center space-x-1 px-2.5 py-1 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-all"
            title="Format JSON"
          >
            <AlignLeft className="w-3.5 h-3.5" />
            <span>Format</span>
          </button>
          <button
            onClick={onReset}
            className="flex items-center space-x-1 px-2.5 py-1 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-all"
            title="Reset to Initial JSON Spec"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
          <button
            onClick={onRender}
            className="flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-lg shadow-md transition-all active:scale-95"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Render</span>
          </button>
        </div>
      </div>

      {/* Editor Main */}
      <div className="flex-1 relative min-h-[280px]">
        <Editor
          height="100%"
          defaultLanguage="json"
          theme="vs-dark"
          value={value}
          onChange={(val) => onChange(val || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            fontFamily: "'JetBrains Mono', monospace",
            formatOnPaste: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            lineNumbersMinChars: 3,
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>

      {/* Error / Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/90 text-xs">
        {validationError ? (
          <div className="flex items-start space-x-2 text-rose-400 bg-rose-950/40 p-2.5 rounded-lg border border-rose-900/50">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div className="font-mono text-xs overflow-x-auto whitespace-pre-wrap">
              {validationError}
            </div>
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-emerald-400 bg-emerald-950/30 p-2 rounded-lg border border-emerald-900/30">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="font-medium">Spec Validated & Rendered</span>
          </div>
        )}
      </div>
    </div>
  );
};
