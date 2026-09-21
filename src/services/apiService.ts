/**
 * API Client Service connecting React Frontend to Python FastAPI Backend.
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface PromptRequest {
  prompt: string;
  provider?: string;
}

export class ApiService {
  /**
   * Check if Python FastAPI backend is online.
   */
  static async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        const data = await res.json();
        return data.status === 'healthy';
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  /**
   * Send Natural Language prompt to Python AI orchestrator -> get validated simulation spec.
   */
  static async generateSpecFromPrompt(prompt: string, provider: string = 'mock'): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/simulations/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, provider }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate simulation spec from AI.');
    }

    return await res.json();
  }

  /**
   * Execute simulation spec on Python backend engine -> get computed physics results.
   */
  static async runSimulationOnPythonBackend(spec: any): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/simulations/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Python engine execution failed.');
    }

    return await res.json();
  }
}
