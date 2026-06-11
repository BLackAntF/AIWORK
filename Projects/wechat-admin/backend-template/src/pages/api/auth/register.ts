import { NextApiRequest, NextApiResponse } from 'next'
import { hashPassword, generateToken } from '@/lib/auth'
import { query, queryOne } from '@/lib/db'
import { withRateLimit } from '@/middleware'

async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { email, password } = req.body

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' })
  }

  const existingUser = await queryOne('SELECT id FROM users WHERE email = ?', [email])

  if (existingUser) {
    return res.status(400).json({ error: 'User already exists' })
  }

  const hashedPassword = await hashPassword(password)

  const [result] = await query(
    'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
    [email, hashedPassword, 'user']
  )

  const userId = (result as any).insertId

  const token = generateToken({ userId: String(userId), email, role: 'user' })

  res.status(201).json({
    success: true,
    data: {
      userId,
      email,
      token
    }
  })
}

export default withRateLimit(10, 60000)(handler)
