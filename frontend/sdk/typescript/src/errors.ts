/**
 * Compass SDK Errors
 */

export class CompassAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'CompassAPIError';
    Object.setPrototypeOf(this, CompassAPIError.prototype);
  }
}

export class CompassAuthenticationError extends CompassAPIError {
  constructor(message: string = 'Authentication failed', response?: any) {
    super(message, 401, response);
    this.name = 'CompassAuthenticationError';
    Object.setPrototypeOf(this, CompassAuthenticationError.prototype);
  }
}

export class CompassNotFoundError extends CompassAPIError {
  constructor(message: string = 'Resource not found', response?: any) {
    super(message, 404, response);
    this.name = 'CompassNotFoundError';
    Object.setPrototypeOf(this, CompassNotFoundError.prototype);
  }
}

export class CompassRateLimitError extends CompassAPIError {
  constructor(message: string = 'Rate limit exceeded', response?: any) {
    super(message, 429, response);
    this.name = 'CompassRateLimitError';
    Object.setPrototypeOf(this, CompassRateLimitError.prototype);
  }
}

export class CompassValidationError extends CompassAPIError {
  constructor(message: string = 'Validation error', response?: any) {
    super(message, 422, response);
    this.name = 'CompassValidationError';
    Object.setPrototypeOf(this, CompassValidationError.prototype);
  }
}
