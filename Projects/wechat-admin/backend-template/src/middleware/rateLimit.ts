import { NextApiRequest, NextApiResponse } from 'next'
import { limiter } from '@/lib/rateLimiter'

export function withRateLimit(maxRequests: number, windowMs: number) {
  return (handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void> | void) => {
    return async (req: NextApiRequest, res: NextApiResponse) => {
      const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'unknown'

      const allowed = await limiter.checkLimit(String(ip), maxRequests, windowMs)

      if (!allowed) {
        return res.status(429).json({ error: 'Rate limit exceeded' })
      }

      return handler(req, res)
    }
  }
}
