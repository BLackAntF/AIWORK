import { NextApiRequest, NextApiResponse } from 'next'
import { verifyToken, hasPermission, Permission, JWTPayload } from '@/lib/auth'
import { errorHandler, ApiError } from '@/lib/error'

export interface AuthenticatedRequest extends NextApiRequest {
  user?: JWTPayload
}

type ApiHandler = (req: AuthenticatedRequest, res: NextApiResponse) => Promise<void> | void

function extractToken(req: NextApiRequest): string | undefined {
  return req.headers.authorization?.replace('Bearer ', '')
}

export function withAuth(handler: ApiHandler) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    try {
      const token = extractToken(req)
      if (!token) {
        throw new ApiError(401, 'Unauthorized')
      }
      const user = verifyToken(token)
      ;(req as AuthenticatedRequest).user = user
      return handler(req as AuthenticatedRequest, res)
    } catch (error) {
      return errorHandler(error, res)
    }
  }
}

export function withPermission(permission: Permission) {
  return (handler: ApiHandler) => {
    return withAuth(async (req, res) => {
      const user = req.user!
      if (!hasPermission(user.role, permission)) {
        throw new ApiError(403, 'Insufficient permissions')
      }
      return handler(req, res)
    })
  }
}
