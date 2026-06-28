import { NextApiRequest, NextApiResponse } from 'next'
import { verifyToken, hasPermission, Permission } from '@/lib/auth'

export interface AuthenticatedRequest extends NextApiRequest {
  user?: {
    userId: string
    email: string
    role: 'admin' | 'user'
  }
}

export function withAuth(handler: (req: AuthenticatedRequest, res: NextApiResponse) => Promise<void> | void) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const token = req.headers.authorization?.replace('Bearer ', '')

    if (!token) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    try {
      const user = verifyToken(token)
      ;(req as AuthenticatedRequest).user = user
      return handler(req as AuthenticatedRequest, res)
    } catch {
      return res.status(401).json({ error: 'Invalid token' })
    }
  }
}

export function withPermission(permission: Permission) {
  return (handler: (req: AuthenticatedRequest, res: NextApiResponse) => Promise<void> | void) => {
    return async (req: NextApiRequest, res: NextApiResponse) => {
      const token = req.headers.authorization?.replace('Bearer ', '')

      if (!token) {
        return res.status(401).json({ error: 'Unauthorized' })
      }

      try {
        const user = verifyToken(token)

        if (!hasPermission({ id: user.userId, role: user.role }, permission)) {
          return res.status(403).json({ error: 'Insufficient permissions' })
        }

        ;(req as AuthenticatedRequest).user = user
        return handler(req as AuthenticatedRequest, res)
      } catch {
        return res.status(401).json({ error: 'Invalid token' })
      }
    }
  }
}
