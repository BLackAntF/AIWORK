import { NextApiRequest, NextApiResponse } from 'next'
import { z } from 'zod'
import { ResultSetHeader } from 'mysql2'
import { hashPassword, generateToken } from '@/lib/auth'
import { query, queryOne } from '@/lib/db'
import { errorHandler, ApiError } from '@/lib/error'
import { withRateLimit } from '@/middleware'

const registerSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(6, 'Password must be at least 6 characters')
})

async function checkUserExists(email: string): Promise<boolean> {
  const user = await queryOne('SELECT id FROM users WHERE email = ?', [email])
  return !!user
}

async function createUser(email: string, passwordHash: string): Promise<number> {
  const [result] = await query<ResultSetHeader>(
    'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
    [email, passwordHash, 'user']
  )
  return result.insertId
}

async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    if (req.method !== 'POST') {
      throw new ApiError(405, 'Method not allowed')
    }

    const { email, password } = registerSchema.parse(req.body)
    const exists = await checkUserExists(email)

    if (exists) {
      throw new ApiError(400, 'User already exists')
    }

    const hashedPassword = await hashPassword(password)
    const userId = await createUser(email, hashedPassword)
    const token = generateToken({ userId: String(userId), email, role: 'user' })

    res.status(201).json({
      success: true,
      data: { userId, email, token }
    })
  } catch (error) {
    errorHandler(error, res)
  }
}

export default withRateLimit(10, 60000)(handler)
