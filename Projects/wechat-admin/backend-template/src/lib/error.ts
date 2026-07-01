import { NextApiResponse } from 'next'
import { ZodError } from 'zod'
import { logger } from './logger'

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message)
    Object.setPrototypeOf(this, ApiError.prototype)
  }
}

export function errorHandler(error: unknown, res: NextApiResponse): void {
  if (error instanceof ApiError) {
    res.status(error.statusCode).json({
      success: false,
      error: error.message
    })
    return
  }

  if (error instanceof ZodError) {
    const details = error.errors.map(e => `${e.path.join('.')}: ${e.message}`)
    res.status(400).json({
      success: false,
      error: 'Validation failed',
      details
    })
    return
  }

  logger.error('Unexpected error', error as Error)

  res.status(500).json({
    success: false,
    error: 'Internal server error'
  })
}
