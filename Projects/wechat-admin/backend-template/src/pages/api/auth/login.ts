import { NextApiRequest, NextApiResponse } from 'next'
import { z } from 'zod'
import { comparePassword, generateToken, UserRole } from '@/lib/auth'
import { queryOne } from '@/lib/db'
import { errorHandler, ApiError } from '@/lib/error'
import { withRateLimit } from '@/middleware'

const loginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(6, 'Password must be at least 6 characters')
})

interface UserRow {
  id: number
  email: string
  password_hash: string
  role: string
}

async function findUserByEmail(email: string): Promise<UserRow | null> {
  return queryOne<UserRow>(
    'SELECT id, email, password_hash, role FROM users WHERE email = ?',
    [email]
  )
}

async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    if (req.method !== 'POST') {
      throw new ApiError(405, 'Method not allowed')
    }

    const { email, password } = loginSchema.parse(req.body)
    const user = await findUserByEmail(email)

    if (!user) {
      throw new ApiError(401, 'Invalid credentials')
    }

    const isValid = await comparePassword(password, user.password_hash)
    if (!isValid) {
      throw new ApiError(401, 'Invalid credentials')
    }

    const token = generateToken({
      userId: String(user.id),
      email: user.email,
      role: user.role as UserRole
    })

    res.status(200).json({
      success: true,
      data: { userId: user.id, email: user.email, role: user.role, token }
    })
  } catch (error) {
    errorHandler(error, res)
  }
}

export default withRateLimit(10, 60000)(handler)
