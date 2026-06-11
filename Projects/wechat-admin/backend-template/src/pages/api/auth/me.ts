import { NextApiResponse } from 'next'
import { withAuth, AuthenticatedRequest } from '@/middleware'

async function handler(req: AuthenticatedRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  res.status(200).json({
    success: true,
    data: {
      userId: req.user?.userId,
      email: req.user?.email,
      role: req.user?.role
    }
  })
}

export default withAuth(handler)
