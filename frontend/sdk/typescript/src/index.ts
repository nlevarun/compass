/**
 * Compass TypeScript SDK
 *
 * Official TypeScript/JavaScript client for the Compass Customer Feedback Intelligence Platform API.
 *
 * @example
 * ```typescript
 * import { CompassClient } from 'compass-sdk';
 *
 * const client = new CompassClient({
 *   apiKey: 'your-api-key',
 *   baseUrl: 'http://localhost:8000'
 * });
 *
 * const feedback = await client.feedback.list({ limit: 10 });
 * console.log(`Found ${feedback.data.length} feedback items`);
 * ```
 */

export { CompassClient } from './client';
export * from './types';
export * from './errors';
export { CompassConfig } from './config';
