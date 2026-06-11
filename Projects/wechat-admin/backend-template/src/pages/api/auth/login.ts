import { NextApiRequest, NextApiResponse } from 'next'
import { comparePassword, generateToken } from '@/lib/auth'
import { queryOne } from '@/lib/db'
import { withRateLimit } from '@/middleware'

async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { email, password } = req.body

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' })
  }

  const user = await queryOne<{ id: number; email: string; password_hash: string; role: string }>(
    'SELECT id, email, password_hash, role FROM users WHERE email = ?',
    [email]
  )

  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' })
  }

  const isPasswordValid = await comparePassword(password, user.password_hash)

  if (!isPasswordValid) {
    return res.status(401).json({ error: 'Invalid credentials' })
  }

  const token = generateToken({
    userId: String(user.id),
    email: user.email,
    role: user.role as 'admin' | 'user'
  })

  res.status(200).json({
    success: true,
    data: {
      userId: user.id,
      email: user.email,
      role: user.role,
      token
    }
  })
}

export default withRateLimit(10, 60000)(handler)
