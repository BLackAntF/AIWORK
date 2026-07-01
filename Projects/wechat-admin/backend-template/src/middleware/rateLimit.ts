import { NextApiRequest, NextApiResponse } from 'next'
import { limiter } from '@/lib/rateLimiter'
import { errorHandler, ApiError } from '@/lib/error'

type ApiHandler = (req: NextApiRequest, res: NextApiResponse) => Promise<void> | void

function getClientIp(req: NextApiRequest): string {
  return String(req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'unknown')
}

export function withRateLimit(maxRequests: number, windowMs: number) {
  return (handler: ApiHandler) => {
    return async (req: NextApiRequest, res: NextApiResponse) => {
      try {
        const ip = getClientIp(req)
        const allowed = await limiter.checkLimit(ip, maxRequests, windowMs)
        if (!allowed) {
          throw new ApiError(429, 'Rate limit exceeded')
        }
        return handler(req, res)
      } catch (error) {
        return errorHandler(error, res)
      }
    }
  }
}
