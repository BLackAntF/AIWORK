import { NextApiResponse } from 'next'

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

  console.error('Unexpected error:', error)

  res.status(500).json({
    success: false,
    error: 'Internal server error'
  })
}
