import { NextApiResponse } from 'next'
import { withAuth, AuthenticatedRequest } from '@/middleware'
import { errorHandler, ApiError } from '@/lib/error'

async function handler(req: AuthenticatedRequest, res: NextApiResponse) {
  try {
    if (req.method !== 'GET') {
      throw new ApiError(405, 'Method not allowed')
    }

    res.status(200).json({
      success: true,
      data: {
        userId: req.user?.userId,
        email: req.user?.email,
        role: req.user?.role
      }
    })
  } catch (error) {
    errorHandler(error, res)
  }
}

export default withAuth(handler)
