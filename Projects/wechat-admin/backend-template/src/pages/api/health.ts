import { NextApiRequest, NextApiResponse } from 'next'
import { errorHandler, ApiError } from '@/lib/error'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    if (req.method !== 'GET') {
      throw new ApiError(405, 'Method not allowed')
    }

    res.status(200).json({
      success: true,
      message: 'Server is running',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    errorHandler(error, res)
  }
}
