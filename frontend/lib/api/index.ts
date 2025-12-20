/**
 * Central export point for all API clients
 */

import { riskApi } from './risk-api';
import { logApi } from './log-save-api';

export { riskApi, logApi };
export { riskApi as api };
export default riskApi;
