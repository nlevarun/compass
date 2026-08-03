/**
 * Compass SDK Configuration
 */

export interface CompassConfig {
  /** Your Compass API key */
  apiKey: string;

  /** Base URL of the Compass API (default: http://localhost:8000) */
  baseUrl?: string;

  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;

  /** Custom headers to include in all requests */
  headers?: Record<string, string>;
}

export const DEFAULT_CONFIG: Partial<CompassConfig> = {
  baseUrl: 'http://localhost:8000',
  timeout: 30000,
  headers: {},
};
